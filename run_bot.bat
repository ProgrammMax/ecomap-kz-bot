@echo off
echo === EcoMap KZ Telegram Bot ===
echo.
echo Проверка зависимостей...
pip install -r requirements.txt
echo.
echo Запуск бота...
python bot.py
echo.
pause 