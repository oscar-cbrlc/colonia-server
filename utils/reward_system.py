from sqlalchemy.orm import Session
from model import models
from config import settings
from crud.boost_inventory_crud import add_boost_to_inventory
from crud.avatar_inventory_crud import add_item_to_inventory
from crud.reward_crud import get_reward_by_id
from utils.user_leveling_system import give_user_xp
from enums.enum_types import Difficulty_Type, Reward_Type

def give_challenge_reward(db: Session, current_user: models.Users, db_challenge: models.Challenge):
    """Otorga al jugador la recompensa de un desafío."""
    reward_id = db_challenge.challenge_reward
    db_reward = get_reward_by_id(db, reward_id)

    reward_type = db_reward.reward_type
    match reward_type:
        case Reward_Type.boost:
            boost_id = db_reward.reward_boost
            boost_amount = db_reward.reward_amount
            add_boost_to_inventory(db, current_user, boost_id, boost_amount)

        case Reward_Type.avatar_Item:
            avatar_item_id = db_reward.reward_item
            add_item_to_inventory(db, current_user, avatar_item_id)

        case Reward_Type.boost_and_item:
            boost_id = db_reward.reward_boost
            avatar_item_id = db_reward.reward_item
            boost_amount = db_reward.reward_amount
            add_boost_to_inventory(db, current_user, boost_id, boost_amount)
            add_item_to_inventory(db, current_user, avatar_item_id)

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
    