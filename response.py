from ast import Num
import json
import requests


def data(log_id):
    log_json = requests.get(f"https://wvw.report/getJson?id={log_id}").json()
    fight_info = [log_json["duration"], log_json["fightName"][15:], len(log_json["targets"]), len(log_json["players"])]
    commander = ""
    player_names = [player["name"] for player in log_json["players"]]

    player_damage_info = []
    player_cleanse_info = []
    player_strip_info = []
    kills_info = []
    downs_info = []
    resses_info = []
    total_kills = 0
    total_deaths = 0
    total_damage_taken = 0
    total_damage_dealt = 0

    for player in log_json["players"]:
        if (player["hasCommanderTag"] == True) & ( player["statsAll"][0]["distToCom"] == 0):
            commander = f"{player['name']} ({player['account']})"

        target_damage = 0
        for target in player["dpsTargets"]:
            target_damage += target[0]["damage"]

        target_dps = round((target_damage / player["activeTimes"][0]) * 1000)

        kills_info.append((player["statsAll"][0]["killed"], player["profession"]))
        downs_info.append((player["statsAll"][0]["downed"], player["profession"]))
        resses_info.append((player["support"][0]["resurrects"], player["profession"]))
        total_kills += player["statsAll"][0]["killed"]
        total_deaths += player["defenses"][0]["deadCount"]
        total_damage_taken += player["defenses"][0]["damageTaken"]
        total_damage_dealt += target_damage

        player_damage_info.append(
            (target_damage, player["profession"], target_dps)
        )
        player_cleanse_info.append(
            (player["support"][0]["condiCleanse"], player["profession"])
        )
        player_strip_info.append(
            (player["support"][0]["boonStrips"], player["profession"])
        )

    player_damage_data = sorted(
        dict(zip(player_names, player_damage_info)).items(),
        key=lambda kv: kv[1],
        reverse=True,
    )

    player_cleanse_data = sorted(
        dict(zip(player_names, player_cleanse_info)).items(),
        key=lambda kv: kv[1],
        reverse=True,
    )

    player_strip_data = sorted(
        dict(zip(player_names, player_strip_info)).items(),
        key=lambda kv: kv[1],
        reverse=True,
    )

    kills_info = sorted(
        dict(zip(player_names, kills_info)).items(),
        key=lambda kv: kv[1],
        reverse=True,
    )

    downs_info = sorted(
        dict(zip(player_names, downs_info)).items(),
        key=lambda kv: kv[1],
        reverse=True,
    )

    resses_info = sorted(
        dict(zip(player_names, resses_info)).items(),
        key=lambda kv: kv[1],
        reverse=True,
    )

    return (
        player_damage_data,
        player_cleanse_data,
        player_strip_data,
        fight_info,
        commander,
        kills_info,
        downs_info,
        resses_info,
        total_kills,
        total_deaths,
        total_damage_taken,
        total_damage_dealt
    )


# def combat_time_format(ms):

#     x = ms // 1000
#     seconds = x % 60
#     x //= 60
#     minutes = x % 60

#     if seconds < 10:
#         seconds = "0" + str(seconds)

#     if minutes < 10:
#         minutes = "0" + str(minutes)

#     return minutes, seconds
