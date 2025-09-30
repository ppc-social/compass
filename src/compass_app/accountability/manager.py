"""
The Compass Community © 2025 - now
www.thecompass.diy
30.09.25, 02:30

Accountability manager
"""

import typing
import logging

from sqlmodel import select
from discord import Thread, ChannelType

from compass_app.config import CONFIG
from compass_app.errors import DuplicateError
from .tables import *

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp

_log = logging.getLogger(__name__)


class AccountabilityManager():
    def __init__(self, app: "CompassApp"):
        self._app = app

    async def run(self) -> None:
        ...
    
    async def start_period(
        self, 
        week: int,
        year: int,
    ) -> Thread:
        """
        Cerates a new accountability period and goal setting thread
        for it.

        Parameters
        ----------
        week : int
            calendar week for this accountability thread
        year : int
            year of the calendar week (needed in case this is still used after 2025)

        Returns
        -------
        Thread
            The discord thread that has been created.

        Raises
        ------
        DuplicateError
            A period for this year+week already exists
        other errors possible
        """
        async with self._app.db.session() as session:
            # check for duplicates
            duplicate = (await session.exec(
                select(AccountabilityPeriod).where(
                    AccountabilityPeriod.week == week,
                    AccountabilityPeriod.year == year,
                )
            )).one_or_none()
            if duplicate is not None:
                raise DuplicateError()
            
            # doesn't exist yet, so we create the period
            period = AccountabilityPeriod.from_week(year, week)
            
            # create thread and send some initial message to inform people about what to do
            channel = self._app.bot.get_channel(CONFIG.ACCOUNTABILITY_CHANNEL_ID)
            assert channel is not None, "Accountability channel must exits"
            thread = await channel.create_thread(
                name=f"Week {week} Accountability Setting 🎯",
                type=ChannelType.public_thread
            )
            await thread.send(
                f"""
                ## :information_source:  Tell us about the goals you want to be held accountable for by the community in week 39 of 2025 (1 message per user only).

                ## :sunny:  Whether you want to take a break, keep the same habit or start a new initiative the community accountability is here for you.
                """
            )
            if not thread:
                raise RuntimeError("Failed to create thread")
            period.goal_channel_id = thread.id
            session.add(period)

            return thread



