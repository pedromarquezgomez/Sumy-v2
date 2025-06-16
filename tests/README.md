# 🧪 Tests Suite - Sumy v2

Esta carpeta contiene todos los tests necesarios para validar el funcionamiento completo de la aplicación Sumy v2.

## 📁 Estructura de Tests

```
tests/
├── unit/           # Tests unitarios para componentes individuales
├── integration/    # Tests de integración entre servicios
├── e2e/           # Tests end-to-end de flujos completos
├── performance/   # Tests de rendimiento y carga
└── README.md      # Esta documentación
```

## 🚀 Ejecutar Tests

### Tests Unitarios
```bash
# Frontend (Vue.js)
cd ui && npm test

# Sumiller Service
cd sumiller-service && python -m pytest tests/unit/

# RAG Service
cd agentic_rag-service && python -m pytest tests/unit/
```

### Tests de Integración
```bash
# Tests de integración completos
python -m pytest tests/integration/ -v
```

### Tests End-to-End
```bash
# Tests E2E con Playwright
cd tests/e2e && npm test
```

### Tests de Performance
```bash
# Tests de carga
cd tests/performance && python load_test.py
```

## 📊 Coverage

Los tests están configurados para generar reportes de cobertura:

```bash
# Coverage frontend
cd ui && npm run test:coverage

# Coverage backend
python -m pytest --cov=sumiller-service --cov=agentic_rag-service --cov-report=html
```

## 🔧 Configuración

Antes de ejecutar los tests:

1. **Variables de entorno**: Copia `.env.test` y configura las variables necesarias
2. **Dependencias**: Instala las dependencias de testing
3. **Servicios**: Asegúrate de que los servicios estén ejecutándose localmente

## 📝 Tipos de Tests Incluidos

- ✅ **Autenticación Firebase**
- ✅ **API Endpoints Sumiller**
- ✅ **RAG Service Functionality**
- ✅ **UI Components**
- ✅ **Integration Flows**
- ✅ **Performance Benchmarks**
- ✅ **Error Handling**
- ✅ **Security Validation** 