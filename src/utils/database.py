import os
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models.transaction import Base, Transaction

logger = logging.getLogger(__name__)

def is_internal_url(url: str) -> bool:
    """Проверяет, является ли URL внутренним (postgres.railway.internal)"""
    return 'postgres.railway.internal' in url

def is_public_url(url: str) -> bool:
    """Проверяет, является ли URL публичным (ballast.proxy.rlwy.net)"""
    return 'ballast.proxy.rlwy.net' in url

class Database:
    def __init__(self):
        # Логируем все переменные окружения (безопасно, так как это только для отладки)
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith('RAILWAY_')}
        logger.info(f"Доступные переменные окружения: {list(env_vars.keys())}")
        
        # Проверяем наличие переменных окружения
        database_url = os.getenv('DATABASE_URL')
        database_public_url = os.getenv('DATABASE_PUBLIC_URL')
        
        logger.info("Проверка переменных окружения для подключения к базе данных")
        
        if not database_url and not database_public_url:
            logger.error("DATABASE_URL и DATABASE_PUBLIC_URL не найдены!")
            logger.error("Проверьте, что PostgreSQL сервис и сервис с ботом находятся в одном проекте")
            raise ValueError("DATABASE_URL и DATABASE_PUBLIC_URL не найдены в переменных окружения")
        
        # Выбираем URL в зависимости от доступности
        if database_url and database_public_url:
            logger.info("Найдены оба URL базы данных:")
            logger.info(f"Внутренний URL (postgres.railway.internal): {is_internal_url(database_url)}")
            logger.info(f"Публичный URL (ballast.proxy.rlwy.net): {is_public_url(database_public_url)}")
            # Используем внутренний URL, так как мы в Railway
            database_url = database_url
            logger.info("Использую внутренний URL (postgres.railway.internal)")
        elif database_url:
            database_url = database_url
            logger.info("Использую доступный DATABASE_URL")
        else:
            database_url = database_public_url
            logger.info("Использую доступный DATABASE_PUBLIC_URL")
            
        # Удаляем 'postgres://' и заменяем на 'postgresql://' если необходимо
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
            logger.info("URL базы данных обновлен для использования postgresql://")
        
        # Логируем только хост и порт для безопасности
        db_parts = database_url.split('@')
        if len(db_parts) > 1:
            logger.info(f"Подключение к базе данных: {db_parts[1]}")
        else:
            logger.info("Подключение к базе данных (формат URL нестандартный)")
        
        try:
            logger.info("Попытка создания движка SQLAlchemy")
            logger.info(f"Используемый URL: {database_url}")
            
            # Добавляем параметры подключения для SQLAlchemy
            connect_args = {
                'connect_timeout': 30,  # Увеличиваем таймаут подключения
                'keepalives': 1,        # Включаем keepalive
                'keepalives_idle': 30,  # Время простоя перед отправкой keepalive
                'keepalives_interval': 10,  # Интервал между keepalive
                'keepalives_count': 5,   # Количество попыток keepalive
                'sslmode': 'require'     # Требуем SSL подключение
            }
            
            self.engine = create_engine(
                database_url,
                connect_args=connect_args,
                pool_size=5,            # Размер пула соединений
                max_overflow=10,        # Максимальное количество дополнительных соединений
                pool_timeout=30,        # Таймаут ожидания соединения из пула
                pool_recycle=1800       # Пересоздаем соединения каждые 30 минут
            )
            
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Движок SQLAlchemy создан успешно")
            
            logger.info("Инициализация базы данных")
            self._init_db()
            logger.info("База данных инициализирована успешно")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {str(e)}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            raise

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