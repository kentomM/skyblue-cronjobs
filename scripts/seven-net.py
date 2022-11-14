import os
import time

import requests
from bs4 import BeautifulSoup


webhook = os.environ.get("DISCORD_WEBHOOK", None)
target_pages = [ f"https://7net.omni7.jp/detail/{x}" for x in os.environ.get("TARGET_PAGES", "").split(",") if x]

print(target_pages)

for url in target_pages:
    print("-"*10)
    print(url)

    res = requests.get(url)
    bs = BeautifulSoup(res.text, "html.parser")

    elm = bs.select_one("[title=予約受付終了]")
    header = bs.select_one("h1").text.strip()

    print(header, elm)

    if elm is None and webhook is not None:
        res = requests.post(
            webhook,
            data={
                "content": f"[{header}]({url}) が購入可能になりました",
            })

    time.sleep(1)
