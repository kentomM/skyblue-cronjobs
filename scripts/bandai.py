import os
import time

import requests
from bs4 import BeautifulSoup


webhook = os.environ.get("DISCORD_WEBHOOK", None)
target_pages = [ f"https://p-bandai.jp/item/{x}/" for x in os.environ.get("TARGET_PAGES", "").split(",") if x]
user_agent = os.environ.get("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")

print(target_pages)

headers = {
    "user-agent": user_agent,
}

for url in target_pages:
    print("-"*10)
    print(url)

    res = requests.get(url, headers=headers)
    bs = BeautifulSoup(res.text, "html.parser")

    header = bs.select_one("#box").text.strip()

    all_stock_out = [x.strip() for x in res.text.split("\n") if "all_stock_out" in x][0]

    print(header, all_stock_out)

    if "在庫無し" not in all_stock_out:
        msg = f"[{header}]({url}) が購入可能になりました"
        print(msg)

        if webhook is not None:
            res = requests.post(
                webhook,
                data={
                    "content": msg,
                })

    time.sleep(1)
