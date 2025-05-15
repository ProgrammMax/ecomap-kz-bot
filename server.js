const express = require('express');
const path = require('path');
const { MongoClient, ObjectId } = require('mongodb');
const multer = require('multer');
const fs = require('fs');
require('dotenv').config();

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://ecomapkz:ecomapkzpassword@cluster0.ewtlfwf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0';
const DB_NAME = process.env.DB_NAME || 'ecomap_kz';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware для обработки JSON
app.use(express.json());

// Настройка multer для загрузки изображений
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = path.join(__dirname, 'public', 'uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ storage: storage });

// Serve static files from webapp/src directory
app.use(express.static(path.join(__dirname, 'webapp', 'src')));
app.use('/uploads', express.static(path.join(__dirname, 'public', 'uploads')));
app.use('/icons', express.static(path.join(__dirname, 'public', 'icons')));
app.use('/demo', express.static(path.join(__dirname, 'public', 'demo')));

// API эндпоинты для экологических проблем
app.get('/api/problems', async (req, res) => {
  try {
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db(DB_NAME);
    const collection = db.collection('eco_problems');
    
    // Получаем данные из MongoDB
    let problems = await collection.find({}).toArray();
    
    // Если данных нет, генерируем демо-данные
    if (!problems || problems.length === 0) {
      problems = [
        {
          id: 1,
          type: 'garbage',
          description: 'Большая несанкционированная свалка',
          location: 'Алматы, мкр. Орбита',
          coordinates: [43.2220, 76.8512],
          createdAt: new Date('2023-05-10T10:00:00').toISOString(),
          confirmations: 5,
          photos: ['demo/garbage1.jpg']
        },
        {
          id: 2,
          type: 'air',
          description: 'Сильный смог от местного завода',
          location: 'Караганда, ул. Заводская',
          coordinates: [49.8015, 73.1021],
          createdAt: new Date('2023-05-15T14:30:00').toISOString(),
          confirmations: 12,
          photos: ['demo/air1.jpg']
        },
        {
          id: 3,
          type: 'water',
          description: 'Загрязнение реки промышленными отходами',
          location: 'Усть-Каменогорск, набережная',
          coordinates: [49.9480, 82.6149],
          createdAt: new Date('2023-05-20T09:15:00').toISOString(),
          confirmations: 8,
          photos: ['demo/water1.jpg']
        },
        {
          id: 4,
          type: 'deforestation',
          description: 'Незаконная вырубка деревьев в парковой зоне',
          location: 'Астана, Центральный парк',
          coordinates: [51.1605, 71.4704],
          createdAt: new Date('2023-05-25T16:45:00').toISOString(),
          confirmations: 15,
          photos: ['demo/forest1.jpg']
        }
      ];
    }
    
    await client.close();
    res.json(problems);
  } catch (error) {
    console.error('Error fetching problems:', error);
    res.status(500).json({ error: 'Failed to fetch problems' });
  }
});

// Добавление новой экопроблемы
app.post('/api/problems', upload.single('photo'), async (req, res) => {
  try {
    const { type, description, location, coordinates } = req.body;
    
    // Проверяем наличие необходимых полей
    if (!type || !description || !location || !coordinates) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    let parsedCoordinates;
    try {
      parsedCoordinates = JSON.parse(coordinates);
    } catch (e) {
      return res.status(400).json({ error: 'Invalid coordinates format' });
    }
    
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db(DB_NAME);
    const collection = db.collection('eco_problems');
    
    // Создаем новую проблему
    const newProblem = {
      type,
      description,
      location,
      coordinates: parsedCoordinates,
      createdAt: new Date().toISOString(),
      confirmations: 0,
      photos: []
    };
    
    // Если есть фото, добавляем его
    if (req.file) {
      newProblem.photos = [`uploads/${req.file.filename}`];
    }
    
    const result = await collection.insertOne(newProblem);
    
    await client.close();
    
    res.status(201).json({ 
      success: true, 
      message: 'Problem reported successfully',
      problem: { ...newProblem, _id: result.insertedId }
    });
  } catch (error) {
    console.error('Error adding problem:', error);
    res.status(500).json({ error: 'Failed to add problem' });
  }
});

// Подтверждение проблемы
app.post('/api/problems/:id/confirm', async (req, res) => {
  try {
    const problemId = req.params.id;
    
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db(DB_NAME);
    const collection = db.collection('eco_problems');
    
    // Увеличиваем счетчик подтверждений
    const result = await collection.updateOne(
      { _id: new ObjectId(problemId) },
      { $inc: { confirmations: 1 } }
    );
    
    if (result.matchedCount === 0) {
      await client.close();
      return res.status(404).json({ error: 'Problem not found' });
    }
    
    await client.close();
    
    res.json({ success: true, message: 'Problem confirmed' });
  } catch (error) {
    console.error('Error confirming problem:', error);
    res.status(500).json({ error: 'Failed to confirm problem' });
  }
});

// API для данных о качестве воздуха
app.get('/api/air-quality', async (req, res) => {
  try {
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db(DB_NAME);
    const collection = db.collection('air_quality');
    
    // Получаем данные о качестве воздуха
    let airQualityData = await collection.find({}).toArray();
    
    // Если данных нет, генерируем демо-данные
    if (!airQualityData || airQualityData.length === 0) {
      airQualityData = {
        'Алматы': { aqi: 95, status: 'Средний', pm25: 35.2 },
        'Астана': { aqi: 55, status: 'Умеренный', pm25: 15.8 },
        'Караганда': { aqi: 120, status: 'Плохой', pm25: 42.5 },
        'Шымкент': { aqi: 85, status: 'Средний', pm25: 28.6 },
        'Актау': { aqi: 45, status: 'Хороший', pm25: 10.2 },
        'Атырау': { aqi: 75, status: 'Умеренный', pm25: 22.1 }
      };
    }
    
    await client.close();
    res.json(airQualityData);
  } catch (error) {
    console.error('Error fetching air quality data:', error);
    res.status(500).json({ error: 'Failed to fetch air quality data' });
  }
});

// API для рекомендаций по устойчивому образу жизни
app.get('/api/eco-tips', async (req, res) => {
  try {
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db(DB_NAME);
    const collection = db.collection('eco_tips');
    
    // Получаем данные из MongoDB
    let ecoTips = await collection.find({}).toArray();
    
    // Если данных нет, возвращаем демо-данные
    if (!ecoTips || ecoTips.length === 0) {
      ecoTips = [
        {
          id: 1,
          title: 'Сортировка отходов',
          description: 'Разделяйте отходы на категории: пластик, бумага, стекло, металл и органические отходы.',
          icon: 'recycling-icon.png'
        },
        {
          id: 2,
          title: 'Экономия воды',
          description: 'Закрывайте кран во время чистки зубов. Используйте режим экономии воды в стиральной машине.',
          icon: 'water-icon.png'
        },
        {
          id: 3,
          title: 'Экономия энергии',
          description: 'Выключайте свет, когда выходите из комнаты. Используйте энергосберегающие лампы.',
          icon: 'energy-icon.png'
        }
      ];
    }
    
    await client.close();
    res.json(ecoTips);
  } catch (error) {
    console.error('Error fetching eco tips:', error);
    res.status(500).json({ error: 'Failed to fetch eco tips' });
  }
});

// API для пунктов приема вторсырья
app.get('/api/recycling-points', async (req, res) => {
  try {
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db(DB_NAME);
    const collection = db.collection('eco_points');
    
    // Получаем данные из MongoDB
    let ecoPoints = await collection.find({}).toArray();
    
    await client.close();
    res.json(ecoPoints);
  } catch (error) {
    console.error('Error fetching recycling points:', error);
    res.status(500).json({ error: 'Failed to fetch recycling points' });
  }
});

// Legacy endpoint for eco data webhook
app.get('/api/webhook', async (req, res) => {
  if (req.query.type === 'eco_data') {
    try {
      const client = new MongoClient(MONGODB_URI);
      await client.connect();
      
      const db = client.db(DB_NAME);
      const collection = db.collection('eco_points');
      
      // Get data
      let ecoPoints = await collection.find({}).toArray();
      
      // Close connection
      await client.close();
      
      // Send response
      res.json(ecoPoints);
    } catch (error) {
      console.error('Error fetching eco data:', error);
      res.status(500).json({ error: 'Failed to fetch eco data' });
    }
  } 
  else if (req.query.type === 'user_data') {
    try {
      // Get user ID from query
      const userId = req.query.user_id || '12345';
      
      // Connect to MongoDB
      const client = new MongoClient(MONGODB_URI);
      await client.connect();
      
      const db = client.db(DB_NAME);
      const collection = db.collection('users');
      
      // Find user
      let user = await collection.findOne({ user_id: userId });
      
      // If user not found, return default data
      if (!user) {
        user = {
          name: 'Максим',
          points: 280,
          streak_days: 7,
          activities: [
            { 
              title: 'Сдача пластика', 
              date: '10 мая 2023', 
              points: 50 
            },
            { 
              title: 'Участие в экосубботнике', 
              date: '5 мая 2023', 
              points: 100 
            },
            { 
              title: 'Сдача макулатуры', 
              date: '2 мая 2023', 
              points: 30 
            }
          ]
        };
      }
      
      // Close connection
      await client.close();
      
      // Send response
      res.json(user);
    } catch (error) {
      console.error('Error fetching user data:', error);
      res.status(500).json({ error: 'Failed to fetch user data' });
    }
  }
  else {
    res.status(400).json({ error: 'Invalid query type' });
  }
});

// Catch-all handler for any other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'webapp', 'src', 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
}); 