import os
from datetime import datetime

import jpholiday
import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from slack_sdk.webhook import WebhookClient


def createChouseisan(name, comment, kouho):
    session = requests.Session()
    res = session.get("https://chouseisan.com/")
    bs = BeautifulSoup(res.text, "html.parser")

    token = bs.select_one("create-new-event-form")[":csrf"].replace("\"", "")

    res = session.post("https://chouseisan.com/schedule/newEvent/create", params={
        "_token": token,
        "name": name,
        "comment": comment,
        "kouho": kouho,
    })

    bs = BeautifulSoup(res.text, "html.parser")
    event_url = bs.select_one("#listUrl")

    return event_url["value"]

labels = ["月", "火", "水", "木", "金", "土", "日"]

discord_webhook = os.environ.get("DISCORD_WEBHOOK", None)
slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL", None)
slack_channel = os.environ.get("SLACK_CHANNEL", None)
slack_username = os.environ.get("SLACK_USERNAME", None)
slack_user_icon = os.environ.get("SLACK_USER_ICON", None)
slack_client = WebhookClient(slack_webhook_url)

today = datetime.now()
next_month_start = today + relativedelta(months=1, day=1)
next_month_end = today + relativedelta(months=2, day=1, days=-1)

holiday = [ x[0] for x in jpholiday.between(next_month_start, next_month_end)]
days = [ next_month_start + relativedelta(days=x) for x in range((next_month_end-next_month_start).days+1)]

suggestion_days = [x for x in days if x in holiday or x.weekday() in [5, 6]]

title = f"{next_month_start.month}月ボドゲ会"
description = "13時頃から適当に集まって任意解散"
kouho = "\n".join([ f"{d.month}/{d.day} ({labels[d.weekday()]}) 13:00-" for d in suggestion_days])

url = createChouseisan(title, description, kouho)

body = f"「{title}」のお知らせ\n{url}"

print(body)

if discord_webhook is not None:
    res = requests.post(
        discord_webhook,
        data={
            "content": f"{body}",
        })

if slack_webhook_url is not None:
    slack_client.send_dict({k: v for k, v in {
            "text": f"<!channel> {body}",
            "channel": slack_channel,
            "username": slack_username,
            "icon_emoji": slack_user_icon,
        }.items() if v is not None})
