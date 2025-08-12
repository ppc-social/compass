
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from sqlalchemy import Column, Integer, String
import os

class CompassDB():

    MARIADB_URL = os.getenv("MARIADB_URL")
    engine = create_async_engine(MARIADB_URL, echo=True)
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    Base = declarative_base()
    session = SessionLocal()

    class User(Base):
        __tablename__ = "compass_users"

        id = Column(Integer, primary_key=True, index=True)  # Local DB ID
        discord_id = Column(String(32), unique=True, index=True)
        username = Column(String(100))
        discriminator = Column(String(4))
        avatar = Column(String(255))
        access_token = Column(String(255))
        refresh_token = Column(String(255))

    async def get_db():
        async with SessionLocal() as session:
            yield session

    def __init__(self, app):
        pass

