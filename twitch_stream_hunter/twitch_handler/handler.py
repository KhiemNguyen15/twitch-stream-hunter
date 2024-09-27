import logging
import requests


logger = logging.getLogger(__name__)


async def validate_token(access_token):
    try:
        response = requests.get(
            "https://id.twitch.tv/oauth2/validate",
            headers={
                "Authorization": f"OAuth {access_token}",
            },
        )

        return response.status_code == 200

    except Exception:
        logger.error("Error while validating access token.")
        return False


async def get_token(client_id, client_secret):
    try:
        response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
        )
        assert response.status_code == 200

        data = response.json()

        return data["access_token"]

    except Exception:
        logger.error("Error while getting access token.")
        return None


async def get_streams(game_id, client_id, access_token):
    try:
        response = requests.get(
            f"https://api.twitch.tv/helix/streams?game_id={game_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": client_id,
            },
        )
        assert response.status_code == 200

        data = response.json()

        return list(data["data"])

    except Exception:
        logger.error("Error while getting streams.")
        return None
