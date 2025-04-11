import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from ..models.transaction import Base, Transaction

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'family_finances.db')
        
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        self._init_db()

    def _init_db(self):
        Base.metadata.create_all(self.engine)

    def add_transaction(self, transaction: Transaction) -> int:
        session = self.Session()
        try:
            session.add(transaction)
            session.commit()
            return transaction.id
        finally:
            session.close()

    def get_transactions(self, chat_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Transaction]:
        session = self.Session()
        try:
            query = session.query(Transaction).filter(Transaction.chat_id == chat_id)
            
            if start_date:
                query = query.filter(Transaction.timestamp >= start_date)
            if end_date:
                query = query.filter(Transaction.timestamp <= end_date)
            
            return query.all()
        finally:
            session.close()

    def get_statistics(self, chat_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> dict:
        session = self.Session()
        try:
            query = session.query(Transaction).filter(Transaction.chat_id == chat_id)
            
            if start_date:
                query = query.filter(Transaction.timestamp >= start_date)
            if end_date:
                query = query.filter(Transaction.timestamp <= end_date)
            
            transactions = query.all()
            
            total_income = sum(t.amount for t in transactions if t.type == 'income')
            total_expense = sum(t.amount for t in transactions if t.type == 'expense')
            
            categories = {}
            for t in transactions:
                if t.type not in categories:
                    categories[t.type] = {}
                if t.category not in categories[t.type]:
                    categories[t.type][t.category] = 0
                categories[t.type][t.category] += t.amount
            
            return {
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': total_income - total_expense,
                'categories': categories
            }
        finally:
            session.close() 