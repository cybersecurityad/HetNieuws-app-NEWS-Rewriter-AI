// Firebase Configuration
const firebaseConfig = {
  apiKey: "AIzaSyDRPdYITsTptnCIRs9wZLeF2HK4Od7WA7w",
  authDomain: "hetnieuws-app.firebaseapp.com",
  databaseURL: "https://hetnieuws-app-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "hetnieuws-app",
  storageBucket: "hetnieuws-app.appspot.com",
  messagingSenderId: "204697555408",
  appId: "1:204697555408:web:9106c50ea7923f77bc29d5"
};

// Initialize Firebase
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const storage = getStorage(app);
export default app;
