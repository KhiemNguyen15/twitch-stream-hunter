from datetime import datetime
import aiohttp
import asyncio
import discord
import logging
import requests
import toml


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=f"logs/logfile_{datetime.today().strftime('%Y-%m-%d')}.log",
    level=logging.DEBUG,
)

config = toml.load("config.toml")

current_streams = set()


async def get_access_token():
    twitch_config = config["Twitch"]

    try:
        response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": twitch_config["client_id"],
                "client_secret": twitch_config["client_secret"],
                "grant_type": "client_credentials",
            },
        )
        assert response.status_code == 200

        data = response.json()

        return data["access_token"]

    except Exception:
        logging.error("Error while getting access token.")
        return None


async def get_streams():
    twitch_config = config["Twitch"]

    try:
        access_token = await get_access_token()
        if not access_token:
            return None

        response = requests.get(
            f"https://api.twitch.tv/helix/streams?game_id={twitch_config['game_id']}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": twitch_config["client_id"],
            },
        )
        assert response.status_code == 200

        data = response.json()

        return list(data["data"])

    except Exception:
        logging.error("Error while getting streams.")
        return None


async def send_message(webhook, stream):
    with open("doe.jpeg", "rb") as f:
        embed_json = {
            "title": "New Stream!",
            "description": f"**{stream['user_name']}** is streaming Duelists of Eden at [twitch.tv/{stream['user_login']}](https://www.twitch.tv/{stream['user_login']})!",
            "color": 0x1A2430,
            "url": f"https://www.twitch.tv/{stream['user_login']}",
            "image": {"url": "attachment://doe.jpeg"},
        }
        embed = discord.Embed.from_dict(embed_json)
        file = discord.File(f)

        await webhook.send(
            embed=embed,
            file=file,
            username="Twitch Watcher",
            avatar_url="https://cdn.discordapp.com/emojis/533758117939511306.webp?size=96&quality=lossless",
        )


async def check_streams():
    streams = await get_streams()
    if not streams:
        return

    global current_streams
    new_streams = set()
    async with aiohttp.ClientSession() as session:
        webhooks = [
            discord.Webhook.from_url(url, session=session)
            for url in config["Webhook"]["urls"]
        ]

        for stream in streams:
            new_streams.add(stream["id"])

            if stream["id"] in current_streams:
                continue

            for webhook in webhooks:
                await send_message(webhook, stream)

    current_streams = new_streams


async def every(__seconds: float, func, *args, **kwargs):
    while True:
        await func(*args, **kwargs)
        await asyncio.sleep(__seconds)


if __name__ == "__main__":
    logging.info("Process started.")

    loop = asyncio.get_event_loop()
    loop.create_task(every(300, check_streams))

    loop.run_forever()
