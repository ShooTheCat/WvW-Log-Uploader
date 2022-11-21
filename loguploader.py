# -*- coding: utf-8 -*-
"""Log uploader for gw2 WvW arcdps logs"""
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import shutil
import requests
import json
from datetime import datetime
from numerize import numerize
import math
import plotly.express as px
import pandas as pd
from pprint import pprint
import time

with open("config.json") as config_file:
    upload_config = json.load(config_file)

colour_map_refrence = {
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


class Handler(FileSystemEventHandler):
    """Define which event's the observer should handle."""

    def __init__(self) -> None:
        self.log_number = 0

    def on_moved(self, event):
        """File has been moved."""
        if ".zevtc" in event.dest_path:
            self.log_number += 1
            event_path = event.dest_path
            log_name = rf'{event_path}'.split('\\')[-1]
            # \033[96m makes the text yellow in the output, \033[0m clears the formatting
            print(f"\033[96mLog #{self.log_number} created\033[0m")
            print(f"Name: {log_name}\n")

            upload_log(event_path, event)

    def on_created(self, event):
        """File has been created."""
        if ".zevtc" in event.src_path:
            self.log_number += 1
            event_path = event.src_path
            log_name = rf'{event_path}'.split('\\')[-1]

            print(f"Log #{self.log_number} created")
            print(f"Name: {log_name}\n")

            upload_log(event_path, event)


class LogObserver:
    """Handle observing file system changes."""
    log_path = upload_config["logPath"]

    def __init__(self) -> None:
        self.observer = Observer()

    def run_observer(self):
        """Run the file observer."""
        handler = Handler()
        self.observer.schedule(handler, self.log_path, recursive=False)

        self.observer.start()
        print("Watching for new log files.\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            self.observer.join()


class SquadPlayer:
    def __init__(self, char_name, profession, commander, damage_done, dps, kills, downs_created, cleanses, strips,
                 deaths, resurrects, damage_taken) -> None:
        self.name = char_name
        self.profession = profession
        self.commander = commander
        self.damage_done = damage_done
        self.dps = dps
        self.kills = kills
        self.downs = downs_created
        self.cleanses = cleanses
        self.strips = strips
        self.deaths = deaths
        self.resurrects = resurrects
        self.damage_taken = damage_taken

    def __repr__(self) -> str:
        return f"{self.name} ({self.profession[:4]})"


class DiscordUpload:
    """Format data and upload it to discord via a webhook"""

    def __init__(self, general_fight_info, squad_info, enemy_info):
        self.webhook_url = upload_config["webhookURL"]
        self.squad_info = squad_info
        self.general_fight_info = general_fight_info
        self.enemy_info = enemy_info
        self.embed_colours = {
            "Red Desert Borderlands": 12454410,
            "Blue Alpine Borderlands": 2197732,
            "Green Alpine Borderlands": 184871,
            "Eternal Battlegrounds": 16777215,
        }

    def format_data(self):
        """Format the squad data for displaying it in discord."""
        commander = ""

        for player in self.squad_info:
            if player.commander:
                commander = player.name

        embed_description = f"**[dps.report]({self.general_fight_info['link']})**" \
                            f"\n**Map**: {self.general_fight_info['map']}" \
                            f"\n**Commander**: {commander}" \
                            f"\n**Duration**: {self.general_fight_info['duration']}"
        embed_colour = [colour for fight_map, colour in self.embed_colours.items() if
                        fight_map == self.general_fight_info['map']]

        df = pd.DataFrame()
        df["Class"] = [player.profession[:4] for player in self.squad_info]
        df["Player"] = [player.name for player in self.squad_info]
        df["Damage"] = [player.damage_done for player in self.squad_info]
        df["DPS"] = [player.dps for player in self.squad_info]
        df["Strips"] = [player.strips for player in self.squad_info]
        df["Cleanses"] = [player.cleanses for player in self.squad_info]
        df["Kills"] = [player.kills for player in self.squad_info]
        df["Downs"] = [player.downs for player in self.squad_info]
        df["Resurrects"] = [player.resurrects for player in self.squad_info]

        column_list = ["Damage", "Cleanses", "Strips", "Downs", "Kills", "Resurrects"]
        discord_embed_field_strings = [self.format_discord_code_field_string(df, col) for col in column_list]

        squad_total_damage = numerize.numerize(sum(map(lambda player: player.damage_done, self.squad_info)), decimals=1)
        enemy_total_damage = numerize.numerize(self.enemy_info['enemy_damage'], decimals=1)
        general_info_string = " Allies: {:^4} | Kills: {:^3} | Damage dealt: {:^6}" \
                              "\n--------------------------------------------------" \
                              "\n Enemies: {:^3} | Kills: {:^3} | Damage dealt: {:^6}" \
                              .format(
                                    len(self.squad_info), sum(df['Kills']), squad_total_damage,
                                    self.enemy_info['amount'], self.enemy_info['total_kills'], enemy_total_damage)

        self.send_to_discord(*embed_colour, embed_description, discord_embed_field_strings, general_info_string)


    def format_discord_code_field_string(self, dataframe, column: str) -> str:
        df = dataframe.sort_values(by=[column], ascending=False)
        rows = {
            1: "Class",
            2: "Player",
            3: "Damage",
            4: "DPS",
            5: "Strips",
            6: "Cleanses",
            7: "Kills",
            8: "Downs",
            9: "Resurrects"
        }

        match column:
            case "Damage":
                df = df.head(10)
                discord_string = " {:<3} {:<8} {:<23} {}" \
                                 "\n--- -------- ----------------------- -----------------" \
                                 .format("#", "Class", "Player", "Damage (DPS)")

                for i, row in enumerate(df.itertuples()):
                    place = i + 1
                    profession = row[1]
                    pname = row[2]
                    damage = f"{numerize.numerize(row[3], decimals=1):<6}"
                    dps = f"{numerize.numerize(row[4], decimals=1)}"
                    discord_string += "\n {:<3} {:<8} {:<26} {} ({}/s)".format(place, profession, pname, damage, dps)
                return discord_string
            case _:
                df = df.head(7)

                discord_string = " {:<3} {:<8} {:<23} {:>8}" \
                                 "\n--- -------- ----------------------- -------------" \
                    .format("#", "Class", "Player", column)

                for i, row in enumerate(df.itertuples()):
                    place = i + 1
                    profession = row[1]
                    pname = row[2]
                    row_numb = 0

                    for key, value in rows.items():
                        if value == column:
                            row_numb = key
                            break
                    colmn = f"{numerize.numerize(row[row_numb]):<4}"
                    discord_string += "\n {:<3} {:<8} {:<23} {:>8}".format(place, profession, pname, colmn)
                return discord_string


    def send_to_discord(self, embed_colour, embed_description, embed_field_strings, general_info_string):
        """Send formatted player data to discord using a webhook."""
        embed_data = {
            "embeds": [
                {
                    "title": "Toxic Elitist Log",
                    "color": embed_colour,
                    # wvw.report/dps.report link, map the fight was on, commanders character and account name, fight duration
                    "description": embed_description,
                    "footer": {
                        "text": "Time of upload",
                        "icon_url": "https://wiki.guildwars2.com/images/6/68/Girly_quaggan_icon.png"
                    },
                    "image": {
                        "url": "attachment://damagegraph.png"
                    },
                    "timestamp": f"{datetime.utcnow()}",
                    "fields": [
                        {
                            "name": "General Info",
                            # Squad and Enemy numbers, kills, damage
                            "value": "```" + general_info_string + "```"
                        },
                        {
                            "name": "Damage",
                            # Top 10 squad damage dealers
                            "value": "```" + f"{embed_field_strings[0]}" + "```",
                        },
                        {
                            "name": "Cleanses",
                            # Top 7 squad cleanses
                            "value": "```" + f"{embed_field_strings[1]}" + "```",
                        },
                        {
                            "name": "Strips",
                            # Top 7 squad strips
                            "value": "```" + f"{embed_field_strings[2]}" + "```",
                        },

                        {
                            "name": "Downed",
                            # Top 10 squad donws generated
                            "value": "```" + f"{embed_field_strings[3]}" + "```"
                        },

                        {
                            "name": "Killed",
                            # Top 10 squad kills generated
                            "value": "```" + f"{embed_field_strings[4]}" + "```"
                        },

                        {
                            "name": "Resurrects",
                            # Top 5 squad allies resurrected
                            "value": "```" + f"{embed_field_strings[5]}" + "```"
                        }
                    ],
                }
            ]
        }

        files = {
            "payload_json": (None, json.dumps(embed_data))
        }

        with open("damagegraph.png", "rb") as f:
            files["_damagegraph.png"] = ("damagegraph.png", f.read())

        # \033[35m makes the text purple in the output, \033[0m clears the formatting
        print(f"\033[35mSending discord webhook.\033[0m")

        result = requests.post(self.webhook_url, files=files)

        if 200 <= result.status_code < 300:
            # \033[32m makes the text green in the output, \033[0m clears the formatting
            print(f"\033[32mWebhook sent!\033[0m")

        else:
            # \033[31m makes the text red in the output, \033[0m clears the formatting
            print(
                f"\033[31mWebhook not sent with {result.status_code}, response:\n{result.json()}!\033[0m"
            )


def upload_log(path: str, event) -> None:
    """Upload the created evtc files to dpsreport."""
    with open(path, "rb") as file:
        log_file = {"file": file}
        upload_url = "https://dps.report/uploadContent"
        upload_params = upload_config["uploadParams"]
        response = requests.post(
            upload_url, files=log_file, params=upload_params)

    if 200 <= response.status_code < 300:
        # Succeeded in uploading the log
        # \033[32m makes the text green in the output, \033[0m clears the formatting
        print(f"\033[32mLog has been uploaded!\033[0m")

        response_json = response.json()
        # \033[94m makes the text blue in the output, \033[0m clears the formatting
        print(f"\033[94mSending data for formatting.\033[0m")
        filtered_data = filter_json_data(response_json)
        disc_upload = DiscordUpload(filtered_data[0], filtered_data[1], filtered_data[2])
        disc_upload.format_data()

        # Delete the log file
        os.remove(f"{event.src_path}")
        # \033[32m makes the text green in the output, \033[0m clears the formatting
        print(f"\033[32mLog file has been deleted!\033[0m\n")

    else:
        # Log upload failed
        # \033[31m makes the text red in the output, \033[0m clears the formatting
        print("\033[31mCouldn't upload the log!\033[0m")
        pprint(response)
        print("\033[94mMoving log file to a different folder.\033[0m")

        shutil.move(path, upload_config["logPath"] + "/failed uploads")

        print("\033[32mLog moved to 'failed uploads' folder.\033[0m")


def filter_json_data(response: dict) -> tuple:
    """Filter the relevant json data gotten as a response from dpsreport.

        :param response:
                Json response from dps.report containing:
                        "id" = Internal dps.report ID
                        "permalink" = Generated report URL
                        "identifier" = Future Update
                        "uploadTime" = Upload date, unix time format
                        "encounterTime" = Encounter date from evtc, unix time format
                        "generator" = Report generator tool used
                        "generatorId" = Internal report generator id.
                        "generatorVersion" = Internal. Report generator version.
                        "language" = Language id from evtc. Can be en, fr, de, es, or zh.
                        "languageId" = Internal language ID, numeric.
                        "userToken" = Your userToken. See userToken documentation above.
                        "error" = Error messages upon uploading, set to null if none are encountered. Report may still be generated even with this set.
                        "encounter" = JSON Object, encounter statistics
                         - "uniqueId" = Encounter 'unique identifier', computed from instance ids. This attempts to uniquely identify raid attempts/encounters across users. This -WILL- be set to null if an identifier cannot be uniquely generated!
                         - "success" = If encounter was successful [boss kill] or not.
                         - "duration" = Time in seconds of encounter. This may not be accurate with server delays and evtc logging issues.
                         - "compDps" = Computed overall DPS of the group.
                         - "numberOfPlayers" = Number of players in the encounter
                         - "numberOfGroups" = Number of party/squad groups in the encounter
                         - "bossId" = Boss ID of encounter. See https://dps.report/docs/bossIds.txt
                         - "boss" = Boss name.
                         - "isCm" = Is encounter Challenge Mode enabled.
                         - "gw2Build" = GW2 client build
                         - "jsonAvailable" = Is extra encounter data available at the /getJson endpoint
                        "evtc" = evtc metadata object
                         - "type" = Should always return 'evtc'
                         - "version" = Version of ARCDPS evtc file was generated in
                         - "bossId" = Boss ID of encounter. Same as encounter->bossId - See https://dps.report/docs/bossIds.txt
                        "players" = Player objects, array. This may be empty on older arc versions.
                         - "display_name" = Login name of the player.
                         - "character_name" = Character name.
                         - "profession" = Profession ID. See https://api.guildwars2.com/v2/professions?ids=all
                         - "elite_spec" = Elite spec traitline ID. See https://api.guildwars2.com/v2/specializations?ids=all
                        "report"
                         - "anonymous" = true/false - If report was generated with anonimized fake players.
                         - "detailed"  = true/false - If report was generated with detailed players.
    """
    log_id = response["id"]
    fight_data_json = requests.get(
        f"https://wvw.report/getJson?id={log_id}").json()

    general_fight_information = {
        "duration": fight_data_json["duration"],
        "map": fight_data_json["fightName"][15:],
        "link": response["permalink"],
        "combat_time": math.ceil(fight_data_json["targets"][0]["lastAware"] / 1000) + 1
    }
    # Save the dps.report link into a file
    with open("dpsreportlinks.txt", 'a') as f:
        f.write(general_fight_information['link'] + "\n")

    squad_info = squad_information(fight_data_json["players"], general_fight_information["combat_time"])
    enemy_info = enemy_information(fight_data_json["targets"], squad_info)

    return general_fight_information, squad_info, enemy_info


def squad_information(player_data: list, combat_time: int) -> list:
    """
    Get information about the players in the squad.
    """
    squad_info = []
    damage_dataframe = pd.DataFrame(columns=["Name", "Damage", "Time"])
    colour_map = {}
    for player in player_data:
        commander = False

        if (player["hasCommanderTag"]) & (player["statsAll"][0]["distToCom"] == 0):
            commander = True

        name = player["name"]
        profession = player["profession"]
        damage_done = player_damage(player, combat_time)  # tuple containing damage and dps (damage, dps)
        strips = player["support"][0]["boonStrips"]
        cleanses = player["support"][0]["condiCleanse"]
        downs_and_kills = player_downs_and_kills(player)  # tuple containing kills and downs (kills, downs)
        deaths = len(player["combatReplayData"]["dead"])  # player["defenses"][0]["deadCount"]
        resurrects = player["support"][0]["resurrects"]
        damage_taken = player["defenses"][0]["damageTaken"]

        # char_name, profession, commander, damage_done, dps, kills, downs_created, cleanses, strips, deaths, resurrects, damage_taken
        player_object = SquadPlayer(
            name, profession, commander, damage_done[0], damage_done[1], downs_and_kills[0],
            downs_and_kills[1],
            cleanses, strips, deaths, resurrects, damage_taken
        )
        squad_info.append(player_object)

        prev_damage = 0

        for i in range(combat_time):
            new_damage = player["damage1S"][0][i] - prev_damage
            prev_damage = player["damage1S"][0][i]
            player_data = [player["name"], new_damage, i]
            damage_dataframe.loc[len(damage_dataframe.index)] = player_data

        colour_map[name] = colour_map_refrence[profession]
    create_spike_graph(damage_dataframe, colour_map, squad_info)

    return squad_info


def player_damage(player: dict, combat_time: int) -> tuple:
    """
    Calculate the total damage a player has done.
    
    Takes in the player dictionary from the json data and the combat time of the squad.
    Returns the total damage the player has done to enemy players.

    Adds the players damage per second to the dataframe for graphing.
    """
    target_damage = sum(map(lambda target: target[0]["damage"], player["dpsTargets"]))
    target_dps = round((target_damage / player["activeTimes"][0]) * 1000)
    return target_damage, target_dps


def player_downs_and_kills(player: dict) -> tuple:
    """
    Calculate the total kills and downs the player has generated.
    
    Takes in the player dictionary from the json data.
    Returns the total kills and downs the player has generated.
    """
    target_kills = sum(map(lambda target: target[0]["killed"], player["statsTargets"]))
    target_downs = sum(map(lambda target: target[0]["downed"], player["statsTargets"]))

    return target_kills, target_downs


def enemy_information(enemy_data: list, squad_data: list) -> dict:
    """
    Get information about the enemies of the squad.
    
    Returns a dictionary containing the number of total enemies the squad was in combat with and
    the number of enemies that died.
    """
    enemy_info = {
        "total_deaths": sum(map(lambda player: player.kills, squad_data)),
        "total_kills": sum(map(lambda player: player.deaths, squad_data)),
        "enemy_damage": sum(map(lambda player: player.damage_taken, squad_data)),
        "amount": len(enemy_data) - 1
    }

    return enemy_info


def create_spike_graph(damage_dataframe, colour_info: dict, squad_info: list) -> None:
    """Create a spike damage graph based on 1s damage intervals."""
    # \033[93m makes the text yellow in the output, \033[0m clears the formatting
    print("\033[93mCreating a damage graph!\033[0m")
    group_pos = [player.name for player in sorted(squad_info, key=lambda player: player.damage_done)]
    fig = px.line(damage_dataframe, x="Time", y="Damage", color="Name", color_discrete_map=colour_info, line_group="Name",
                  title="Spike Damage", render_mode="svg", line_shape="spline",
                  category_orders={
                      "Name": group_pos
                  })
    fig.update_layout(legend=dict(orientation="h"))
    fig.update_traces(line=dict(smoothing=0.5, width=2))
    fig.write_image('damagegraph.png', width=1500, height=750)
    # \033[93m makes the text yellow in the output, \033[0m clears the formatting
    print("\033[93mDamage graph done!\033[0m")


if __name__ == "__main__":
    LogObserver().run_observer()
