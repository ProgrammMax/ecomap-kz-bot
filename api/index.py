from flask import Flask, Response, request, jsonify
import os
import json
import telegram
from telegram import Update
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получение токена из переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    print("TELEGRAM_TOKEN не найден в .env файле")

# Создание экземпляра Flask
app = Flask(__name__)

# Создание бота Telegram
bot = telegram.Bot(token=TOKEN) if TOKEN else None

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({
        "status": "ok",
        "message": "API EcoMap KZ работает"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Обработчик вебхуков от Telegram.
    """
    if not bot:
        return jsonify({'status': 'error', 'message': 'Bot token not configured'})
    
    try:
        data = request.get_json()
        update = Update.de_json(data, bot)
        
        # Обработка входящего сообщения
        # В реальном приложении здесь будет код для обработки сообщений
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"Ошибка при обработке вебхука: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

# Определяем handler для Vercel
def handler(request, context):
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port) 