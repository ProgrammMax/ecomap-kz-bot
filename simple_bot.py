import os
import time
import json
import logging
import threading
import requests
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

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

# MongoDB подключение
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://ecomapkz:ecomapkzpassword@cluster0.ewtlfwf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
DB_NAME = os.getenv('DB_NAME', 'ecomap_kz')

# Base URL для Telegram API
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text, reply_markup=None):
    """Отправить сообщение пользователю"""
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if reply_markup:
        data["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=data)
        print(f"Отправка сообщения: {response.json()}")
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        return None

def send_app_button(chat_id):
    """Отправить кнопку для открытия веб-приложения"""
    # Используем URL с Vercel для Telegram WebApp
    web_app_url = "https://ecomapkz-bot.vercel.app"
    
    inline_keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🌍 Открыть EcoMap KZ 🌍",
                    "web_app": {"url": web_app_url}
                }
            ]
        ]
    }
    
    return send_message(
        chat_id, 
        "🌿 Нажмите на кнопку ниже, чтобы открыть экологическую карту Казахстана 🌿", 
        inline_keyboard
    )

def handle_update(update):
    """Обработать входящее обновление от Telegram"""
    print(f"Получено обновление: {update}")
    
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        
        # Проверяем, есть ли текст в сообщении
        if "text" in message:
            text = message["text"]
            print(f"Получен текст: {text}")
            
            # Специальная обработка команды /start
            if text == "/start":
                print("Обрабатываем команду /start")
            
        # На любое сообщение отправляем кнопку с приложением
        print(f"Отправляем кнопку пользователю {chat_id}")
        send_app_button(chat_id)

def get_updates(offset=None):
    """Получить обновления от Telegram API"""
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при получении обновлений: {e}")
        return {"ok": False, "result": []}

def polling():
    """Основной цикл опроса Telegram API"""
    offset = None
    
    logger.info("Запуск бота")
    print(f"EcoMap KZ Bot запускается...")
    print(f"Используется токен: {TOKEN}")
    
    while True:
        try:
            updates = get_updates(offset)
            
            if updates.get("ok") and "result" in updates:
                updates_count = len(updates["result"])
                if updates_count > 0:
                    print(f"Получено {updates_count} обновлений")
                    
                for update in updates["result"]:
                    handle_update(update)
                    offset = update["update_id"] + 1
            
            time.sleep(1)
        except Exception as e:
            logger.error(f"Ошибка в цикле опроса: {e}")
            print(f"Ошибка в цикле опроса: {e}")
            time.sleep(5)

def set_webhook():
    """Установить вебхук для Telegram бота"""
    url = f"{BASE_URL}/setWebhook"
    webhook_url = "https://ecomap-kz-bot.vercel.app/api/webhook"
    data = {"url": webhook_url}
    
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при установке вебхука: {e}")
        return None

def delete_webhook():
    """Удалить вебхук для Telegram бота"""
    url = f"{BASE_URL}/deleteWebhook"
    
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при удалении вебхука: {e}")
        return None

if __name__ == "__main__":
    # Удаляем вебхук перед запуском polling
    print("Удаление вебхука...")
    delete_result = delete_webhook()
    if delete_result and delete_result.get("ok"):
        print("Вебхук успешно удален")
    else:
        print("Ошибка при удалении вебхука")
    
    # Запускаем опрос Telegram API
    polling() 