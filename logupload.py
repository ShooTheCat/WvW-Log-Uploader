import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import formating
import json
from datetime import datetime
import pytz

if __name__ == "__main__":
    my_event_handler = FileSystemEventHandler()

     # Get data fromg config file
    with open("config.json") as config_file:
        upload_config = json.load(config_file)

    def on_moved(event):
        if ".zevtc" in event.dest_path:
            print(f"\nLog {event.dest_path} has been created!")

            print(f"Uploading the log to dps.report.")

            with open(f"{event.dest_path}", "rb") as f:
                log_file = {"file": f}
                upload_url = "https://dps.report/uploadContent"
                params = upload_config["uploadParams"] 
                response = requests.post(upload_url, files=log_file, params=params)

            if 200 <= response.status_code < 300:
                print(f"Log has been uploaded!")

                response_json = response.json()
                link = response_json["permalink"] # wvw.report/dps.report link
                log_id = response_json["id"] 

                print(f"Formating data for discord.")
                stats = formating.get_response(log_id)

                # Discord webhook
                webhook_url = upload_config["webhookURL"]

                data = {
                    "embeds": [
                        {
                            "title": "Toxic Elitist Log",
                            "color": 10354879,
                            "description": f"**[dps.report]({link})**\n**Map**: {stats[3][1]}\n**Commander**: {stats[4]}\n**Duration**: {stats[3][0]}", # wvw.report/dps.report link, map the fight was on, commanders character and account name, fight duration
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
                                    "value": "```" + f"{stats[8]}" + "```" # Squad and Enemy numbers, kills, damage
                                },
                                {
                                    "name": "Damage",
                                    "value": "```" + f"{stats[0]}" + "```", # Top 10 squad damage dealers
                                },
                                {
                                    "name": "Cleanses",
                                    "value": "```" + f"{stats[1]}" + "```", # Top 10 squad cleanses
                                },
                                {
                                    "name": "Strips",
                                    "value": "```" + f"{stats[2]}" + "```", # Top 10 squad strips
                                },
                                
                                {
                                    "name": "Downed",
                                    "value": "```" + f"{stats[6]}" + "```" # Top 10 squad donws generated
                                },
                                
                                {
                                    "name": "Killed",
                                    "value": "```" + f"{stats[5]}" + "```" # Top 10 squad kills generated
                                },
                                
                                {
                                    "name": "Resurrects",
                                    "value": "```" + f"{stats[7]}" + "```" # Top 5 squad allies resurrected
                                }
                            ],
                        }
                    ]
                }
                files = {}

                with open("newplot3.png", "rb") as f:
                    files["_newplot3.png"] = ("newplot3.png", f.read())

                files["payload_json"] = (None, json.dumps(data))

                print(f"Sending discord webhook.")

                result = requests.post(webhook_url, files=files)

                if 200 <= result.status_code < 300:
                    print(f"Webhook sent!")
                else:
                    print(
                        f"Webhook not sent with {result.status_code}, response:\n{result.json()}!"
                    )

                # Delete the log file
                os.remove(f"{event.dest_path}")
                print(f"Log file has been deleted!")
            else:
                # Log upload failed
                print("Couldn't upload the log!")
                print(response)
                print("Moving log file to a different folder.")

                shutil.move(event.dest_path, (path + "/failed uploads"))

                print("Log moved to 'failed uploads' folder.")

    my_event_handler.on_moved = on_moved

    # Path to WvW log file directory
    path = upload_config["logPath"]
    go_recursively = False # Don't check subdirectories 
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    my_observer.start()
    print("Watching for new files.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
