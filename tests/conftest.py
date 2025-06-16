"""
Configuración global para tests
Configuración de mocks y environment para evitar conexiones reales a servicios
"""
import os
import pytest
from unittest.mock import patch, Mock

# Mock de credenciales de Google Cloud antes de cualquier importación
# Usar variables de entorno que deshabiliten la autenticación real
os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)  # Eliminar si existe
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project-123"
os.environ["GCLOUD_PROJECT"] = "test-project-123"

# Mock global de vertexai.init para evitar inicialización real
@pytest.fixture(autouse=True)
def mock_vertexai_init():
    with patch('vertexai.init') as mock:
        mock.return_value = None
        yield mock

# Mock global de GenerativeModel para evitar conexiones reales
@pytest.fixture(autouse=True)
def mock_generative_model():
    with patch('vertexai.generative_models.GenerativeModel') as mock:
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.text = "Mock response from AI"
        mock_instance.generate_content.return_value = mock_response
        mock.return_value = mock_instance
        yield mock

# Mock de Firestore para evitar conexiones reales
@pytest.fixture(autouse=True)
def mock_firestore():
    with patch('firebase_admin.firestore.client') as mock:
        mock.return_value = Mock()
        yield mock

# Mock de ChromaDB para evitar conexiones reales
@pytest.fixture(autouse=True)
def mock_chromadb():
    with patch('chromadb.Client') as mock:
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]],
            'ids': [[]]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock.return_value = mock_client
        yield mock

# Mock de sentence-transformers para evitar descargas
@pytest.fixture(autouse=True)
def mock_sentence_transformer():
    with patch('sentence_transformers.SentenceTransformer') as mock:
        mock_instance = Mock()
        mock_instance.encode.return_value = [[0.1, 0.2, 0.3, 0.4]]
        mock.return_value = mock_instance
        yield mock 