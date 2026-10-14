from sqlalchemy.orm import Session
from model import models
from crud import (
    user_crud, 
    team_crud, 
    obtained_achievements_crud, 
    avatar_item_crud, 
    boost_crud, 
    reward_crud, 
    challenge_crud, 
    active_challenges_crud,
    started_challenges_crud
)
from schema.user_schema import (
    UserResponse,
    UserBaseResponse,
    UserAvatarResponse,
    UserStatsResponse,
    UserTeamResponse
)
from enums.enum_types import (
    TeamRole, 
    UserType, 
    Message_Type, 
    Boost_Type, 
    Achievement_Type, 
    Objective_Type, 
    Difficulty_Type, 
    AvatarItemType, 
    Reward_Type
)
from schema.team_schema import TeamMember
from schema.team_chat_schema import MessageUserResponse, MessageResponse
from schema.boost_schema import BoostResponse
from schema.boost_inventory_schema import BoostInventoryResponse
from schema.achievement_schema import AchievementResponse
from schema.challenge_schema import ChallengeResponse
from schema.active_challenges_schema import ActiveChallengeResponse
from schema.obtained_achievements_schema import AchievementDetails
from schema.avatar_item_schema import AvatarItemResponse
from schema.reward_schema import RewardResponse
from schema.started_challenges_schema import StartedChallengeResponse
from utils.user_leveling_system import get_user_level
from config import settings

def search_item_data(db: Session, item_id: int):
    return (
        db.query(models.AvatarItem)
        .filter(models.AvatarItem.avatar_item_id == item_id)
        .first()
    )

def get_user_data(db: Session, db_user: models.Users):
    """Obtener datos de un usuario para usar en Response"""

    # Todo - Implementar item_crud para obtener urls
    head_data = None
    neck_data = None
    body_data = None
    footwear_data = None
    if db_user.avatar_head is not None:
        avatar_item = search_item_data(db, db_user.avatar_head)
        if avatar_item is not None:
            head_data = avatar_item.item_url

    if db_user.avatar_neck is not None:
        avatar_item = search_item_data(db, db_user.avatar_neck)
        if avatar_item is not None:
            neck_data = avatar_item.item_url

    if db_user.avatar_body is not None:
        avatar_item = search_item_data(db, db_user.avatar_body)
        if avatar_item is not None:
            body_data = avatar_item.item_url

    if db_user.avatar_footwear is not None:
        avatar_item = search_item_data(db, db_user.avatar_footwear)
        if avatar_item is not None:
            footwear_data = avatar_item.item_url

    avatar = UserAvatarResponse(
        user_thumbnail = db_user.user_thumbnail,
        model_url = settings.model_url,
        avatar_head = head_data,
        avatar_neck = neck_data,
        avatar_body = body_data,
        avatar_footwear = footwear_data,
        avatar_color = db_user.avatar_color
    )
    user_level = get_user_level(db_user)
    stats = UserStatsResponse(
        user_xp = db_user.user_exp,
        user_level = user_level[0],
        total_distance = db_user.total_distance,
        total_time = db_user.total_time,
        total_attack = db_user.total_attack,
        total_defence = db_user.total_defence,
        territories_captured = db_user.territories_captured
    )

    team = None

    if db_user.user_team is not None:
        db_team = (
            db.query(models.Team)
            .filter(
                models.Team.team_id == db_user.user_team
            )
            .first()
        )

        if db_team:
            team = UserTeamResponse(
                team_id = db_team.team_id,
                team_name = db_team.team_name,
                team_role = TeamRole(db_user.team_role).name,
                team_color = db_team.team_color
            )

    return avatar, stats, team

def get_user_response(db: Session, db_user: models.Users):
    """Construye Response para usuario autentificado."""
    avatar, stats, team = get_user_data(db, db_user)
    user_level = get_user_level(db_user)
    obtained_achievements = get_obtained_achievements_data(db, db_user.user_id)
    locked_achievements = get_locked_achievements_data(db, db_user.user_id)
    achievements = obtained_achievements + locked_achievements

    return UserResponse(
        user_id = db_user.user_id,
        user_name = db_user.user_name,
        email = db_user.email,
        user_type = UserType(db_user.user_type).name,
        coin_amount = db_user.coin_amount,
        avatar = avatar,
        xp_for_next_level = user_level[1],
        stats = stats,
        team = team,
        achievements = achievements
    )

