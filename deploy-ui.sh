#!/bin/bash

# ==============================================================================
# SCRIPT DE DESPLIEGUE DE UI PARA FIREBASE HOSTING
# Proyecto: maitre-ia
# Este script automatiza el build y despliegue de la interfaz de usuario
# ==============================================================================

set -e

echo "🚀 Iniciando despliegue de UI en Firebase Hosting..."

# Verificar que estamos en el directorio correcto
if [ ! -d "ui" ]; then
  echo "❌ ERROR: No se encuentra el directorio 'ui'. Ejecuta este script desde la raíz del proyecto."
  exit 1
fi

# Verificar que Firebase CLI está instalado
if ! command -v firebase &> /dev/null; then
  echo "❌ ERROR: Firebase CLI no está instalado. Instálalo con: npm install -g firebase-tools"
  exit 1
fi

# Cambiar al directorio UI
cd ui

echo "📦 Instalando dependencias..."
npm install

echo "🔨 Construyendo aplicación para producción..."
npm run build

echo "🚀 Desplegando en Firebase Hosting..."
firebase deploy --only hosting

echo "✅ ¡Despliegue completado!"
echo "🌐 URL de la aplicación: https://maitre-ia.web.app"

# Volver al directorio raíz
cd ..

echo "🎉 ¡Todo listo! La aplicación está disponible en línea." 