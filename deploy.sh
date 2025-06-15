#!/bin/bash

# ==============================================================================
# SCRIPT DE DESPLIEGUE SEGURO PARA GOOGLE CLOUD RUN
# Proyecto: sumy-2
# Este script automatiza el despliegue de los servicios de backend,
# utilizando Google Secret Manager para gestionar las claves de API de forma segura.
# ==============================================================================

# Detiene la ejecución del script si algún comando falla.
set -e

# --- Configuración ---
PROJECT_ID="sumy-2"
REGION="europe-west1" # Cambiado a la región que hemos estado usando
SECRET_NAME="openai-api-key-v2" # Nombre del secreto en Secret Manager

# --- Funciones de Ayuda ---
# Función para imprimir mensajes de estado
log() {
  echo "✅ $1"
}

# Función para imprimir errores
error() {
  echo "❌ ERROR: $1" >&2
  exit 1
}

# --- Verificaciones Previas ---
log "Iniciando verificaciones previas..."

# Verificar que gcloud y docker están instalados
command -v gcloud >/dev/null 2>&1 || error "gcloud CLI no está instalado. Por favor, instálalo."
command -v docker >/dev/null 2>&1 || error "Docker no está instalado. Por favor, inícialo."

# Configurar el proyecto de gcloud por si no está seteado
gcloud config set project $PROJECT_ID

# --- Gestión de Secretos ---
log "Gestionando el secreto de la API Key de OpenAI..."

# Verificar si el secreto ya existe
if ! gcloud secrets describe $SECRET_NAME >/dev/null 2>&1; then
  log "El secreto '$SECRET_NAME' no existe. Creándolo ahora..."
  
  # Pedir la clave de forma segura sin que se vea en la terminal
  read -sp "Por favor, introduce tu OPENAI_API_KEY y presiona Enter: " API_KEY
  echo
  
  if [ -z "$API_KEY" ]; then
    error "La API Key no puede estar vacía."
  fi
  
  # Crear el secreto y añadir la clave
  gcloud secrets create $SECRET_NAME --replication-policy="automatic"
  printf "%s" "$API_KEY" | gcloud secrets versions add $SECRET_NAME --data-file=-
  log "Secreto '$SECRET_NAME' creado y configurado."
else
  log "El secreto '$SECRET_NAME' ya existe. Usando la versión existente."
fi


# --- Despliegue del Servicio RAG ---
log "Iniciando despliegue de 'agentic-rag-service-v2'..."

# 1. Construir y subir la imagen Docker.
# El flag --source construye y sube la imagen en un solo paso optimizado.
gcloud builds submit ./agentic-rag-service --tag gcr.io/$PROJECT_ID/agentic-rag-service-v2

# 2. Desplegar el servicio en Cloud Run.
log "Desplegando 'agentic-rag-service-v2' en Cloud Run..."
gcloud run deploy agentic-rag-service-v2 \
  --image gcr.io/$PROJECT_ID/agentic-rag-service-v2 \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --project=$PROJECT_ID

RAG_SERVICE_URL=$(gcloud run services describe agentic-rag-service-v2 --region=$REGION --format="value(status.url)")
log "'agentic-rag-service-v2' desplegado en: $RAG_SERVICE_URL"


# --- Despliegue del Servicio Sumiller ---
log "Iniciando despliegue de 'sumiller-service-v2'..."

# 3. Construir y subir la imagen Docker.
gcloud builds submit ./sumiller-service --tag gcr.io/$PROJECT_ID/sumiller-service-v2

# 4. Desplegar el servicio, inyectando el secreto y la URL del servicio RAG.
log "Desplegando 'sumiller-service-v2' en Cloud Run..."
gcloud run deploy sumiller-service-v2 \
  --image gcr.io/$PROJECT_ID/sumiller-service-v2 \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --project=$PROJECT_ID \
  --set-env-vars="SEARCH_SERVICE_URL=$RAG_SERVICE_URL" \
  --set-secrets="OPENAI_API_KEY=$SECRET_NAME:latest" # <-- Forma segura de usar la clave

SUMILLER_SERVICE_URL=$(gcloud run services describe sumiller-service-v2 --region=$REGION --format="value(status.url)")
log "'sumiller-service-v2' desplegado en: $SUMILLER_SERVICE_URL"


# --- Resumen Final ---
echo
log "🎉 ¡DESPLIEGUE COMPLETADO!"
echo "-----------------------------------------------------"
echo "  RAG Service URL: $RAG_SERVICE_URL"
echo "  Sumiller Service URL: $SUMILLER_SERVICE_URL"
echo "-----------------------------------------------------"
echo "Ahora puedes desplegar tu UI apuntando a la URL del Sumiller Service."

