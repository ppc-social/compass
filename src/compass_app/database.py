"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 18:50

Database subsystem for data storage
"""

import os
import typing
import asyncio
import logging
import contextlib

import discord
from sqlmodel import SQLModel, Field, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import String, BigInteger
from sqlalchemy.ext.asyncio import create_async_engine
from el.async_tools import synchronize

from compass_app.config import CONFIG

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp


_log = logging.getLogger(__name__)


class CompassUser(SQLModel, table=True):
    """
    The user identifies a compass community member and is globally used
    by all subsystems.
    """
    __tablename__ = "compass_user"

    id: int                     = Field(primary_key=True, index=True)
    discord_id: int             = Field(sa_type=BigInteger, unique=True, index=True)
    username: str               = Field(sa_type=String(100))
    discriminator: str | None   = Field(sa_type=String(4))
    avatar: str | None          = Field(sa_type=String(255))
    access_token: str | None    = Field(sa_type=String(255))
    refresh_token: str | None   = Field(sa_type=String(255))

    @classmethod
    def from_discord(cls, user: discord.User | discord.Member):
        """Initializes a user from a discord.py User or Member object"""
        return CompassUser(
            discord_id=user.id,
            username=user.name,
            avatar=user.display_avatar.url,
        )

    @classmethod
    async def get_or_create_from_discord(
        cls, 
        session: AsyncSession, 
        dc_user: discord.User | discord.Member
    ):
        """Gets or creates the DB user from the associated discord user"""
        user = await session.scalar(
            select(CompassUser).where(CompassUser.discord_id == dc_user.id)
        )
        if user is None:
            user = CompassUser.from_discord(dc_user)
            session.add(user)
        return user




class CompassDB:

    def __init__(self, app: "CompassApp"):
        self._app = app
        self.engine = create_async_engine(CONFIG.DB_URL)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        
        self._is_ready: asyncio.Future[bool] = asyncio.get_event_loop().create_future()

    @contextlib.asynccontextmanager
    async def session(self):
        """Creates a new session and starts a transaction.

        This waits until the DB is ready.

        Yields
        ------
        AsyncSession
            session with an active transaction.
            As soon as the context manager exits the transaction is
            automatically committed or rolled back in case of errors.
        """
        # wait for db to become ready
        if not await self._is_ready:
            raise RuntimeError("Cannot access database because it failed to initialize")

        async with AsyncSession(self.engine, expire_on_commit=False) as session:
            async with session.begin():
                yield session
    
    async def run(self) -> None:
        # first we do some database initialization
        try:
            # initialize tables
            # This runs after all subsystems have been imported,
            # so it is safe to access the metadata here.
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)

            # set db as ready so other subsystems can use it
            self._is_ready.set_result(True)
        except Exception as e:
            _log.warning(f"DB initialization failed: {e}")
            _log.warning("Subsystems that require the DB will not work.")
            self._is_ready.set_result(False)
            