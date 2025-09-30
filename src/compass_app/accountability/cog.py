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
from sqlmodel import select, or_

from compass_app.database import CompassUser
from compass_app.config import CONFIG
from compass_app.errors import DuplicateError
from .tables import *

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

        ## create webhooks for the accountability messages if they don't exist yet
        #self._app.bot.get_channel(CONFIG.ACCOUNTABILITY_CHANNEL_ID).webhooks

    @commands.hybrid_group()
    async def accountability(self, ctx: commands.Context):
        """
        Group for all accountability commands
        """
        pass
        
    @accountability.command()
    async def start_period(
        self, 
        ctx: commands.Context,
        week: int | None = None,
        year: int | None = None,
    ):
        """
        Starts a new accountability period by creating it's goal setting thread.
        """
        today = date.today()
        if year is None:
            year = today.year
        if week is None:
            # compass accountability uses US-style week numbers
            # (%U: weeks start on Sunday)
            # TODO: this may break after 2025, maybe switch to ISO numbering after that?
            week = int(today.strftime("%U"))
        
        try:
            thread = await self._app.accountability.start_period(week, year)
        except DuplicateError:
            await ctx.reply(
                f"An accountability thread for week {week} of {year} already exists, can't create another one.",
                ephemeral=True
            )
            return
        await ctx.reply(
            f"Goal setting thread has been created: {thread.jump_url}",
            ephemeral=True
        )

    
    def _is_relevante_message(self, message: discord.Message) -> bool:
        """Checks whether `message` is relevant for accountability"""
        if message.author == self._app.bot.user:
            return False
        
        # we are only interested in messages of threads in the accountability channel
        if message.channel.type not in (ChannelType.public_thread, ChannelType.private_thread):
            return False
        channel = message.channel.parent
        if channel is None or channel.id != CONFIG.ACCOUNTABILITY_CHANNEL_ID:
            return False

        return True

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self._is_relevante_message(message):
            return

        async with self._app.db.session() as session:
            # get the accountability period this message belongs to
            period = (await session.exec(
                select(AccountabilityPeriod).where(or_(
                    AccountabilityPeriod.goal_channel_id == message.channel.id,
                    AccountabilityPeriod.result_channel_id == message.channel.id
                ))
            )).one_or_none()

            if period is None:
                # message not associated with any accountability thread -> ignore it
                return

            # goal setting message
            if period.goal_channel_id == message.channel.id:
                # TODO: continue here
                ...

            # result message
            else:
                ...


            user = await CompassUser.get_or_create_from_discord(session, message.author)
            
            _log.info(f"Received accountability message in '{message.channel}' from '{message.author}' ({user}): '{message.content}'")
    
    @commands.Cog.listener()
    async def on_message_edit(self, old: discord.Message, new: discord.Message):
        if not self._is_relevante_message(new):
            return
        
        _log.info(f"Message edit: {old.content} ({old.id}) -> {new.content} ({new.id})")

    @commands.Cog.listener()
    async def on_message_delete(self, old: discord.Message):
        if not self._is_relevante_message(old):
            return
        
        _log.info(f"Message delete: {old.content}")
        
