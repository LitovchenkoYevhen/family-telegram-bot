from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # 'income' или 'expense'
    category = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)

    @classmethod
    def create_expense(cls, amount: float, category: str, description: str, user_id: int, chat_id: int) -> 'Transaction':
        return cls(
            amount=amount,
            type='expense',
            category=category,
            description=description,
            user_id=user_id,
            chat_id=chat_id,
            timestamp=datetime.now()
        )

    @classmethod
    def create_income(cls, amount: float, category: str, description: str, user_id: int, chat_id: int) -> 'Transaction':
        return cls(
            amount=amount,
            type='income',
            category=category,
            description=description,
            user_id=user_id,
            chat_id=chat_id,
            timestamp=datetime.now()
        ) 