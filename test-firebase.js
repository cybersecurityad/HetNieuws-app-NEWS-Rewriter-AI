// Firebase Connection Test
const admin = require('firebase-admin');

console.log('🔥 Testing Firebase Connection...');

// Initialize Firebase Admin
try {
    if (!admin.apps.length) {
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
    }
} catch (error) {
    console.error('❌ Error initializing Firebase Admin:', error.message);
    console.log('\n🔧 To fix this issue:');
    console.log('1. Download your service account key from Firebase Console');
    console.log('2. Save it as "serviceAccountKey.json" in your project root');
    console.log('3. Or set up Application Default Credentials: gcloud auth application-default login');
    process.exit(1);
}

const db = admin.firestore();

async function testFirestoreConnection() {
    try {
        console.log('📡 Testing Firestore connection...');
        
        // Test writing a document
        const testDoc = db.collection('test').doc('connection-test');
        await testDoc.set({
            message: 'Firebase connection test',
            timestamp: admin.firestore.FieldValue.serverTimestamp()
        });
        console.log('✅ Successfully wrote test document to Firestore');
        
        // Test reading the document
        const docSnapshot = await testDoc.get();
        if (docSnapshot.exists) {
            console.log('✅ Successfully read test document from Firestore');
            console.log('📄 Document data:', docSnapshot.data());
        }
        
        // Clean up test document
        await testDoc.delete();
        console.log('🗑️  Test document cleaned up');
        
        // Test querying the HetNieuws.RW collection
        console.log('📰 Checking HetNieuws.RW collection...');
        const rwCollection = db.collection('HetNieuws.RW');
        const snapshot = await rwCollection.limit(5).get();
        
        if (snapshot.empty) {
            console.log('ℹ️  HetNieuws.RW collection is empty');
        } else {
            console.log(`✅ Found ${snapshot.size} documents in HetNieuws.RW collection`);
            snapshot.forEach(doc => {
                const data = doc.data();
                console.log(`  - ${data.title || 'Untitled'} (${data.category || 'No category'})`);
            });
        }
        
    } catch (error) {
        console.error('❌ Firestore connection test failed:', error.message);
        
        if (error.code === 'permission-denied') {
            console.log('\n🔐 Permission denied. This might be because:');
            console.log('  1. Application Default Credentials are not set up');
            console.log('  2. Service account key is not properly configured');
            console.log('  3. Firestore security rules are too restrictive');
            console.log('\nTo fix this:');
            console.log('  • Run: gcloud auth application-default login');
            console.log('  • Or set up a service account key');
            console.log('  • Check your Firestore security rules');
        } else if (error.code === 'not-found') {
            console.log('\n🔍 Project not found. Make sure:');
            console.log('  • Project ID "hetnieuws-app" is correct');
            console.log('  • You have access to this Firebase project');
            console.log('  • Firestore is enabled in the Firebase Console');
        }
        
        process.exit(1);
    }
}

async function testFirebaseStorage() {
    try {
        console.log('🗄️  Testing Firebase Storage...');
        const bucket = admin.storage().bucket();
        
        // Test bucket access
        const [exists] = await bucket.exists();
        if (exists) {
            console.log('✅ Firebase Storage bucket accessible');
        } else {
            console.log('❌ Firebase Storage bucket not found');
        }
        
    } catch (error) {
        console.error('❌ Firebase Storage test failed:', error.message);
    }
}

async function runTests() {
    try {
        await testFirestoreConnection();
        await testFirebaseStorage();
        
        console.log('\n🎉 All Firebase tests completed!');
        console.log('\n📝 Next steps:');
        console.log('  1. Run your server: node server-firebase.js');
        console.log('  2. Open index.html in your browser');
        console.log('  3. Check browser console for any errors');
        
    } catch (error) {
        console.error('❌ Test suite failed:', error);
    }
    
    process.exit(0);
}

runTests();
