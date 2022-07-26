# WvW Log Uploader

## Usage
Make sure you have python 3.10 or newer installed, set up the config file and run the loguploader.py file.<br/>
It will automatically detect new created log files and upload them to dps.report and send a short overview to a discord channel.<br/>
If the upload of the logs fails it will place them in a new folder, and you can manually upload them to the site or drag them to the original log folder while running the uploader to try again.


## Config
**In config.json replace**<br />
`"PATH/TO/LOG/DIRECTORY"` with the directory of your arcdps logs<br />
`"DISCORD WEBHOOK URL"` with the url of your [discord webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)<br />
`"DPS.REPORT USERTOKEN"` with an usertoken generated [here](https://dps.report/getUserToken).

**Example config**
```
"webhookURL": "https://discord.com/api/webhooks/123456789876543210/somerandomgiberish"
"logPath": "C:/Users/User/Documents/Guild Wars 2/addons/arcdps/arcdps.cbtlogs/WvW"
"uploadParams": 
        {
            "json": 1,
            "generator": "ei",
            "userToken": "nc7umunoufe12he3r69g9rwow9toxicok3",
            "detailedwvw": "true",
            "anonymous": "false"
        }
```

Description of the upload parameters from [dps report api](https://dps.report/api).
```
json=1 - Return only a JSON object, as defined below. [Recommend, not default]
generator=ei - What log generating tool to use. [Currently only supports 'ei' for Elite Insights]
userToken=% - Optional userToken to store previous uploads and future features.
anonymous=false - Set to 'true' to enable anonymized reports.
detailedwvw=false - Set to 'true' to enabled detailed WvW reports. This may break and return a 500 error with particularly long logs.
```
## TO-DO
Make a GUI<br/>
Rewrite it in C++ or Rust
