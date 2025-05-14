import os
import json
import logging
from http.server import BaseHTTPRequestHandler
import sys
import importlib.util

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем необходимые модули
import database
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
from telegram.constants import ParseMode

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем токен из переменных окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in environment variables")

# Инициализируем приложение
application = Application.builder().token(TOKEN).build()

# Импортируем обработчики команд из основного файла бота
spec = importlib.util.spec_from_file_location("bot_module", 
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bot.py"))
bot_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot_module)

# Состояния для разговора при отправке отчета о проблеме
PHOTO, DESCRIPTION, LOCATION = range(3)

# Регистрируем обработчики
def setup_handlers():
    # Регистрируем обработчик разговора для отчетов о проблемах
    report_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("report", bot_module.report_problem),
            MessageHandler(filters.Regex("^📸 Сообщить о проблеме$"), bot_module.report_problem)
        ],
        states={
            PHOTO: [MessageHandler(filters.Regex("^(🗑️ Незаконная свалка|💧 Загрязнение воды|🏭 Промышленные выбросы|🚗 Транспортное загрязнение|🔙 Главное меню)$"), bot_module.handle_problem_type)],
            DESCRIPTION: [
                MessageHandler(filters.PHOTO, bot_module.handle_photo),
                CommandHandler("skip", bot_module.skip_photo)
            ],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot_module.handle_description)]
        },
        fallbacks=[
            CommandHandler("cancel", bot_module.cancel),
            MessageHandler(filters.Regex("^🔙 Главное меню$"), bot_module.cancel)
        ]
    )
    
    # Регистрируем обработчик разговора
    application.add_handler(report_conv_handler)
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", bot_module.start))
    application.add_handler(CommandHandler("help", bot_module.help_command))
    application.add_handler(CommandHandler("eco", bot_module.eco_info))
    application.add_handler(CommandHandler("tips", bot_module.eco_tips))
    application.add_handler(CommandHandler("events", bot_module.show_events))
    application.add_handler(CommandHandler("my_reports", bot_module.my_reports))
    
    # Регистрируем обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(bot_module.city_info, pattern=r"^city_"))
    application.add_handler(CallbackQueryHandler(bot_module.show_map, pattern=r"^map_"))
    application.add_handler(CallbackQueryHandler(bot_module.back_to_cities, pattern=r"^back_to_cities"))
    application.add_handler(CallbackQueryHandler(bot_module.next_tip, pattern=r"^next_tip"))
    application.add_handler(CallbackQueryHandler(bot_module.join_event, pattern=r"^join_event"))
    
    # Регистрируем обработчик сообщений для всех остальных текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_module.handle_message))
    
    # Регистрируем обработчик местоположения
    application.add_handler(MessageHandler(filters.LOCATION, bot_module.handle_location))

# Устанавливаем обработчики
setup_handlers()

# Функция для обработки POST-запросов от вебхуков Telegram
async def process_update(request_data):
    try:
        update = Update.de_json(request_data, application.bot)
        await application.process_update(update)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return {"status": "error", "message": str(e)}

# Класс обработчика HTTP-запросов
class handler(BaseHTTPRequestHandler):
    async def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            result = await process_update(request_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
    
    def do_GET(self):
        # Для проверки работоспособности сервера
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "active", "message": "EcoMap KZ Bot is running"}).encode('utf-8'))

# Создаем функцию для ручной установки вебхука
async def set_webhook(webhook_url):
    await application.bot.set_webhook(webhook_url)
    print(f"Webhook set to {webhook_url}")

# Для локального тестирования
if __name__ == "__main__":
    import uvicorn
    import asyncio
    
    async def main():
        # Для локальных тестов можно использовать ngrok
        webhook_url = os.environ.get("WEBHOOK_URL", "https://your-vercel-app.vercel.app/api")
        await set_webhook(webhook_url)
    
    asyncio.run(main())
    
    # Запускаем локальный сервер для обработки вебхуков
    uvicorn.run("index:handler", host="0.0.0.0", port=8000) 