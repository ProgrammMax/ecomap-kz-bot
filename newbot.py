import asyncio
import os
from dotenv import load_dotenv
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from datetime import datetime

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение токена из переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN', '7543391406:AAGdZn8Pk0o95MtVlPiZHKz-efkwQPF4aEc')

# Создание бота и диспетчера
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создание клавиатуры
reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Открыть EcoMap KZ 🗺️")]
    ],
    resize_keyboard=True
)

# Определение состояний для FSM
class ReportStates(StatesGroup):
    location = State()
    description = State()
    photo = State()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, <b>{message.from_user.first_name}</b>! Я бот экологической карты Казахстана. "
        f"Я помогу вам отслеживать экологические проблемы в разных регионах страны.\n\n"
        f"Используйте кнопку ниже для доступа к экологической карте:",
        reply_markup=reply_kb
    )

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать взаимодействие с ботом\n"
        "/help - Показать это сообщение\n"
        "/map - Показать экологическую карту\n"
        "/report - Сообщить о проблеме\n"
        "/info - Информация о проекте"
    )
    await message.answer(help_text)

@dp.message_handler(lambda message: message.text == "Открыть EcoMap KZ 🗺️")
async def open_ecomap(message: types.Message):
    url = "https://ecomap-kz-bot.vercel.app"
    text = "🌍 Нажмите на кнопку ниже, чтобы открыть экологическую карту Казахстана 🌍"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🗺️ Открыть EcoMap KZ 🗺️", web_app=WebAppInfo(url=url)))
    await message.answer(text, reply_markup=keyboard)

@dp.message_handler(commands=['map'])
async def map_command(message: types.Message):
    url = "https://ecomap-kz-bot.vercel.app"
    text = "Экологическая карта Казахстана доступна по ссылке:"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🗺️ Открыть карту", web_app=WebAppInfo(url=url)))
    await message.answer(text, reply_markup=keyboard)

@dp.message_handler(commands=['info'])
async def info_command(message: types.Message):
    info_text = (
        "EcoMap KZ - проект экологической карты Казахстана.\n\n"
        "Наша цель - создать интерактивную карту экологических проблем "
        "и помочь гражданам и организациям отслеживать экологическую ситуацию "
        "в разных регионах страны.\n\n"
        "Сайт проекта: https://ecomap-kz-bot.vercel.app/"
    )
    await message.answer(info_text)

@dp.message_handler(commands=['report'])
async def report_start(message: types.Message):
    await ReportStates.location.set()
    await message.answer(
        "Пожалуйста, отправьте местоположение проблемы. "
        "Вы можете использовать функцию 'Отправить местоположение' в Telegram "
        "или просто написать название региона/города."
    )

@dp.message_handler(state=ReportStates.location)
async def location_received(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['location'] = message.text
    
    await ReportStates.description.set()
    await message.answer(
        f"Местоположение '{message.text}' сохранено. "
        f"Теперь, пожалуйста, опишите проблему."
    )

@dp.message_handler(state=ReportStates.description)
async def description_received(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    
    await ReportStates.photo.set()
    await message.answer(
        "Спасибо за описание! Если у вас есть фотография проблемы, "
        "пожалуйста, отправьте ее сейчас. Если нет, отправьте /skip."
    )

@dp.message_handler(content_types=['photo'], state=ReportStates.photo)
async def photo_received(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        location = data.get('location', 'Не указано')
        description = data.get('description', 'Не указано')
    
    photo = message.photo[-1]
    
    # Добавляем интеграцию с MongoDB
    try:
        from database_mongo import get_database
        db = get_database()
        report_id = db.save_report(
            user_id=message.from_user.id,
            location=location,
            description=description,
            photo_id=photo.file_id
        )
        logging.info(f"Сохранено сообщение о проблеме с ID: {report_id}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении в базу данных: {e}")
    
    await message.answer(
        f"Спасибо за сообщение о проблеме!\n\n"
        f"Местоположение: {location}\n"
        f"Описание: {description}\n\n"
        f"Ваше сообщение будет рассмотрено нашей командой."
    )
    await state.finish()

@dp.message_handler(commands=['skip'], state=ReportStates.photo)
async def skip_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        location = data.get('location', 'Не указано')
        description = data.get('description', 'Не указано')
    
    # Добавляем интеграцию с MongoDB
    try:
        from database_mongo import get_database
        db = get_database()
        report_id = db.save_report(
            user_id=message.from_user.id,
            location=location,
            description=description
        )
        logging.info(f"Сохранено сообщение о проблеме с ID: {report_id}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении в базу данных: {e}")
    
    await message.answer(
        f"Спасибо за сообщение о проблеме!\n\n"
        f"Местоположение: {location}\n"
        f"Описание: {description}\n\n"
        f"Ваше сообщение будет рассмотрено нашей командой."
    )
    await state.finish()

@dp.message_handler(commands=['cancel'], state='*')
async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.answer("Процесс сообщения о проблеме отменен.")

@dp.message_handler()
async def echo_handler(message: types.Message):
    await message.answer("Я не понимаю эту команду. Используйте /help для получения списка доступных команд.")

def main():
    print("EcoMap KZ Bot запускается...")
    print(f"Используется токен: {TOKEN}")
    
    try:
        print("Бот успешно настроен, запускаем...")
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == '__main__':
    main() 