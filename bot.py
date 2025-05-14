#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler
import requests
import json
from PIL import Image
from io import BytesIO
import folium
import database

# Пытаемся загрузить переменные из .env файла, если не получается, используем config.py
try:
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TOKEN_HERE")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY")
    
    # Данные по экологии (в реальном проекте будут браться из API)
    eco_data = {
        "Алматы": {
            "air_quality": "Средний",
            "pm25": 42,
            "temperature": 22,
            "humidity": 45,
            "lat": 43.238949,
            "lon": 76.889709,
            "tips": [
                "Избегайте интенсивных физических нагрузок на открытом воздухе",
                "Используйте маску при выходе из дома"
            ]
        },
        "Нур-Султан": {
            "air_quality": "Хороший",
            "pm25": 15,
            "temperature": 18,
            "humidity": 30,
            "lat": 51.169392,
            "lon": 71.449074,
            "tips": [
                "Погода благоприятна для прогулок"
            ]
        },
        "Шымкент": {
            "air_quality": "Плохой",
            "pm25": 87,
            "temperature": 25,
            "humidity": 20,
            "lat": 42.315514,
            "lon": 69.586907,
            "tips": [
                "Ограничьте время пребывания на улице",
                "Не открывайте окна в течение дня"
            ]
        }
    }
    
    # Волонтерские мероприятия
    eco_events = [
        {
            "name": "Очистка берега реки Или",
            "date": "15 июня 2025",
            "location": "Река Или, 25 км от Алматы",
            "description": "Сбор мусора и очистка прибрежной территории"
        },
        {
            "name": "Посадка деревьев в парке",
            "date": "22 июня 2025",
            "location": "Центральный парк, Нур-Султан",
            "description": "Посадка 100 саженцев деревьев и кустарников"
        },
        {
            "name": "Сбор раздельного мусора",
            "date": "10 июня 2025",
            "location": "Двор школы №24, Шымкент",
            "description": "Обучение школьников раздельному сбору мусора"
        }
    ]
    
    # Эко-советы
    tips = [
        "<b>🌱 Сокращайте потребление пластика</b>\nИспользуйте многоразовые бутылки и сумки для покупок.",
        
        "<b>♻️ Сортируйте мусор</b>\nДаже небольшие усилия по сортировке могут привести к значительному сокращению отходов на свалках.",
        
        "<b>💧 Экономьте воду</b>\nЗакрывайте кран, когда чистите зубы, и принимайте короткий душ вместо ванны.",
        
        "<b>🔌 Экономьте электроэнергию</b>\nВыключайте свет и приборы, когда они не используются.",
        
        "<b>🚶 Ходите пешком или используйте велосипед</b>\nЭто не только полезно для экологии, но и для вашего здоровья."
    ]
except:
    # Если .env не найден, используем config.py
    import config
    TOKEN = config.TELEGRAM_TOKEN
    OPENWEATHER_API_KEY = config.OPENWEATHER_API_KEY
    eco_data = config.ECO_DATA
    eco_events = config.ECO_EVENTS
    tips = config.ECO_TIPS

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для разговора при отправке отчета о проблеме
PHOTO, DESCRIPTION, LOCATION = range(3)

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("📊 Экологическая информация")],
        [KeyboardButton("📸 Сообщить о проблеме")],
        [KeyboardButton("🌿 Эко-советы")],
        [KeyboardButton("📅 Волонтерские мероприятия")],
        [KeyboardButton("📋 Мои отчеты")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    user = update.effective_user
    update.message.reply_text(
        f"Здравствуйте, {user.first_name}! 👋\n\n"
        f"Добро пожаловать в EcoMap KZ - бот для мониторинга экологической ситуации в Казахстане.\n\n"
        f"Что вы хотите узнать?",
        reply_markup=reply_markup
    )
    
    # Проверяем статистику пользователя
    user_stats = database.get_user_stats(user.id)
    if user_stats:
        reports_count = user_stats["reports_count"]
        if reports_count > 0:
            update.message.reply_text(
                f"У вас уже есть {reports_count} отчетов о проблемах. Спасибо за вашу активность!"
            )

# Функция для обработки команды /help
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Как пользоваться ботом EcoMap KZ:\n\n"
        "/start - запустить бота\n"
        "/help - получить помощь\n"
        "/eco - узнать экологические данные\n"
        "/report - сообщить о проблеме\n"
        "/tips - получить экологические советы\n"
        "/events - узнать о волонтерских мероприятиях\n"
        "/my_reports - просмотреть ваши отчеты о проблемах\n\n"
        "Также вы можете использовать кнопки меню для навигации."
    )

