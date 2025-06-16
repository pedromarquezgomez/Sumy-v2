<template>
  <div>
    <!-- Banner de Consentimiento -->
    <div 
      v-show="showBanner"
      id="consent-banner" 
      class="fixed bottom-0 left-0 right-0 p-4 bg-white shadow-lg border-t border-gray-200 z-50 md:p-6"
      role="dialog"
      aria-labelledby="consent-title"
      aria-modal="true"
    >
      <div class="max-w-6xl mx-auto flex flex-col gap-4">
        <div class="flex justify-between items-start">
          <h3 id="consent-title" class="text-lg font-semibold">{{ title }}</h3>
          <button 
            @click="hideBanner" 
            class="text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500" 
            :aria-label="closeText"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        <p class="text-sm text-gray-600">{{ description }}</p>
        
        <!-- Panel de configuración detallada -->
        <div v-show="showDetails" id="consent-details" class="space-y-3 py-3 border-t border-b border-gray-200 my-2">
          
          <!-- Cookies Necesarias -->
          <div class="flex items-center justify-between">
            <div>
              <h4 class="font-medium text-sm">Cookies necesarias</h4>
              <p class="text-xs text-gray-500">Esenciales para el funcionamiento del sitio</p>
            </div>
            <div class="relative inline-block w-10 align-middle select-none">
              <input 
                type="checkbox" 
                id="consent-necessary" 
                class="opacity-0 absolute block w-6 h-6 cursor-not-allowed"
                :checked="true"
                disabled
                aria-label="Cookies necesarias (siempre activas)"
              />
              <label 
                for="consent-necessary" 
                class="block overflow-hidden h-6 rounded-full bg-blue-600 cursor-not-allowed"
              >
                <span class="absolute left-4 w-6 h-6 bg-white rounded-full border border-gray-300 transition-transform duration-300"></span>
              </label>
            </div>
          </div>
          
          <!-- Cookies Analíticas -->
          <div class="flex items-center justify-between">
            <div>
              <h4 class="font-medium text-sm">Cookies analíticas</h4>
              <p class="text-xs text-gray-500">Nos ayudan a mejorar el sitio</p>
            </div>
            <div class="relative inline-block w-10 align-middle select-none">
              <input 
                type="checkbox" 
                id="consent-analytics" 
                v-model="consentSettings.analytics"
                class="opacity-0 absolute block w-6 h-6 cursor-pointer"
                aria-label="Activar cookies analíticas"
              />
              <label 
                for="consent-analytics" 
                class="toggle-label block overflow-hidden h-6 rounded-full cursor-pointer"
                :class="consentSettings.analytics ? 'bg-blue-600' : 'bg-gray-300'"
              >
                <span 
                  class="absolute w-6 h-6 bg-white rounded-full border border-gray-300 transition-transform duration-300"
                  :class="consentSettings.analytics ? 'translate-x-4' : 'translate-x-0'"
                ></span>
              </label>
            </div>
          </div>
          
          <!-- Cookies de Marketing -->
          <div class="flex items-center justify-between">
            <div>
              <h4 class="font-medium text-sm">Cookies de marketing</h4>
              <p class="text-xs text-gray-500">Permiten mostrar publicidad relevante</p>
            </div>
            <div class="relative inline-block w-10 align-middle select-none">
              <input 
                type="checkbox" 
                id="consent-marketing" 
                v-model="consentSettings.marketing"
                class="opacity-0 absolute block w-6 h-6 cursor-pointer"
                aria-label="Activar cookies de marketing"
              />
              <label 
                for="consent-marketing" 
                class="toggle-label block overflow-hidden h-6 rounded-full cursor-pointer"
                :class="consentSettings.marketing ? 'bg-blue-600' : 'bg-gray-300'"
              >
                <span 
                  class="absolute w-6 h-6 bg-white rounded-full border border-gray-300 transition-transform duration-300"
                  :class="consentSettings.marketing ? 'translate-x-4' : 'translate-x-0'"
                ></span>
              </label>
            </div>
          </div>
          
          <!-- Cookies de Preferencias -->
          <div class="flex items-center justify-between">
            <div>
              <h4 class="font-medium text-sm">Cookies de preferencias</h4>
              <p class="text-xs text-gray-500">Recuerdan tus preferencias</p>
            </div>
            <div class="relative inline-block w-10 align-middle select-none">
              <input 
                type="checkbox" 
                id="consent-preferences" 
                v-model="consentSettings.preferences"
                class="opacity-0 absolute block w-6 h-6 cursor-pointer"
                aria-label="Activar cookies de preferencias"
              />
              <label 
                for="consent-preferences" 
                class="toggle-label block overflow-hidden h-6 rounded-full cursor-pointer"
                :class="consentSettings.preferences ? 'bg-blue-600' : 'bg-gray-300'"
              >
                <span 
                  class="absolute w-6 h-6 bg-white rounded-full border border-gray-300 transition-transform duration-300"
                  :class="consentSettings.preferences ? 'translate-x-4' : 'translate-x-0'"
                ></span>
              </label>
            </div>
          </div>
          
          <button 
            @click="saveCustomSettings" 
            class="w-full py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {{ saveSettingsText }}
          </button>
        </div>
        
        <!-- Botones de acción -->
        <div class="flex flex-wrap gap-2 md:gap-3">
          <button 
            @click="acceptOnlyNecessary" 
            class="flex-1 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            {{ onlyNecessaryText }}
          </button>
          <button 
            @click="acceptAll" 
            class="flex-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {{ acceptAllText }}
          </button>
          <button 
            @click="rejectAll" 
            class="flex-1 px-4 py-2 bg-gray-100 text-gray-800 text-sm font-medium rounded-md hover:bg-gray-200 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            {{ rejectAllText }}
          </button>
          <button 
            @click="showDetails = !showDetails" 
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            {{ showDetails ? 'Ocultar' : settingsText }}
          </button>
        </div>
      </div>
    </div>

    <!-- Botón flotante para abrir panel de consentimiento -->
    <button 
      v-show="showButton"
      @click="showBanner = true"
      id="consent-button" 
      class="fixed bottom-24 right-4 p-2 bg-gray-800 text-white rounded-full shadow-lg z-40 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
      aria-label="Configurar cookies"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    </button>

    <!-- Notificación -->
    <div 
      v-show="showNotification"
      id="consent-notification" 
      class="fixed bottom-4 left-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-[9999] transition-opacity duration-500"
      role="alert" 
      aria-live="polite"
    >
      <span>{{ notificationMessage }}</span>
    </div>
  </div>
