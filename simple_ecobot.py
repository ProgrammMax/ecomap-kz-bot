import os
import logging
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# API Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7543391406:AAGdZn8Pk0o95MtVlPiZHKz-efkwQPF4aEc')
API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Веб-приложение
WEBAPP_URL = "https://ecomapkz-bb3c2vacc-maksims-projects-e6a56a85.vercel.app"

def send_message(chat_id, text):
    """Отправка сообщения в Telegram."""
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    return response.json()

def get_updates(offset=None):
    """Получение обновлений от Telegram."""
    url = f"{API_URL}/getUpdates"
    params = {"timeout": 100, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    response = requests.get(url, params=params)
    return response.json()

def process_message(message):
    """Обработка сообщения от пользователя."""
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    first_name = message["from"].get("first_name", "пользователь")
    
    if text == "/start":
        response_text = f"""
Привет, <b>{first_name}</b>! 

Я бот экологической карты Казахстана. Я помогу вам отслеживать экологические проблемы в разных регионах страны.

Вы можете открыть нашу интерактивную карту по этой ссылке:
{WEBAPP_URL}

Доступные команды:
/start - Начать взаимодействие с ботом
/help - Показать справку
/map - Получить ссылку на карту
/info - Информация о проекте
        """
        send_message(chat_id, response_text)
    
    elif text == "/help":
        help_text = """
Доступные команды:
/start - Начать взаимодействие с ботом
/help - Показать это сообщение
/map - Получить ссылку на экологическую карту
/info - Информация о проекте
        """
        send_message(chat_id, help_text)
    
    elif text == "/map":
        map_text = f"""
Экологическая карта Казахстана доступна по ссылке:
{WEBAPP_URL}

На карте вы можете:
- Видеть экологические проблемы
- Фильтровать по типу проблемы и региону
- Сообщать о новых проблемах
- Получать информацию о качестве воздуха
        """
        send_message(chat_id, map_text)
    
    elif text == "/info":
        info_text = f"""
EcoMap KZ - проект экологической карты Казахстана.

Наша цель - создать интерактивную карту экологических проблем и помочь гражданам и организациям отслеживать экологическую ситуацию в разных регионах страны.

Сайт проекта: {WEBAPP_URL}
        """
        send_message(chat_id, info_text)
    
    else:
        echo_text = "Я не понимаю эту команду. Используйте /help для получения списка доступных команд."
        send_message(chat_id, echo_text)

def main():
    """Основной цикл бота."""
    print("EcoMap KZ Bot запускается...")
    
    try:
        print(f"Используется токен: {TELEGRAM_TOKEN}")
        print("Бот успешно настроен, запускаем...")
        
        # Проверяем соединение
        response = requests.get(f"{API_URL}/getMe")
        if not response.json().get("ok"):
            print(f"Ошибка соединения с Telegram API: {response.json()}")
            return
        
        bot_info = response.json()["result"]
        print(f"Бот @{bot_info['username']} успешно запущен")
        
        # Последний update_id для избежания повторной обработки
        last_update_id = None
        
        # Основной цикл
        while True:
            # Получение обновлений
            updates = get_updates(last_update_id)
            
            if not updates.get("ok"):
                print(f"Ошибка получения обновлений: {updates}")
                continue
            
            # Обработка каждого обновления
            for update in updates.get("result", []):
                # Обновление last_update_id
                last_update_id = update["update_id"] + 1
                
                # Обработка сообщения, если оно есть
                if "message" in update:
                    process_message(update["message"])
    
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main() 