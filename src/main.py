import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from utils.database import Database
from utils.message_parser import MessageParser
from utils.visualization import Visualizer
from models.transaction import Transaction

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Я бот для учета семейных расходов и доходов.\n\n"
        "Просто отправляйте сообщения о расходах или доходах в формате:\n"
        "500 продукты\n"
        "1000+ зарплата\n\n"
        "Доступные команды:\n"
        "/stats - статистика за последний месяц\n"
        "/report - подробный отчет\n"
        "/help - справка"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "Как пользоваться ботом:\n\n"
        "1. Отправляйте сообщения о расходах:\n"
        "   - 500 продукты\n"
        "   - 1000 транспорт\n"
        "   - 2000 развлечения\n\n"
        "2. Отправляйте сообщения о доходах:\n"
        "   - 50000+ зарплата\n"
        "   - 1000+ доход\n\n"
        "3. Используйте команды:\n"
        "   /stats - статистика за месяц\n"
        "   /report - подробный отчет\n"
        "   /help - эта справка"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    chat_id = update.effective_chat.id
    start_date = datetime.now() - timedelta(days=30)
    
    # Получаем статистику
    stats = db.get_statistics(chat_id, start_date)
    
    # Создаем сообщение
    message = (
        f"📊 Статистика за последние 30 дней:\n\n"
        f"💰 Доходы: {stats['total_income']:.2f}\n"
        f"💸 Расходы: {stats['total_expense']:.2f}\n"
        f"📈 Баланс: {stats['balance']:.2f}\n\n"
    )
    
    # Добавляем топ категорий расходов
    if stats['categories'].get('expense'):
        message += "📉 Топ категорий расходов:\n"
        for category, amount in sorted(
            stats['categories']['expense'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]:
            message += f"- {category}: {amount:.2f}\n"
    
    await update.message.reply_text(message)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /report"""
    chat_id = update.effective_chat.id
    start_date = datetime.now() - timedelta(days=30)
    
    # Получаем транзакции
    transactions = db.get_transactions(chat_id, start_date)
    
    if not transactions:
        await update.message.reply_text("Нет данных за последние 30 дней")
        return
    
    # Создаем графики
    visualizer = Visualizer()
    
    # Круговая диаграмма расходов
    expense_chart = visualizer.create_pie_chart(transactions, 'expense')
    if expense_chart:
        await update.message.reply_photo(expense_chart)
    
    # Круговая диаграмма доходов
    income_chart = visualizer.create_pie_chart(transactions, 'income')
    if income_chart:
        await update.message.reply_photo(income_chart)
    
    # График по времени
    time_chart = visualizer.create_time_series(transactions)
    if time_chart:
        await update.message.reply_photo(time_chart)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    if not update.message or not update.message.text:
        return
    
    # Парсим сообщение
    parsed = MessageParser.parse_message(update.message.text)
    if not parsed:
        return
    
    # Создаем транзакцию
    transaction = Transaction(
        id=None,
        amount=parsed.amount,
        type=parsed.type,
        category=parsed.category,
        description=parsed.description,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        timestamp=datetime.now()
    )
    
    # Сохраняем в базу
    db.add_transaction(transaction)
    
    # Отправляем подтверждение
    type_emoji = "💰" if parsed.type == "income" else "💸"
    await update.message.reply_text(
        f"{type_emoji} Записано:\n"
        f"Сумма: {parsed.amount:.2f}\n"
        f"Тип: {'доход' if parsed.type == 'income' else 'расход'}\n"
        f"Категория: {parsed.category}"
    )

def main():
    """Запуск бота"""
    # Получаем токен из переменных окружения
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Не найден TELEGRAM_BOT_TOKEN")
        return
    
    # Создаем приложение
    application = Application.builder().token(token).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main() 