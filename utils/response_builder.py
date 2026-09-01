from sqlalchemy.orm import Session
from model import models
from crud import user_crud, team_crud
from schema.user_schema import (
    UserResponse,
    UserBaseResponse,
    UserAvatarResponse,
    UserStatsResponse,
    UserTeamResponse
)
from schema.team_schema import TeamMember
from schema.team_chat_schema import MessageUserResponse, MessageResponse
from enums.enum_types import TeamRole, UserType
from config import settings

def search_item_data(db: Session, item_id: int):
    return (
        db.query(models.AvatarItem)
        .filter(models.AvatarItem.avatar_item_id == item_id)
        .first()
    )

def build_user_data(db: Session, db_user: models.Users):
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

    stats = UserStatsResponse(
        total_distance = db_user.total_distance,
        total_time = db_user.total_time
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
    """Construir Response para usuario autentificado."""
    avatar, stats, team = build_user_data(db, db_user)

    return UserResponse(
        user_id = db_user.user_id,
        user_name = db_user.user_name,
        email = db_user.email,
        user_type = UserType(db_user.user_type).name,
        coin_amount = db_user.coin_amount,
        avatar = avatar,
        stats = stats,
        team = team
    )

def get_user_base_response(db: Session, db_user: models.Users):
    """Construir Response para usuario."""
    avatar, stats, team = build_user_data(db ,db_user)

    return UserBaseResponse(
        user_id = db_user.user_id,
        user_name = db_user.user_name,
        avatar = avatar,
        stats = stats,
        team = team
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
    """Construir Response para mensaje de chat."""
    user_data = None
    if not db_message.is_from_system:
        db_user = user_crud.get_user_by_id(db, db_message.user_id)
        user_data = MessageUserResponse(
            user_id = db_user.user_id,
            user_thumbnail = db_user.user_thumbnail,
            username = db_user.user_name,
            role = TeamRole(db_user.team_role).name
        )

    return {
        "message_id": db_message.message_id,
        "chat_message": db_message.chat_message,
        "message_date": db_message.message_date,
        "is_from_system": db_message.is_from_system,
        "user": user_data
    }