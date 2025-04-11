import re
from typing import Optional, Tuple
from dataclasses import dataclass

@dataclass
class ParsedTransaction:
    amount: float
    type: str
    category: str
    description: str

class MessageParser:
    # Словарь ключевых слов для определения типа транзакции
    INCOME_KEYWORDS = {'доход', 'зарплата', 'прибыль', '+'}
    EXPENSE_KEYWORDS = {'расход', 'трата', 'покупка', '-'}
    
    # Словарь категорий по умолчанию
    DEFAULT_CATEGORIES = {
        'продукты': ['еда', 'продукты', 'магазин'],
        'транспорт': ['транспорт', 'такси', 'метро', 'автобус'],
        'развлечения': ['развлечения', 'кино', 'театр', 'ресторан'],
        'коммунальные': ['коммунальные', 'квартира', 'дом'],
        'здоровье': ['здоровье', 'медицина', 'аптека'],
        'образование': ['образование', 'курсы', 'учеба'],
        'другое': ['другое', 'прочее']
    }

    @classmethod
    def parse_message(cls, text: str) -> Optional[ParsedTransaction]:
        """Парсит сообщение и извлекает информацию о транзакции"""
        # Ищем сумму в сообщении
        amount_match = re.search(r'(\d+(?:\.\d{1,2})?)', text)
        if not amount_match:
            return None

        amount = float(amount_match.group(1))
        
        # Определяем тип транзакции
        transaction_type = 'expense'
        if any(keyword in text.lower() for keyword in cls.INCOME_KEYWORDS):
            transaction_type = 'income'
        
        # Определяем категорию
        category = 'другое'
        text_lower = text.lower()
        for cat, keywords in cls.DEFAULT_CATEGORIES.items():
            if any(keyword in text_lower for keyword in keywords):
                category = cat
                break
        
        # Формируем описание
        description = text.strip()
        
        return ParsedTransaction(
            amount=amount,
            type=transaction_type,
            category=category,
            description=description
        ) 