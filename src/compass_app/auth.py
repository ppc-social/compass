"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 18:49

User authentication portal to access the web-app.
"""

import os
import typing
import logging

import httpx
from urllib.parse import urlencode
from fastapi import Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import select

from compass_app.config import CONFIG
from compass_app.database import CompassUser

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp

_log = logging.getLogger(__name__)


class CompassAuth():

    DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize"
    DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
    DISCORD_API_URL = "https://discord.com/api/users/@me"

    def __init__(self, app: "CompassApp"):
        self._app = app

        @app.web.get("/login")
        async def login():
            params = {
                "client_id": CONFIG.DISCORD_CLIENT_ID,
                "redirect_uri": CONFIG.DISCORD_REDIRECT_URL,
                "response_type": "code",
                "scope": "identify email",
            }
            return RedirectResponse(f"{self.DISCORD_AUTH_URL}?{urlencode(params)}")

        @app.web.get("/callback")
        async def callback(code: str):
            # Exchange code for token
            data = {
                "client_id": CONFIG.DISCORD_CLIENT_ID,
                "client_secret": CONFIG.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": CONFIG.DISCORD_REDIRECT_URL,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            async with httpx.AsyncClient() as client:
                token_resp = await client.post(self.DISCORD_TOKEN_URL, data=data, headers=headers)
                token_data = token_resp.json()

                if "access_token" not in token_data:
                    raise HTTPException(status_code=400, detail="Failed to get access token")

                access_token = token_data["access_token"]

                # Get user info
                user_resp = await client.get(
                    self.DISCORD_API_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                user_data = user_resp.json()

            # Store user in DB
            async with app.db.session() as session:
                user = (await session.exec(
                    select(CompassUser).where(CompassUser.discord_id == user_data["id"])
                )).one_or_none()

                if user is not None:
                    user.access_token = access_token
                else:
                    user = CompassUser(
                        discord_id=user_data["id"],
                        username=user_data["username"],
                        discriminator=user_data["discriminator"],
                        avatar=user_data["avatar"],
                        access_token=access_token,
                        refresh_token=token_data.get("refresh_token")
                    )
                    session.add(user)

            return {"message": "Logged in successfully", "user": user_data}

    async def run(self) -> None:
        ...