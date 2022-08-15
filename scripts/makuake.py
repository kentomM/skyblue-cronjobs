import os
from datetime import datetime, timedelta

import requests
from slack_sdk.webhook import WebhookClient
from termcolor import colored
from bs4 import BeautifulSoup


threshold_day = os.environ.get("THRESHOLD_DAY", 1)
threshold = datetime.now() - timedelta(days=threshold_day)
slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL", None)
slack_channel = os.environ.get("SLACK_CHANNEL", None)
slack_username = os.environ.get("SLACK_USERNAME", None)
slack_user_icon = os.environ.get("SLACK_USER_ICON", None)
slack_client = WebhookClient(slack_webhook_url)

print("-"*10)
print(f"threshold day: {threshold}")
print(f"slack channel: {slack_channel}")
print(f"slack username: {slack_username}")
print(f"slack user icon: {slack_user_icon}")
if slack_webhook_url is None:
    print("disable slack notification")
else:
    print("enable slack notification")
print("-"*10)

res = requests.get("https://api.makuake.com/v2/projects", params={
    "page": 1,
    "per_page": 15,
    "tag_ids": 141,
})

try:
    data = res.json()
except:
    print(res.text)
    exit(1)
else:
    if not res.ok:
        print(data)
        exit(1)

for d in data["projects"]:
    name = d["title"]
    id = d["id"]
    is_new = d["is_new"]
    url = d["url"]

    if is_new:
        res = requests.get(url)
        bs = BeautifulSoup(res.text, 'html.parser')
        start_at_str = bs.select("meta[property='note:start_at']")[0]["content"]
        start_at = datetime.strptime(start_at_str, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)
    else:
        print(f"{name} is not new")
        continue

    print(f"check: {name} ({is_new}) {start_at}", end=" ")
    if threshold < start_at:
        msg = f"{name}のクラウドファンディングが始まりました\n{url}"

        if slack_webhook_url is None:
            print(colored("skip(slack disabled)", "red"))
            continue

        slack_client.send_dict({k: v for k, v in {
            "text": msg,
            "channel": slack_channel,
            "username": slack_username,
            "icon_emoji": slack_user_icon,
        }.items() if v is not None})
    else:
        print(colored("skip", "red"))
