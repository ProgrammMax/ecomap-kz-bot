# Деплой на Vercel

## Шаг 1: Подготовка проекта

1. Проект уже подготовлен с правильной структурой для Vercel:
   - `/api` - содержит файлы для серверлесс-функций
   - `/public` - содержит статические файлы
   - `vercel.json` - конфигурация для Vercel

## Шаг 2: Создание и настройка проекта на Vercel

1. Откройте [Vercel Dashboard](https://vercel.com/dashboard)
2. Нажмите на "New Project"
3. В разделе "Import Git Repository", нажмите "Import Third-Party Git Repository" или выберите опцию загрузки вручную
4. Нажмите "Upload" и выберите папку с проектом или перетащите папку в указанную область

## Шаг 3: Настройка проекта

1. Имя проекта: ecomap-kz-bot
2. Framework Preset: Other
3. Root Directory: ./
4. Build Command: оставьте пустым
5. Output Directory: оставьте пустым
6. Install Command: pip install -r requirements.txt

## Шаг 4: Настройка переменных окружения

1. Раскройте раздел "Environment Variables"
2. Добавьте следующие переменные:
   - Имя: `TELEGRAM_TOKEN`, Значение: `7543391406:AAGdZn8Pk0o95MtVlPiZHKz-efkwQPF4aEc`
   - Имя: `MONGODB_URI`, Значение: [ваша строка подключения к MongoDB]
   - Имя: `DB_NAME`, Значение: `ecomap_kz`

## Шаг 5: Деплой

1. Нажмите кнопку "Deploy"
2. Дождитесь завершения деплоя

## Шаг 6: Настройка вебхука Telegram

1. После успешного деплоя, вы получите URL вашего проекта (например, https://ecomap-kz-bot.vercel.app)
2. Настройте вебхук для Telegram бота, открыв следующую ссылку в браузере (заменив YOUR_VERCEL_URL на ваш URL):
```
https://api.telegram.org/bot7543391406:AAGdZn8Pk0o95MtVlPiZHKz-efkwQPF4aEc/setWebhook?url=YOUR_VERCEL_URL/api/webhook
```

## Шаг 7: Проверка

1. Откройте бота в Telegram (@ecomap_kz_bot)
2. Отправьте команду `/start`
3. Проверьте, что бот отвечает на команды 