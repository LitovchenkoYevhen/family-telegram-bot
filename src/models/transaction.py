from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Transaction:
    id: Optional[int]
    amount: float
    type: str  # 'income' или 'expense'
    category: str
    description: str
    user_id: int
    chat_id: int
    timestamp: datetime

    @classmethod
    def create_expense(cls, amount: float, category: str, description: str, user_id: int, chat_id: int) -> 'Transaction':
        return cls(
            id=None,
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
            id=None,
            amount=amount,
            type='income',
            category=category,
            description=description,
            user_id=user_id,
            chat_id=chat_id,
            timestamp=datetime.now()
        ) 