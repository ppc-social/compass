"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 20:54

discord Cog for accountability subsystem
"""

import os
import typing
import logging

import discord
from discord import ChannelType
from discord.ext import commands
from el.async_tools import synchronize
from sqlmodel import select

from compass_app.database import User
from compass_app.config import CONFIG

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp

_log = logging.getLogger(__name__)


class AccountabilityCommands(
    commands.Cog,
    description="Commands for accountability tracking",
):

    def __init__(self, app: "CompassApp") -> None:
        super().__init__()
        self._app = app
        self._app.bot.on_message_cb.register(self.on_message)

        ## create webhooks for the accountability messages if they don't exist yet
        #self._app.bot.get_channel(CONFIG.ACCOUNTABILITY_CHANNEL_ID).webhooks

    @synchronize
    async def on_message(self, message: discord.Message) -> None:
        # we are only interested in messages of threads in the accountability channel
        if message.channel.type not in (ChannelType.public_thread, ChannelType.private_thread):
            return
        channel = message.channel.parent
        if channel is None or channel.id != CONFIG.ACCOUNTABILITY_CHANNEL_ID:
            return
        
        async with self._app.db.session() as session:
            user = await session.scalar(
                select(User).where(User.discord_id == message.author.id)
            )
            if user is None:
                user = User.from_discord(message.author)
                session.add(user)
            
            _log.info(f"Received accountability message in '{message.channel}' from '{message.author}' ({user}): '{message.content}'")

        

    @commands.hybrid_group()
    async def accountability(self, ctx: commands.Context):
        """
        Group for all accountability commands
        """
        pass

    @accountability.command()
    async def test(self, ctx: commands.Context):
        """
        Test Command
        """
        _log.info("Test Command executed")
        await ctx.reply(
            f"Hello from command (accountability)"
        )
        