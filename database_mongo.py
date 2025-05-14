import os
from pymongo import MongoClient
from dotenv import load_dotenv
import logging
from datetime import datetime

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение данных для подключения к MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'ecomap_kz')

class Database:
    def __init__(self):
        """
        Инициализация подключения к базе данных MongoDB.
        """
        if not MONGODB_URI:
            logger.error("MONGODB_URI не найден в переменных окружения")
            raise ValueError("MONGODB_URI не найден в .env файле")
        
        try:
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[DB_NAME]
            logger.info(f"Подключен к базе данных MongoDB: {DB_NAME}")
        except Exception as e:
            logger.error(f"Ошибка подключения к MongoDB: {e}")
            raise
        
        # Инициализация коллекций
        self.reports = self.db.reports
        self.users = self.db.users
    
    def save_report(self, user_id, location, description, photo_id=None):
        """
        Сохранение нового отчета о проблеме в базу данных.
        
        Args:
            user_id (int): ID пользователя Telegram
            location (str): Локация проблемы
            description (str): Описание проблемы
            photo_id (str, optional): ID фотографии, если есть
            
        Returns:
            str: ID созданного отчета
        """
        try:
            report_data = {
                'user_id': user_id,
                'location': location,
                'description': description,
                'created_at': datetime.now(),
                'status': 'new'
            }
            
            if photo_id:
                report_data['photo_id'] = photo_id
                
            result = self.reports.insert_one(report_data)
            logger.info(f"Создан новый отчет с ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Ошибка при сохранении отчета: {e}")
            return None
    
    def get_reports_by_location(self, location):
        """
        Получить отчеты по заданной локации.
        
        Args:
            location (str): Локация для поиска
            
        Returns:
            list: Список отчетов
        """
        try:
            reports = list(self.reports.find({"location": {"$regex": location, "$options": "i"}}))
            return reports
        except Exception as e:
            logger.error(f"Ошибка при получении отчетов по локации: {e}")
            return []
    
    def save_user(self, user_id, username=None, first_name=None, last_name=None):
        """
        Сохранение данных пользователя в базу данных.
        
        Args:
            user_id (int): ID пользователя Telegram
            username (str, optional): Имя пользователя Telegram
            first_name (str, optional): Имя пользователя
            last_name (str, optional): Фамилия пользователя
            
        Returns:
            bool: True если успешно, иначе False
        """
        try:
            user_data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'last_activity': datetime.now()
            }
            
            # Обновляем пользователя если он существует, иначе создаем нового
            result = self.users.update_one(
                {'user_id': user_id}, 
                {'$set': user_data}, 
                upsert=True
            )
            
            logger.info(f"Пользователь с ID {user_id} сохранен/обновлен в базе данных")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении пользователя: {e}")
            return False

# Создаем экземпляр базы данных
db = Database()

# Для импорта из других файлов
def get_database():
    """
    Возвращает экземпляр базы данных для использования в других модулях.
    """
    return db 