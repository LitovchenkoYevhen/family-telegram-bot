import sqlite3
from typing import List, Optional
from datetime import datetime
from ..models.transaction import Transaction

class Database:
    def __init__(self, db_path: str = "family_finances.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    user_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')
            conn.commit()

    def add_transaction(self, transaction: Transaction) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (amount, type, category, description, user_id, chat_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction.amount,
                transaction.type,
                transaction.category,
                transaction.description,
                transaction.user_id,
                transaction.chat_id,
                transaction.timestamp
            ))
            conn.commit()
            return cursor.lastrowid

    def get_transactions(self, chat_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Transaction]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT id, amount, type, category, description, user_id, chat_id, timestamp
                FROM transactions
                WHERE chat_id = ?
            '''
            params = [chat_id]

            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date)
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date)

            cursor.execute(query, params)
            return [
                Transaction(
                    id=row[0],
                    amount=row[1],
                    type=row[2],
                    category=row[3],
                    description=row[4],
                    user_id=row[5],
                    chat_id=row[6],
                    timestamp=datetime.fromisoformat(row[7])
                )
                for row in cursor.fetchall()
            ]

    def get_statistics(self, chat_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> dict:
        transactions = self.get_transactions(chat_id, start_date, end_date)
        
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