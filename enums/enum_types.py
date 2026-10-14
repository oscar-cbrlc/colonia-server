from enum import IntEnum

class UserType(IntEnum):
    player = 1
    admin = 2

class TeamRole(IntEnum):
    member = 1
    moderator = 2
    leader = 3

class AvatarItemType(IntEnum):
    head = 1
    neck = 2
    body = 3
    footwear = 4

class Notification_Type(IntEnum):
    global_notification = 1
    join_team_request_recieved = 2
    join_team_request_accepted = 3
    join_team_request_denied = 4
    team_kick = 5
    warning = 6

class Objective_Type(IntEnum):
    total_time = 1
    walk_time = 2
    run_time = 3
    bike_time = 4
    total_distance = 5
    walk_distance = 6
    run_distance = 7
    bike_distance = 8
    captured_territories = 9
    route = 10

class Achievement_Type(IntEnum):
    total_distance = 1
    total_time = 2
    captured_territories = 3 
    total_attack = 4
    total_defense = 5

class Reward_Type(IntEnum):
    boost = 1
    avatar_Item = 2
    boost_and_item = 3

class Offer_Type(IntEnum):
    item = 1
    bundle = 2

class Message_Type(IntEnum):
    user_message = 1
    team_join = 2
    team_exit = 3
    team_kick = 4

class Boost_Type(IntEnum):
    score = 1
    impact_area = 2
    impact_distance = 3

class Difficulty_Type(IntEnum):
    easy = 1
    normal = 2
    hard = 3

class Activity_Type(IntEnum):
    walk = 1
    run = 2
    bike = 3