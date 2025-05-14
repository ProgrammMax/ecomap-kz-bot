const express = require('express');
const path = require('path');
const { MongoClient } = require('mongodb');
require('dotenv').config();

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://ecomapkz:ecomapkzpassword@cluster0.ewtlfwf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0';
const DB_NAME = process.env.DB_NAME || 'ecomap_kz';

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from webapp/src directory
app.use(express.static(path.join(__dirname, 'webapp', 'src')));

// API endpoint for eco data
app.get('/api/webhook', async (req, res) => {
  if (req.query.type === 'eco_data') {
    try {
      // Fetch eco data from MongoDB or simulate if not available
      const client = new MongoClient(MONGODB_URI);
      await client.connect();
      
      const db = client.db(DB_NAME);
      const collection = db.collection('eco_points');
      
      // Get data
      let ecoPoints = await collection.find({}).toArray();
      
      // If no data in MongoDB, return simulated data
      if (!ecoPoints || ecoPoints.length === 0) {
        ecoPoints = [
          {
            name: 'Пункт приема макулатуры',
            address: 'ул. Абая, 45, Алматы',
            coordinates: [43.238949, 76.889709],
            air_quality: 'Хорошее',
            temperature: '22.3',
            last_updated: new Date().toISOString()
          },
          {
            name: 'Пункт приема пластика',
            address: 'ул. Жандосова, 58, Алматы',
            coordinates: [43.226782, 76.877457],
            air_quality: 'Среднее',
            temperature: '23.1',
            last_updated: new Date().toISOString()
          },
          {
            name: 'Экоцентр "Зеленая Алматы"',
            address: 'пр. Достык, 85, Алматы',
            coordinates: [43.245163, 76.957306],
            air_quality: 'Хорошее',
            temperature: '21.5',
            last_updated: new Date().toISOString()
          }
        ];
      } else {
        // Update with fresh real-time data
        ecoPoints = ecoPoints.map(point => {
          const airQualityLevels = ['Хорошее', 'Среднее', 'Плохое'];
          const randomAirQuality = airQualityLevels[Math.floor(Math.random() * airQualityLevels.length)];
          const temperature = (15 + Math.random() * 10).toFixed(1);
          
          return {
            ...point,
            air_quality: randomAirQuality,
            temperature: temperature,
            last_updated: new Date().toISOString()
          };
        });
      }
      
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
          name: 'Максимввв',
          points: 280,
          streak_days: 3543,
          activities: [
            { 
              title: 'Сдача пластика', 
              date: '10 мая 2025', 
              points: 50 
            },
            { 
              title: 'Участие в экосубботнике', 
              date: '5 мая 2025', 
              points: 100 
            },
            { 
              title: 'Сдача макулатуры', 
              date: '2 мая 2025', 
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