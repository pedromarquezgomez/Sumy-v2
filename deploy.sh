#!/bin/bash

# ==============================================================================
# SCRIPT DE DESPLIEGUE CON VERTEX AI
# Proyecto: sumy-2
# Versión simplificada: no necesita secretos de OpenAI ni VPC Connector.
# ==============================================================================

set -e

# --- Configuración ---
PROJECT_ID="sumy-2"
REGION="europe-west1"

# --- Funciones de Ayuda ---
log() { echo "✅ $1"; }
error() { echo "❌ ERROR: $1" >&2; exit 1; }

# --- Verificaciones Previas ---
log "Iniciando verificaciones previas..."
command -v gcloud >/dev/null 2>&1 || error "gcloud CLI no está instalado."
gcloud config set project $PROJECT_ID
log "Proyecto gcloud configurado a '$PROJECT_ID'."

# --- Habilitar APIs necesarias ---
log "Habilitando las APIs de Cloud Build, Cloud Run y Vertex AI..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com aiplatform.googleapis.com --project=$PROJECT_ID

# --- Despliegue del Servicio RAG (sin cambios) ---
log "Iniciando despliegue de 'agentic-rag-service-v2'..."
gcloud builds submit ./agentic_rag-service --tag gcr.io/$PROJECT_ID/agentic-rag-service-v2
gcloud run deploy agentic-rag-service-v2 \
  --image gcr.io/$PROJECT_ID/agentic-rag-service-v2 \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --project=$PROJECT_ID
RAG_SERVICE_URL=$(gcloud run services describe agentic-rag-service-v2 --region=$REGION --format="value(status.url)")
log "'agentic-rag-service-v2' desplegado en: $RAG_SERVICE_URL"

# --- Despliegue del Servicio Sumiller (con Vertex AI) ---
log "Iniciando despliegue de 'sumiller-service-v2' con Vertex AI..."
gcloud builds submit ./sumiller-service --tag gcr.io/$PROJECT_ID/sumiller-service-v2

# Despliegue simplificado: sin secretos ni conector de red
gcloud run deploy sumiller-service-v2 \
  --image gcr.io/$PROJECT_ID/sumiller-service-v2 \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --project=$PROJECT_ID \
  --set-env-vars="SEARCH_SERVICE_URL=$RAG_SERVICE_URL,GCP_PROJECT=$PROJECT_ID,GCP_REGION=$REGION"

SUMILLER_SERVICE_URL=$(gcloud run services describe sumiller-service-v2 --region=$REGION --format="value(status.url)")
log "'sumiller-service-v2' desplegado en: $SUMILLER_SERVICE_URL"

# --- Resumen Final ---
echo
log "🎉 ¡DESPLIEGUE COMPLETADO CON VERTEX AI!"
echo "-----------------------------------------------------"
echo "  RAG Service URL: $RAG_SERVICE_URL"
echo "  Sumiller Service URL: $SUMILLER_SERVICE_URL"
echo "-----------------------------------------------------"
echo "La configuración de red y secretos ha sido simplificada."
