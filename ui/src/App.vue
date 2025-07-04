<!-- ui/src/App.vue -->
<template>
  <div class="flex flex-col h-full bg-brand-light font-sans antialiased">
    
    <!-- Encabezado -->
    <header class="fixed top-0 w-full bg-brand-dark text-white shadow-lg p-4 flex justify-between items-center z-10">
      <!-- Título a la Izquierda -->
      <div class="flex items-center">
        <h1 class="font-hand text-2xl sm:text-4xl text-brand-cream">{{ appName }}</h1>
      </div>

      <!-- Avatar Centrado -->
      <div class="absolute left-1/2 top-full -translate-x-1/2 -translate-y-1/2">
        <img src="./assets/sumi.png" alt="Sumi-IA Avatar" class="w-24 h-24 sm:w-32 sm:h-32 rounded-full">
      </div>

      <!-- Info de Usuario a la Derecha -->
      <div v-if="user" class="flex items-center gap-1 sm:gap-4">
        <span class="text-brand-cream hidden md:inline text-sm">{{ user.displayName }}</span>
        <button @click="showWineMenu = true" class="btn-wine-carta text-white font-semibold py-1.5 px-2 sm:py-2 sm:px-4 rounded-lg transition-all duration-300 transform hover:scale-105 text-xs sm:text-sm flex items-center gap-1 sm:gap-2 shadow-lg">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span class="hidden sm:inline">Ver Carta</span>
          <span class="sm:hidden">Carta</span>
        </button>
        <button @click="handleSignOut" class="btn-exit text-white font-semibold py-1.5 px-2 sm:py-2 sm:px-4 rounded-lg transition-all duration-300 transform hover:scale-105 text-xs sm:text-sm shadow-lg">
          Salir
        </button>
      </div>
    </header>

    <!-- Componente de Login -->
    <Login v-if="!user" />

    <!-- Contenedor del Chat -->
    <main class="flex-1 overflow-y-auto px-6 pb-24 pt-36 bg-brand-cream" ref="chatContainer" v-else>
      <div class="max-w-3xl mx-auto w-full space-y-6">
        <div v-for="message in messages" :key="message.id" class="flex items-end gap-3" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
          <!-- Avatar del Bot -->
          <div v-if="message.role === 'bot'" class="w-10 h-10 rounded-full bg-brand-dark flex items-center justify-center text-white font-serif text-xl flex-shrink-0">
            S
          </div>
          <!-- Burbuja de Mensaje -->
          <div class="py-3 px-5 rounded-2xl max-w-lg shadow-md" :class="{
            'bg-brand-red text-white rounded-br-lg': message.role === 'user',
            'bg-white text-brand-dark rounded-bl-lg': message.role === 'bot'
          }">
            <div v-if="message.role === 'bot'" class="prose prose-sm max-w-none prose-brand" v-html="renderMarkdown(message.text)"></div>
            <p v-else class="text-base">{{ message.text }}</p>
          </div>
        </div>
  
        <!-- Indicador de Carga -->
        <div v-if="isLoading" class="flex items-end gap-3 justify-start">
           <div class="w-10 h-10 rounded-full bg-brand-dark flex items-center justify-center text-white font-serif text-xl flex-shrink-0">S</div>
            <div class="py-3 px-5 rounded-2xl bg-white shadow-md">
                <div class="flex items-center space-x-2">
                    <div class="w-2 h-2 bg-brand-gray rounded-full animate-bounce" style="animation-delay: -0.3s;"></div>
                    <div class="w-2 h-2 bg-brand-gray rounded-full animate-bounce" style="animation-delay: -0.15s;"></div>
                    <div class="w-2 h-2 bg-brand-gray rounded-full animate-bounce"></div>
                </div>
              </div>
            </div>
          </div>
        </main>
  
    <!-- Pie de página con el input -->
    <footer class="fixed bottom-0 w-full bg-brand-light border-t border-brand-cream p-4" v-if="user">
      <div class="max-w-3xl mx-auto">
        <form @submit.prevent="sendMessage" class="flex items-center gap-3">
          <input 
            type="text" 
            v-model="userQuery" 
            :disabled="isLoading"
            placeholder="Recomiéndame un vino para..." 
            class="flex-1 p-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-red text-brand-dark placeholder-brand-gray"
          />
          <button 
            type="submit"
            :disabled="isLoading"
            class="btn-send text-white font-semibold p-3 rounded-lg disabled:opacity-50 transition-all duration-300 flex-shrink-0"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 12h14" /></svg>
          </button>
        </form>
      </div>
    </footer>

    <!-- Modal de la Carta de Vinos -->
    <WineMenu :isVisible="showWineMenu" @close="showWineMenu = false" />
    
    <!-- Banner de Consentimiento de Cookies -->
    <ConsentBanner @consent-updated="handleConsentUpdate" />
  </div>
