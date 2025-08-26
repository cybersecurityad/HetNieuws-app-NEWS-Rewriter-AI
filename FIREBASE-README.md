# HetNieuws.app - Firebase Migration Guide

## 🔥 Firebase Setup Complete!

Your HetNieuws.app has been successfully configured to use Firebase instead of MongoDB. Here's everything you need to know:

## 📁 New Files Created

### Frontend Configuration
- `firebase-config.js` - Firebase client configuration
- `index.html` - Updated with Firebase SDK integration

### Backend Configuration
- `server-firebase.js` - Express server using Firestore
- `firebase-rewriter.py` - Python script for Firestore operations
- `test-firebase.js` - Connection testing utility

### Firebase Configuration
- `firestore.rules` - Security rules for Firestore
- `firestore.indexes.json` - Database indexes
- `firebase.json` - Updated Firebase project configuration

### Setup Utilities
- `setup-firebase.sh` - Automated setup script

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Set Up Firebase Authentication
Choose one of these methods:

#### Option A: Application Default Credentials (Recommended)
```bash
# Run the setup script
./setup-firebase.sh

# Or manually:
npm install -g firebase-tools
firebase login
gcloud auth application-default login
gcloud config set project hetnieuws-app
```

#### Option B: Service Account Key
1. Go to [Firebase Console > Service Accounts](https://console.firebase.google.com/project/hetnieuws-app/settings/serviceaccounts/adminsdk)
2. Click "Generate new private key"
3. Download and save as `serviceAccountKey.json`
4. Update `server-firebase.js` to use the key file

### 3. Test Firebase Connection
```bash
node test-firebase.js
```

### 4. Start Your Server
```bash
# Use the new Firebase server
node server-firebase.js

# Or keep using the original MongoDB server
node server.js
```

### 5. Open Your Website
Open `index.html` in your browser or deploy to Firebase Hosting.

## 🔧 Configuration Details

### Firebase Project Configuration
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyDRPdYITsTptnCIRs9wZLeF2HK4Od7WA7w",
  authDomain: "hetnieuws-app.firebaseapp.com",
  databaseURL: "https://hetnieuws-app-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "hetnieuws-app",
  storageBucket: "hetnieuws-app.appspot.com",
  messagingSenderId: "204697555408",
  appId: "1:204697555408:web:9106c50ea7923f77bc29d5"
};
```

### Database Collections
- `HetNieuws.Raw` - Original scraped articles
- `HetNieuws.RW` - Processed/rewritten articles

### API Endpoints (server-firebase.js)
- `GET /get-blogs` - Fetch latest articles
- `GET /blogs/category/:category` - Fetch articles by category
- `GET /blog/:category/:slug` - Fetch single article
- `GET /health` - Health check

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Permission Denied" Error
```bash
# Set up authentication
gcloud auth application-default login
```

#### 2. "Project Not Found" Error
```bash
# Verify project ID
gcloud config set project hetnieuws-app
```

#### 3. "No Data Loading" in Frontend
- Check browser console for errors
- Verify Firestore security rules
- Test API endpoints directly

#### 4. Python Script Issues
```bash
# Install required packages
pip install firebase-admin google-cloud-firestore
```

### Firebase Console Links
- [Project Overview](https://console.firebase.google.com/project/hetnieuws-app)
- [Firestore Database](https://console.firebase.google.com/project/hetnieuws-app/firestore)
- [Storage](https://console.firebase.google.com/project/hetnieuws-app/storage)
- [Hosting](https://console.firebase.google.com/project/hetnieuws-app/hosting)

## 🔄 Migration from MongoDB

Your original MongoDB setup is preserved. The new Firebase setup runs alongside it:

### Original Files (MongoDB)
- `server.js` - Original Express server
- `rw-nl-hetnieuws-app.py` - Original Python script

### New Files (Firebase)
- `server-firebase.js` - New Express server
- `firebase-rewriter.py` - New Python script

You can run both systems and migrate data gradually.

## 📊 Data Migration

To migrate your existing MongoDB data to Firestore:

1. Export data from MongoDB
2. Transform the data format if needed
3. Import to Firestore using the Admin SDK
4. Update your frontend to use the new API

## 🚀 Deployment

### Deploy to Firebase Hosting
```bash
firebase deploy
```

### Deploy to Heroku (with Firebase backend)
```bash
# Update Procfile to use the new server
echo "web: node server-firebase.js" > Procfile
git add .
git commit -m "Switch to Firebase backend"
git push heroku main
```

## 📝 Environment Variables

Set these environment variables for production:

```bash
# For Python scripts
export OPENAI_API_KEY="your-openai-api-key"

# For Google Cloud authentication (if using service account)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"
```

## 🔍 Monitoring and Logs

### View Logs
```bash
# Firebase Functions logs
firebase functions:log

# Firestore operations
# Check Firebase Console > Firestore > Usage tab
```

### Performance Monitoring
- Enable Firebase Performance Monitoring in the console
- Monitor API response times and error rates

## 📞 Support

If you encounter issues:

1. Check the browser console for frontend errors
2. Check server logs for backend errors
3. Verify Firebase project permissions
4. Test with the `test-firebase.js` script

## 🎉 Success!

Your HetNieuws.app is now powered by Firebase! This provides:

- ✅ Scalable cloud database (Firestore)
- ✅ Fast CDN hosting (Firebase Hosting)
- ✅ Secure file storage (Cloud Storage)
- ✅ Real-time capabilities (if needed)
- ✅ Built-in analytics and monitoring
