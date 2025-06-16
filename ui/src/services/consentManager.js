/**
 * Sistema simplificado de gestión de consentimiento para Vue.js
 * Basado en el sistema modular original
 */

// Categorías de cookies disponibles
export const CookieCategory = {
  NECESSARY: 'necessary',
  ANALYTICS: 'analytics',
  MARKETING: 'marketing',
  PREFERENCES: 'preferences'
}

// Configuración por defecto
const DEFAULT_CONSENT_SETTINGS = {
  [CookieCategory.NECESSARY]: true,
  [CookieCategory.ANALYTICS]: false,
  [CookieCategory.MARKETING]: false,
  [CookieCategory.PREFERENCES]: false
}

class ConsentManager {
  constructor() {
    this.storageKey = 'cookie-consent'
    this.version = '1.0'
    this.eventListeners = new Map()
  }

  /**
   * Obtiene el registro de consentimiento actual
   */
  getConsentRecord() {
    try {
      const stored = localStorage.getItem(this.storageKey)
      return stored ? JSON.parse(stored) : null
    } catch (error) {
      console.error('Error al leer el consentimiento:', error)
      return null
    }
  }

  /**
   * Guarda el consentimiento
   */
  saveConsent(settings, method = 'explicit') {
    const consentRecord = {
      timestamp: Date.now(),
      version: this.version,
      settings: { ...DEFAULT_CONSENT_SETTINGS, ...settings },
      lastUpdated: new Date().toISOString(),
      method: method
    }

    try {
      localStorage.setItem(this.storageKey, JSON.stringify(consentRecord))
      this.notifyListeners('save', consentRecord)
      return consentRecord
    } catch (error) {
      console.error('Error al guardar el consentimiento:', error)
      return null
    }
  }

  /**
   * Verifica si el usuario ha dado consentimiento para una categoría específica
   */
  hasConsent(category) {
    const record = this.getConsentRecord()
    if (!record) return false
    return record.settings[category] === true
  }

  /**
   * Verifica si existe algún consentimiento guardado
   */
  hasAnyConsent() {
    return this.getConsentRecord() !== null
  }

  /**
   * Acepta todas las cookies
   */
  acceptAll() {
    const settings = {
      [CookieCategory.NECESSARY]: true,
      [CookieCategory.ANALYTICS]: true,
      [CookieCategory.MARKETING]: true,
      [CookieCategory.PREFERENCES]: true
    }
    return this.saveConsent(settings, 'explicit')
  }

  /**
   * Rechaza todas las cookies opcionales
   */
  rejectAll() {
    const settings = {
      [CookieCategory.NECESSARY]: true,
      [CookieCategory.ANALYTICS]: false,
      [CookieCategory.MARKETING]: false,
      [CookieCategory.PREFERENCES]: false
    }
    return this.saveConsent(settings, 'explicit')
  }

  /**
   * Acepta solo las cookies necesarias
   */
  acceptOnlyNecessary() {
    return this.rejectAll() // Son lo mismo
  }

  /**
   * Resetea todo el consentimiento
   */
  resetConsent() {
    try {
      localStorage.removeItem(this.storageKey)
      this.notifyListeners('reset', null)
      return true
    } catch (error) {
      console.error('Error al resetear el consentimiento:', error)
      return false
    }
  }

  /**
   * Actualiza el consentimiento para una categoría específica
   */
  updateConsent(category, granted) {
    const currentRecord = this.getConsentRecord()
    const currentSettings = currentRecord ? currentRecord.settings : DEFAULT_CONSENT_SETTINGS
    
    const newSettings = {
      ...currentSettings,
      [category]: granted
    }
    
    return this.saveConsent(newSettings, 'explicit')
  }

  /**
   * Añade un listener para eventos de consentimiento
   */
  addEventListener(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set())
    }
    this.eventListeners.get(event).add(callback)
  }

  /**
   * Remueve un listener de eventos
   */
  removeEventListener(event, callback) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).delete(callback)
    }
  }

  /**
   * Notifica a todos los listeners de un evento
   */
  notifyListeners(event, data) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('Error en listener de consentimiento:', error)
        }
      })
    }
  }

  /**
   * Función de depuración para mostrar el estado del sistema
   */
  debug() {
    const consentRecord = this.getConsentRecord()
    
    const debug = {
      consent: consentRecord,
      hasConsent: {
        necessary: this.hasConsent(CookieCategory.NECESSARY),
        analytics: this.hasConsent(CookieCategory.ANALYTICS),
        marketing: this.hasConsent(CookieCategory.MARKETING),
        preferences: this.hasConsent(CookieCategory.PREFERENCES)
      },
      cookies: document.cookie.split(';').map(c => c.trim().split('=')[0]).filter(Boolean),
      localStorage: {
        available: typeof Storage !== 'undefined',
        used: this.getStorageUsage()
      }
    }

    console.group('🍪 Sistema de Consentimiento - Debug')
    console.table({
      'Consentimiento Necesario': debug.hasConsent.necessary,
      'Consentimiento Analíticas': debug.hasConsent.analytics,
      'Consentimiento Marketing': debug.hasConsent.marketing,
      'Consentimiento Preferencias': debug.hasConsent.preferences,
      'Método de consentimiento': consentRecord?.method ?? 'ninguno',
      'Última actualización': consentRecord?.lastUpdated ?? 'nunca',
    })
    console.log('Estado detallado:', debug)
    console.groupEnd()

    return debug
  }

  /**
   * Obtiene información sobre el uso del localStorage
   */
  getStorageUsage() {
    try {
      const data = localStorage.getItem(this.storageKey)
      return {
        size: data ? new Blob([data]).size : 0,
        sizeFormatted: data ? this.formatBytes(new Blob([data]).size) : '0 B'
      }
    } catch (error) {
      return { size: 0, sizeFormatted: '0 B' }
    }
  }

  /**
   * Formatea bytes en unidades legibles
   */
  formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 B'
    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
  }
}

// Instancia singleton
export const consentManager = new ConsentManager()

// Exponer funciones globales para depuración
if (typeof window !== 'undefined') {
  window.verifyConsentSystem = () => consentManager.debug()
  window.resetConsentSystem = () => consentManager.resetConsent()
}

export default consentManager 