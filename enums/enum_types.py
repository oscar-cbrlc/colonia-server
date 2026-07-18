from enum import IntEnum

class UserType(IntEnum):
    player = 1
    admin = 2

class TeamRole(IntEnum):
    member = 1
    moderator = 2
    leader = 3

class TeamAccess(IntEnum):
    public = 1
    private = 2

class AvatarItemType(IntEnum):
    head = 1
    neck = 2
    body = 3
    footwear = 4

class NotificationType(IntEnum):
    global_notification = 1
    join_team_request_recieved = 2
    join_team_request_accepted = 3
    join_team_request_denied = 4
    team_kick = 5
    warning = 6

class ObjectiveType(IntEnum):
    complete_distance = 1
    complete_time = 2
    complete_speed = 3
    complete_pace = 4

class Reward_Type(IntEnum):
    boost = 1
    avatar_Item = 2
    boost_and_item = 3

class Offer_Type(IntEnum):
    item = 1
    bundle = 2