import io
from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pandas as pd
from ..models.transaction import Transaction

class Visualizer:
    @staticmethod
    def create_pie_chart(transactions: List[Transaction], transaction_type: str) -> io.BytesIO:
        """Создает круговую диаграмму для расходов или доходов по категориям"""
        df = pd.DataFrame([
            {'category': t.category, 'amount': t.amount}
            for t in transactions if t.type == transaction_type
        ])
        
        if df.empty:
            return None

        plt.figure(figsize=(10, 8))
        plt.pie(df['amount'], labels=df['category'], autopct='%1.1f%%')
        plt.title(f'Распределение по категориям ({transaction_type})')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return buf

    @staticmethod
    def create_time_series(transactions: List[Transaction], days: int = 30) -> io.BytesIO:
        """Создает график расходов/доходов по времени"""
        df = pd.DataFrame([
            {
                'date': t.timestamp.date(),
                'amount': t.amount,
                'type': t.type
            }
            for t in transactions
        ])
        
        if df.empty:
            return None

        start_date = datetime.now().date() - timedelta(days=days)
        df = df[df['date'] >= start_date]
        
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x='date', y='amount', hue='type')
        plt.title('Динамика доходов и расходов')
        plt.xticks(rotation=45)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return buf

    @staticmethod
    def create_category_bar_chart(transactions: List[Transaction]) -> io.BytesIO:
        """Создает столбчатую диаграмму по категориям"""
        df = pd.DataFrame([
            {'category': t.category, 'amount': t.amount, 'type': t.type}
            for t in transactions
        ])
        
        if df.empty:
            return None

        plt.figure(figsize=(12, 6))
        sns.barplot(data=df, x='category', y='amount', hue='type')
        plt.title('Сравнение доходов и расходов по категориям')
        plt.xticks(rotation=45)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return buf 