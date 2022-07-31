# import json
import requests
import math
import plotly.express as px
import pandas as pd
from tqdm import tqdm

colour_map_refrence={
                "Guardian": "#9fc5e8",
                "Dragonhunter": "#3796ea",
                "Firebrand": "#1461a4",
                "Willbender": "#56cdd6",
                "Revenant": "#ad3636",
                "Herald": "#ad3636",
                "Renegade": "#ad3636",
                "Vindicator": "#ad3636",
                "Warrior": "#ebc53b",
                "Berserker": "#ebc53b",
                "Spellbreaker": "#ebc53b",
                "Bladesworn": "#ebc53b",
                "Engineer": "#cc9243",
                "Scrapper": "#e2c6ac",
                "Holosmith": "#cc9243",
                "Mechanist": "#cc9243",
                "Ranger": "#BDD966",
                "Druid": "#BDD966",
                "Soulbeast": "#BDD966",
                "Untamed": "#BDD966",
                "Thief": "#b57474",
                "Daredevil": "#b57474",
                "Deadeye": "#b57474",
                "Specter": "#b57474",
                "Elementalist": "#ed5426",
                "Tempest": "#e06666",
                "Weaver": "#ed5426",
                "Catalyst": "#ed5426",
                "Mesmer": " #c274e8",
                "Chronomancer": "#df8bf0",
                "Mirage": " #c274e8",
                "Virtuoso": " #c274e8",
                "Necromancer": "#21D379",
                "Reaper": "#21D379",
                "Scourge": "#93c47d",
                "Harbinger": "#21D379",
            }

def data(log_id):
    log_json = requests.get(f"https://wvw.report/getJson?id={log_id}").json()
    # log_json = json.load(open(log_id))
    fight_info = [log_json["duration"], log_json["fightName"][15:], len(log_json["targets"][1:]), len(log_json["players"])]
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

    for enemy in tqdm(log_json["targets"][1:], desc="Enemies", ncols=75):
        total_kills += len(enemy["combatReplayData"]["dead"])

    combat_time = math.ceil(log_json["targets"][0]["lastAware"] / 1000) + 1

    df = pd.DataFrame(columns=["Name", "Damage", "Time"])
    colour_map = {}

    for player in tqdm(log_json["players"], desc="Players", ncols=100):
        if (player["hasCommanderTag"] == True) & ( player["statsAll"][0]["distToCom"] == 0):
            commander = f"{player['name']} ({player['account']})"

        prev_damage = 0

        for i in range(combat_time):
            new_damage = player["damage1S"][0][i] - prev_damage
            prev_damage = player["damage1S"][0][i]
            player_data = [player["name"], new_damage, i]
            df.loc[len(df.index)] = player_data
        colour_map[player["name"]] = colour_map_refrence[player["profession"]]

        target_damage = 0
        for target in player["dpsTargets"]:
            target_damage += target[0]["damage"]

        kills = 0
        downs = 0
        for target in player["statsTargets"]:
            kills += target[0]["killed"]
            downs += target[0]["downed"]

        target_dps = round((target_damage / player["activeTimes"][0]) * 1000)

        resses_info.append((player["support"][0]["resurrects"], player["profession"]))
        kills_info.append((kills, player["profession"]))
        downs_info.append((downs, player["profession"]))
        total_deaths += len(player["combatReplayData"]["dead"])
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

    group_pos = []

    for player in player_damage_data:
        group_pos.append(player[0])

    print("Creating a damage graph!")
    fig = px.line(df, x="Time", y="Damage", color="Name", color_discrete_map = colour_map, line_group="Name", title="Spike Damage", render_mode="svg", line_shape="spline",
              category_orders={
                "Name": group_pos
              })
    fig.update_layout(legend=dict(orientation="h"))
    fig.update_traces(line=dict(smoothing=0.8, width=2))
    fig.write_image('damagegraph.png', width=1500, height=750)
    # fig.write_html("damagegraph.html")
    print("Damage graph done!")
    
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
