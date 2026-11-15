from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from model import models
from schema.territory_schema import TerritoryCreate, TerritoryOwnerResponse, TerritoryImpactResult
from schema.user_training_schema import UserStatsResult, UserTrainingCreate, TrainingResult
from schema.challenge_schema import Challenge_metrics
from crud.territory_crud import create_territory, get_locked_territory
from crud.user_training_crud import create_training, get_training_by_id, update_training_results
from crud.boost_inventory_crud import remove_boost_from_inventory
from routers.boosts import get_existing_boost
from utils.achievement_tracker import check_achievements
from utils.response_builder import build_achievement_response, build_started_challenge_response, build_boost_response
from utils.challenge_tracker import check_challenges
from utils.user_leveling_system import give_training_xp
from enums.enum_types import Boost_Type
from decimal import Decimal, ROUND_HALF_UP
from config import settings
import hashlib
import json
import traceback

def generate_training_hash(training_in: UserTrainingCreate) -> str:
    """Genera un hash usando la información de un entrenamiento"""
    payload = training_in.model_dump(
        mode="json",
        exclude={"training_uuid"}
    )

    # Ordenar territorios para mantener un hash consistente
    payload["territories"] = sorted(
        payload["territories"],
        key=lambda x: x["territory_id"]
    )

    normalized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()

def apply_points_to_territory(territory: models.Territory, user_team: int, points: Decimal) -> str:
    """Determina la acción realizada sobre el territorio y se realizan calculos de puntaje"""
    current_health = Decimal(territory.health_points or 0)

    if territory.team_id == user_team:
        territory.health_points = min(
            settings.max_territory_health,
            current_health + points)
        return "defend"

    remaining_health = current_health - points

    if remaining_health <= 0:
        territory.team_id = user_team
        territory.health_points = min(
            settings.max_territory_health,
            settings.base_territory_health + abs(remaining_health))
        return "capture"

    territory.health_points = remaining_health
    return "attack"

def round_points(points: Decimal) -> Decimal:
    return points.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

def get_challenge_metrics(training_in: UserTrainingCreate, territories_captured: int) -> Challenge_metrics:
    """Obtiene datos de todas las métricas de progreso para los desafíos"""

    territories_list = set()
    for territory in training_in.territories:
        territory_id = territory.territory_id
        territories_list.add(territory_id)

    return Challenge_metrics(
        total_time = training_in.training_time,
        walk_time = training_in.seconds_walk,
        run_time = training_in.seconds_run,
        bike_time = training_in.seconds_bike,
        total_distance = training_in.training_distance,
        walk_distance = training_in.meters_walk,
        run_distance = training_in.meters_run,
        bike_distance = training_in.meters_bike,
        captured_territories = territories_captured,
        traversed_territories = territories_list
    )

