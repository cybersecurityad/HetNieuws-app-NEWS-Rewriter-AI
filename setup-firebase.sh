#!/bin/bash

echo "🔥 Firebase Setup Script for HetNieuws.app"
echo "=========================================="

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Installing..."
    npm install -g firebase-tools
else
    echo "✅ Firebase CLI is installed"
fi

# Check if gcloud CLI is installed (needed for Application Default Credentials)
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    echo "Or run: curl https://sdk.cloud.google.com | bash"
else
    echo "✅ Google Cloud CLI is installed"
fi

echo ""
echo "🔧 Setting up Firebase authentication..."
echo "Choose your authentication method:"
echo "1. Use Application Default Credentials (Recommended)"
echo "2. Use Service Account Key file"
echo ""

read -p "Enter your choice (1 or 2): " auth_choice

if [ "$auth_choice" = "1" ]; then
    echo ""
    echo "🔑 Setting up Application Default Credentials..."
    echo "This will open a browser window for authentication."
    echo ""
    
    # Login to Firebase
    firebase login
    
    # Set up gcloud credentials
    gcloud auth application-default login
    
    # Set the project
    gcloud config set project hetnieuws-app
    
    echo ""
    echo "✅ Application Default Credentials configured!"
    echo "Your application will now use these credentials automatically."
    
elif [ "$auth_choice" = "2" ]; then
    echo ""
    echo "📋 To use a Service Account Key:"
    echo "1. Go to: https://console.firebase.google.com/project/hetnieuws-app/settings/serviceaccounts/adminsdk"
    echo "2. Click 'Generate new private key'"
    echo "3. Download the JSON file"
    echo "4. Save it as 'serviceAccountKey.json' in your project root"
    echo "5. Update the server-firebase.js file to use the service account key"
    echo ""
    echo "⚠️  Remember to add 'serviceAccountKey.json' to your .gitignore file!"
    
else
    echo "❌ Invalid choice. Please run the script again."
    exit 1
fi

echo ""
echo "📦 Installing Node.js dependencies..."
npm install

echo ""
echo "🔥 Firebase setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Make sure your Firestore database is set up in the Firebase Console"
echo "2. Update your security rules if needed"
echo "3. Run 'node server-firebase.js' to start your server"
echo "4. Open your index.html to test the connection"
echo ""
echo "🌐 Firebase Console: https://console.firebase.google.com/project/hetnieuws-app"
echo ""
