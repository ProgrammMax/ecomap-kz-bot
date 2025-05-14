from flask import Flask, request, jsonify
import json
import os
import telegram
from telegram import Update
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получение токена из переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден в .env файле")

# Создание экземпляра Flask
app = Flask(__name__)

# Создание бота Telegram
bot = telegram.Bot(token=TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Обработчик вебхуков от Telegram.
    """
    try:
        data = request.get_json()
        update = Update.de_json(data, bot)
        
        # Обработка входящего сообщения
        # В реальном приложении здесь будет код для обработки сообщений
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"Ошибка при обработке вебхука: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000))) 