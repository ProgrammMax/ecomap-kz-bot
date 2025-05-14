# Интеграция EcoMap KZ Telegram-бота с веб-приложением

Этот документ описывает, как интегрировать Telegram-бота EcoMap KZ с веб-приложением для расширения функциональности.

## Настройка Telegram WebApp

Telegram позволяет интегрировать полноценные веб-приложения прямо в бота с помощью WebApp API.

### Шаг 1: Создание простого веб-приложения

1. Создайте HTML/CSS/JS веб-страницу для отображения экологической карты 
2. Разместите ее на хостинге с поддержкой HTTPS (например, GitHub Pages, Netlify)
3. Убедитесь, что сайт работает по HTTPS и доступен публично

Минимальный пример HTML-страницы с отображением карты:

```html
<!DOCTYPE html>
<html>
<head>
    <title>EcoMap KZ</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { 
            margin: 0; 
            padding: 0; 
            font-family: Arial, sans-serif; 
        }
        #map { 
            height: 100vh; 
            width: 100%; 
        }
        .info-box {
            padding: 10px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        // Инициализация Telegram WebApp
        const tg = window.Telegram.WebApp;
        tg.expand();
        
        // Инициализация карты
        const map = L.map('map').setView([48.0196, 66.9237], 5);
        
        // Добавление слоя OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        // Добавление маркеров для городов
        const cities = [
            {name: "Алматы", air_quality: "Средний", pm25: 42, temp: 22, lat: 43.238949, lon: 76.889709, color: "orange"},
            {name: "Нур-Султан", air_quality: "Хороший", pm25: 15, temp: 18, lat: 51.169392, lon: 71.449074, color: "green"},
            {name: "Шымкент", air_quality: "Плохой", pm25: 87, temp: 25, lat: 42.315514, lon: 69.586907, color: "red"}
        ];
        
        cities.forEach(city => {
            const marker = L.circleMarker([city.lat, city.lon], {
                color: city.color,
                fillColor: city.color,
                fillOpacity: 0.5,
                radius: 10
            }).addTo(map);
            
            marker.bindPopup(`
                <div class="info-box">
                    <h3>${city.name}</h3>
                    <p>Качество воздуха: ${city.air_quality}</p>
                    <p>PM2.5: ${city.pm25} мкг/м³</p>
                    <p>Температура: ${city.temp}°C</p>
                </div>
            `);
        });
        
        // Получение данных из Telegram (если они переданы)
        document.addEventListener("DOMContentLoaded", function() {
            const initData = tg.initData || '';
            if (initData) {
                try {
                    const data = JSON.parse(decodeURIComponent(initData));
                    // Можно использовать данные, переданные из бота
                    console.log(data);
                } catch (e) {
                    console.error(e);
                }
            }
        });
    </script>
</body>
</html>
```

### Шаг 2: Настройка бота для WebApp

1. Перейдите к @BotFather в Telegram
2. Отправьте команду /mybots
3. Выберите вашего бота
4. Нажмите "Bot Settings" → "Menu Button" → "Configure menu button"
5. Отправьте URL вашего веб-приложения
6. Укажите текст для кнопки (например, "Открыть карту")

### Шаг 3: Добавление кнопки WebApp в бота

Добавьте следующий код в функцию start() в боте:

```python
def start(update: Update, context: CallbackContext) -> None:
    # ... существующий код ...
    
    # Добавляем кнопку WebApp
    web_app_button = WebAppInfo(url="https://your-webapp-url.com")
    keyboard = [
        [KeyboardButton("📊 Экологическая информация")],
        [KeyboardButton("📸 Сообщить о проблеме")],
        [KeyboardButton("🌿 Эко-советы")],
        [KeyboardButton("📅 Волонтерские мероприятия")],
        [KeyboardButton("📋 Мои отчеты")],
        [KeyboardButton("🗺️ Открыть интерактивную карту", web_app=web_app_button)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ... оставшийся код ...
```

## Обмен данными между ботом и веб-приложением

### Передача данных от бота к веб-приложению

Добавьте в бота следующий код для передачи данных:

```python
def open_webapp(update: Update, context: CallbackContext) -> None:
    reports = database.get_all_reports()
    
    # Подготовка данных для передачи в веб-приложение
    data = {
        "reports": reports,
        "eco_data": eco_data
    }
    
    # Сериализация данных в JSON
    serialized_data = json.dumps(data)
    
    # Создание URL с параметрами
    webapp_url = f"https://your-webapp-url.com?data={urllib.parse.quote(serialized_data)}"
    
    # Создание кнопки WebApp
    web_app_button = WebAppInfo(url=webapp_url)
    keyboard = [[KeyboardButton("Открыть карту", web_app=web_app_button)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "Нажмите кнопку ниже, чтобы открыть интерактивную карту:",
        reply_markup=reply_markup
    )
```

### Получение данных из веб-приложения в боте

Для получения данных, отправленных из веб-приложения обратно в бота, используйте следующий код:

```python
# Обработчик для данных из WebApp
def handle_webapp_data(update: Update, context: CallbackContext) -> None:
    # Получаем данные из запроса WebApp
    webapp_data = update.effective_message.web_app_data.data
    
    try:
        # Парсим JSON данные
        data = json.loads(webapp_data)
        
        # Обрабатываем полученные данные
        if "report" in data:
            report = data["report"]
            report_id = database.add_report(
                user_id=update.effective_user.id,
                username=update.effective_user.username or update.effective_user.first_name,
                problem_type=report.get("problem_type", "Не указано"),
                description=report.get("description", "Не указано"),
                location=report.get("location", "Не указано"),
                photo_id=None
            )
            
            update.message.reply_text(f"Спасибо за отчет! Ему присвоен номер: {report_id}")
            
    except json.JSONDecodeError:
        update.message.reply_text("Ошибка при обработке данных")

# Регистрируем обработчик
dispatcher.add_handler(MessageHandler(Filters.status_update.web_app_data, handle_webapp_data))
```

## Размещение веб-приложения

Для размещения веб-приложения рекомендуется использовать:

1. **GitHub Pages** - бесплатное размещение статических сайтов
2. **Netlify** - бесплатное размещение с автоматическим деплоем из репозитория
3. **Vercel** - бесплатное размещение сервисов на JavaScript/Next.js

## Ресурсы

- [Документация Telegram Bot API по WebApp](https://core.telegram.org/bots/webapps)
- [Telegram JavaScript SDK](https://core.telegram.org/bots/webapps#initializing-mini-apps)
- [Leaflet.js - библиотека для интерактивных карт](https://leafletjs.com/) 