def get_user_base_response(db: Session, db_user: models.Users):
    """Construye Response para usuario."""
    avatar, stats, team = get_user_data(db ,db_user)
    achievements = get_obtained_achievements_data(db, db_user.user_id)

    return UserBaseResponse(
        user_id = db_user.user_id,
        user_name = db_user.user_name,
        avatar = avatar,
        stats = stats,
        team = team,
        achievements = achievements
    )

def build_team_member_response(user: models.Users):
    """Obtiene datos de los miembros de un equipo."""
    return TeamMember(
        user_id = user.user_id,
        user_name = user.user_name,
        user_thumbnail = user.user_thumbnail,
        team_role = TeamRole(user.team_role).name
    )

def build_team_data(db: Session, db_team: models.Team, details: bool = False):
    """Obtener los datos completos de un equipo para TeamResponse."""
    data = {
        "team_id": db_team.team_id,
        "team_name": db_team.team_name,
        "team_color": db_team.team_color,
        "is_public": db_team.is_public,
    }

    data["stats"] = team_crud.get_team_stats(db, db_team.team_id)

    if(details):
        data["team_description"] = db_team.team_description
        
        users = user_crud.get_all_team_users(db, db_team.team_id)
        data["members"] = [
            build_team_member_response(user)
            for user in users
        ]
    return data
    
def build_chat_message_data(db: Session, db_message: models.TeamChat):
    """Construye Response para mensaje de chat."""
    db_user = user_crud.get_user_by_id(db, db_message.user_id)

    user_role = None
    if db_user.user_team is not None:
        user_role = TeamRole(db_user.team_role).name

    user_data = MessageUserResponse(
        user_id = db_user.user_id,
        user_thumbnail = db_user.user_thumbnail,
        username = db_user.user_name,
        role = user_role
    )

    return MessageResponse(
        message_id = db_message.message_id,
        chat_message = db_message.chat_message,
        message_date = db_message.message_date,
        message_type = Message_Type(db_message.message_type).name,
        user = user_data
    )

def build_boost_response(db_boost: models.Boost):
    """Construye Response para potenciadores"""
    return BoostResponse(
        boost_id = db_boost.boost_id,
        boost_effect = db_boost.boost_effect,
        boost_type = Boost_Type(db_boost.boost_type).name
    )

def build_boost_inventory_response(db_inventory: models.BoostInventory, db_boost: models.Boost):
    """Construye Response para inventario de potenciadores de usuario."""

    return BoostInventoryResponse(
        boost_id = db_inventory.boost_id,
        boost_type = Boost_Type(db_boost.boost_type).name,
        inventory_quantity = db_inventory.boost_amount,
        boost_effect = db_boost.boost_effect
    )

def build_achievement_response(db_achievement: models.Achievement):
    """Contruye Response para logros de usuario."""

    return AchievementResponse(
        achievement_id = db_achievement.achievement_id,
        achievement_name = db_achievement.achievement_name,
        achievement_type = Achievement_Type(db_achievement.achievement_type).name,
        achievement_objective = db_achievement.achievement_objective
    )

def get_achievement_details(db_obtained_achievement: models.ObtainedAchievements, db_achievement: models.Achievement):
    """Obtiene detalles de un logro"""

    adquisition_date = None
    if db_obtained_achievement is not None:
        adquisition_date = db_obtained_achievement.achievement_acquisition_date

    return AchievementDetails(
        achievement_id = db_achievement.achievement_id,
        achievement_name = db_achievement.achievement_name,
        achievement_type = Achievement_Type(db_achievement.achievement_type).name,
        achievement_objective = db_achievement.achievement_objective,
        achievement_acquisition_date = adquisition_date
    )

def get_obtained_achievements_data(db: Session, user_id: int):
    """Obtiene los datos de los logros desbloqueados de un jugador"""
    obtained = obtained_achievements_crud.get_user_achievement_list(db, user_id)

    return  [
        get_achievement_details(obtained_achievement, achievement)
        for obtained_achievement, achievement in obtained
    ]

def get_locked_achievements_data(db: Session, user_id: int):
    """Obtiene los datos de los logros por desbloquear de un jugador"""
    locked = obtained_achievements_crud.get_locked_achievements(db, user_id)

    return [
        get_achievement_details(None, achievement)
        for achievement in locked
    ]

