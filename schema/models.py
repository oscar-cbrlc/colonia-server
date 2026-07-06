from typing import Optional
import datetime
import decimal

from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Boost(Base):
    __tablename__ = 'boost'
    __table_args__ = (
        PrimaryKeyConstraint('boost_id', name='boost_pkey'),
    )

    boost_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    boost_name: Mapped[str] = mapped_column(Text, nullable=False)
    boost_description: Mapped[str] = mapped_column(Text, nullable=False)
    boost_effect: Mapped[decimal.Decimal] = mapped_column(Numeric, nullable=False)
    boost_image: Mapped[str] = mapped_column(Text, nullable=False)

    reward: Mapped[list['Reward']] = relationship('Reward', back_populates='boost')
    boost_inventory: Mapped[list['BoostInventory']] = relationship('BoostInventory', back_populates='boost')


class Bundle(Base):
    __tablename__ = 'bundle'
    __table_args__ = (
        PrimaryKeyConstraint('bundle_id', name='bundle_pkey'),
    )

    bundle_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    bundle_name: Mapped[str] = mapped_column(Text, nullable=False)
    bundle_image: Mapped[str] = mapped_column(Text, nullable=False)

    avatar_item: Mapped[list['AvatarItem']] = relationship('AvatarItem', secondary='item_bundle', back_populates='bundle')
    store_catalog: Mapped[list['StoreCatalog']] = relationship('StoreCatalog', back_populates='bundle')


class NotificationType(Base):
    __tablename__ = 'notification_type'
    __table_args__ = (
        PrimaryKeyConstraint('notification_type_id', name='notification_type_pkey'),
    )

    notification_type_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    notification_type_name: Mapped[str] = mapped_column(Text, nullable=False)

    notification: Mapped[list['Notification']] = relationship('Notification', back_populates='notification_type_')


class ObjectiveType(Base):
    __tablename__ = 'objective_type'
    __table_args__ = (
        PrimaryKeyConstraint('objective_type_id', name='objective_type_pkey'),
    )

    objective_type_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    objective_type_name: Mapped[str] = mapped_column(Text, nullable=False)

    objective: Mapped[list['Objective']] = relationship('Objective', back_populates='objective_type_')


class OfferType(Base):
    __tablename__ = 'offer_type'
    __table_args__ = (
        PrimaryKeyConstraint('offer_type_id', name='offer_type_pkey'),
    )

    offer_type_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    offer_type_name: Mapped[str] = mapped_column(Text, nullable=False)

    store_catalog: Mapped[list['StoreCatalog']] = relationship('StoreCatalog', back_populates='offer_type_')


class RequestState(Base):
    __tablename__ = 'request_state'
    __table_args__ = (
        PrimaryKeyConstraint('request_state_id', name='request_state_pkey'),
    )

    request_state_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    request_state_name: Mapped[str] = mapped_column(Text, nullable=False)

    team_request: Mapped[list['TeamRequest']] = relationship('TeamRequest', back_populates='request_state_')


class RewardType(Base):
    __tablename__ = 'reward_type'
    __table_args__ = (
        PrimaryKeyConstraint('reward_type_id', name='reward_type_pkey'),
    )

    reward_type_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    reward_name: Mapped[str] = mapped_column(Text, nullable=False)

    reward: Mapped[list['Reward']] = relationship('Reward', back_populates='reward_type_')


class TeamAccessType(Base):
    __tablename__ = 'team_access_type'
    __table_args__ = (
        PrimaryKeyConstraint('access_type_id', name='team_access_type_pkey'),
    )

    access_type_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    access_type_name: Mapped[str] = mapped_column(Text, nullable=False)

    team: Mapped[list['Team']] = relationship('Team', back_populates='team_access_type')


class TeamRole(Base):
    __tablename__ = 'team_role'
    __table_args__ = (
        PrimaryKeyConstraint('team_role_id', name='team_role_pkey'),
    )

    team_role_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(Text, nullable=False)

    users: Mapped[list['Users']] = relationship('Users', back_populates='team_role_')


