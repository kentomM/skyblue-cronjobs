import os
from datetime import datetime, timedelta

import requests
from slack_sdk.webhook import WebhookClient


ENV_PREFIX="CRONJOB_KICKSTARTER_"

threshold_day = os.environ.get(f"{ENV_PREFIX}THRESHOLD_DAY", 10)
user_agent = os.environ.get(f"{ENV_PREFIX}USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
slack_webhook_url = os.environ.get(f"{ENV_PREFIX}SLACK_WEBHOOK_URL", None)
slack_channel = os.environ.get(f"{ENV_PREFIX}SLACK_CHANNEL", None)
slack_username = os.environ.get(f"{ENV_PREFIX}SLACK_USERNAME", None)
slack_user_icon = os.environ.get(f"{ENV_PREFIX}SLACK_USER_ICON", None)
slack_client = WebhookClient(slack_webhook_url)

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

threshold = datetime.now() - timedelta(days=threshold_day)

for project in data["projects"]:
    name = project["name"]
    launched_at = datetime.fromtimestamp(project["launched_at"])
    url = project["urls"]["web"]["project"]

    print("check: ", name, threshold, launched_at)
    if threshold < launched_at:
        print("slack post: ", name)

        if slack_webhook_url is None:
            print("slack webhook url is None skipping")
            continue

        msg = f"{name} のクラウドファンディングが開始しました\n{url}"
        slack_client.send_dict({k: v for k, v in {
            "text": msg,
            "channel": slack_channel,
            "username": slack_username,
            "icon_emoji": slack_user_icon,
        }.items() if v is not None})
