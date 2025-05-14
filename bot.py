import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from telegram.constants import ParseMode
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
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден в .env файле")

# Состояния для ConversationHandler
LOCATION, DESCRIPTION, PHOTO = range(3)

async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я бот экологической карты Казахстана. "
        f"Я помогу вам отслеживать экологические проблемы в разных регионах страны.\n\n"
        f"Используйте /help для получения списка доступных команд."
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /help."""
    help_text = (
        "Доступные команды:\n"
        "/start - Начать взаимодействие с ботом\n"
        "/help - Показать это сообщение\n"
        "/map - Показать экологическую карту\n"
        "/report - Сообщить о проблеме\n"
        "/info - Информация о проекте"
    )
    await update.message.reply_text(help_text)

async def map_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /map для отображения карты."""
    await update.message.reply_text(
        "Экологическая карта Казахстана доступна по ссылке: "
        "https://ecomap-kz-bot.vercel.app/"
    )

async def info_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /info."""
    info_text = (
        "EcoMap KZ - проект экологической карты Казахстана.\n\n"
        "Наша цель - создать интерактивную карту экологических проблем "
        "и помочь гражданам и организациям отслеживать экологическую ситуацию "
        "в разных регионах страны.\n\n"
        "Сайт проекта: https://ecomap-kz-bot.vercel.app/"
    )
    await update.message.reply_text(info_text)

async def report_start(update: Update, context: CallbackContext) -> int:
    """Начинает процесс сообщения о проблеме."""
    await update.message.reply_text(
        "Пожалуйста, отправьте местоположение проблемы. "
        "Вы можете использовать функцию 'Отправить местоположение' в Telegram "
        "или просто написать название региона/города."
    )
    return LOCATION

async def location_received(update: Update, context: CallbackContext) -> int:
    """Обрабатывает полученное местоположение."""
    user = update.effective_user
    location_text = update.message.text
    
    # Сохраняем местоположение в данных пользователя
    context.user_data['location'] = location_text
    
    await update.message.reply_text(
        f"Местоположение '{location_text}' сохранено. "
        f"Теперь, пожалуйста, опишите проблему."
    )
    return DESCRIPTION

async def description_received(update: Update, context: CallbackContext) -> int:
    """Обрабатывает полученное описание проблемы."""
    description = update.message.text
    
    # Сохраняем описание в данных пользователя
    context.user_data['description'] = description
    
    await update.message.reply_text(
        "Спасибо за описание! Если у вас есть фотография проблемы, "
        "пожалуйста, отправьте ее сейчас. Если нет, отправьте /skip."
    )
    return PHOTO

async def photo_received(update: Update, context: CallbackContext) -> int:
    """Обрабатывает полученную фотографию."""
    user = update.effective_user
    photo_file = await update.message.photo[-1].get_file()
    
    # В реальном приложении здесь можно сохранить фото и другие данные в базу данных
    location = context.user_data.get('location', 'Не указано')
    description = context.user_data.get('description', 'Не указано')
    
    # Здесь будет код для сохранения данных в базе данных
    
    await update.message.reply_text(
        f"Спасибо за сообщение о проблеме!\n\n"
        f"Местоположение: {location}\n"
        f"Описание: {description}\n\n"
        f"Ваше сообщение будет рассмотрено нашей командой."
    )
    
    # Очищаем данные пользователя
    context.user_data.clear()
    return ConversationHandler.END

async def skip_photo(update: Update, context: CallbackContext) -> int:
    """Пропускает этап отправки фото."""
    user = update.effective_user
    
    # В реальном приложении здесь можно сохранить данные в базу данных
    location = context.user_data.get('location', 'Не указано')
    description = context.user_data.get('description', 'Не указано')
    
    # Здесь будет код для сохранения данных в базе данных
    
    await update.message.reply_text(
        f"Спасибо за сообщение о проблеме!\n\n"
        f"Местоположение: {location}\n"
        f"Описание: {description}\n\n"
        f"Ваше сообщение будет рассмотрено нашей командой."
    )
    
    # Очищаем данные пользователя
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    """Отменяет и заканчивает разговор."""
    await update.message.reply_text("Процесс сообщения о проблеме отменен.")
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    """Запуск бота."""
    # Создание приложения и передача токена
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("map", map_command))
    application.add_handler(CommandHandler("info", info_command))
    
    # Создание ConversationHandler для обработки сообщений о проблемах
    report_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("report", report_start)],
        states={
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location_received)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description_received)],
            PHOTO: [
                MessageHandler(filters.PHOTO, photo_received),
                CommandHandler("skip", skip_photo)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(report_conv_handler)

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 