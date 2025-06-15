<template>
  <div class="login-container">
    <!-- Este componente ya no se usa, pero lo mantengo por si lo necesitas. -->
    <!-- La lógica de login ahora está integrada directamente en App.vue para una mejor experiencia. -->
    <div v-if="!user" class="login-box">
      <h2 class="welcome-title">Bienvenido a Sumy</h2>
      <p class="welcome-subtitle">Tu Sumiller Personal con IA</p>
      <button @click="signInWithGoogle" class="google-btn">
        <svg class="google-icon" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
          <path fill="#4285F4" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8c-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039L38.485 14.85C34.643 11.333 29.636 9 24 9C12.954 9 4 17.954 4 29s8.954 20 20 20s20-8.954 20-20c0-1.341-.138-2.65-.389-3.917z"/>
          <path fill="#34A853" d="M6.306 14.691L11.09 18.21c1.331-4.333 5.06-7.491 9.91-8.582L6.306 5.309C3.693 8.627 2 12.934 2 17.5c0 1.56.233 3.06.66 4.475l-4.73 3.55C.67 22.99 0 20.36 0 17.5s.67-5.49 2.1-7.899z" transform="translate(20,20) rotate(45) translate(-20,-20)"/>
          <path fill="#FBBC05" d="M24 44c5.166 0 9.6-1.691 12.821-4.561L31.545 35.7C29.2 37.331 26.75 38 24 38c-4.965 0-9.101-3.326-10.56-7.818L8.71 26.638C11.383 31.331 17.213 35 24 35z" transform="translate(20,20) rotate(-45) translate(-20,-20)"/>
          <path fill="#EA4335" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-2.75 0-5.2-0.669-7.29-1.802l-4.73 3.55C14.4 37.318 18.964 40 24 40c5.636 0 10.643-2.333 14.485-6.15L43.611 20.083z"/>
        </svg>
        <span>Acceder con Google!!</span>
      </button>
    </div>
    <div v-else class="user-info">
      <img :src="user.photoURL" :alt="user.displayName" class="user-avatar" />
      <span class="user-name">{{ user.displayName }}</span>
      <button @click="signOut" class="logout-btn">Salir</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut as firebaseSignOut, User } from 'firebase/auth';

// Inicializa Firebase (asume que ya está hecho en tu main.ts o un plugin)
const auth = getAuth();
const googleProvider = new GoogleAuthProvider();

const user = ref<User | null>(null);

onMounted(() => {
  onAuthStateChanged(auth, (newUser) => {
    user.value = newUser;
  });
});

const signInWithGoogle = async () => {
  try {
    await signInWithPopup(auth, googleProvider);
  } catch (error) {
    console.error('Error al iniciar sesión:', error);
  }
};

const signOut = async () => {
  try {
    await firebaseSignOut(auth);
  } catch (error) {
    console.error('Error al cerrar sesión:', error);
  }
};
</script>

<style scoped>
/* Estilos generales del contenedor */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #EFE6DD; /* Color crema de tu marca */
  font-family: 'Inter', sans-serif;
}

.login-box {
  background: #F5F5F5; /* Color claro de tu marca */
  padding: 3rem 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
  width: 90%;
  border: 1px solid #ddd;
}

.welcome-title {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  color: #2B2118; /* Oscuro de tu marca */
  margin-bottom: 0.5rem;
}

.welcome-subtitle {
  color: #6F1A07; /* Rojo de tu marca */
  margin-bottom: 2.5rem;
  font-size: 1.1rem;
}

/* --- ESTILO DEL BOTÓN DE GOOGLE MEJORADO --- */
.google-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  background-color: #4285F4; /* Azul de Google */
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 14px 0 rgba(0, 118, 255, 0.39);
}

.google-btn:hover {
  background-color: #357ae8;
  box-shadow: 0 6px 20px 0 rgba(0, 118, 255, 0.23);
  transform: translateY(-2px);
}

.google-icon {
  width: 24px;
  height: 24px;
  background: white;
  border-radius: 50%;
  padding: 2px;
}
/* ------------------------------------------- */

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: white;
  padding: 0.75rem 1.5rem;
  border-radius: 50px; /* Forma de píldora */
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #6F1A07; /* Borde con color de marca */
}

.user-name {
  font-weight: 600;
  color: #2B2118;
}

.logout-btn {
  background: #6F1A07; /* Rojo de tu marca */
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #A52A2A; /* Un rojo un poco más oscuro al pasar el ratón */
}
</style>
