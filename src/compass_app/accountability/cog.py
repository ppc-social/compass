"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 20:54

discord Cog for accountability subsystem
"""

import os
import enum
import typing
import logging
import asyncio
import datetime


import discord
from discord import ChannelType, app_commands
from discord.ext import commands
from el.async_tools import synchronize
from el.errors import DuplicateError
from sqlmodel import select, or_

from compass_app.database import CompassUser
from compass_app.config import CONFIG
from .tables import AccountabilityPeriod, AccountabilityEntry, AccountabilityGoal, AccountabilityResult

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp

_log = logging.getLogger(__name__)


class TimeTransformer(app_commands.Transformer):
    @typing.override
    async def transform(
        self, 
        interaction: discord.Interaction, 
        value: str
    ) -> datetime.time:
        return datetime.datetime.strptime(value, "%H:%M").time()


class Weekday(enum.Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6


class AccountabilityCommands(
    commands.Cog,
    description="Commands for accountability tracking",
):

    def __init__(self, app: "CompassApp") -> None:
        super().__init__()
        self._app = app

        ## create webhooks for the accountability messages if they don't exist yet
        # self._app.bot.get_channel(CONFIG.ACCOUNTABILITY_CHANNEL_ID).webhooks

    accountability = app_commands.Group(
        name="accountability",
        description="Commands for accountability tracking"
    )

    @accountability.command()
    async def start_period(
        self, 
        interaction: discord.Interaction,
        week: int | None = None,
        year: int | None = None,
    ):
        """
        Starts a new accountability period by creating it's goal setting thread.

        Parameters
        ----------
        week : int | None, optional
            Optional calendar week of the period to start, by default the current week
        year : int | None, optional
            Optional year of the week, by default the current year
        """
        # Thread creation might take a while
        await interaction.response.defer(ephemeral=True)

        today = datetime.date.today()
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
            await interaction.response.send_message(
                f"A goal setting thread for week {week} of {year} already exists, can't create another one.",
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"Goal setting thread has been created: {thread.jump_url}",
            ephemeral=True
        )

    @accountability.command()
    async def end_period(
        self, 
        interaction: discord.Interaction,
        week: int | None = None,
        year: int | None = None,
    ):
        """
        Ends an active accountability period by creating it's results thread.

        Parameters
        ----------
        week : int | None, optional
            Optional calendar week of the period to start, by default the last week
        year : int | None, optional
            Optional year of the week, by default the current year
        """
        # Thread creation might take a while
        await interaction.response.defer(ephemeral=True)

        today = datetime.date.today()
        if year is None:
            year = today.year
        if week is None:
            # compass accountability uses US-style week numbers
            # (%U: weeks start on Sunday)
            # TODO: this may break after 2025, maybe switch to ISO numbering after that?
            week = int(today.strftime("%U")) - 1

        try:
            thread = await self._app.accountability.end_period(week, year)
        except IndexError:
            await interaction.response.send_message(
                f"No accountability period exists for week {week} of {year} so it can't be ended.",
                ephemeral=True
            )
            return
        except DuplicateError:
            await interaction.response.send_message(
                f"The accountability period for week {week} of {year} has already ended and a thread already exists, can't create another one.",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            f"Results thread has been created: {thread.jump_url}",
            ephemeral=True
        )

    @accountability.command()
    async def reset_period(
        self, 
        interaction: discord.Interaction,
        week: int,
        year: int,
        delete_threads: bool = False,
    ):
        """
        Resets recorded accountability for the provided week+year

        Parameters
        ----------
        week : int
            Week to reset period for
        year : int
            Year of the week to reset period for
        delete_threads : bool
            Whether to also delete the discord threads or just the internal record (false by default)
        """
        # Thread deletion might take a while
        await interaction.response.defer(ephemeral=True)

        async with self._app.db.session() as session:
            # find the period
            period = (await session.exec(
                select(AccountabilityPeriod).where(
                    AccountabilityPeriod.week == week,
                    AccountabilityPeriod.year == year,
                )
            )).one_or_none()
            if period is None:
                await interaction.response.send_message(
                    f"No accountability period exists for week {week} of {year} so it can't be reset.",
                    ephemeral=True
                )
                return

            if delete_threads:
                try:
                    if period.goal_channel_id is not None:
                        # delete thread itself
                        ch = self._app.bot.get_channel(period.goal_channel_id)
                        if ch is not None:
                            await ch.delete()
                        # delete starter message
                        ach = self._app.bot.get_channel(CONFIG.ACCOUNTABILITY_CHANNEL_ID)
                        if ach is not None:
                            msg = await ach.fetch_message(period.goal_channel_id) # has same ID as thread
                            if msg is not None:
                                await msg.delete()
                    if period.result_channel_id is not None:
                        ch = self._app.bot.get_channel(period.result_channel_id)
                        if ch is not None:
                            await ch.delete()
                        # delete starter message
                        ach = self._app.bot.get_channel(CONFIG.ACCOUNTABILITY_CHANNEL_ID)
                        if ach is not None:
                            msg = await ach.fetch_message(period.result_channel_id) # has same ID as thread
                            if msg is not None:
                                await msg.delete()

                except discord.errors.Forbidden as e:
                    await interaction.response.send_message(
                        f"Failed to delete threads: {e}",
                        ephemeral=True
                    )
                    return

            await session.delete(period)

        await interaction.response.send_message(
            f"Accountability for week {week} of year {year} has been reset{", threads have been deleted." if delete_threads else "."}",
            ephemeral=True
        )

    @accountability.command()
    async def automation(
        self, 
        interaction: discord.Interaction,
        enabled: bool | None = None,
        weekday: Weekday | None = None,
        time: app_commands.Transform[datetime.time, TimeTransformer] | None = None,
    ):
        """
        Shows or configures the automatic accountability thread creation parameters.

        Parameters
        ----------
        enabled : bool | None, optional
            Whether to enable or disable automation, by default keeps previous
        weekday : app_commands.Choice[int] | None, optional
            On what day of the week to start a period, by default keeps previous
        time : time | None, optional
            At what time (UTC) to start a new period, by default keeps previous
        """
        if enabled is not None:
            self._app.settings.accountability_period_automation = enabled
        if weekday is not None:
            self._app.settings.accountability_period_weekday = weekday.value
        if time is not None:
            self._app.settings.accountability_period_time = time

        self._app.settings.model_save_to_disk()

        await interaction.response.send_message(
            f"Automatic accountability period creation at {self._app.settings.accountability_period_time.strftime("%H:%M")} every {Weekday(self._app.settings.accountability_period_weekday).name} is {"enabled :green_square:" if self._app.settings.accountability_period_automation else "disabled :red_square:"}.",
            ephemeral=True,
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
