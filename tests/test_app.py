"""
Pytest tests for Flask URL Shortener.
"""
import os
import sys
import importlib
import pytest
from pathlib import Path


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Create a test Flask app with temporary database."""
    # Set environment variable to use temporary database BEFORE importing
    test_db_path = str(tmp_path / 'test_shorty.db')
    monkeypatch.setenv('DB_PATH', test_db_path)
    monkeypatch.setenv('BASE_URL', 'http://localhost:8000')
    
    # Remove app from cache if it exists, then import fresh
    if 'app' in sys.modules:
        del sys.modules['app']
    
    # Import app (will use the new DB_PATH from env)
    from app import app as test_app
    
    # Set test config
    test_app.config['TESTING'] = True
    
    yield test_app
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


def test_health_ok(client):
    """Test /health returns 200 and body 'ok'."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'ok'


def test_shorten_and_redirect_and_stats(client):
    """Test full flow: shorten, redirect, and stats."""
    # POST a valid URL
    response = client.post(
        '/api/shorten',
        json={'url': 'https://example.com/very/long'},
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'code' in data
    assert 'short_url' in data
    assert len(data['code']) == 6
    code = data['code']
    
    # GET /<code> returns 302 with Location header
    response = client.get(f'/{code}', follow_redirects=False)
    assert response.status_code == 302
    assert response.location == 'https://example.com/very/long'
    
    # GET /api/stats/<code> returns clicks >= 1
    response = client.get(f'/api/stats/{code}')
    assert response.status_code == 200
    stats_data = response.get_json()
    assert stats_data['code'] == code
    assert stats_data['url'] == 'https://example.com/very/long'
    assert stats_data['clicks'] >= 1
    assert 'created_at' in stats_data
    assert stats_data['created_at'].endswith('Z')


def test_shorten_rejects_invalid_url(client):
    """Test that bad payloads or non-http(s) URLs return 400."""
    # Missing url field
    response = client.post(
        '/api/shorten',
        json={},
        content_type='application/json'
    )
    assert response.status_code == 400
    assert 'error' in response.get_json()
    
    # Invalid URL (no http/https)
    response = client.post(
        '/api/shorten',
        json={'url': 'not-a-url'},
        content_type='application/json'
    )
    assert response.status_code == 400
    assert 'error' in response.get_json()
    
    # Invalid URL (ftp)
    response = client.post(
        '/api/shorten',
        json={'url': 'ftp://example.com'},
        content_type='application/json'
    )
    assert response.status_code == 400
    assert 'error' in response.get_json()
    
    # Missing JSON body (Flask returns 415 for unsupported media type)
    response = client.post('/api/shorten')
    assert response.status_code in [400, 415]  # Flask may return 415 for missing JSON


def test_redirect_unknown_code(client):
    """Test redirect with unknown code returns 404."""
    response = client.get('/Unknown')
    assert response.status_code == 404
    assert 'error' in response.get_json()


def test_stats_unknown_code(client):
    """Test stats with unknown code returns 404."""
    response = client.get('/api/stats/Unknown')
    assert response.status_code == 404
    assert 'error' in response.get_json()


def test_shorten_http_url(client):
    """Test that http:// URLs are accepted."""
    response = client.post(
        '/api/shorten',
        json={'url': 'http://example.com/test'},
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'code' in data
    assert 'short_url' in data

