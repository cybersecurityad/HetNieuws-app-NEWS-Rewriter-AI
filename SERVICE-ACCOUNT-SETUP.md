# 🔑 Firebase Service Account Key Setup Guide

## Step-by-Step Instructions

### 1. Download Service Account Key

1. **Go to Firebase Console:**
   ```
   https://console.firebase.google.com/project/hetnieuws-app/settings/serviceaccounts/adminsdk
   ```

2. **Generate New Private Key:**
   - Click the "Generate new private key" button
   - A dialog will warn you about keeping the key secure
   - Click "Generate key"

3. **Download the JSON File:**
   - The file will automatically download
   - It will have a name like: `hetnieuws-app-firebase-adminsdk-xxxxx-xxxxxxxxxx.json`

### 2. Save the Key File

1. **Rename and Move the File:**
   ```bash
   # Move the downloaded file to your project root and rename it
   mv ~/Downloads/hetnieuws-app-firebase-adminsdk-*.json ./serviceAccountKey.json
   ```

2. **Verify the File Location:**
   ```bash
   ls -la serviceAccountKey.json
   ```
   You should see the file in your project root directory.

### 3. Security Check

✅ **The file is already added to `.gitignore`** - this prevents accidentally committing it to version control.

**Verify it's in .gitignore:**
```bash
grep -n "serviceAccountKey.json" .gitignore
```

### 4. Test the Setup

**Run the Firebase test:**
```bash
node test-firebase.js
```

**Expected output:**
```
🔥 Testing Firebase Connection...
🔑 Using service account key for Firebase authentication
✅ Firebase Admin initialized successfully
📡 Testing Firestore connection...
✅ Successfully wrote test document to Firestore
✅ Successfully read test document from Firestore
🗑️  Test document cleaned up
📰 Checking HetNieuws.RW collection...
ℹ️  HetNieuws.RW collection is empty
🗄️  Testing Firebase Storage...
✅ Firebase Storage bucket accessible

🎉 All Firebase tests completed!
```

### 5. Start Your Server

**Start the Firebase-enabled server:**
```bash
node server-firebase.js
```

**Expected output:**
```
🔑 Using service account key for Firebase authentication
✅ Firebase Admin initialized successfully
Server is running on port 3000
Health check available at: http://localhost:3000/health
Database: Firestore
Project ID: hetnieuws-app
```

### 6. Test Your Website

1. **Open your browser to:**
   ```
   http://localhost:3000
   ```

2. **Or open the static file directly:**
   ```bash
   open index.html
   ```

3. **Check the browser console** for any Firebase connection messages.

## 🔒 Security Best Practices

### ✅ DO:
- Keep the service account key file secure
- Never commit it to version control
- Use environment variables in production
- Rotate keys regularly (every 90 days recommended)
- Limit service account permissions to minimum required

### ❌ DON'T:
- Share the key file via email or chat
- Store it in public repositories
- Use the same key across multiple environments
- Leave it in Downloads folder

## 🚀 Production Deployment

For production environments, consider these alternatives:

### Option 1: Environment Variable
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"
```

### Option 2: Cloud Provider Secrets
- **Heroku:** Use config vars
- **Vercel:** Use environment variables
- **AWS/GCP:** Use their secret management services

### Option 3: Application Default Credentials
```bash
# On your production server
gcloud auth application-default login
```

## 🛠️ Troubleshooting

### "File not found" Error
```bash
# Check if file exists
ls -la serviceAccountKey.json

# Check file permissions
chmod 600 serviceAccountKey.json
```

### "Invalid key format" Error
- Ensure the JSON file is not corrupted
- Re-download from Firebase Console
- Check file encoding (should be UTF-8)

### "Permission denied" Error
- Verify the service account has the correct roles:
  - Firebase Admin SDK Administrator Service Agent
  - Cloud Datastore User
  - Storage Admin (if using Firebase Storage)

## 📞 Need Help?

If you encounter issues:

1. **Run the test script:** `node test-firebase.js`
2. **Check the error messages** - they usually contain helpful hints
3. **Verify your Firebase project settings** in the console
4. **Try regenerating the service account key** if authentication fails

## 🎉 Success!

Once everything is working, you should see:
- ✅ Firebase test passes
- ✅ Server starts without errors
- ✅ Website loads data from Firestore
- ✅ No authentication errors in logs

Your HetNieuws.app is now securely connected to Firebase! 🔥
