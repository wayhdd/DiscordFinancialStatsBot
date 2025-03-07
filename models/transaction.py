import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from . import Base

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    guild_id = Column(String)      # ID de la guild associée à la transaction
    user = Column(String)
    ticker = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    time = Column(DateTime, default=datetime.datetime.utcnow)
