"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 17:48

Discord Bot subsystem entrypoint
"""

import os
import logging
import typing

import discord
from discord.ext import commands
from discord.ext.commands import errors
from discord.ext.commands.context import Context

from el.observable import filters
from el.async_tools import synchronize

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp

_log = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    def __init__(self, app: "CompassApp", **kwargs) -> None:
        self._app = app

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!", 
            intents=intents, 
            **kwargs
        )

    async def run(self) -> None:
        async with self:
            self._app.exited >> filters.call_if_true(synchronize(self.close))
            await self.start(self.TOKEN)

    @typing.override
    async def on_ready(self):
        _log.info(f"logged in as {self.user}")

        #await self.add_cog(AdminCommands(self))
        #await self.add_cog(AmogusCommands(self))

    @typing.override
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello to the Compass community!')