class Training(Base):
    __tablename__ = 'training'
    __table_args__ = (
        PrimaryKeyConstraint('training_id', name='training_pkey'),
    )

    training_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    training_name: Mapped[str] = mapped_column(Text, nullable=False)
    attack_points: Mapped[int] = mapped_column(Integer, nullable=False)
    defence_points: Mapped[int] = mapped_column(Integer, nullable=False)


class UserType(Base):
    __tablename__ = 'user_type'
    __table_args__ = (
        PrimaryKeyConstraint('user_type_id', name='user_type_pkey'),
    )

    user_type_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    user_type_name: Mapped[str] = mapped_column(Text, nullable=False)

    users: Mapped[list['Users']] = relationship('Users', back_populates='user_type_')


class AvatarItem(Base):
    __tablename__ = 'avatar_item'
    __table_args__ = (
        ForeignKeyConstraint(['item_type'], ['avatar_item_type.avatar_item_type_id'], ondelete='CASCADE', onupdate='CASCADE', name='item_type_fk'),
        PrimaryKeyConstraint('avatar_item_id', name='avatar_item_pkey')
    )

    avatar_item_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    item_name: Mapped[str] = mapped_column(Text, nullable=False)
    item_type: Mapped[int] = mapped_column(Integer, nullable=False)
    item_image: Mapped[str] = mapped_column(Text, nullable=False)

    avatar_item_type: Mapped['AvatarItemType'] = relationship('AvatarItemType', back_populates='avatar_item')
    bundle: Mapped[list['Bundle']] = relationship('Bundle', secondary='item_bundle', back_populates='avatar_item')
    reward: Mapped[list['Reward']] = relationship('Reward', back_populates='avatar_item')
    store_catalog: Mapped[list['StoreCatalog']] = relationship('StoreCatalog', back_populates='avatar_item')
    users_avatar_body: Mapped[list['Users']] = relationship('Users', foreign_keys='[Users.avatar_body]', back_populates='avatar_item')
    users_avatar_footwear: Mapped[list['Users']] = relationship('Users', foreign_keys='[Users.avatar_footwear]', back_populates='avatar_item_')
    users_avatar_head: Mapped[list['Users']] = relationship('Users', foreign_keys='[Users.avatar_head]', back_populates='avatar_item1')
    users_avatar_neck: Mapped[list['Users']] = relationship('Users', foreign_keys='[Users.avatar_neck]', back_populates='avatar_item2')
    avatar_inventory: Mapped[list['AvatarInventory']] = relationship('AvatarInventory', back_populates='avatar_item')


class Objective(Base):
    __tablename__ = 'objective'
    __table_args__ = (
        ForeignKeyConstraint(['objective_type'], ['objective_type.objective_type_id'], ondelete='CASCADE', onupdate='CASCADE', name='objective_type_fk'),
        PrimaryKeyConstraint('objective_id', name='objective_pkey')
    )

    objective_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    objective_type: Mapped[int] = mapped_column(Integer, nullable=False)
    objective_condition: Mapped[dict] = mapped_column(JSONB, nullable=False)

    objective_type_: Mapped['ObjectiveType'] = relationship('ObjectiveType', back_populates='objective')
    achievement: Mapped[list['Achievement']] = relationship('Achievement', back_populates='objective')
    challenge: Mapped[list['Challenge']] = relationship('Challenge', back_populates='objective')