def build_avatar_item_response(db_item: models.AvatarItem):
    """Construye el Response de un item de avatar"""
    return AvatarItemResponse(
        avatar_item_id = db_item.avatar_item_id,
        item_name = db_item.item_name,
        item_type = AvatarItemType(db_item).name,
        item_image = db_item.item_image,
        item_url = db_item.item_url
    )

def get_reward_object_data(db: Session, objects_id: list[int | None], reward_type: int):
    """Obtiene los datos de un objeto de recompensa"""
    boost_data = None
    item_data = None
    match(reward_type):
        case Reward_Type.boost:
            db_boost = boost_crud.get_boost_by_id(db, objects_id[0])
            boost_data = build_boost_response(db_boost)

        case Reward_Type.avatar_Item:
            db_item = avatar_item_crud.get_item_by_id(db, objects_id[1])
            item_data = build_avatar_item_response(db_item)

        case Reward_Type.boost_and_item:
            db_boost = boost_crud.get_boost_by_id(db, objects_id[0])
            boost_data = build_boost_response(db_boost)

            db_item = avatar_item_crud.get_item_by_id(db, objects_id[1])
            item_data = build_avatar_item_response(db_item)

    return boost_data, item_data

def build_reward_response(db: Session, db_reward: models.Reward):
    "Obtiene los datos de una recompensa"
    boost_data, item_data = get_reward_object_data(
        db, [db_reward.reward_boost, db_reward.reward_item], db_reward.reward_type
    )

    return RewardResponse(
        reward_id = db_reward.reward_id,
        reward_type = Reward_Type(db_reward.reward_type).name,
        reward_amount = db_reward.reward_amount,
        reward_item = item_data,
        reward_boost = boost_data
    )

def build_challenge_response(db: Session, db_challenge: models.Challenge):
    """Contruye Response para un desafío."""
    db_reward = reward_crud.get_reward_by_id(db, db_challenge.challenge_reward)
    reward_data = build_reward_response(db, db_reward) 
    challenge_difficulty = db_challenge.challenge_difficulty

    return ChallengeResponse(
        challenge_id = db_challenge.challenge_id,
        challenge_name = db_challenge.challenge_name,
        challege_reward = reward_data,
        objective_type = Objective_Type(db_challenge.objective_type).name,
        objective_condition = db_challenge.objective_condition,
        challenge_difficulty = Difficulty_Type(challenge_difficulty).name,
        challenge_xp_reward = settings.challenge_exp_reward[challenge_difficulty - 1]
    )

def build_active_challenge_response(
        db: Session, 
        db_active_challenge: models.ActiveChallenges
    ):
    """Contruye Response para un desafío activo."""
    challenge_id = db_active_challenge.challenge_id
    db_challenge = challenge_crud.get_challenge_by_id(db, challenge_id)
    
    return ActiveChallengeResponse(
        active_challenge_id = db_active_challenge.active_challenge_id,
        challenge = build_challenge_response(db, db_challenge),
        challenge_start_date = db_active_challenge.challenge_start_date,
        challenge_end_date = db_active_challenge.challenge_end_date
    )

def build_started_challenge_response(
        db: Session, 
        db_started_challenge: models.StartedChallenges, 
        db_active_challenge: models.ActiveChallenges
    ):
    """Contruye Response un desafío iniciado por el jugador"""
    progress = 0
    is_complete = False
    
    if db_started_challenge is not None:
        progress = db_started_challenge.progress
        is_complete = db_started_challenge.is_complete

    if db_active_challenge is None:
            active_challenge_id = db_started_challenge.active_challenge_id
            db_active_challenge = active_challenges_crud.get_active_challenge_by_id(db, active_challenge_id)

    return StartedChallengeResponse(
        challenge = build_active_challenge_response(db, db_active_challenge),
        progress = progress,
        is_complete = is_complete
    )

def get_started_challenges_data(db: Session, current_user: models.Users):
    """Obtiene los datos de los desafíos iniciadospor el jugador"""
    started = started_challenges_crud.get_user_started_challenges(db, current_user)
    return  [
        build_started_challenge_response(db, started_challenges, active_challenges)
        for started_challenges, active_challenges in started
    ]

def get_active_challenges_data(db: Session, current_user: models.Users):
    """Obtiene los datos de los desafíos activos actualmente"""
    active = started_challenges_crud.get_active_challenges(db, current_user)
    return  [
        build_started_challenge_response(db, None, active_challenges)
        for active_challenges in active
    ]