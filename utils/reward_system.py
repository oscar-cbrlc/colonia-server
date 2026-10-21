from sqlalchemy.orm import Session
from model import models
from config import settings
from crud.boost_inventory_crud import add_boost_to_inventory
from crud.avatar_inventory_crud import add_item_to_inventory
from crud.boost_reward_crud import get_boosts_by_challenge_id
from utils.user_leveling_system import give_user_xp
from enums.enum_types import Difficulty_Type

def give_boost_reward(db: Session, current_user: models.Users, challenge_boost: models.ChallengeBoosts):
    """Otorga al jugador la recompensa de potenciadores de un desafío"""
    boost_id = challenge_boost.boost_id
    boost_amount = challenge_boost.boost_amount
    add_boost_to_inventory(db, current_user, boost_id, boost_amount)

def give_challenge_reward(db: Session, current_user: models.Users, db_challenge: models.Challenge):
    """Otorga al jugador la recompensa de un desafío."""

    boost_rewards = get_boosts_by_challenge_id(db, db_challenge.challenge_id)
    for challenge_boost, _  in boost_rewards:
        give_boost_reward(db, current_user, challenge_boost)

    if db_challenge.avatar_item_id is not None:
        add_item_to_inventory(db, current_user, db_challenge.avatar_item_id)

    challenge_difficulty = db_challenge.challenge_difficulty
    exp_reward = 0
    match challenge_difficulty:
        case Difficulty_Type.easy:
            exp_reward = settings.challenge_exp_reward[0]
        case Difficulty_Type.normal:
            exp_reward = settings.challenge_exp_reward[1]
        case Difficulty_Type.hard:
            exp_reward = settings.challenge_exp_reward[2]
            
    give_user_xp(current_user, exp_reward)
    