</template>
  
<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut } from 'firebase/auth'
import { doc, setDoc, addDoc, collection, serverTimestamp } from 'firebase/firestore'
import { auth, db } from './firebase'
import axios from 'axios'
import { marked } from 'marked'
import Login from './components/Login.vue'
import WineMenu from './components/WineMenu.vue'
import ConsentBanner from './components/ConsentBanner.vue'

// Firebase ya está configurado en ./firebase.ts

// --- Estado Reactivo ---
const user = ref(null)
const messages = ref([])
const userQuery = ref('')
const isLoading = ref(false)
const error = ref(null)
const chatContainer = ref(null)
const conversationHistory = ref([])
const userPreferences = ref({})
const hasShownWelcome = ref(false)
const showWineMenu = ref(false)

// --- Gestión de Memoria Local ---
const buildConversationHistory = () => {
  return messages.value
    .filter(msg => msg.role === 'user' || msg.role === 'bot')
    .map(msg => ({
      role: msg.role === 'bot' ? 'assistant' : 'user',
      content: msg.text,
      timestamp: new Date().toISOString()
    }))
}



// --- Lógica de Guardado en Firestore ---
const saveUserToFirestore = async (userData) => {
  if (!userData) return;
  const userRef = doc(db, "users", userData.uid);
  try {
    await setDoc(userRef, {
      uid: userData.uid,
      displayName: userData.displayName,
      email: userData.email,
      lastLogin: serverTimestamp(),
    }, { merge: true });
  } catch (err) {
    console.error("Error al guardar el usuario en Firestore:", err);
  }
};

const saveConversationToFirestore = async (question, answer) => {
  if (!user.value) return;
  
  if (!answer || answer === undefined || answer === null) {
    console.warn("No se puede guardar conversación: respuesta vacía o undefined");
    return;
  }
  
  try {
    await addDoc(collection(db, 'conversations'), {
      userId: user.value.uid,
      userName: user.value.displayName || 'Usuario',
      question: question || '',
      answer: String(answer),
      createdAt: serverTimestamp(),
      metadata: {
        confidence: 0.95,  // Valor por defecto
        wine_type: null,   // Se puede extraer de la respuesta
        dish: null,        // Se puede extraer de la respuesta
        alternatives: 0    // Se puede extraer de la respuesta
      }
    });
  } catch (err) {
    console.error("Error al guardar la conversación en Firestore:", err);
  }
};

// --- Lógica de Autenticación ---
onMounted(() => {
  onAuthStateChanged(auth, async (currentUser) => {
    user.value = currentUser
    if (currentUser) {
      await saveUserToFirestore(currentUser);
      
      // Solo mostrar mensaje de bienvenida si no hay historial
      if (messages.value.length === 0 && !hasShownWelcome.value) {
        const firstName = currentUser.displayName ? currentUser.displayName.split(' ')[0] : 'Usuario';
        messages.value.push({
          id: Date.now(),
          role: 'bot',
          text: `¡Bienvenido, ${firstName}! Soy Sumy, tu sumiller digital. Si tienes cualquier duda sobre la carta de vinos, un maridaje o simplemente te apetece que te sorprenda, no dudes en preguntarme.`
        });
        hasShownWelcome.value = true;
      }
    }
  })
})



const handleSignOut = async () => {
  await signOut(auth)
  messages.value = []
  userQuery.value = ''
  conversationHistory.value = []
  userPreferences.value = {}
  hasShownWelcome.value = false
}

