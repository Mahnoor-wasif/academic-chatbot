import pytest
from unittest.mock import patch
from app import app, build_prompt, generate_answer_from_context

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

def test_build_prompt_includes_context_and_question():
    """Prompt builder should substitute the user question and policy context."""
    prompt = build_prompt(
        user_question="What is the attendance policy?",
        retrieved_context="Attendance requires 75% presence.",
        policy_title="Attendance Policy"
    )
    assert "What is the attendance policy?" in prompt
    assert "Attendance requires 75% presence." in prompt
    assert "Attendance Policy" in prompt


def test_generate_answer_from_context_returns_structured_output():
    """Generated responses should follow the required format."""
    result = generate_answer_from_context(
        user_question="What is the attendance policy?",
        retrieved_context="Attendance requires 75% presence.",
        policy_title="Attendance Policy"
    )
    assert result["answer"].startswith("Answer:")
    assert result["source"] == "Attendance Policy"
    assert result["confidence"] in {"High", "Medium", "Low"}

@patch('app.INDEX', None)
def test_system_not_ready(client):
    """Check if the system reports when the index is not loaded"""
    response = client.post('/chat', json={"message": "Hi"})
    data = response.get_json()
    assert "System is not ready" in data['answer']