const express = require('express');
const bodyParser = require('body-parser');
const redis = require('redis');
const cors = require('cors');

// Create an express app
const app = express();

// Connect to Redis (you can modify the host/port if you're using Docker differently)
const client = redis.createClient({
  host: 'localhost',  // Update this if you're using Docker or a different host
  port: 6379,         // Redis default port
});

app.use(cors());
app.use(bodyParser.json());

// Save session data to Redis
app.post('/save-session', (req, res) => {
    const { userId, sessionData } = req.body;
    if (!userId || !sessionData) {
        return res.status(400).send({ error: 'Invalid request format' });
    }
    
    // Store the session data in Redis (key = userId)
    client.set(userId, JSON.stringify(sessionData), (err, reply) => {
        if (err) {
            return res.status(500).send({ error: 'Failed to save session' });
        }
        res.status(200).send({ message: 'Session saved successfully' });
    });
});

// Retrieve session data from Redis
app.get('/get-session/:userId', (req, res) => {
    const userId = req.params.userId;

    // Retrieve session data from Redis
    client.get(userId, (err, data) => {
        if (err) {
            return res.status(500).send({ error: 'Failed to retrieve session' });
        }
        if (data) {
            return res.status(200).send({ sessionData: JSON.parse(data) });
        }
        res.status(404).send({ message: 'Session not found' });
    });
});

// Start the server
app.listen(5000, () => console.log('Server running on port 5000'));