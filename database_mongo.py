"""
Модуль для работы с базой данных EcoMap KZ, адаптированный для работы с MongoDB Atlas.
Это позволит хранить данные в облачной базе данных, что необходимо для работы на Vercel.
"""

import os
import pymongo
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем URI для подключения к MongoDB Atlas из переменных окружения
MONGODB_URI = os.environ.get("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI не указан в переменных окружения")

# Создаем клиента MongoDB
client = pymongo.MongoClient(MONGODB_URI)
db = client.ecomap_kz  # Используем базу данных 'ecomap_kz'

# Коллекции для хранения данных
reports_collection = db.reports
users_collection = db.users

def init_db():
    """Инициализация индексов базы данных"""
    # Создаем индексы для более быстрого поиска
    reports_collection.create_index("user_id")
    reports_collection.create_index("status")
    print("База данных MongoDB инициализирована")

def add_report(user_id, username, problem_type, description, location, photo_id=None):
    """Добавление нового отчета о проблеме"""
    # Создаем новый отчет
    # Получаем максимальный ID из существующих отчетов
    max_id_doc = reports_collection.find_one(sort=[("id", pymongo.DESCENDING)])
    next_id = 1
    if max_id_doc:
        next_id = max_id_doc["id"] + 1
    
    report = {
        "id": next_id,
        "user_id": user_id,
        "username": username,
        "problem_type": problem_type,
        "description": description,
        "location": location,
        "photo_id": photo_id,
        "timestamp": datetime.now().isoformat(),
        "status": "new"  # new, in-progress, resolved
    }

    # Добавляем отчет в коллекцию
    reports_collection.insert_one(report)

    # Обновляем информацию о пользователе
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        users_collection.insert_one({
            "user_id": user_id,
            "username": username,
            "reports_count": 1,
            "joined_at": datetime.now().isoformat()
        })
    else:
        users_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"reports_count": 1}}
        )

    return next_id

def get_user_reports(user_id):
    """Получение отчетов пользователя"""
    return list(reports_collection.find({"user_id": user_id}, {'_id': 0}))

def get_all_reports():
    """Получение всех отчетов"""
    return list(reports_collection.find({}, {'_id': 0}))

def get_report_by_id(report_id):
    """Получение отчета по ID"""
    return reports_collection.find_one({"id": report_id}, {'_id': 0})

def update_report_status(report_id, new_status):
    """Обновление статуса отчета"""
    result = reports_collection.update_one(
        {"id": report_id},
        {"$set": {"status": new_status}}
    )
    return result.modified_count > 0

def get_user_stats(user_id):
    """Получение статистики пользователя"""
    user = users_collection.find_one({"user_id": user_id}, {'_id': 0})
    return user

# Инициализация базы данных при импорте модуля
try:
    init_db()
except Exception as e:
    print(f"Ошибка инициализации базы данных: {e}")
    # Если не удалось подключиться к MongoDB, используем заглушки для функций
    def get_user_reports(user_id):
        return []
    
    def get_all_reports():
        return []
    
    def get_report_by_id(report_id):
        return None
    
    def update_report_status(report_id, new_status):
        return False
    
    def get_user_stats(user_id):
        return None
    
    def add_report(*args, **kwargs):
        return 0 