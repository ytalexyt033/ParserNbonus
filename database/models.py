from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    balance = Column(Integer, default=0)
    last_bonus_time = Column(DateTime)
    next_bonus_time = Column(DateTime)
    cookies = Column(String)  # Serialized cookies
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Account(username='{self.username}', balance={self.balance})>"