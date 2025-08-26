const express = require('express');
const { MongoClient } = require('mongodb');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3000;

// MongoDB connection string from environment variable
const mongoUri =
    process.env.MONGO_URI ||
    'mongodb+srv://uas1:3890Hoi123@cluster0.elk3l4f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0';

let db;
MongoClient.connect(mongoUri, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
    .then((client) => {
        db = client.db('HetNieuws-app'); // Connect to the HetNieuws-app database
        console.log('Connected to Database');
    })
    .catch((error) => console.error(error));

app.use(cors());

// Endpoint to get blogs from 'HetNieuws.RW' collection
app.get('/get-blogs', async (req, res) => {
    try {
        const collection = db.collection('HetNieuws.RW'); // Fetch from HetNieuws.RW collection
        const blogs = await collection.find().toArray();
        res.json(blogs);
    } catch (error) {
        console.error('Error fetching blogs:', error);
        res.status(500).send('Error fetching blogs');
    }
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
