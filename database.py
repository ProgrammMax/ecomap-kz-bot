"""
Модуль для работы с базой данных EcoMap KZ.
В данном примере используется простая реализация на основе JSON-файла.
В реальном проекте рекомендуется использовать SQLite или PostgreSQL.
"""

import json
import os
from datetime import datetime

# Путь к файлу с данными пользовательских отчетов
DATA_FILE = "user_reports.json"

# Структура для хранения данных
default_data = {
    "reports": [],
    "users": {}
}

def init_db():
    """Инициализация базы данных"""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        print(f"База данных инициализирована в файле {DATA_FILE}")
    else:
        print(f"База данных уже существует: {DATA_FILE}")

def get_data():
    """Получение всех данных из файла"""
    if not os.path.exists(DATA_FILE):
        init_db()
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Ошибка чтения файла {DATA_FILE}. Создание новой структуры данных.")
        return default_data

def save_data(data):
    """Сохранение данных в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_report(user_id, username, problem_type, description, location, photo_id=None):
    """Добавление нового отчета о проблеме"""
    data = get_data()
    
    # Создаем новый отчет
    report = {
        "id": len(data["reports"]) + 1,
        "user_id": user_id,
        "username": username,
        "problem_type": problem_type,
        "description": description,
        "location": location,
        "photo_id": photo_id,
        "timestamp": datetime.now().isoformat(),
        "status": "new"  # new, in-progress, resolved
    }
    
    # Добавляем отчет в список
    data["reports"].append(report)
    
    # Обновляем информацию о пользователе
    if str(user_id) not in data["users"]:
        data["users"][str(user_id)] = {
            "username": username,
            "reports_count": 1,
            "joined_at": datetime.now().isoformat()
        }
    else:
        data["users"][str(user_id)]["reports_count"] += 1
    
    # Сохраняем изменения
    save_data(data)
    
    return report["id"]

def get_user_reports(user_id):
    """Получение отчетов пользователя"""
    data = get_data()
    return [report for report in data["reports"] if report["user_id"] == user_id]

def get_all_reports():
    """Получение всех отчетов"""
    data = get_data()
    return data["reports"]

def get_report_by_id(report_id):
    """Получение отчета по ID"""
    data = get_data()
    for report in data["reports"]:
        if report["id"] == report_id:
            return report
    return None

def update_report_status(report_id, new_status):
    """Обновление статуса отчета"""
    data = get_data()
    for report in data["reports"]:
        if report["id"] == report_id:
            report["status"] = new_status
            save_data(data)
            return True
    return False

def get_user_stats(user_id):
    """Получение статистики пользователя"""
    data = get_data()
    if str(user_id) in data["users"]:
        return data["users"][str(user_id)]
    return None

# Инициализация базы данных при импорте модуля
init_db() 