import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyA6X3j5LVixUbSHkbIAs__QswXcATcDlgU",
  authDomain: "benchodlender.firebaseapp.com",
  projectId: "benchodlender",
  storageBucket: "benchodlender.firebasestorage.app",
  messagingSenderId: "138057350474",
  appId: "1:138057350474:web:f7543fc475148d322a55b3",
  measurementId: "G-41LCTQW4YB"
};

// Initialize Firebase and Export Firestore Database
const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);