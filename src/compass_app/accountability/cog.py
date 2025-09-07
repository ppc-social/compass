"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 20:54

discord Cog for accountability subsystem
"""

import typing
import logging

import discord
from discord.ext import commands

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp

_log = logging.getLogger(__name__)


class AccountabilityCommands(
    commands.Cog,
    description="Commands for accountability tracking",
):
    def __init__(self, bot) -> None:
        super().__init__()
        self._bot: commands.Bot = bot

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
        