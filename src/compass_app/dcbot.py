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
from el.callback_manager import CallbackManager

from compass_app.config import CONFIG
from compass_app.accountability.cog import AccountabilityCommands

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp

_log = logging.getLogger(__name__)



class DiscordBot(commands.Bot):

    def __init__(self, app: "CompassApp", **kwargs) -> None:
        self._app = app

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!", 
            intents=intents, 
            **kwargs
        )

        self.on_message_cb = CallbackManager[discord.Message]()

    async def run(self) -> None:
        async with self:
            self._app.exited >> filters.call_if_true(synchronize(self.close))
            await self.start(CONFIG.DISCORD_BOT_TOKEN)

    async def sync(self) -> int:
        """Syncs the commands to the target guild"""
        guild = self.get_guild(CONFIG.DISCORD_GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        return len(await self.tree.sync(guild=guild))

    async def sync_global(self) -> int:
        """Syncs the commands globally"""
        return len(await self.tree.sync())
        
    @typing.override
    async def on_ready(self):
        _log.info(f"logged in as {self.user}")

        await self.add_cog(AccountabilityCommands(self._app))

    @typing.override
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return
        
        # notify other subsystems who need message callbacks
        self.on_message_cb.notify_all(message)

        if message.content.startswith('Hello Loadstone'):
            await message.channel.send('Hello to the Compass community!')

        await super().on_message(message)


