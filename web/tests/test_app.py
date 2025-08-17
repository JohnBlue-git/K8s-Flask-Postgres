import pytest
from unittest.mock import patch
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('psycopg2.connect')
def test_hello_success(mock_connect, client):
    # Mock successful database connection
    mock_connect.return_value = None
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "✅ Connected to PostgreSQL!"

@patch('psycopg2.connect')
def test_hello_db_failure(mock_connect, client):
    # Mock database connection failure
    mock_connect.side_effect = Exception("Connection refused")
    response = client.get('/')
    assert response.status_code == 200
    assert "❌ Failed to connect to DB: Connection refused" in response.data.decode('utf-8')