// --- Lógica del Chat ---
const sendMessage = async () => {
  if (!userQuery.value.trim() || isLoading.value) return

  const query = userQuery.value
  messages.value.push({ id: Date.now(), role: 'user', text: query })
  userQuery.value = ''
  isLoading.value = true
  error.value = null

  await nextTick()
  scrollToBottom()

  try {
    const token = await user.value.getIdToken()
    
    // Construir historial para el backend
    const conversationHistoryForBackend = buildConversationHistory()
    
    const apiUrl = import.meta.env.DEV 
      ? '/api/query' 
      : `${import.meta.env.VITE_MAITRE_URL}/query`

    const result = await axios.post(apiUrl, { 
      query: query,
      user_id: user.value.uid,
      user_name: user.value.displayName,
      conversation_history: conversationHistoryForBackend,
      user_preferences: userPreferences.value
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    // Manejar la nueva respuesta con metadatos
    const responseData = result.data;
    const botResponse = responseData.response || responseData || 'Lo siento, no pude procesar tu consulta correctamente.';
    
    // LOGGING DE TRAZABILIDAD EN CONSOLA
    console.group('🍷 Sumy - Trazabilidad de Respuesta');
    console.log('📝 Consulta:', query);
    console.log('💬 Respuesta:', botResponse);
    
    if (responseData.metadata) {
      console.log('📊 Metadatos completos:', responseData.metadata);
      
      const ragData = responseData.metadata.rag_data;
      if (ragData) {
        console.log('🔍 RAG utilizado:', ragData.rag_used);
        if (ragData.rag_used) {
          console.log('📚 Fuente de datos:', ragData.source);
          console.log('📈 Total resultados RAG:', ragData.total_results);
          
          if (ragData.sources) {
            console.log('🍷 Vinos de BD:', ragData.sources.wine_database_results);
            console.log('📖 Conocimiento de texto:', ragData.sources.knowledge_text_results);
            console.log('❓ Resultados desconocidos:', ragData.sources.unknown_results);
            
            if (ragData.sources.details && ragData.sources.details.length > 0) {
              console.log('📋 Detalles de fuentes:', ragData.sources.details);
            }
          }
        } else {
          console.log('❌ RAG no utilizado - Razón:', ragData.reason);
        }
      }
      
      console.log('🏷️ Categoría de consulta:', responseData.metadata.category);
      console.log('🎯 Clasificación:', responseData.metadata.classification);
      console.log('🤖 Fuente de respuesta:', responseData.metadata.response_source);
    } else {
      console.log('⚠️ No hay metadatos de trazabilidad disponibles');
    }
    console.groupEnd();

    // Agregar respuesta del bot
    messages.value.push({
      id: Date.now() + Math.random(),
      role: 'bot',
      text: botResponse
    });

    // Actualizar historial local
    conversationHistory.value = buildConversationHistory();

    // Guardar en Firestore con nombre de usuario
    await saveConversationToFirestore(query, botResponse);

  } catch (err) {
    const errorMessage = err.response?.data?.detail || 'No he podido procesar su consulta. Inténtelo de nuevo.'
    error.value = errorMessage
    messages.value.push({
      id: Date.now() + 1,
      role: 'bot',
      text: `Disculpe, ha ocurrido un error: ${errorMessage}`
    })
    console.error("Error en la consulta:", err)
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// --- Utilidades ---
const renderMarkdown = (text) => {
  return marked(text || '', { breaks: true, gfm: true });
}

const handleConsentUpdate = (consentRecord) => {
  console.log('🍪 Consentimiento actualizado:', consentRecord);
  
  // Aquí se pueden manejar las actualizaciones de consentimiento
  // Por ejemplo, cargar/descargar servicios de terceros basados en el consentimiento
  
  if (consentRecord.settings.analytics) {
    console.log('📊 Analytics habilitadas');
    // Cargar Google Analytics, etc.
  }
  
  if (consentRecord.settings.marketing) {
    console.log('📢 Marketing habilitado');
    // Cargar herramientas de marketing
  }
  
  if (consentRecord.settings.preferences) {
    console.log('⚙️ Preferencias habilitadas');
    // Cargar configuraciones de preferencias
  }
}

const appName = computed(() => "Sumy")
</script>

<style>
/* Modificamos los estilos de la prosa generada por `marked` para que coincidan con la nueva paleta de colores */
.prose-brand h1, .prose-brand h2, .prose-brand h3, .prose-brand h4 {
  color: #2B2118; /* brand-dark */
  font-family: 'Playfair Display', serif;
}
.prose-brand p {
  color: #2B2118;
  opacity: 0.9;
}
.prose-brand ul {
  list-style-type: '🍷';
  padding-left: 1.5em;
}
.prose-brand li::marker {
  font-size: 0.8em;
  padding-right: 0.5em;
}
.prose-brand strong {
  color: #6F1A07; /* brand-red */
}

/* Paleta inspirada en vino tinto - Botones elegantes */
.btn-wine-carta {
  background-color: #8c1c13; /* Burdeos oscuro */
  border: none;
}
.btn-wine-carta:hover {
  background-color: #6b1510; /* Burdeos más oscuro en hover */
  box-shadow: 0 8px 25px rgba(140, 28, 19, 0.3);
}

.btn-exit {
  background-color: #424242; /* Gris oscuro */
  border: none;
}
.btn-exit:hover {
  background-color: #333333; /* Gris más oscuro en hover */
  box-shadow: 0 8px 25px rgba(66, 66, 66, 0.3);
}

.btn-send {
  background-color: #a62929; /* Burdeos medio */
  border: none;
}
.btn-send:hover:not(:disabled) {
  background-color: #8c1c13; /* Burdeos oscuro en hover */
  box-shadow: 0 6px 20px rgba(166, 41, 41, 0.4);
  transform: translateY(-1px);
}
</style>