class Team(Base):
    __tablename__ = 'team'
    __table_args__ = (
        ForeignKeyConstraint(['access_type'], ['team_access_type.access_type_id'], ondelete='SET DEFAULT', onupdate='CASCADE', name='team_access_fk'),
        PrimaryKeyConstraint('team_id', name='team_pkey')
    )

    team_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    team_name: Mapped[str] = mapped_column(Text, nullable=False)
    team_color: Mapped[int] = mapped_column(Integer, nullable=False)
    access_type: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    team_description: Mapped[Optional[str]] = mapped_column(Text)

    team_access_type: Mapped['TeamAccessType'] = relationship('TeamAccessType', back_populates='team')
    territory: Mapped[list['Territory']] = relationship('Territory', back_populates='team')
    users: Mapped[list['Users']] = relationship('Users', back_populates='team')
    team_chat: Mapped[list['TeamChat']] = relationship('TeamChat', back_populates='team')
    team_request: Mapped[list['TeamRequest']] = relationship('TeamRequest', back_populates='team')


class Achievement(Base):
    __tablename__ = 'achievement'
    __table_args__ = (
        ForeignKeyConstraint(['achievement_objective'], ['objective.objective_id'], ondelete='CASCADE', onupdate='CASCADE', name='achievement_objective_fk'),
        PrimaryKeyConstraint('achievement_id', name='achievement_pkey')
    )

    achievement_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    achievement_name: Mapped[str] = mapped_column(Text, nullable=False)
    achievement_description: Mapped[str] = mapped_column(Text, nullable=False)
    achievement_image: Mapped[str] = mapped_column(Text, nullable=False)
    achievement_objective: Mapped[int] = mapped_column(Integer, nullable=False)

    objective: Mapped['Objective'] = relationship('Objective', back_populates='achievement')
    obtained_achievements: Mapped[list['ObtainedAchievements']] = relationship('ObtainedAchievements', back_populates='achievement')


t_item_bundle = Table(
    'item_bundle', Base.metadata,
    Column('avatar_item_id', Integer, primary_key=True),
    Column('bundle_id', Integer, primary_key=True),
    ForeignKeyConstraint(['avatar_item_id'], ['avatar_item.avatar_item_id'], ondelete='CASCADE', onupdate='CASCADE', name='item_bundle_fk'),
    ForeignKeyConstraint(['bundle_id'], ['bundle.bundle_id'], ondelete='CASCADE', onupdate='CASCADE', name='bundle_id_fk'),
    PrimaryKeyConstraint('avatar_item_id', 'bundle_id', name='item_bundle_pkey')
)


class Reward(Base):
    __tablename__ = 'reward'
    __table_args__ = (
        ForeignKeyConstraint(['reward_boost'], ['boost.boost_id'], ondelete='CASCADE', onupdate='CASCADE', name='reward_boost_fk'),
        ForeignKeyConstraint(['reward_item'], ['avatar_item.avatar_item_id'], ondelete='CASCADE', onupdate='CASCADE', name='reward_item_fk'),
        ForeignKeyConstraint(['reward_type'], ['reward_type.reward_type_id'], ondelete='CASCADE', onupdate='CASCADE', name='reward_type_fk'),
        PrimaryKeyConstraint('reward_id', name='reward_pkey')
    )

    reward_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    reward_type: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_item: Mapped[Optional[int]] = mapped_column(Integer)
    reward_boost: Mapped[Optional[int]] = mapped_column(Integer)

    boost: Mapped[Optional['Boost']] = relationship('Boost', back_populates='reward')
    avatar_item: Mapped[Optional['AvatarItem']] = relationship('AvatarItem', back_populates='reward')
    reward_type_: Mapped['RewardType'] = relationship('RewardType', back_populates='reward')
    challenge: Mapped[list['Challenge']] = relationship('Challenge', back_populates='reward')


