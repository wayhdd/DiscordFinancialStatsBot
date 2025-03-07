from sqlalchemy import Column, String
from . import Base

class GuildConfig(Base):
    __tablename__ = 'guild_config'
    guild_id = Column(String, primary_key=True)
    channel_id = Column(String)
