import pytest
from unittest.mock import patch
from app import app

@pytest.fixture
def client():
    """Flask test client setup"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Check if the home page (index.html) loads correctly"""
    response = client.get('/')
    assert response.status_code == 200

def test_chat_empty_message(client):
    """Check if the system handles empty messages properly"""
    response = client.post('/chat', json={"message": ""})
    data = response.get_json()
    assert response.status_code == 200
    assert "Please enter a question" in data['answer']

@patch('app.INDEX', None)
def test_system_not_ready(client):
    """Check if the system reports when the index is not loaded"""
    response = client.post('/chat', json={"message": "Hi"})
    data = response.get_json()
    assert "System is not ready" in data['answer']