# Функция для отображения экологической информации
def eco_info(update: Update, context: CallbackContext) -> None:
    keyboard = []
    for city in eco_data.keys():
        keyboard.append([InlineKeyboardButton(city, callback_data=f"city_{city}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Выберите город для получения экологической информации:",
        reply_markup=reply_markup
    )

# Функция для отображения информации о выбранном городе
def city_info(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    city = query.data.replace("city_", "")
    data = eco_data.get(city)
    
    if not data:
        query.edit_message_text(text=f"Извините, данные для города {city} не найдены.")
        return
    
    # Цвет индикатора в зависимости от качества воздуха
    air_quality = data["air_quality"]
    if air_quality == "Хороший":
        air_indicator = "🟢"
    elif air_quality == "Средний":
        air_indicator = "🟡"
    else:
        air_indicator = "🔴"
    
    # Формируем сообщение
    message = (
        f"📍 <b>{city}</b>\n\n"
        f"Качество воздуха: {air_indicator} {air_quality}\n"
        f"PM2.5: {data['pm25']} мкг/м³\n"
        f"Температура: {data['temperature']}°C\n"
        f"Влажность: {data['humidity']}%\n\n"
        f"<b>Рекомендации:</b>\n"
    )
    
    for tip in data["tips"]:
        message += f"• {tip}\n"
    
    keyboard = [
        [InlineKeyboardButton("Посмотреть на карте", callback_data=f"map_{city}")],
        [InlineKeyboardButton("« Назад", callback_data="back_to_cities")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

# Функция для отображения карты
def show_map(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    city = query.data.replace("map_", "")
    data = eco_data.get(city)
    
    if not data:
        query.edit_message_text(text=f"Извините, данные для города {city} не найдены.")
        return
    
    query.edit_message_text(text=f"Генерирую карту для {city}...")
    
    # Создаем карту
    map_center = [data['lat'], data['lon']]
    m = folium.Map(location=map_center, zoom_start=12)
    
    # Добавляем маркер с информацией о качестве воздуха
    popup_text = f"""
    <b>{city}</b><br>
    Качество воздуха: {data['air_quality']}<br>
    PM2.5: {data['pm25']} мкг/м³<br>
    Температура: {data['temperature']}°C<br>
    """
    
    # Определяем цвет маркера
    if data['air_quality'] == "Хороший":
        color = "green"
    elif data['air_quality'] == "Средний":
        color = "orange"
    else:
        color = "red"
    
    folium.Marker(
        location=map_center,
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color=color)
    ).add_to(m)
    
    # Сохраняем карту во временный файл
    map_path = f"map_{city.lower()}.html"
    m.save(map_path)
    
    # Отправляем сообщение с ссылкой на карту (в реальном проекте можно отправить изображение)
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"К сожалению, отправка HTML-карты напрямую в Telegram невозможна. В реальном проекте здесь будет статическое изображение карты или ссылка на веб-версию."
    )
    
    # Загружаем отчеты о проблемах для этого города
    reports = database.get_all_reports()
    city_reports = [r for r in reports if city.lower() in r.get("location", "").lower()]
    
    if city_reports:
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"В городе {city} пользователи сообщили о {len(city_reports)} экологических проблемах."
        )
    
    # Возвращаемся к информации о городе
    city_info(update, context)

# Функция для возврата к списку городов
def back_to_cities(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    keyboard = []
    for city in eco_data.keys():
        keyboard.append([InlineKeyboardButton(city, callback_data=f"city_{city}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Выберите город для получения экологической информации:",
        reply_markup=reply_markup
    )

# Функция для начала процесса сообщения о проблеме
def report_problem(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [KeyboardButton("🗑️ Незаконная свалка")],
        [KeyboardButton("💧 Загрязнение воды")],
        [KeyboardButton("🏭 Промышленные выбросы")],
        [KeyboardButton("🚗 Транспортное загрязнение")],
        [KeyboardButton("🔙 Главное меню")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "Выберите тип экологической проблемы, о которой хотите сообщить:",
        reply_markup=reply_markup
    )
    
    return PHOTO

# Функция для обработки выбора проблемы и запроса фото
def handle_problem_type(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    
    if text == "🔙 Главное меню":
        start(update, context)
        return ConversationHandler.END
    
    if text in ["🗑️ Незаконная свалка", "💧 Загрязнение воды", "🏭 Промышленные выбросы", "🚗 Транспортное загрязнение"]:
        problem_type = text.split(" ", 1)[1]
        context.user_data['problem_type'] = problem_type
        
        update.message.reply_text(
            f"Вы выбрали проблему: {problem_type}.\n\n"
            "Пожалуйста, отправьте фотографию проблемы. "
            "Или отправьте /skip, если у вас нет фотографии."
        )
        return DESCRIPTION
    else:
        update.message.reply_text(
            "Пожалуйста, выберите тип проблемы из предложенных вариантов."
        )
        return PHOTO

# Функция для обработки фото и запроса описания
def handle_photo(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    photo_file = update.message.photo[-1].get_file()
    photo_id = update.message.photo[-1].file_id
    
    # В реальном проекте здесь будет загрузка фото на сервер
    context.user_data['photo_id'] = photo_id
    
    update.message.reply_text(
        "Спасибо за фотографию! Теперь пожалуйста отправьте описание проблемы."
    )
    
    return LOCATION

# Функция для пропуска отправки фото
def skip_photo(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Фотография не отправлена. Пожалуйста, опишите проблему текстом."
    )
    
    return LOCATION

# Функция для обработки описания и запроса местоположения
def handle_description(update: Update, context: CallbackContext) -> int:
    description = update.message.text
    context.user_data['description'] = description
    
    update.message.reply_text(
        "Спасибо за описание! Пожалуйста, отправьте местоположение проблемы.\n\n"
        "Вы можете отправить текстовое описание места или отправить геолокацию через функцию Telegram."
    )
    
    return ConversationHandler.END

# Функция для обработки местоположения и завершения отчета
def handle_location(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    
    if update.message.location:
        location = f"Координаты: {update.message.location.latitude}, {update.message.location.longitude}"
    else:
        location = update.message.text
    
    context.user_data['location'] = location
    
    # Собираем все данные для отчета
    problem_type = context.user_data.get('problem_type', 'Не указано')
    description = context.user_data.get('description', 'Не указано')
    photo_id = context.user_data.get('photo_id')
    
    # Сохраняем отчет в базу данных
    report_id = database.add_report(
        user_id=user.id,
        username=user.username or user.first_name,
        problem_type=problem_type,
        description=description,
        location=location,
        photo_id=photo_id
    )
    
    # Отправляем сообщение с благодарностью
    update.message.reply_text(
        f"Спасибо за ваш отчет! Ему присвоен номер: {report_id}\n\n"
        f"Тип проблемы: {problem_type}\n"
        f"Описание: {description}\n"
        f"Местоположение: {location}\n\n"
        f"Ваш отчет принят и будет рассмотрен специалистами."
    )
    
    # Сбрасываем данные пользователя
    context.user_data.clear()
    
    # Возвращаемся в главное меню
    start(update, context)
    
    return ConversationHandler.END

# Функция для отмены отчета
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Отчет о проблеме отменен. Вы вернулись в главное меню."
    )
    
    # Сбрасываем данные пользователя
    context.user_data.clear()
    
    # Возвращаемся в главное меню
    start(update, context)
    
    return ConversationHandler.END

# Функция для отображения эко-советов
def eco_tips(update: Update, context: CallbackContext) -> None:
    tip_index = 0
    if context.user_data and 'tip_index' in context.user_data:
        tip_index = (context.user_data['tip_index'] + 1) % len(tips)
    context.user_data['tip_index'] = tip_index
    
    keyboard = [
        [InlineKeyboardButton("Следующий совет »", callback_data="next_tip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        f"Совет дня:\n\n{tips[tip_index]}",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

# Функция для отображения следующего совета
def next_tip(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    tip_index = 0
    if context.user_data and 'tip_index' in context.user_data:
        tip_index = (context.user_data['tip_index'] + 1) % len(tips)
    context.user_data['tip_index'] = tip_index
    
    keyboard = [
        [InlineKeyboardButton("Следующий совет »", callback_data="next_tip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text=f"Совет дня:\n\n{tips[tip_index]}",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

# Функция для отображения волонтерских мероприятий
def show_events(update: Update, context: CallbackContext) -> None:
    if not eco_events:
        update.message.reply_text("В настоящее время нет запланированных мероприятий.")
        return
    
    message = "<b>📅 Предстоящие экологические мероприятия:</b>\n\n"
    
    for i, event in enumerate(eco_events):
        message += (
            f"<b>{event['name']}</b>\n"
            f"📆 {event['date']}\n"
            f"📍 {event['location']}\n"
            f"ℹ️ {event['description']}\n\n"
        )
    
    keyboard = [
        [InlineKeyboardButton("Я хочу участвовать!", callback_data="join_event")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

# Функция для присоединения к мероприятию
def join_event(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    query.edit_message_text(
        text="Спасибо за интерес к мероприятию! В реальном проекте здесь будет форма для регистрации.\n\n"
             "Для получения дополнительной информации свяжитесь с организаторами или следите за обновлениями в нашем боте.",
        parse_mode=ParseMode.HTML
    )

# Функция для просмотра своих отчетов
def my_reports(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    reports = database.get_user_reports(user.id)
    
    if not reports:
        update.message.reply_text(
            "У вас пока нет отчетов о проблемах. Вы можете создать новый отчет с помощью кнопки '📸 Сообщить о проблеме'."
        )
        return
    
    message = "<b>📋 Ваши отчеты о проблемах:</b>\n\n"
    
    for report in reports:
        # Иконка статуса
        if report["status"] == "new":
            status_icon = "🆕"
            status_text = "Новый"
        elif report["status"] == "in-progress":
            status_icon = "⏳"
            status_text = "В обработке"
        else:  # resolved
            status_icon = "✅"
            status_text = "Решено"
        
        message += (
            f"<b>Отчет #{report['id']}</b> {status_icon}\n"
            f"Тип: {report['problem_type']}\n"
            f"Статус: {status_text}\n"
            f"Дата: {report['timestamp'].split('T')[0]}\n\n"
        )
    
    update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML
    )

# Функция для обработки текстовых сообщений
def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    
    if text == "📊 Экологическая информация":
        eco_info(update, context)
    elif text == "📸 Сообщить о проблеме":
        report_problem(update, context)
    elif text == "🌿 Эко-советы":
        eco_tips(update, context)
    elif text == "📅 Волонтерские мероприятия":
        show_events(update, context)
    elif text == "📋 Мои отчеты":
        my_reports(update, context)
    elif text == "🔙 Главное меню":
        start(update, context)
    else:
        update.message.reply_text(
            "Извините, я не понимаю эту команду.\n"
            "Используйте кнопки меню для навигации или введите /help для справки."
        )

# Основная функция
def main() -> None:
    # Создаем Updater и передаем ему токен бота
    updater = Updater(TOKEN)
    
    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher
    
    # Создаем обработчик разговора для отчетов о проблемах
    report_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("report", report_problem),
            MessageHandler(Filters.regex("^📸 Сообщить о проблеме$"), report_problem)
        ],
        states={
            PHOTO: [MessageHandler(Filters.regex("^(🗑️ Незаконная свалка|💧 Загрязнение воды|🏭 Промышленные выбросы|🚗 Транспортное загрязнение|🔙 Главное меню)$"), handle_problem_type)],
            DESCRIPTION: [
                MessageHandler(Filters.photo, handle_photo),
                CommandHandler("skip", skip_photo)
            ],
            LOCATION: [MessageHandler(Filters.text & ~Filters.command, handle_description)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(Filters.regex("^🔙 Главное меню$"), cancel)
        ]
    )
    
    # Регистрируем обработчик разговора
    dispatcher.add_handler(report_conv_handler)
    
    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("eco", eco_info))
    dispatcher.add_handler(CommandHandler("tips", eco_tips))
    dispatcher.add_handler(CommandHandler("events", show_events))
    dispatcher.add_handler(CommandHandler("my_reports", my_reports))
    
    # Регистрируем обработчики callback-запросов
    dispatcher.add_handler(CallbackQueryHandler(city_info, pattern=r"^city_"))
    dispatcher.add_handler(CallbackQueryHandler(show_map, pattern=r"^map_"))
    dispatcher.add_handler(CallbackQueryHandler(back_to_cities, pattern=r"^back_to_cities"))
    dispatcher.add_handler(CallbackQueryHandler(next_tip, pattern=r"^next_tip"))
    dispatcher.add_handler(CallbackQueryHandler(join_event, pattern=r"^join_event"))
    
    # Регистрируем обработчик сообщений для всех остальных текстовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Регистрируем обработчик местоположения
    dispatcher.add_handler(MessageHandler(Filters.location, handle_location))
    
    # Выводим информацию о запуске
    print(f"EcoMap KZ Telegram бот запущен!")
    print(f"Откройте Telegram и найдите бота, которого вы создали через @BotFather")
    print(f"Или перейдите по ссылке https://t.me/[ваш_бот]")
    print(f"Для остановки бота нажмите Ctrl+C")
    
    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main() 