class StoreCatalog(Base):
    __tablename__ = 'store_catalog'
    __table_args__ = (
        ForeignKeyConstraint(['avatar_item_id'], ['avatar_item.avatar_item_id'], ondelete='CASCADE', onupdate='CASCADE', name='offer_item_fk'),
        ForeignKeyConstraint(['bundle_id'], ['bundle.bundle_id'], ondelete='CASCADE', onupdate='CASCADE', name='offer_bundle_fk'),
        ForeignKeyConstraint(['offer_type'], ['offer_type.offer_type_id'], ondelete='CASCADE', onupdate='CASCADE', name='offer_type_fk'),
        PrimaryKeyConstraint('offer_id', name='store_catalog_pkey')
    )

    offer_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    offer_name: Mapped[str] = mapped_column(Text, nullable=False)
    offer_type: Mapped[int] = mapped_column(Integer, nullable=False)
    offer_image: Mapped[str] = mapped_column(Text, nullable=False)
    offer_price: Mapped[int] = mapped_column(Integer, nullable=False)
    avatar_item_id: Mapped[Optional[int]] = mapped_column(Integer)
    bundle_id: Mapped[Optional[int]] = mapped_column(Integer)

    avatar_item: Mapped[Optional['AvatarItem']] = relationship('AvatarItem', back_populates='store_catalog')
    bundle: Mapped[Optional['Bundle']] = relationship('Bundle', back_populates='store_catalog')
    offer_type_: Mapped['OfferType'] = relationship('OfferType', back_populates='store_catalog')


class Territory(Base):
    __tablename__ = 'territory'
    __table_args__ = (
        ForeignKeyConstraint(['team_id'], ['team.team_id'], ondelete='SET NULL', onupdate='CASCADE', name='team_territory_fk'),
        PrimaryKeyConstraint('territory_id', name='territory_pkey')
    )

    territory_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    location: Mapped[dict] = mapped_column(JSONB, nullable=False)
    health_points: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[Optional[int]] = mapped_column(Integer)

    team: Mapped[Optional['Team']] = relationship('Team', back_populates='territory')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['avatar_body'], ['avatar_item.avatar_item_id'], ondelete='SET NULL', onupdate='CASCADE', name='user_avatar_body_fk'),
        ForeignKeyConstraint(['avatar_footwear'], ['avatar_item.avatar_item_id'], ondelete='SET NULL', onupdate='CASCADE', name='user_avatar_footwear_fk'),
        ForeignKeyConstraint(['avatar_head'], ['avatar_item.avatar_item_id'], ondelete='SET NULL', onupdate='CASCADE', name='user_avatar_head_fk'),
        ForeignKeyConstraint(['avatar_neck'], ['avatar_item.avatar_item_id'], ondelete='SET NULL', onupdate='CASCADE', name='user_avatar_neck_fk'),
        ForeignKeyConstraint(['team_role'], ['team_role.team_role_id'], ondelete='SET NULL', onupdate='CASCADE', name='user_team_role_fk'),
        ForeignKeyConstraint(['user_team'], ['team.team_id'], ondelete='SET NULL', onupdate='CASCADE', name='user_team_fk'),
        ForeignKeyConstraint(['user_type'], ['user_type.user_type_id'], ondelete='SET DEFAULT', onupdate='CASCADE', name='user_type_fk'),
        PrimaryKeyConstraint('user_id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key')
    )

    user_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    total_distance: Mapped[decimal.Decimal] = mapped_column(Numeric, nullable=False, server_default=text('0'))
    total_time: Mapped[decimal.Decimal] = mapped_column(Numeric, nullable=False, server_default=text('0'))
    user_type: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    avatar_color: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('13398016'))
    coin_amount: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    user_team: Mapped[Optional[int]] = mapped_column(Integer)
    team_role: Mapped[Optional[int]] = mapped_column(Integer)
    avatar_head: Mapped[Optional[int]] = mapped_column(Integer)
    avatar_neck: Mapped[Optional[int]] = mapped_column(Integer)
    avatar_body: Mapped[Optional[int]] = mapped_column(Integer)
    avatar_footwear: Mapped[Optional[int]] = mapped_column(Integer)
    user_thumbnail: Mapped[Optional[str]] = mapped_column(Text)

    avatar_item: Mapped[Optional['AvatarItem']] = relationship('AvatarItem', foreign_keys=[avatar_body], back_populates='users_avatar_body')
    avatar_item_: Mapped[Optional['AvatarItem']] = relationship('AvatarItem', foreign_keys=[avatar_footwear], back_populates='users_avatar_footwear')
    avatar_item1: Mapped[Optional['AvatarItem']] = relationship('AvatarItem', foreign_keys=[avatar_head], back_populates='users_avatar_head')
    avatar_item2: Mapped[Optional['AvatarItem']] = relationship('AvatarItem', foreign_keys=[avatar_neck], back_populates='users_avatar_neck')
    team_role_: Mapped[Optional['TeamRole']] = relationship('TeamRole', back_populates='users')
    team: Mapped[Optional['Team']] = relationship('Team', back_populates='users')
    user_type_: Mapped['UserType'] = relationship('UserType', back_populates='users')
    avatar_inventory: Mapped[list['AvatarInventory']] = relationship('AvatarInventory', back_populates='user')
    boost_inventory: Mapped[list['BoostInventory']] = relationship('BoostInventory', back_populates='user')
    notification: Mapped[list['Notification']] = relationship('Notification', back_populates='user')
    obtained_achievements: Mapped[list['ObtainedAchievements']] = relationship('ObtainedAchievements', back_populates='user')
    team_chat: Mapped[list['TeamChat']] = relationship('TeamChat', back_populates='user')
    team_request: Mapped[list['TeamRequest']] = relationship('TeamRequest', back_populates='user')
    started_challenges: Mapped[list['StartedChallenges']] = relationship('StartedChallenges', back_populates='user')


