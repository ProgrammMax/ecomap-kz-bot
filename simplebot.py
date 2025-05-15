import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN', '7543391406:AAGdZn8Pk0o95MtVlPiZHKz-efkwQPF4aEc')

# Обработчики команд
def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    web_app_url = "https://ecomapkz-bb3c2vacc-maksims-projects-e6a56a85.vercel.app"
    
    keyboard = [
        [InlineKeyboardButton("🗺️ Открыть EcoMap KZ 🗺️", web_app=WebAppInfo(url=web_app_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_html(
        f"Привет, <b>{user.first_name}</b>! Я бот экологической карты Казахстана. "
        f"Я помогу вам отслеживать экологические проблемы в разных регионах страны.\n\n"
        f"Используйте кнопку ниже для доступа к экологической карте:",
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /help."""
    help_text = (
        "Доступные команды:\n"
        "/start - Начать взаимодействие с ботом\n"
        "/help - Показать это сообщение\n"
        "/map - Показать экологическую карту\n"
        "/info - Информация о проекте"
    )
    update.message.reply_text(help_text)

def map_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /map."""
    web_app_url = "https://ecomapkz-bb3c2vacc-maksims-projects-e6a56a85.vercel.app"
    keyboard = [
        [InlineKeyboardButton("🗺️ Открыть карту", web_app=WebAppInfo(url=web_app_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Экологическая карта Казахстана доступна по ссылке:",
        reply_markup=reply_markup
    )

def info_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /info."""
    info_text = (
        "EcoMap KZ - проект экологической карты Казахстана.\n\n"
        "Наша цель - создать интерактивную карту экологических проблем "
        "и помочь гражданам и организациям отслеживать экологическую ситуацию "
        "в разных регионах страны.\n\n"
        "Сайт проекта: https://ecomapkz-bb3c2vacc-maksims-projects-e6a56a85.vercel.app/"
    )
    update.message.reply_text(info_text)

def echo(update: Update, context: CallbackContext) -> None:
    """Обработчик любых сообщений."""
    update.message.reply_text("Я не понимаю эту команду. Используйте /help для получения списка доступных команд.")

def main() -> None:
    """Запуск бота."""
    print("EcoMap KZ Bot запускается...")
    print(f"Используется токен: {TOKEN}")
    
    try:
        # Создание Updater и передача токена
        updater = Updater(TOKEN)

        # Получение диспетчера
        dispatcher = updater.dispatcher

        # Регистрация обработчиков команд
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("map", map_command))
        dispatcher.add_handler(CommandHandler("info", info_command))

        # Регистрация обработчика сообщений
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

        # Запуск бота
        print("Бот успешно настроен, запускаем...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == '__main__':
    main() 