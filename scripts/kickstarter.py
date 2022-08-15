import os
from datetime import datetime, timedelta

import requests
from slack_sdk.webhook import WebhookClient
from termcolor import colored


threshold_day = os.environ.get("THRESHOLD_DAY", 1)
threshold = datetime.now() - timedelta(days=threshold_day)
user_agent = os.environ.get("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL", None)
slack_channel = os.environ.get("SLACK_CHANNEL", None)
slack_username = os.environ.get("SLACK_USERNAME", None)
slack_user_icon = os.environ.get("SLACK_USER_ICON", None)
slack_client = WebhookClient(slack_webhook_url)

print("-"*10)
print(f"user-agent: {user_agent}")
print(f"threshold day: {threshold}")
print(f"slack channel: {slack_channel}")
print(f"slack username: {slack_username}")
print(f"slack user icon: {slack_user_icon}")
if slack_webhook_url is None:
    print("disable slack notification")
else:
    print("enable slack notification")
print("-"*10)

url = "https://www.kickstarter.com/discover/advanced"
session = requests.session()

params = {
    "category_id": 34,
    "woe_id": 23424856,
    "sort": "newest",
    "seed": "2733207",
    "page": 1,
    "format": "json",
}
headers = {
    "user-agent": user_agent,
    "authority": "www.kickstarter.com",
}

res = session.get(url, params=params, headers=headers)

try:
    data = res.json()
except:
    print(res.text)
    exit(1)

for project in data["projects"]:
    name = project["name"]
    launched_at = datetime.fromtimestamp(project["launched_at"])
    url = project["urls"]["web"]["project"]

    print(f"check: {name} ({launched_at})", end=" ")
    if threshold < launched_at:
        if slack_webhook_url is None:
            print(colored("skip(slack disabled)", "red"))
            continue

        print(colored("post", "green"))
        msg = f"{name} のクラウドファンディングが開始しました\n{url}"
        slack_client.send_dict({k: v for k, v in {
            "text": msg,
            "channel": slack_channel,
            "username": slack_username,
            "icon_emoji": slack_user_icon,
        }.items() if v is not None})
    else:
        print(colored("skip", "red"))
