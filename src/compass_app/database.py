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
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy import Column, Integer, String
from el.async_tools import synchronize

from compass_app.config import CONFIG

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp


_log = logging.getLogger(__name__)


# global DB base
class Base(DeclarativeBase):
    ...


class User(Base):
    """
    The user identifies a compass community member and is globally used
    by all subsystems.
    """
    __tablename__ = "compass_users"

    # TODO: remove the defaults here and replace that by proper user data fetching in the places
    # where it is needed or implement nullability if required.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    discord_id: Mapped[int] = mapped_column(String(32), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100))
    discriminator: Mapped[str] = mapped_column(String(4), default="")
    avatar: Mapped[str] = mapped_column(String(255), default="")
    access_token: Mapped[str] = mapped_column(String(255), default="")
    refresh_token: Mapped[str] = mapped_column(String(255), default="")

    @classmethod
    def from_discord(cls, user: discord.User | discord.Member):
        """Initializes a user from a discord.py User or Member object"""
        return cls(
            discord_id=user.id,
            username=user.name
        )


class CompassDB:

    def __init__(self, app: "CompassApp"):
        self._app = app
        self.engine = create_async_engine(CONFIG.DB_URL)
        
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

        async with AsyncSession(self.engine) as session:
            async with session.begin():
                yield session
    
    async def run(self) -> None:
        # first we do some database initialization
        try:
            # initialize tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # set db as ready so other subsystems can use it
            self._is_ready.set_result(True)
        except Exception as e:
            _log.warning(f"DB initialization failed: {e}")
            _log.warning("Subsystems that require the DB will not work.")
            self._is_ready.set_result(False)
            