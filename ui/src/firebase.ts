import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Configuración de Firebase para maitre-ia-app
const firebaseConfig = {
  apiKey: "AIzaSyBdPSgUy8Tn848tXha3w_Tp3SHRmBRSq70",
  authDomain: "maitre-ia-app.firebaseapp.com",
  projectId: "maitre-ia-app",
  storageBucket: "maitre-ia-app.firebasestorage.app",
  messagingSenderId: "541283103325",
  appId: "1:541283103325:web:3e22532f28ea418590d3b4"
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);

// Exportar servicios
export const auth = getAuth(app);
export const db = getFirestore(app);

export default app; 