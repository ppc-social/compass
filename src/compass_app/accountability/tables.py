"""
The Compass Community © 2025 - now
www.thecompass.diy
29.09.25, 21:57

database tables for accountability tracking
"""

from typing import Optional

import discord
from datetime import date, datetime, timezone, timedelta
from sqlmodel import SQLModel, Field, Relationship, BigInteger, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncAttrs

from compass_app.database import CompassUser


class AccountabilityPeriod(SQLModel, table=True):
    __tablename__ = "accountability_period"
    id: int = Field(primary_key=True)

    year: int
    week: int
    period_start: date
    period_end: date

    goal_channel_id: int | None = Field(sa_type=BigInteger, default=None)
    result_channel_id: int | None = Field(sa_type=BigInteger, default=None)

    entries: list["AccountabilityEntry"] = Relationship(back_populates="period")

    @classmethod
    def from_week(
        self, 
        year: int, 
        week: int,
    ):
        """
        Creates a new accountability period for the specified 
        calendar week or the current one.
        """
        
        # TODO: Fix this absolute bullshit of US year calculations.
        # This current botch might not even work for 2026 or any other
        # year than 2025, I don't even know. These fucking US weeks seem
        # to be impossible to calculate arrrr.... there doesn't even seem to be
        # a proper standard, some websites give an answer similar to ISO but with sunday
        # as first, others give one week earlier, and nothing makes any sense.
        # https://support.claris.com/s/article/ISO-Week-Number-Calculation-1503692914822?language=en_US
        # https://savvytime.com/current-week
        # https://chatgpt.com/share/68db1ce1-f96c-8001-b841-e3010c0aa1db
        # https://chatgpt.com/share/68db1cf2-4730-8001-b865-5052c50739e7
        # For compass we need the weird week where sunday is first day and
        # Sunday Jan. 5th 2025 is the first day of week 1 anyway, whatever
        # standard that is and the following is working for 2025.
        jan1 = datetime(year, 1, 1)
        # Find the Sunday on or before Jan 1
        days_to_sunday = jan1.weekday() + 1  # weekday(): Mon=0, Sun=6
        first_sunday = jan1 - timedelta(days=days_to_sunday % 7)
        
        # Calculate start and end dates of the requested week
        start_date = first_sunday + timedelta(weeks=week)
        end_date = start_date + timedelta(days=6)

        #today = date.today()
        ## weekday(): Monday=0 ... Sunday=6
        #weekday = today.weekday()
        ## find Sunday (start of week in US style)
        #sunday = today - datetime.timedelta(days=(weekday + 1) % 7)
        ## the next Saturday (end of week) is 6 days after Sunday
        #saturday = sunday + datetime.timedelta(days=6)
        
        return AccountabilityPeriod(
            year=year,
            week=week,
            period_start=start_date.date(),
            period_end=end_date.date(),
        )


class AccountabilityEntry(AsyncAttrs, SQLModel, table=True):
    __tablename__ = "accountability_entry"
    id: int = Field(primary_key=True)

    user_id: int = Field(foreign_key="compass_user.id")
    user: CompassUser = Relationship() # for now, no back population as we can't go from user to goal

    period_id: int = Field(foreign_key="accountability_period.id")
    period: AccountabilityPeriod = Relationship(back_populates="entries")
    
    goal_id: int | None = Field(foreign_key="accountability_goal.id", default=None)
    goal: Optional["AccountabilityGoal"] = Relationship(back_populates="entry")

    result_id: int | None = Field(foreign_key="accountability_result.id", default=None)
    result: Optional["AccountabilityResult"] = Relationship(back_populates="entry")

    @classmethod
    async def get_or_create(
        cls, 
        session: AsyncSession,
        period: AccountabilityPeriod,
        user: CompassUser,
    ):
        """Gets or creates an entry matching a user and period"""
        entry = await session.scalar(
            select(AccountabilityEntry).where(
                AccountabilityEntry.user == user,
                AccountabilityEntry.period == period
            )
        )
        if entry is None:
            entry = AccountabilityEntry(
                user=user,
                period=period,
            )
            session.add(entry)
        return entry


class AccountabilityGoal(SQLModel, table=True):
    __tablename__ = "accountability_goal"
    id: int = Field(primary_key=True)
    
    message_id: int = Field(sa_type=BigInteger, index=True)
    text: str
    date_created: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))

    entry: AccountabilityEntry = Relationship(back_populates="goal")


class AccountabilityResult(SQLModel, table=True):
    __tablename__ = "accountability_result"
    id: int = Field(primary_key=True)
    
    message_id: int | None = Field(sa_type=BigInteger, default=None, index=True)
    text: str = ""
    success_count: int | None = None
    fail_count: int | None = None
    date_created: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))

    entry: AccountabilityEntry = Relationship(back_populates="result")

    def update_count(self) -> None:
        """Updates success and fail count from text"""
        self.success_count = 0
        self.fail_count = 0
        # count both the discord or unicode representation of the emojis 
        self.success_count += self.text.count(":white_check_mark:")
        self.success_count += self.text.count("✅")
        self.fail_count += self.text.count(":x:")
        self.fail_count += self.text.count("❌")

    @property
    def ratio(self) -> float:
        return self.success_count / (self.success_count + self.fail_count)