def process_user_training(
        db: Session,
        current_user: models.Users,
        user_training_in: UserTrainingCreate
    ) -> TrainingResult:
    """
    Procesa el entrenamiento de un usuario en una sola transaccion.
    Realiza cambios a territorios afectados durante el entrenamiento.
    Incrementa estadisticas del usuario y verifica su progreso en desafiós y logros.
    """
    territory_results: list[TerritoryImpactResult] = []
    training_attack_points = 0
    training_defence_points = 0
    territories_captured = 0
        
    try:
        # Bloquear al usuario
        locked_user = (
            db.query(models.Users)
            .filter(
                models.Users.user_id == current_user.user_id
            )
            .populate_existing()
            .with_for_update()
            .one()
        )

        if locked_user.user_team is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario no pertenece a ningún equipo."
            )

        # Insertar datos iniciales del entrenamiento
        training_hash = generate_training_hash(user_training_in)
        inserted_uuid = create_training(
            db,
            {
                "user_id": locked_user.user_id,
                "training_uuid": user_training_in.training_uuid,
                "training_distance": user_training_in.training_distance,
                "training_time": user_training_in.training_time,
                "started_at": user_training_in.started_at,
                "boost_id": user_training_in.boost_id,
                "seconds_walk": user_training_in.seconds_walk,
                "seconds_run": user_training_in.seconds_run,
                "seconds_bike": user_training_in.seconds_bike,
                "meters_walk": user_training_in.meters_walk,
                "meters_run": user_training_in.meters_run,
                "meters_bike": user_training_in.meters_bike,
                "payload_hash": training_hash,
            }
        )

        # Verificar si el entrenamiento actual no ha sido registrado anteriormente
        if inserted_uuid is None:
            existing_training = get_training_by_id(db, locked_user.user_id, user_training_in.training_uuid)
            if existing_training.payload_hash != training_hash:
                raise HTTPException(
                    status_code=409,
                    detail="El entrenamiento ya existe con datos diferentes."
                )

            if existing_training.processing_result is None:
                raise HTTPException(
                    status_code=500,
                    detail="El entrenamiento existente no tiene un resultado almacenado."
                )
            
            previous_result = existing_training.processing_result
            db.rollback()
            return TrainingResult.model_validate(previous_result)

        # Procesar uso de potenciadores
        score_multiplier = 1
        boost_id = user_training_in.boost_id
        boost_data = None
        if(boost_id is not None):
            db_boost = get_existing_boost(boost_id, db)
            removed = remove_boost_from_inventory(db, locked_user, boost_id)

            if removed is False:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Potenciador no disponible en inventario",
                )
            
            boost_data = build_boost_response(db_boost)
            if(db_boost.boost_type == Boost_Type.score):
                score_multiplier = db_boost.boost_effect

        # Procesar territorios afectados, orden fijo para reducir posibilidad de deadlocks
        territories = sorted(
            user_training_in.territories,
            key=lambda x: x.territory_id
        )

        for territory_input in territories:
            territory = get_locked_territory(db, territory_input.territory_id)

            if territory is None:
                new_territory = TerritoryCreate(
                    territory_id = territory_input.territory_id
                )
                territory = create_territory(db, new_territory)

            points = round_points(territory_input.points) * score_multiplier
            action = apply_points_to_territory(territory, locked_user.user_team, points)

            match action:
                case "defend":
                    training_defence_points += points
                case "attack":
                    training_attack_points += points
                case "capture":
                    territories_captured += 1
                    training_attack_points += points

            # Obtener información del equipo
            team = None
            if territory.team_id is not None:
                team = (
                    db.query(models.Team)
                    .filter(
                        models.Team.team_id ==
                        territory.team_id
                    )
                    .first()
                )

            team_response = None
            if team:
                team_response = TerritoryOwnerResponse(
                    team_id = team.team_id,
                    team_name = team.team_name,
                    team_color = team.team_color
                )

            territory_results.append(
                TerritoryImpactResult(
                    territory_id = territory.territory_id,
                    team = team_response,
                    health_points = territory.health_points,
                    action = action
                )
            )

        # Actualizar estadísticas del usuario
        locked_user.total_distance = (
            Decimal(locked_user.total_distance or 0)
            + user_training_in.training_distance
        )

        locked_user.total_time = (
            int(locked_user.total_time or 0)
            + user_training_in.training_time
        )

        locked_user.total_attack = (
            int(locked_user.total_attack or 0)
            + training_attack_points
        )

        locked_user.total_defence = (
            int(locked_user.total_defence or 0)
            + training_defence_points
        )
        locked_user.territories_captured = (
            int(locked_user.territories_captured or 0)
            + territories_captured
        )

        # Procesos de verificación de progreso en logros y desafiós
        unlocked_achievements = check_achievements(db, locked_user)
        challenge_progress = get_challenge_metrics(user_training_in, territories_captured)
        progressed_challenges = check_challenges(db, locked_user, challenge_progress)
        training = give_training_xp(locked_user, challenge_progress)
        
        achievements_results = [
            build_achievement_response(achievement)
            for achievement in unlocked_achievements
        ]

        challenges_results = [
            build_started_challenge_response(db, db_started_challenge, None)
            for db_started_challenge in progressed_challenges
        ]

        response = TrainingResult(
            training_uuid = user_training_in.training_uuid,
            user = UserStatsResult(
                user_id = locked_user.user_id,
                user_name = locked_user.user_name,
                total_distance = locked_user.total_distance,
                total_time = locked_user.total_time,
                total_territories = locked_user.territories_captured,
                total_attack = locked_user.total_attack,
                total_defence = locked_user.total_defence
            ),
            training = training,
            territories = territory_results,
            boost = boost_data,
            achievements = achievements_results,
            challenges = challenges_results
        )

        # Actualiza campos calculados para el entrenamiento registrado
        db_training = get_training_by_id(db, locked_user.user_id, user_training_in.training_uuid)
        update_training_results(
            db_training,
            captured_territories = territories_captured,
            training_attack = training_attack_points,
            training_defence = training_defence_points,
            processing_result=response.model_dump(mode="json")
        )

        db.commit()
        return response

    except Exception as Error:
        db.rollback()
        print(Error)
        traceback.print_exc()
        raise