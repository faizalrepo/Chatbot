const express = require('express');  // Import express to create the server
const bodyParser = require('body-parser');  // For handling request data
const { createClient } = require('redis');  // Redis client to interact with Redis

const app = express();  // Create an express app
app.use(bodyParser.json());  // Allow express to read JSON data from requests

// Connect to Redis server
const redisClient = createClient();
redisClient.connect().catch(console.error);

// A route to receive user input (chat messages)
app.post('/chat', async (req, res) => {
    const { sessionId, message } = req.body;  // Extract sessionId and message from request

    // Retrieve the current session data from Redis using the sessionId
    let chatSession = await redisClient.get(sessionId);

    if (!chatSession) {
        // If no session exists, start a new chat session
        chatSession = JSON.stringify([]);  // Start with an empty array
    }

    // Parse the session data (to work with it as an object)
    const sessionData = JSON.parse(chatSession);

    // Add the new user message and chatbot response to the session
    sessionData.push({ user: message, bot: 'Response from chatbot' });

    // Save the updated session data back to Redis
    await redisClient.set(sessionId, JSON.stringify(sessionData));

    // Send the updated session back as a response
    res.json({ sessionId, sessionData });
});

// A route to retrieve the chat session for a user
app.get('/chat/:sessionId', async (req, res) => {
    const sessionId = req.params.sessionId;  // Extract sessionId from URL

    // Retrieve the session data for this user from Redis
    const sessionData = await redisClient.get(sessionId);
    res.json({ sessionData: JSON.parse(sessionData) || [] });  // Send the session data as response
});

// Start the server
app.listen(3000, () => console.log('Server running on http://localhost:3000'));
