import os
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from termcolor import colored
from slack_sdk.webhook import WebhookClient


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

origin = "https://camp-fire.jp"

res = requests.get(f"{origin}/projects/search", params={
    "sort": "fresh",
    "word": "ボードゲーム",
    "category": "game",
    "project_status[]": "opened",
})

bs = BeautifulSoup(res.text, "html.parser")

for project in bs.select(".box-in"):
    name = project.select_one(".box-title > a > h4").get_text()
    url = origin + project.select_one(".box-title > a")["href"]
    # プログレスバーがない場合はサロン扱い
    is_salon = project.select_one(".bar") is None
 
    if is_salon:
        continue

    res = requests.get(url)
    start_at_str = BeautifulSoup(res.text, "html.parser").select_one("meta[property='note:start_at']")["content"]
    start_at = datetime.strptime(start_at_str, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)

    print(f"check: {name} {start_at}", end=" ")
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
