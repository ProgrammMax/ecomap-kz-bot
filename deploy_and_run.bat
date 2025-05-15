@echo off
echo ======================================================
echo =       EcoMap KZ Bot - Deploy and Run Script       =
echo ======================================================
echo.

REM Настройка переменных окружения
set TELEGRAM_TOKEN=7543391406:AAGdZn8Pk0o95MtVlPiZHKz-efkwQPF4aEc
echo [INFO] Токен Telegram установлен

REM Проверка установки необходимых пакетов
echo [INFO] Проверка и установка необходимых пакетов...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ошибка при установке зависимостей
    goto :end
)

REM Деплой на Vercel
echo.
echo [INFO] Хотите выполнить деплой на Vercel? (Y/N)
set /p deploy_choice=
if /i "%deploy_choice%"=="Y" (
    echo.
    echo [INFO] Выполняется деплой на Vercel...
    call vercel --prod
    
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Ошибка при деплое на Vercel
        echo [INFO] Пожалуйста, убедитесь что vercel CLI установлен (npm i -g vercel)
    ) else (
        echo [SUCCESS] Деплой на Vercel успешно выполнен
        echo [INFO] Не забудьте настроить вебхук:
        echo https://api.telegram.org/bot%TELEGRAM_TOKEN%/setWebhook?url=YOUR_VERCEL_URL/api/webhook
    )
)

REM Запуск бота локально
echo.
echo [INFO] Хотите запустить бота локально? (Y/N)
set /p run_choice=
if /i "%run_choice%"=="Y" (
    echo.
    echo [INFO] Запуск бота в локальном режиме...
    echo.
    
    REM Запускаем улучшенную версию бота с исправленной кодировкой
    python -c "import os; os.environ['PYTHONIOENCODING'] = 'utf-8'; import bot_new; bot_new.main()"
    
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Ошибка при запуске бота
        echo [INFO] Попробуем запустить альтернативным методом...
        call run_bot_fixed.bat
    )
)

:end
echo.
echo [INFO] Скрипт выполнен
pause 