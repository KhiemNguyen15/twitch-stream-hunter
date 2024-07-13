import aiohttp
import asyncio
import discord
import requests
import toml


config = toml.load("config.toml")

current_streams = set()


async def get_streams():
    try:
        twitch_config = config["Twitch"]

        response = requests.get(
            f"https://api.twitch.tv/helix/streams?game_id={twitch_config['game_id']}",
            headers={
                "Authorization": f"Bearer {twitch_config['access_token']}",
                "Client-Id": twitch_config["client_id"],
            },
        )
        assert response.status_code == 200

        data = response.json()

        return list(data["data"])

    except Exception:
        print("Error while getting streams.")
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
    loop = asyncio.get_event_loop()
    loop.create_task(every(300, check_streams))

    loop.run_forever()
