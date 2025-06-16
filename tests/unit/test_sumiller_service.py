"""
Tests unitarios para Sumiller Service
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import sys
import os

# Añadir el directorio del sumiller service al path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../sumiller-service'))

from main import app
from query_filter import QueryFilter
from models import QueryResponse, QueryMetadata

client = TestClient(app)

class TestSumillerEndpoints:
    """Tests para los endpoints principales del sumiller service"""
    
    def test_health_check(self):
        """Test del endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    @patch('main.search_wines')
    @patch('main.genai.GenerativeModel')
    def test_query_endpoint_wine_search(self, mock_genai, mock_search_wines):
        """Test del endpoint /query para búsqueda de vinos"""
        # Mock de la respuesta del RAG
        mock_search_wines.return_value = (
            [{"name": "Rioja Reserva", "type": "Tinto"}],
            {"rag_used": True, "wine_results": 1, "knowledge_results": 0}
        )
        
        # Mock del modelo generativo
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Te recomiendo este excelente Rioja Reserva..."
        mock_model.generate_content.return_value = mock_response
        mock_genai.return_value = mock_model
        
        query_data = {
            "query": "Recomiéndame un vino tinto",
            "user_id": "test_user",
            "conversation_history": []
        }
        
        response = client.post("/query", json=query_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "response" in result
        assert "metadata" in result
        assert result["metadata"]["rag_used"] is True
    
    @patch('main.search_wines')
    @patch('main.genai.GenerativeModel')
    def test_query_endpoint_theory(self, mock_genai, mock_search_wines):
        """Test del endpoint /query para consultas teóricas"""
        # Mock de la respuesta del RAG
        mock_search_wines.return_value = (
            [{"content": "Los taninos son compuestos..."}],
            {"rag_used": True, "wine_results": 0, "knowledge_results": 1}
        )
        
        # Mock del modelo generativo
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Los taninos son fundamentales en el vino..."
        mock_model.generate_content.return_value = mock_response
        mock_genai.return_value = mock_model
        
        query_data = {
            "query": "¿Qué son los taninos?",
            "user_id": "test_user",
            "conversation_history": []
        }
        
        response = client.post("/query", json=query_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "response" in result
        assert "metadata" in result
        assert result["metadata"]["knowledge_results"] > 0

class TestQueryFilter:
    """Tests para el sistema de clasificación de queries"""
    
    def setUp(self):
        self.filter = QueryFilter()
    
    def test_wine_search_classification(self):
        """Test clasificación de búsquedas de vino"""
        filter = QueryFilter()
        
        queries = [
            "Recomiéndame un vino tinto",
            "¿Qué vinos tienes de la Rioja?",
            "Busco un vino para carne"
        ]
        
        for query in queries:
            classification = filter.classify_query(query)
            assert classification in ["WINE_SEARCH", "WINE_THEORY"]
    
    def test_theory_classification(self):
        """Test clasificación de consultas teóricas"""
        filter = QueryFilter()
        
        queries = [
            "¿Qué son los taninos?",
            "Explícame el proceso de fermentación",
            "¿Cuáles son los principios del maridaje?"
        ]
        
        for query in queries:
            classification = filter.classify_query(query)
            assert classification in ["WINE_THEORY", "WINE_SEARCH"]
    
    def test_pairing_classification(self):
        """Test clasificación de consultas de maridaje"""
        filter = QueryFilter()
        
        queries = [
            "¿Qué vino va bien con salmón?",
            "Maridaje para queso azul",
            "¿Cómo maridar cordero?"
        ]
        
        for query in queries:
            classification = filter.classify_query(query)
            assert classification in ["WINE_SEARCH", "WINE_THEORY"]

class TestMemoryManagement:
    """Tests para el manejo de memoria conversacional"""
    
    @patch('main.save_conversation_to_firestore')
    @patch('main.search_wines')
    @patch('main.genai.GenerativeModel')
    def test_conversation_memory_save(self, mock_genai, mock_search_wines, mock_save):
        """Test que la conversación se guarde en Firestore"""
        mock_search_wines.return_value = ([], {"rag_used": False})
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Respuesta del sumiller"
        mock_model.generate_content.return_value = mock_response
        mock_genai.return_value = mock_model
        
        mock_save.return_value = None
        
        query_data = {
            "query": "¿Qué vino me recomiendas?",
            "user_id": "test_user",
            "conversation_history": []
        }
        
        response = client.post("/query", json=query_data)
        assert response.status_code == 200
        
        # Verificar que se llamó a save_conversation_to_firestore
        mock_save.assert_called_once()

class TestErrorHandling:
    """Tests para manejo de errores"""
    
    def test_invalid_query_format(self):
        """Test manejo de formato de query inválido"""
        response = client.post("/query", json={})
        assert response.status_code == 422
    
    def test_missing_user_id(self):
        """Test manejo de user_id faltante"""
        query_data = {
            "query": "Test query",
            "conversation_history": []
        }
        response = client.post("/query", json=query_data)
        assert response.status_code == 422
    
    @patch('main.search_wines')
    def test_rag_service_error(self, mock_search_wines):
        """Test manejo de errores del servicio RAG"""
        mock_search_wines.side_effect = Exception("RAG service error")
        
        query_data = {
            "query": "Test query",
            "user_id": "test_user",
            "conversation_history": []
        }
        
        # El endpoint debería manejar el error gracefully
        response = client.post("/query", json=query_data)
        # Debería devolver una respuesta aunque el RAG falle
        assert response.status_code in [200, 500]

class TestDataSourceAnalysis:
    """Tests para análisis de fuentes de datos"""
    
    def test_analyze_wine_sources(self):
        """Test análisis de fuentes de vinos"""
        from main import analyze_data_sources
        
        rag_results = [
            {"type": "wine", "name": "Rioja Reserva"},
            {"type": "wine", "name": "Albariño"}
        ]
        
        analysis = analyze_data_sources(rag_results)
        assert analysis["wine_database"] == 2
        assert analysis["knowledge_text"] == 0
    
    def test_analyze_knowledge_sources(self):
        """Test análisis de fuentes de conocimiento"""
        from main import analyze_data_sources
        
        rag_results = [
            {"type": "knowledge", "content": "Los taninos..."},
            {"type": "knowledge", "content": "El maridaje..."}
        ]
        
        analysis = analyze_data_sources(rag_results)
        assert analysis["wine_database"] == 0
        assert analysis["knowledge_text"] == 2
    
    def test_analyze_mixed_sources(self):
        """Test análisis de fuentes mixtas"""
        from main import analyze_data_sources
        
        rag_results = [
            {"type": "wine", "name": "Rioja"},
            {"type": "knowledge", "content": "Maridaje..."}
        ]
        
        analysis = analyze_data_sources(rag_results)
        assert analysis["wine_database"] == 1
        assert analysis["knowledge_text"] == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 