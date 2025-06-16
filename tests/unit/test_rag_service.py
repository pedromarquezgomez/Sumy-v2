"""
Tests unitarios para RAG Service
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Añadir el directorio del RAG service al path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../agentic_rag-service'))

from main import app

client = TestClient(app)

class TestRAGEndpoints:
    """Tests para los endpoints del RAG service"""
    
    def test_health_check(self):
        """Test del endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    @patch('main.collection')
    def test_search_endpoint_wine_query(self, mock_collection):
        """Test del endpoint /search para búsqueda de vinos"""
        # Mock de la respuesta de ChromaDB
        mock_result = {
            'documents': [['Rioja Reserva 2018 - Vino tinto...']],
            'metadatas': [[{'type': 'wine', 'name': 'Rioja Reserva', 'region': 'La Rioja'}]],
            'distances': [[0.2]]
        }
        mock_collection.query.return_value = mock_result
        
        search_data = {
            "query": "vino tinto rioja",
            "max_results": 3
        }
        
        response = client.post("/search", json=search_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "results" in result
        assert "metadata" in result
        assert len(result["results"]) > 0
        assert result["metadata"]["total_results"] > 0
    
    @patch('main.collection')
    def test_search_endpoint_knowledge_query(self, mock_collection):
        """Test del endpoint /search para consultas de conocimiento"""
        # Mock de la respuesta de ChromaDB
        mock_result = {
            'documents': [['Los taninos son compuestos polifenólicos...']],
            'metadatas': [[{'type': 'knowledge', 'source': 'maestria_enologica', 'chunk_id': 15}]],
            'distances': [[0.15]]
        }
        mock_collection.query.return_value = mock_result
        
        search_data = {
            "query": "qué son los taninos",
            "max_results": 5
        }
        
        response = client.post("/search", json=search_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "results" in result
        assert "metadata" in result
        assert result["results"][0]["type"] == "knowledge"
    
    @patch('main.collection')
    def test_search_with_filters(self, mock_collection):
        """Test búsqueda con filtros específicos"""
        mock_result = {
            'documents': [['Albariño 2022 - Vino blanco...']],
            'metadatas': [[{'type': 'wine', 'wine_type': 'Blanco', 'region': 'Rías Baixas'}]],
            'distances': [[0.1]]
        }
        mock_collection.query.return_value = mock_result
        
        search_data = {
            "query": "vino blanco",
            "max_results": 3,
            "filter": {"wine_type": "Blanco"}
        }
        
        response = client.post("/search", json=search_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["results"][0]["wine_type"] == "Blanco"

class TestSearchFunctionality:
    """Tests para la funcionalidad de búsqueda"""
    
    @patch('main.collection')
    def test_search_wines_function(self, mock_collection):
        """Test de la función search_wines"""
        from main import search_wines
        
        mock_result = {
            'documents': [['Vino test']],
            'metadatas': [[{'type': 'wine'}]],
            'distances': [[0.2]]
        }
        mock_collection.query.return_value = mock_result
        
        results = search_wines("vino tinto", max_results=3)
        assert isinstance(results, list)
        assert len(results) > 0
    
    @patch('main.collection')
    def test_search_empty_query(self, mock_collection):
        """Test búsqueda con query vacío"""
        mock_collection.query.return_value = {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        response = client.post("/search", json={"query": "", "max_results": 3})
        assert response.status_code == 200
        
        result = response.json()
        assert result["metadata"]["total_results"] == 0
    
    @patch('main.collection')
    def test_search_no_results(self, mock_collection):
        """Test búsqueda sin resultados"""
        mock_collection.query.return_value = {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        response = client.post("/search", json={"query": "query imposible", "max_results": 3})
        assert response.status_code == 200
        
        result = response.json()
        assert result["metadata"]["total_results"] == 0
        assert len(result["results"]) == 0

class TestDataLoading:
    """Tests para carga de datos"""
    
    @patch('builtins.open')
    @patch('json.load')
    def test_load_wine_data(self, mock_json_load, mock_open):
        """Test carga de datos de vinos"""
        from main import load_wine_data
        
        mock_wine_data = [
            {
                "name": "Test Wine",
                "type": "Tinto",
                "region": "Test Region",
                "description": "Test description"
            }
        ]
        mock_json_load.return_value = mock_wine_data
        
        wines = load_wine_data("test_path.json")
        assert isinstance(wines, list)
        assert len(wines) > 0
        assert wines[0]["name"] == "Test Wine"
    
    @patch('builtins.open')
    def test_load_knowledge_data(self, mock_open):
        """Test carga de datos de conocimiento"""
        from main import load_knowledge_data
        
        mock_open.return_value.__enter__.return_value.read.return_value = """
        Los principios del maridaje.
        
        El maridaje es el arte de combinar vinos y comidas.
        
        Los taninos en el vino.
        """
        
        chunks = load_knowledge_data("test_path.txt")
        assert isinstance(chunks, list)
        assert len(chunks) > 0

class TestChunkingStrategy:
    """Tests para la estrategia de chunking"""
    
    def test_chunk_by_paragraphs(self):
        """Test chunking por párrafos"""
        from main import chunk_text_by_paragraphs
        
        text = """Párrafo uno sobre vinos.

Párrafo dos sobre maridajes.

Párrafo tres sobre cata."""
        
        chunks = chunk_text_by_paragraphs(text)
        assert len(chunks) == 3
        assert "vinos" in chunks[0]
        assert "maridajes" in chunks[1]
        assert "cata" in chunks[2]
    
    def test_chunk_long_paragraph(self):
        """Test chunking de párrafos largos"""
        from main import chunk_text_by_paragraphs
        
        # Crear un párrafo muy largo
        long_paragraph = "Esta es una oración muy larga. " * 50
        
        chunks = chunk_text_by_paragraphs(long_paragraph)
        # Debería dividirse en chunks más pequeños
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 800  # Límite configurado

class TestEmbeddings:
    """Tests para generación de embeddings"""
    
    @patch('main.embedding_model')
    def test_generate_embeddings(self, mock_model):
        """Test generación de embeddings"""
        from main import generate_embeddings
        
        mock_model.encode.return_value = [[0.1, 0.2, 0.3, 0.4]]
        
        texts = ["Test text"]
        embeddings = generate_embeddings(texts)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 4

class TestErrorHandling:
    """Tests para manejo de errores en RAG service"""
    
    def test_invalid_search_request(self):
        """Test manejo de request inválido"""
        response = client.post("/search", json={})
        assert response.status_code == 422
    
    def test_invalid_max_results(self):
        """Test manejo de max_results inválido"""
        response = client.post("/search", json={
            "query": "test",
            "max_results": -1
        })
        assert response.status_code == 422
    
    @patch('main.collection')
    def test_chromadb_error(self, mock_collection):
        """Test manejo de errores de ChromaDB"""
        mock_collection.query.side_effect = Exception("ChromaDB error")
        
        response = client.post("/search", json={
            "query": "test query",
            "max_results": 3
        })
        # Debería manejar el error gracefully
        assert response.status_code in [200, 500]

class TestMetadata:
    """Tests para metadatos de resultados"""
    
    @patch('main.collection')
    def test_metadata_wine_results(self, mock_collection):
        """Test metadatos para resultados de vinos"""
        mock_result = {
            'documents': [['Vino test 1'], ['Vino test 2']],
            'metadatas': [[{'type': 'wine'}], [{'type': 'wine'}]],
            'distances': [[0.1], [0.2]]
        }
        mock_collection.query.return_value = mock_result
        
        response = client.post("/search", json={
            "query": "vino",
            "max_results": 5
        })
        
        result = response.json()
        metadata = result["metadata"]
        assert metadata["wine_results"] == 2
        assert metadata["knowledge_results"] == 0
        assert metadata["total_results"] == 2
    
    @patch('main.collection')
    def test_metadata_knowledge_results(self, mock_collection):
        """Test metadatos para resultados de conocimiento"""
        mock_result = {
            'documents': [['Conocimiento test']],
            'metadatas': [[{'type': 'knowledge'}]],
            'distances': [[0.15]]
        }
        mock_collection.query.return_value = mock_result
        
        response = client.post("/search", json={
            "query": "teoría",
            "max_results": 5
        })
        
        result = response.json()
        metadata = result["metadata"]
        assert metadata["wine_results"] == 0
        assert metadata["knowledge_results"] == 1
        assert metadata["total_results"] == 1

class TestPerformance:
    """Tests básicos de performance"""
    
    @patch('main.collection')
    def test_large_query_handling(self, mock_collection):
        """Test manejo de queries grandes"""
        mock_collection.query.return_value = {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        large_query = "palabra " * 1000  # Query muy largo
        
        response = client.post("/search", json={
            "query": large_query,
            "max_results": 10
        })
        
        # Debería manejar queries largos sin fallar
        assert response.status_code == 200
    
    @patch('main.collection')
    def test_high_max_results(self, mock_collection):
        """Test con max_results alto"""
        mock_collection.query.return_value = {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        response = client.post("/search", json={
            "query": "test",
            "max_results": 100
        })
        
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 