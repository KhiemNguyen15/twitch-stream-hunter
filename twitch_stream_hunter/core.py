import asyncio
import json
import logging
import os

from database_handler.populate import populate_db
from dotenv import load_dotenv
from twitch_handler import handler
import aiohttp
import discord


logger = logging.getLogger(__name__)

load_dotenv()


async def send_message(webhook, stream):
    with open("doe.jpeg", "rb") as image:
        embed_json = {
            "title": "New Stream!",
            "description": f"**{stream['user_name']}** is streaming Duelists of Eden at [twitch.tv/{stream['user_login']}](https://www.twitch.tv/{stream['user_login']})!",
            "color": 0x1A2430,
            "url": f"https://www.twitch.tv/{stream['user_login']}",
            "image": {"url": "attachment://doe.jpeg"},
        }
        embed = discord.Embed.from_dict(embed_json)
        file = discord.File(image)

        await webhook.send(
            embed=embed,
            file=file,
            username="Twitch Watcher",
            avatar_url="https://cdn.discordapp.com/emojis/533758117939511306.webp?size=96&quality=lossless",
        )


async def check_streams():
    global access_token
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not await handler.validate_token(access_token):
        access_token = await handler.get_token(client_id, client_secret)

    with open("urls.json", "r") as data:
        webhook_objects = json.load(data)

    global current_streams
    new_streams = set()
    async with aiohttp.ClientSession() as session:
        for webhook_object in webhook_objects:
            webhook = discord.Webhook.from_url(webhook_object["url"], session=session)

            streams = await handler.get_streams(
                webhook_object["game_id"], client_id, access_token
            )
            if not streams:
                continue

            for stream in streams:
                new_streams.add(stream["id"])

                if stream["id"] in current_streams:
                    continue

                await send_message(webhook, stream)

    current_streams = new_streams


async def every(__seconds: float, func, *args, **kwargs):
    while True:
        await func(*args, **kwargs)
        await asyncio.sleep(__seconds)


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )

    logger.info("Process started.")

    global access_token
    global current_streams
    access_token = ""
    current_streams = set()

    url = os.getenv("API_URL")

    loop = asyncio.get_event_loop()
    loop.create_task(every(300, check_streams))
    loop.create_task(every(604800, populate_db, url))

    loop.run_forever()


if __name__ == "__main__":
    main()
