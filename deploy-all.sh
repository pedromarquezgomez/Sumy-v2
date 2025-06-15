#!/bin/bash

# ==============================================================================
# SCRIPT DE DESPLIEGUE COMPLETO - SUMY V2
# Este script despliega tanto el backend (Google Cloud Run) como el frontend (Firebase)
# ==============================================================================

set -e

echo "🚀 INICIANDO DESPLIEGUE COMPLETO DE SUMY V2"
echo "=============================================="

# Verificar que los scripts existen
if [ ! -f "deploy.sh" ]; then
  echo "❌ ERROR: No se encuentra deploy.sh para el backend"
  exit 1
fi

if [ ! -f "deploy-ui.sh" ]; then
  echo "❌ ERROR: No se encuentra deploy-ui.sh para el frontend"
  exit 1
fi

echo "📋 PLAN DE DESPLIEGUE:"
echo "1. Backend (Google Cloud Run)"
echo "   - agentic-rag-service-v2"
echo "   - sumiller-service-v2"
echo "2. Frontend (Firebase Hosting)"
echo "   - UI en https://maitre-ia.web.app"
echo ""

read -p "¿Continuar con el despliegue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "❌ Despliegue cancelado"
  exit 1
fi

echo ""
echo "🔧 PASO 1: Desplegando Backend en Google Cloud Run..."
echo "=================================================="
./deploy.sh

echo ""
echo "🎨 PASO 2: Desplegando Frontend en Firebase Hosting..."
echo "===================================================="
./deploy-ui.sh

echo ""
echo "🎉 ¡DESPLIEGUE COMPLETO EXITOSO!"
echo "================================"
echo "📍 Backend URLs:"
echo "   - RAG Service: https://agentic-rag-service-v2-1080926141475.europe-west1.run.app"
echo "   - Sumiller Service: https://sumiller-service-v2-1080926141475.europe-west1.run.app"
echo ""
echo "📍 Frontend URL:"
echo "   - Aplicación Web: https://maitre-ia.web.app"
echo ""
echo "✅ El sistema completo está desplegado y funcionando!" 