</template>

<script>
import consentManager, { CookieCategory } from '../services/consentManager.js'

export default {
  name: 'ConsentBanner',
  props: {
    title: {
      type: String,
      default: 'Utilizamos cookies'
    },
    description: {
      type: String,
      default: 'Este sitio utiliza cookies para mejorar tu experiencia. Puedes elegir qué tipos de cookies aceptar. Las cookies necesarias son esenciales para el funcionamiento del sitio y no pueden desactivarse.'
    },
    acceptAllText: {
      type: String,
      default: 'Aceptar todo'
    },
    rejectAllText: {
      type: String,
      default: 'Rechazar todo'
    },
    settingsText: {
      type: String,
      default: 'Configurar'
    },
    closeText: {
      type: String,
      default: 'Cerrar'
    },
    saveSettingsText: {
      type: String,
      default: 'Guardar preferencias'
    },
    onlyNecessaryText: {
      type: String,
      default: 'Solo necesarias'
    }
  },
  data() {
    return {
      showBanner: false,
      showButton: false,
      showDetails: false,
      showNotification: false,
      notificationMessage: 'Preferencias de cookies actualizadas',
      consentSettings: {
        necessary: true,
        analytics: false,
        marketing: false,
        preferences: false
      }
    }
  },
  mounted() {
    this.checkConsentStatus();
    
    // Escuchar eventos del gestor de consentimiento
    consentManager.addEventListener('save', this.onConsentSaved);
  },
  beforeUnmount() {
    // Limpiar listeners
    consentManager.removeEventListener('save', this.onConsentSaved);
  },
  methods: {
    checkConsentStatus() {
      // Usar el gestor de consentimiento
      if (!consentManager.hasAnyConsent()) {
        // Si no hay consentimiento previo, mostrar banner
        this.showBanner = true;
      } else {
        // Si ya hay consentimiento, mostrar solo el botón flotante
        this.showButton = true;
        const record = consentManager.getConsentRecord();
        if (record) {
          this.consentSettings = { ...this.consentSettings, ...record.settings };
        }
      }
    },
    
    onConsentSaved(consentRecord) {
      // Callback para cuando se guarda el consentimiento
      this.$emit('consent-updated', consentRecord);
    },
    
    saveConsent(method = 'explicit') {
      const consentRecord = consentManager.saveConsent(this.consentSettings, method);
      
      if (consentRecord) {
        // Aplicar las configuraciones de cookies
        this.applyConsentSettings();
        
        this.showNotification = true;
        setTimeout(() => {
          this.showNotification = false;
        }, 3000);
      }
    },
    
    applyConsentSettings() {
      // Aquí se aplicarían las configuraciones reales de cookies
      if (this.consentSettings.analytics) {
        this.loadAnalytics();
      } else {
        this.removeAnalytics();
      }
      
      if (this.consentSettings.marketing) {
        this.loadMarketing();
      } else {
        this.removeMarketing();
      }
      
      if (this.consentSettings.preferences) {
        this.loadPreferences();
      } else {
        this.removePreferences();
      }
    },
    
    loadAnalytics() {
      // Placeholder para cargar Google Analytics u otras herramientas
      console.log('📊 Cargando herramientas de análisis...');
      // Aquí se cargaría Google Analytics
      if (typeof gtag !== 'undefined') {
        gtag('config', 'GA_MEASUREMENT_ID');
      }
    },
    
    removeAnalytics() {
      console.log('📊 Desactivando herramientas de análisis...');
      // Aquí se eliminarían las cookies de analytics
    },
    
    loadMarketing() {
      console.log('📢 Cargando herramientas de marketing...');
      // Aquí se cargarían herramientas de marketing
    },
    
    removeMarketing() {
      console.log('📢 Desactivando herramientas de marketing...');
      // Aquí se eliminarían las cookies de marketing
    },
    
    loadPreferences() {
      console.log('⚙️ Cargando configuraciones de preferencias...');
      // Aquí se cargarían configuraciones de preferencias
    },
    
    removePreferences() {
      console.log('⚙️ Desactivando configuraciones de preferencias...');
      // Aquí se eliminarían las cookies de preferencias
    },
    
    acceptAll() {
      consentManager.acceptAll();
      this.consentSettings = {
        necessary: true,
        analytics: true,
        marketing: true,
        preferences: true
      };
      this.applyConsentSettings();
      this.hideBanner();
      this.notificationMessage = 'Se han aceptado todas las cookies';
      this.showNotification = true;
      setTimeout(() => { this.showNotification = false; }, 3000);
    },
    
    rejectAll() {
      consentManager.rejectAll();
      this.consentSettings = {
        necessary: true,
        analytics: false,
        marketing: false,
        preferences: false
      };
      this.applyConsentSettings();
      this.hideBanner();
      this.notificationMessage = 'Se han rechazado las cookies opcionales';
      this.showNotification = true;
      setTimeout(() => { this.showNotification = false; }, 3000);
    },
    
    acceptOnlyNecessary() {
      consentManager.acceptOnlyNecessary();
      this.consentSettings = {
        necessary: true,
        analytics: false,
        marketing: false,
        preferences: false
      };
      this.applyConsentSettings();
      this.hideBanner();
      this.notificationMessage = 'Solo se han aceptado las cookies necesarias';
      this.showNotification = true;
      setTimeout(() => { this.showNotification = false; }, 3000);
    },
    
    saveCustomSettings() {
      this.saveConsent('explicit');
      this.hideBanner();
      this.notificationMessage = 'Configuración personalizada guardada';
    },
    
    hideBanner() {
      this.showBanner = false;
      this.showButton = true;
      this.showDetails = false;
    },
    
    // Función global para verificar el estado (para debugging)
    verifyConsentSystem() {
      return consentManager.debug();
    }
  }
}
</script>

<style scoped>
/* Los estilos ya están incluidos en las clases de Tailwind */
</style> 