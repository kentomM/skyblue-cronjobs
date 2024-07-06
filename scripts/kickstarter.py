import json
import os
import urllib

from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver

from slack_sdk.webhook import WebhookClient


threshold_day = os.environ.get("THRESHOLD_DAY", 1)
threshold = datetime.now() - timedelta(days=threshold_day)
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL", 1)

slack_client = WebhookClient(slack_webhook_url) if slack_webhook_url else None

print("-"*10)
print(f"user-agent: {user_agent}")
print(f"threshold day: {threshold}")
print("-"*10)

params = {
    "category_id": 337,
    "sort": "newest",
    "seed": "2866362",
    "page": 1,
}

driver = webdriver.Remote(
    command_executor="http://selenium:4444/wd/hub",
    options=webdriver.ChromeOptions()
)
url = f"https://www.kickstarter.com/discover/advanced.json?{urllib.parse.urlencode(params)}"
driver.get(url)

try:
    data = json.loads(BeautifulSoup(driver.page_source, "html.parser").find("body").text)
    for project in data["projects"]:
        name = project["name"]
        launched_at = datetime.fromtimestamp(project["launched_at"])
        url = project["urls"]["web"]["project"]

        print(f"check: {name} ({launched_at})", end=" ")
        if threshold < launched_at:
            if slack_webhook_url is None:
                print("skip(slack disabled)")
                continue

            print("post")
            msg = f"Kickstarterで {name} のクラウドファンディングが開始しました\n{url}"
            slack_client.send(
                text=msg,
                unfurl_links=True,
            )
        else:
            print("skip")

except Exception as e:
    print(e)
    exit(1)
finally:
    driver.quit()
