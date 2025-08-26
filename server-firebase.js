const express = require('express');
const cors = require('cors');

// Firebase Admin SDK setup
const admin = require('firebase-admin');

// Initialize Firebase Admin
if (!admin.apps.length) {
    try {
        // First, try to use service account key if it exists
        const fs = require('fs');
        const path = require('path');
        const serviceAccountPath = path.join(__dirname, 'serviceAccountKey.json');
        
        if (fs.existsSync(serviceAccountPath)) {
            console.log('🔑 Using service account key for Firebase authentication');
            const serviceAccount = require('./serviceAccountKey.json');
            admin.initializeApp({
                credential: admin.credential.cert(serviceAccount),
                projectId: 'hetnieuws-app',
                storageBucket: 'hetnieuws-app.appspot.com'
            });
        } else {
            // Fallback to Application Default Credentials
            console.log('🔑 Using Application Default Credentials for Firebase authentication');
            admin.initializeApp({
                projectId: 'hetnieuws-app',
                storageBucket: 'hetnieuws-app.appspot.com'
            });
        }
        
        console.log('✅ Firebase Admin initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing Firebase Admin:', error.message);
        console.log('\n🔧 To fix this issue:');
        console.log('1. Download your service account key from Firebase Console');
        console.log('2. Save it as "serviceAccountKey.json" in your project root');
        console.log('3. Or set up Application Default Credentials: gcloud auth application-default login');
        process.exit(1);
    }
}

const db = admin.firestore();

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Serve static files
app.use(express.static('.'));

// Endpoint to get blogs from Firestore 'HetNieuws.RW' collection
app.get('/get-blogs', async (req, res) => {
    try {
        console.log('Fetching blogs from Firestore...');
        const blogsCollection = db.collection('HetNieuws.RW');
        const snapshot = await blogsCollection.orderBy('timestamp', 'desc').limit(20).get();
        
        if (snapshot.empty) {
            console.log('No blogs found in Firestore');
            return res.json([]);
        }

        const blogs = [];
        snapshot.forEach(doc => {
            const data = doc.data();
            blogs.push({
                id: doc.id,
                ...data
            });
        });

        console.log(`Found ${blogs.length} blogs in Firestore`);
        res.json(blogs);
    } catch (error) {
        console.error('Error fetching blogs from Firestore:', error);
        res.status(500).json({ 
            error: 'Error fetching blogs',
            details: error.message 
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        service: 'HetNieuws.app API',
        database: 'Firestore',
        timestamp: new Date().toISOString()
    });
});

// Endpoint to get blogs by category
app.get('/blogs/category/:category', async (req, res) => {
    try {
        const category = req.params.category;
        console.log(`Fetching blogs for category: ${category}`);
        
        const blogsCollection = db.collection('HetNieuws.RW');
        const snapshot = await blogsCollection
            .where('category', '==', category)
            .orderBy('timestamp', 'desc')
            .limit(10)
            .get();
        
        const blogs = [];
        snapshot.forEach(doc => {
            const data = doc.data();
            blogs.push({
                id: doc.id,
                ...data
            });
        });

        console.log(`Found ${blogs.length} blogs for category ${category}`);
        res.json(blogs);
    } catch (error) {
        console.error('Error fetching blogs by category:', error);
        res.status(500).json({ 
            error: 'Error fetching blogs by category',
            details: error.message 
        });
    }
});

// Endpoint to get a single blog by slug
app.get('/blog/:category/:slug', async (req, res) => {
    try {
        const { category, slug } = req.params;
        console.log(`Fetching blog: ${category}/${slug}`);
        
        const blogsCollection = db.collection('HetNieuws.RW');
        const snapshot = await blogsCollection
            .where('category', '==', category)
            .where('slug', '==', slug)
            .limit(1)
            .get();
        
        if (snapshot.empty) {
            return res.status(404).json({ error: 'Blog not found' });
        }

        const doc = snapshot.docs[0];
        const blog = {
            id: doc.id,
            ...doc.data()
        };

        res.json(blog);
    } catch (error) {
        console.error('Error fetching single blog:', error);
        res.status(500).json({ 
            error: 'Error fetching blog',
            details: error.message 
        });
    }
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Unhandled error:', error);
    res.status(500).json({ 
        error: 'Internal server error',
        details: error.message 
    });
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
    console.log(`Health check available at: http://localhost:${port}/health`);
    console.log('Database: Firestore');
    console.log('Project ID: hetnieuws-app');
});

module.exports = app;
