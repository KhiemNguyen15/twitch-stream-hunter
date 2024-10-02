import json

import requests


async def download_game_data():
    url = (
        "https://raw.githubusercontent.com/Nerothos/TwithGameList/master/game_info.json"
    )
    res = requests.get(url, allow_redirects=True)

    with open("data/game_info.json", "wb") as file:
        file.write(res.content)


async def populate_db(url):
    await download_game_data()

    with open("data/game_info.json", "r") as data:
        games = json.load(data)

    for game in games:
        body = {
            "id": int(game["id"]),
            "name": game["name"],
            "image_url": game["box_art_url"],
        }

        requests.post(url, body)