class AvatarInventory(Base):
    __tablename__ = 'avatar_inventory'
    __table_args__ = (
        ForeignKeyConstraint(['avatar_item_id'], ['avatar_item.avatar_item_id'], ondelete='CASCADE', onupdate='CASCADE', name='item_inventory_fk'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', onupdate='CASCADE', name='user_item_inventory_fk'),
        PrimaryKeyConstraint('avatar_item_id', 'user_id', name='avatar_inventory_pkey')
    )

    avatar_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_acquisition_date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    avatar_item: Mapped['AvatarItem'] = relationship('AvatarItem', back_populates='avatar_inventory')
    user: Mapped['Users'] = relationship('Users', back_populates='avatar_inventory')


class BoostInventory(Base):
    __tablename__ = 'boost_inventory'
    __table_args__ = (
        ForeignKeyConstraint(['boost_id'], ['boost.boost_id'], ondelete='CASCADE', onupdate='CASCADE', name='boost_inventory_fk'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', onupdate='CASCADE', name='user_boost_inventory_fk'),
        PrimaryKeyConstraint('boost_id', 'user_id', name='boost_inventory_pkey')
    )

    boost_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    boost_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    boost: Mapped['Boost'] = relationship('Boost', back_populates='boost_inventory')
    user: Mapped['Users'] = relationship('Users', back_populates='boost_inventory')


class Challenge(Base):
    __tablename__ = 'challenge'
    __table_args__ = (
        ForeignKeyConstraint(['challenge_objective'], ['objective.objective_id'], ondelete='CASCADE', onupdate='CASCADE', name='challenge_objective_fk'),
        ForeignKeyConstraint(['challenge_reward'], ['reward.reward_id'], ondelete='CASCADE', onupdate='CASCADE', name='challenge_reward_fk'),
        PrimaryKeyConstraint('challenge_id', name='challenge_pkey')
    )

    challenge_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    challenge_name: Mapped[str] = mapped_column(Text, nullable=False)
    challenge_description: Mapped[str] = mapped_column(Text, nullable=False)
    challenge_start_date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    challenge_end_date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    challenge_image: Mapped[str] = mapped_column(Text, nullable=False)
    challenge_reward: Mapped[int] = mapped_column(Integer, nullable=False)
    challenge_objective: Mapped[int] = mapped_column(Integer, nullable=False)

    objective: Mapped['Objective'] = relationship('Objective', back_populates='challenge')
    reward: Mapped['Reward'] = relationship('Reward', back_populates='challenge')
    started_challenges: Mapped[list['StartedChallenges']] = relationship('StartedChallenges', back_populates='challenge')


class Notification(Base):
    __tablename__ = 'notification'
    __table_args__ = (
        ForeignKeyConstraint(['notification_type'], ['notification_type.notification_type_id'], ondelete='CASCADE', onupdate='CASCADE', name='notification_type_fk'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', onupdate='CASCADE', name='user_notification_fk'),
        PrimaryKeyConstraint('notification_id', name='notification_pkey')
    )

    notification_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    notification_type: Mapped[int] = mapped_column(Integer, nullable=False)
    notification_message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    notification_type_: Mapped['NotificationType'] = relationship('NotificationType', back_populates='notification')
    user: Mapped['Users'] = relationship('Users', back_populates='notification')


class ObtainedAchievements(Base):
    __tablename__ = 'obtained_achievements'
    __table_args__ = (
        ForeignKeyConstraint(['achievement_id'], ['achievement.achievement_id'], ondelete='CASCADE', onupdate='CASCADE', name='achievement_obtained_fk'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', onupdate='CASCADE', name='user_achievement_fk'),
        PrimaryKeyConstraint('achievement_id', 'user_id', name='obtained_achievements_pkey')
    )

    achievement_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    achievement_acquisition_date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    achievement: Mapped['Achievement'] = relationship('Achievement', back_populates='obtained_achievements')
    user: Mapped['Users'] = relationship('Users', back_populates='obtained_achievements')


class TeamChat(Base):
    __tablename__ = 'team_chat'
    __table_args__ = (
        ForeignKeyConstraint(['team_id'], ['team.team_id'], ondelete='CASCADE', onupdate='CASCADE', name='team_chat_fk'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', onupdate='CASCADE', name='user_team_chat_fk'),
        PrimaryKeyConstraint('chat_id', name='team_chat_pkey')
    )

    chat_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_message: Mapped[str] = mapped_column(Text, nullable=False)
    message_date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    team: Mapped['Team'] = relationship('Team', back_populates='team_chat')
    user: Mapped['Users'] = relationship('Users', back_populates='team_chat')


class TeamRequest(Base):
    __tablename__ = 'team_request'
    __table_args__ = (
        ForeignKeyConstraint(['request_state'], ['request_state.request_state_id'], ondelete='CASCADE', onupdate='CASCADE', name='request_state_fk'),
        ForeignKeyConstraint(['team_id'], ['team.team_id'], ondelete='CASCADE', onupdate='CASCADE', name='request_team_fk'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', onupdate='CASCADE', name='request_user_fk'),
        PrimaryKeyConstraint('request_id', name='team_request_pkey')
    )

    request_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    request_state: Mapped[int] = mapped_column(Integer, nullable=False)

    request_state_: Mapped['RequestState'] = relationship('RequestState', back_populates='team_request')
    team: Mapped['Team'] = relationship('Team', back_populates='team_request')
    user: Mapped['Users'] = relationship('Users', back_populates='team_request')


class StartedChallenges(Base):
    __tablename__ = 'started_challenges'
    __table_args__ = (
        ForeignKeyConstraint(['challenge_id'], ['challenge.challenge_id'], ondelete='CASCADE', onupdate='CASCADE', name='challenge_started_fk'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', onupdate='CASCADE', name='user_challenge_fk'),
        PrimaryKeyConstraint('challenge_id', 'user_id', name='started_challenges_pkey')
    )

    challenge_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    progress: Mapped[int] = mapped_column(Integer, nullable=False)

    challenge: Mapped['Challenge'] = relationship('Challenge', back_populates='started_challenges')
    user: Mapped['Users'] = relationship('Users', back_populates='started_challenges')
