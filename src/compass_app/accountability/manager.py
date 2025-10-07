"""
The Compass Community © 2025 - now
www.thecompass.diy
30.09.25, 02:30

Accountability manager
"""

import typing
import logging
import asyncio
from datetime import datetime, time, timezone, timedelta

from sqlmodel import select
from discord import Thread, ChannelType
from el.errors import DuplicateError
from el.async_tools import synchronize

from .tables import *

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp

_log = logging.getLogger(__name__)


class AccountabilityManager():
    def __init__(self, app: "CompassApp"):
        self._app = app

    async def run(self) -> None:
        self._creation_automation()
        #self._scoring_automation()
    
    @synchronize
    async def _creation_automation(self) -> None:
        """
        Runs the accountability automation in the background, periodically
        checking whether it's time to start a new accountability period.
        This is in a task so it's instantly stopped on app exit.
        """
        while True:
            await asyncio.sleep(30)
            # if automation is disabled, do nothing
            if not self._app.settings.accountability_period_automation:
                continue
    
            # otherwise check if it's the right day
            now = datetime.now(timezone.utc)    # we use UTC time for this
            # here we use ISO weekdays
            if now.weekday() != self._app.settings.accountability_period_weekday:
                continue
            
            # create comparable datetime object 
            target_dt = datetime.combine(
                now.date(), 
                self._app.settings.accountability_period_time, 
                timezone.utc
            )
            
            # if we are before the target time do nothing
            if now < target_dt:
                continue
            
            # were after the target time.
            # calculate the difference between now and the set time
            # and see if we are within one minute of it to avoid 
            # running multiple times.
            td = now - target_dt
            if td > timedelta(minutes=1):
                continue
            
            # at this point we can end the previous period and start the next one
            year = now.year
            week = int(now.strftime("%U"))  # here we now have to use the US weeks bc of compass convention
            
            _log.info(f"Accountability automation triggered, ending week {week - 1} and starting week {week}")
            
            try:
                await self.end_period(week - 1, year)   # end last period
            except (DuplicateError, IndexError) as e:
                _log.warning(f"Failed to automatically end period for week {week - 1} of {year}: {e}")

            try:
                await self.start_period(week, year)
            except DuplicateError:
                # period for this week already exists, do nothing other than warn about it
                _log.warning(f"Attempted to automatically start period for week {week} of {year} but it exists already")
            
            # then we wait longer than 1 minute to ensure we don't re-trigger in the same one-minute window
            await asyncio.sleep(61)

    @synchronize
    async def _scoring_automation(self) -> None:
        """
        Runs the accountability scoring automation in the background, periodically
        checking whether it's time to score an accountability period.
        This is in a task so it's instantly stopped on app exit.
        """
        while True:
            await asyncio.sleep(30)
            # if automation is disabled, do nothing
            if not self._app.settings.accountability_scoring_automation:
                continue
    
            # otherwise check if it's the right day
            now = datetime.now(timezone.utc)    # we use UTC time for this
            # here we use ISO weekdays
            if now.weekday() != self._app.settings.accountability_scoring_weekday:
                continue
            
            # create comparable datetime object 
            target_dt = datetime.combine(
                now.date(), 
                self._app.settings.accountability_scoring_time, 
                timezone.utc
            )
            
            # if we are before the target time do nothing
            if now < target_dt:
                continue
            
            # were after the target time.
            # calculate the difference between now and the set time
            # and see if we are within one minute of it to avoid 
            # running multiple times.
            td = now - target_dt
            if td > timedelta(minutes=1):
                continue
            
            # at this point we can end the previous period and start the next one
            year = now.year
            week = int(now.strftime("%U")) - 1  # here we now have to use the US weeks bc of compass convention
            #                                ^ also we score the previous period 

            
            try:
                # TODO: run scoring if needed
                ...
            except (DuplicateError, IndexError) as e:
                _log.warning(f"Failed to score period for week {week} of {year}: {e}")

            # then we wait longer than 1 minute to ensure we don't re-trigger in the same time period
            await asyncio.sleep(61)

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
            channel = self._app.bot.get_channel(self._app.config.accountability_channel_id)
            assert channel is not None, "Accountability channel must exits"
            thread = await channel.create_thread(
                name=f"Week {week} Accountability Setting 🎯",
                type=ChannelType.public_thread
            )
            await thread.send(
                f"""
                ## :information_source:  Tell us about the goals you want to be held accountable for by the community in week {week} of {year} (1 message per user only).

                ## :sunny:  Whether you want to take a break, keep the same habit or start a new initiative the community accountability is here for you.
                """
            )
            if not thread:
                raise RuntimeError("Failed to create thread")
            period.goal_channel_id = thread.id
            session.add(period)

            return thread

    async def end_period(
        self, 
        week: int,
        year: int,
    ) -> Thread:
        """
        Ends an existing accountability period by creating it's
        results thread.

        Parameters
        ----------
        week : int
            calendar week of the period to end (and the number on the thread)
        year : int
            year of the calendar week (needed in case this is still used after 2025)

        Returns
        -------
        Thread
            The discord thread that has been created.

        Raises
        ------
        IndexError
            This period doesn't exist yet, so we can't end it
        DuplicateError
            The period is already ended and a results thread exists
        """
        async with self._app.db.session() as session:
            # find the period
            period = (await session.exec(
                select(AccountabilityPeriod).where(
                    AccountabilityPeriod.week == week,
                    AccountabilityPeriod.year == year,
                )
            )).one_or_none()
            if period is None:
                raise IndexError("Period to end doesn't exist")
            
            if period.result_channel_id is not None:
                raise DuplicateError("Period has already ended")

            # create result thread and send some initial message to inform people about what to do
            channel = self._app.bot.get_channel(self._app.config.accountability_channel_id)
            assert channel is not None, "Accountability channel must exits"
            thread = await channel.create_thread(
                name=f"Week {week} Accountability Check In ✅❌",
                type=ChannelType.public_thread
            )
            await thread.send(
                f"""
                ## :information_source:  How was week {week} for you? Tell us about the results for your goals using the :white_check_mark: symbol for success or the :x: symbol for failure. You can use more than one if you had multiple goals.
                """
            )
            if not thread:
                raise RuntimeError("Failed to create thread")
            period.result_channel_id = thread.id
            session.add(period)

            return thread


