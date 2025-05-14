"""
Утилиты для работы с картами и геоданными.
"""

import folium
import tempfile
import os
from PIL import Image
from io import BytesIO
import base64
import requests

def create_eco_map(city_name, lat, lon, air_quality, pm25, temperature, humidity):
    """
    Создает карту с экологическими данными для указанного города.
    
    Args:
        city_name (str): Название города
        lat (float): Широта
        lon (float): Долгота
        air_quality (str): Качество воздуха (текстовое описание)
        pm25 (int): Значение PM2.5
        temperature (int): Температура
        humidity (int): Влажность
        
    Returns:
        str: Путь к созданному HTML-файлу карты
    """
    # Создаем карту
    map_center = [lat, lon]
    m = folium.Map(location=map_center, zoom_start=12)
    
    # Добавляем маркер с информацией о качестве воздуха
    popup_text = f"""
    <b>{city_name}</b><br>
    Качество воздуха: {air_quality}<br>
    PM2.5: {pm25} мкг/м³<br>
    Температура: {temperature}°C<br>
    Влажность: {humidity}%<br>
    """
    
    # Определяем цвет маркера
    if air_quality == "Хороший":
        color = "green"
    elif air_quality == "Средний":
        color = "orange"
    else:
        color = "red"
    
    folium.Marker(
        location=map_center,
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color=color)
    ).add_to(m)
    
    # Сохраняем карту во временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
        map_path = tmp.name
        m.save(map_path)
    
    return map_path

def get_air_quality_icon(air_quality):
    """
    Возвращает иконку для качества воздуха.
    
    Args:
        air_quality (str): Качество воздуха (текстовое описание)
        
    Returns:
        str: Emoji-иконка для качества воздуха
    """
    if air_quality == "Хороший":
        return "🟢"
    elif air_quality == "Средний":
        return "🟡"
    else:
        return "🔴"

def get_location_coords(location_text):
    """
    Функция для преобразования текстового описания местоположения в координаты.
    В реальном проекте здесь будет обращение к геокодеру API.
    
    Args:
        location_text (str): Текстовое описание местоположения
        
    Returns:
        tuple: (lat, lon) или None, если не удалось определить
    """
    # Примитивная реализация для демонстрации
    if "Алматы" in location_text:
        return (43.238949, 76.889709)
    elif "Нур-Султан" in location_text or "Астана" in location_text:
        return (51.169392, 71.449074)
    elif "Шымкент" in location_text:
        return (42.315514, 69.586907)
    elif "Координаты:" in location_text:
        # Парсим строку с координатами
        try:
            coords = location_text.replace("Координаты:", "").strip().split(",")
            return (float(coords[0]), float(coords[1]))
        except:
            return None
    
    return None

def add_problem_markers_to_map(m, reports):
    """
    Добавляет маркеры с проблемами на карту.
    
    Args:
        m (folium.Map): Объект карты folium
        reports (list): Список отчетов о проблемах
        
    Returns:
        folium.Map: Обновленная карта с маркерами
    """
    for report in reports:
        # Получаем координаты
        coords = get_location_coords(report.get("location", ""))
        if not coords:
            continue
        
        # Создаем всплывающее окно
        popup_text = f"""
        <b>Проблема: {report['problem_type']}</b><br>
        Описание: {report['description']}<br>
        Статус: {report['status']}<br>
        """
        
        # Выбираем цвет в зависимости от типа проблемы
        if "свалка" in report['problem_type'].lower():
            icon = folium.Icon(color="black", icon="trash", prefix='fa')
        elif "вода" in report['problem_type'].lower():
            icon = folium.Icon(color="blue", icon="tint", prefix='fa')
        elif "выброс" in report['problem_type'].lower():
            icon = folium.Icon(color="purple", icon="industry", prefix='fa')
        elif "транспорт" in report['problem_type'].lower():
            icon = folium.Icon(color="darkred", icon="car", prefix='fa')
        else:
            icon = folium.Icon(color="gray", icon="exclamation-circle", prefix='fa')
        
        # Добавляем маркер
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_text, max_width=300),
            icon=icon
        ).add_to(m)
    
    return m 