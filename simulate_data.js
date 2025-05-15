// Script to generate and upload simulated eco data to MongoDB
const { MongoClient } = require('mongodb');
require('dotenv').config();

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://ecomapkz:ecomapkzpassword@cluster0.ewtlfwf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0';
const DB_NAME = process.env.DB_NAME || 'ecomap_kz';

// Simulated eco points data (Kazakhstan locations)
const ecoPointsData = [
    {
        name: 'Пункт приема макулатуры',
        address: 'ул. Абая, 45, Алматы',
        coordinates: [43.238949, 76.889709], 
        type: 'recycling',
        accepts: ['paper', 'cardboard']
    },
    {
        name: 'Пункт приема пластика',
        address: 'ул. Жандосова, 58, Алматы',
        coordinates: [43.226782, 76.877457], 
        type: 'recycling',
        accepts: ['plastic', 'pet']
    },
    {
        name: 'Экоцентр "Зеленая Алматы"',
        address: 'пр. Достык, 85, Алматы',
        coordinates: [43.245163, 76.957306], 
        type: 'eco_center',
        accepts: ['paper', 'plastic', 'glass', 'metal']
    },
    {
        name: 'Пункт приема стекла',
        address: 'ул. Тимирязева, 42, Алматы',
        coordinates: [43.233726, 76.945264], 
        type: 'recycling',
        accepts: ['glass']
    },
    {
        name: 'Экопункт "Прогресс"',
        address: 'ул. Сатпаева, 90, Алматы',
        coordinates: [43.226453, 76.879389], 
        type: 'eco_center',
        accepts: ['paper', 'plastic', 'glass', 'metal', 'batteries']
    },
    {
        name: 'Пункт сбора батареек',
        address: 'пр. Аль-Фараби, 77, Алматы',
        coordinates: [43.207337, 76.928282], 
        type: 'recycling',
        accepts: ['batteries']
    },
    {
        name: 'Экомаркет',
        address: 'ул. Байтурсынова, 126, Алматы',
        coordinates: [43.240822, 76.923453], 
        type: 'eco_market',
        accepts: ['paper', 'plastic', 'glass', 'clothing']
    },
    {
        name: 'Пункт приема бытовой техники',
        address: 'ул. Розыбакиева, 247, Алматы',
        coordinates: [43.219781, 76.891956], 
        type: 'recycling',
        accepts: ['electronics']
    },
    {
        name: 'Астана Эко Центр',
        address: 'пр. Кабанбай батыра, 53, Астана',
        coordinates: [51.090707, 71.418365], 
        type: 'eco_center',
        accepts: ['paper', 'plastic', 'glass', 'metal', 'batteries', 'electronics']
    },
    {
        name: 'Эко Пункт Караганда',
        address: 'ул. Алиханова, 12, Караганда',
        coordinates: [49.801510, 73.087934], 
        type: 'recycling',
        accepts: ['paper', 'plastic', 'glass']
    }
];

// Function to generate random air quality data
function generateAirQualityData() {
    const airQualityLevels = ['Хорошее', 'Среднее', 'Плохое'];
    const weights = [0.5, 0.3, 0.2]; // Probabilities for each quality level
    
    // Weighted random selection
    const random = Math.random();
    let sum = 0;
    for (let i = 0; i < weights.length; i++) {
        sum += weights[i];
        if (random < sum) {
            return airQualityLevels[i];
        }
    }
    return airQualityLevels[0];
}

// Function to generate temperature based on location (simulated)
function generateTemperature(latitude) {
    // Basic simulation: more north = cooler
    const baseTemp = 25; // Base temperature in celsius
    const latitudeFactor = (latitude - 40) * 0.5; // Rough adjustment based on latitude
    const randomFactor = (Math.random() * 6) - 3; // Random variation ±3°C
    
    return (baseTemp - latitudeFactor + randomFactor).toFixed(1);
}

// Main function to upload data to MongoDB
async function uploadEcoData() {
    let client;
    
    try {
        // Connect to MongoDB
        client = new MongoClient(MONGODB_URI);
        await client.connect();
        console.log('Connected to MongoDB');
        
        const db = client.db(DB_NAME);
        const collection = db.collection('eco_points');
        
        // Clear existing data
        await collection.deleteMany({});
        console.log('Cleared existing eco_points data');
        
        // Prepare data with real-time info
        const dataToInsert = ecoPointsData.map(point => {
            return {
                ...point,
                air_quality: generateAirQualityData(),
                temperature: generateTemperature(point.coordinates[0]),
                last_updated: new Date().toISOString()
            };
        });
        
        // Insert data
        const result = await collection.insertMany(dataToInsert);
        console.log(`Inserted ${result.insertedCount} eco points into MongoDB`);
        
        // Create sample user data
        const userCollection = db.collection('users');
        await userCollection.deleteMany({});
        
        await userCollection.insertOne({
            user_id: '12345',
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
        });
        
        console.log('Created sample user data');
        
    } catch (error) {
        console.error('Error uploading eco data:', error);
    } finally {
        if (client) {
            await client.close();
            console.log('MongoDB connection closed');
        }
    }
}

// Run the function to upload data
uploadEcoData()
    .then(() => console.log('Data upload complete'))
    .catch(err => console.error('Error in main execution:', err));

// To run this script: 
// 1. Install dependencies: npm install mongodb dotenv
// 2. Execute: node simulate_data.js 