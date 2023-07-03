import os

import requests
from bs4 import BeautifulSoup


discord_webhook = os.environ.get("DISCORD_WEBHOOK", None)

wifi_url = "https://jp.candyhouse.co/products/new-wifi"

res = requests.get(wifi_url)
bs = BeautifulSoup(res.text, "html.parser")

button = bs.select("form button")[0]
button_text = button.getText()

if not button_text == "売り切れ":
    if discord_webhook is not None:
        body = f"{wifi_url} の在庫があります"
        res = requests.post(
            discord_webhook,
            data={
                "content": f"{body}",
            })
