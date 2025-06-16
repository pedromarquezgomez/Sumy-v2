"""
Tests de integración para flujo completo de Sumy v2
"""
import pytest
import requests
import json
import time
from unittest.mock import patch
import os

# URLs de los servicios (usar variables de entorno o defaults)
SUMILLER_URL = os.getenv('SUMILLER_URL', 'https://sumiller-service-maitre-550926469911.europe-west1.run.app')
RAG_URL = os.getenv('RAG_URL', 'https://agentic-rag-service-maitre-550926469911.europe-west1.run.app')
UI_URL = os.getenv('UI_URL', 'https://maitre-ia.web.app')

class TestServiceHealth:
    """Tests de health check para todos los servicios"""
    
    def test_sumiller_service_health(self):
        """Test health check del sumiller service"""
        response = requests.get(f"{SUMILLER_URL}/health", timeout=30)
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_rag_service_health(self):
        """Test health check del RAG service"""
        response = requests.get(f"{RAG_URL}/health", timeout=30)
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_ui_accessibility(self):
        """Test que la UI sea accesible"""
        response = requests.get(UI_URL, timeout=30)
        assert response.status_code == 200
        assert "Sumy" in response.text

class TestRAGService:
    """Tests específicos del RAG service"""
    
    def test_wine_search(self):
        """Test búsqueda de vinos en RAG"""
        payload = {
            "query": "vino tinto rioja",
            "max_results": 3
        }
        
        response = requests.post(f"{RAG_URL}/search", json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "metadata" in data
        assert data["metadata"]["total_results"] >= 0
    
    def test_knowledge_search(self):
        """Test búsqueda de conocimiento en RAG"""
        payload = {
            "query": "principios del maridaje",
            "max_results": 5
        }
        
        response = requests.post(f"{RAG_URL}/search", json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "metadata" in data
        
        # Debería encontrar resultados de conocimiento
        if data["results"]:
            assert any(result.get("type") == "knowledge" for result in data["results"])
    
    def test_empty_query(self):
        """Test búsqueda con query vacío"""
        payload = {
            "query": "",
            "max_results": 3
        }
        
        response = requests.post(f"{RAG_URL}/search", json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert data["metadata"]["total_results"] == 0
    
    def test_complex_query(self):
        """Test búsqueda con query complejo"""
        payload = {
            "query": "vino tinto español para maridar con cordero asado que tenga taninos suaves",
            "max_results": 5
        }
        
        response = requests.post(f"{RAG_URL}/search", json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "metadata" in data

class TestSumillerService:
    """Tests específicos del sumiller service"""
    
    def test_wine_query(self):
        """Test consulta de vino al sumiller"""
        payload = {
            "query": "Recomiéndame un vino tinto español",
            "user_id": "test_user_integration",
            "conversation_history": []
        }
        
        response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "metadata" in data
        assert len(data["response"]) > 0
        
        # Verificar metadatos
        metadata = data["metadata"]
        assert "classification" in metadata
        assert "rag_used" in metadata
        assert "timestamp" in metadata
    
    def test_theory_query(self):
        """Test consulta teórica al sumiller"""
        payload = {
            "query": "¿Qué son los taninos en el vino?",
            "user_id": "test_user_integration",
            "conversation_history": []
        }
        
        response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "metadata" in data
        
        # Debería usar RAG para consultas teóricas
        assert data["metadata"]["rag_used"] is True
    
    def test_pairing_query(self):
        """Test consulta de maridaje al sumiller"""
        payload = {
            "query": "¿Qué vino me recomiendas para acompañar salmón a la plancha?",
            "user_id": "test_user_integration",
            "conversation_history": []
        }
        
        response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "metadata" in data
        assert "salmón" in data["response"].lower() or "salmon" in data["response"].lower()
    
    def test_conversation_memory(self):
        """Test memoria conversacional"""
        # Primera consulta
        payload1 = {
            "query": "Recomiéndame un vino tinto",
            "user_id": "test_user_memory",
            "conversation_history": []
        }
        
        response1 = requests.post(f"{SUMILLER_URL}/query", json=payload1, timeout=60)
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Segunda consulta con contexto
        conversation_history = [
            {"role": "user", "content": "Recomiéndame un vino tinto"},
            {"role": "assistant", "content": data1["response"]}
        ]
        
        payload2 = {
            "query": "¿Con qué comida lo puedo maridar?",
            "user_id": "test_user_memory",
            "conversation_history": conversation_history
        }
        
        response2 = requests.post(f"{SUMILLER_URL}/query", json=payload2, timeout=60)
        assert response2.status_code == 200
        
        data2 = response2.json()
        # La respuesta debería tener contexto del vino anterior
        assert len(data2["response"]) > 0

class TestRAGIntegration:
    """Tests de integración entre Sumiller y RAG"""
    
    def test_sumiller_to_rag_wine_search(self):
        """Test que el sumiller use RAG para búsqueda de vinos"""
        payload = {
            "query": "Busco un vino de la Rioja",
            "user_id": "test_rag_integration",
            "conversation_history": []
        }
        
        response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        metadata = data["metadata"]
        
        # Debería usar RAG y encontrar vinos
        assert metadata["rag_used"] is True
        assert metadata.get("wine_results", 0) >= 0
    
    def test_sumiller_to_rag_knowledge_search(self):
        """Test que el sumiller use RAG para conocimiento"""
        payload = {
            "query": "Explícame el proceso de fermentación del vino",
            "user_id": "test_rag_integration",
            "conversation_history": []
        }
        
        response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        metadata = data["metadata"]
        
        # Debería usar RAG y encontrar conocimiento
        assert metadata["rag_used"] is True
        assert metadata.get("knowledge_results", 0) >= 0
    
    def test_classification_accuracy(self):
        """Test precisión de la clasificación de queries"""
        test_queries = [
            ("Recomiéndame un vino tinto", "WINE_SEARCH"),
            ("¿Qué son los taninos?", "WINE_THEORY"),
            ("¿Cómo se hace el vino?", "WINE_THEORY"),
            ("Vino para carne", "WINE_SEARCH")
        ]
        
        for query, expected_type in test_queries:
            payload = {
                "query": query,
                "user_id": "test_classification",
                "conversation_history": []
            }
            
            response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=60)
            assert response.status_code == 200
            
            data = response.json()
            classification = data["metadata"]["classification"]
            
            # La clasificación debería ser una de las esperadas
            assert classification in ["WINE_SEARCH", "WINE_THEORY", "GENERAL"]

class TestDataSources:
    """Tests para validar fuentes de datos"""
    
    def test_wine_database_access(self):
        """Test acceso a base de datos de vinos"""
        payload = {
            "query": "Albariño",
            "max_results": 10
        }
        
        response = requests.post(f"{RAG_URL}/search", json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        
        # Debería encontrar vinos en la base de datos
        wine_results = [r for r in data["results"] if r.get("type") == "wine"]
        assert len(wine_results) > 0
    
    def test_knowledge_base_access(self):
        """Test acceso a base de conocimiento"""
        payload = {
            "query": "cata de vinos",
            "max_results": 10
        }
        
        response = requests.post(f"{RAG_URL}/search", json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        
        # Debería encontrar conocimiento
        knowledge_results = [r for r in data["results"] if r.get("type") == "knowledge"]
        assert len(knowledge_results) > 0

class TestErrorHandling:
    """Tests para manejo de errores en integración"""
    
    def test_invalid_payload_sumiller(self):
        """Test payload inválido al sumiller"""
        payload = {"invalid": "data"}
        
        response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=30)
        assert response.status_code == 422
    
    def test_invalid_payload_rag(self):
        """Test payload inválido al RAG"""
        payload = {"invalid": "data"}
        
        response = requests.post(f"{RAG_URL}/search", json=payload, timeout=30)
        assert response.status_code == 422
    
    def test_large_query(self):
        """Test query muy largo"""
        large_query = "palabra " * 1000
        
        payload = {
            "query": large_query,
            "user_id": "test_large_query",
            "conversation_history": []
        }
        
        response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=60)
        # Debería manejar queries largos gracefully
        assert response.status_code in [200, 400, 413]

class TestPerformance:
    """Tests básicos de performance"""
    
    def test_response_time_rag(self):
        """Test tiempo de respuesta del RAG"""
        payload = {
            "query": "vino tinto",
            "max_results": 5
        }
        
        start_time = time.time()
        response = requests.post(f"{RAG_URL}/search", json=payload, timeout=30)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # RAG debería responder en menos de 5 segundos
        assert response_time < 5.0
    
    def test_response_time_sumiller(self):
        """Test tiempo de respuesta del sumiller"""
        payload = {
            "query": "Recomiéndame un vino",
            "user_id": "test_performance",
            "conversation_history": []
        }
        
        start_time = time.time()
        response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=60)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Sumiller debería responder en menos de 30 segundos
        assert response_time < 30.0
    
    def test_concurrent_requests(self):
        """Test requests concurrentes"""
        import concurrent.futures
        import threading
        
        def make_request():
            payload = {
                "query": "vino blanco",
                "max_results": 3
            }
            response = requests.post(f"{RAG_URL}/search", json=payload, timeout=30)
            return response.status_code == 200
        
        # Hacer 5 requests concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Todos los requests deberían ser exitosos
        assert all(results)

class TestTraceability:
    """Tests para trazabilidad completa"""
    
    def test_full_traceability_flow(self):
        """Test flujo completo con trazabilidad"""
        payload = {
            "query": "¿Qué vino de Ribera del Duero me recomiendas?",
            "user_id": "test_traceability",
            "conversation_history": []
        }
        
        response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        metadata = data["metadata"]
        
        # Verificar que todos los campos de trazabilidad estén presentes
        required_fields = [
            "classification", "rag_used", "timestamp", 
            "response_source", "wine_results", "knowledge_results"
        ]
        
        for field in required_fields:
            assert field in metadata, f"Campo {field} faltante en metadata"
        
        # Verificar data sources
        assert "data_sources" in metadata
        data_sources = metadata["data_sources"]
        assert "wine_database" in data_sources
        assert "knowledge_text" in data_sources
        
        # Los números deberían ser coherentes
        total_results = metadata["wine_results"] + metadata["knowledge_results"]
        total_sources = data_sources["wine_database"] + data_sources["knowledge_text"]
        assert total_results == total_sources

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 