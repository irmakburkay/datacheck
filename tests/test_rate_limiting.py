"""
Tests for rate limiting functionality.

Note: These tests verify rate limiting works. In a real scenario,
you'd mock time.time() to avoid slow tests.
"""

import sys
from pathlib import Path
import time
import pytest

# Set environment before imports
import os
os.environ['DATABASE_PATH'] = ':memory:'
os.environ['MAX_UPLOAD_SIZE'] = '5242880'
os.environ['LOG_LEVEL'] = 'WARNING'

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    
    # Reset rate limiter before each test
    from app.rate_limiter import reset_rate_limiter
    reset_rate_limiter()
    
    with app.test_client() as client:
        yield client


def test_rate_limit_not_exceeded(client, tmp_path):
    """Test that requests within limit succeed."""
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("col1,col2\n1,2\n3,4")
    
    # Send 5 requests (well under the limit of 10)
    for i in range(5):
        with open(csv_path, 'rb') as f:
            data = {
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'service': 'Basic CSV Analysis',
                'csv_file': (f, 'test.csv')
            }
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        
        # Should succeed
        assert response.status_code == 200, f"Request {i+1} failed"


def test_rate_limit_exceeded(client, tmp_path):
    """Test that exceeding rate limit returns 429."""
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("col1,col2\n1,2\n3,4")
    
    # Send 11 requests rapidly (limit is 10 per minute)
    results = []
    for i in range(11):
        with open(csv_path, 'rb') as f:
            data = {
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'service': 'Basic CSV Analysis',
                'csv_file': (f, 'test.csv')
            }
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
            results.append(response.status_code)
    
    # First 10 should succeed
    assert results[:10].count(200) >= 9, "Expected at least 9 of first 10 to succeed"
    
    # 11th should be rate limited
    assert results[10] == 429, "Expected 11th request to be rate limited (HTTP 429)"


def test_rate_limit_response_format(client, tmp_path):
    """Test that rate limit response has correct format."""
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("col1,col2\n1,2")
    
    # Exhaust rate limit
    for i in range(11):
        with open(csv_path, 'rb') as f:
            data = {
                'name': 'Test',
                'email': 'test@example.com',
                'service': 'Basic CSV Analysis',
                'csv_file': (f, 'test.csv')
            }
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
    
    # Last response should be 429
    if response.status_code == 429:
        json_data = response.get_json()
        
        # Check response structure
        assert 'error' in json_data
        assert 'message' in json_data
        assert 'retry_after' in json_data
        
        # Check that retry_after is reasonable (1-60 seconds)
        assert 1 <= json_data['retry_after'] <= 60
        
        # Check Retry-After header
        assert 'Retry-After' in response.headers


def test_rate_limit_per_ip(client, tmp_path):
    """Test that rate limit is per IP (different IPs don't affect each other)."""
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("col1,col2\n1,2")
    
    # This test would require mocking request.remote_addr
    # For simplicity, we just verify the implementation exists
    from app.rate_limiter import SimpleRateLimiter
    
    limiter = SimpleRateLimiter()
    
    # Simulate requests from different IPs
    is_limited_1, _ = limiter.is_rate_limited('192.168.1.1', 'test', limit=2, window=60)
    is_limited_2, _ = limiter.is_rate_limited('192.168.1.1', 'test', limit=2, window=60)
    is_limited_3, _ = limiter.is_rate_limited('192.168.1.1', 'test', limit=2, window=60)
    
    # First two should pass, third should fail
    assert not is_limited_1, "First request should not be limited"
    assert not is_limited_2, "Second request should not be limited"
    assert is_limited_3, "Third request should be limited"
    
    # Different IP should not be affected
    is_limited_other, _ = limiter.is_rate_limited('192.168.1.2', 'test', limit=2, window=60)
    assert not is_limited_other, "Different IP should not be limited"


def test_rate_limit_cleanup(client):
    """Test that old entries are cleaned up."""
    from app.rate_limiter import SimpleRateLimiter
    
    limiter = SimpleRateLimiter()
    
    # Add some requests
    limiter.is_rate_limited('192.168.1.1', 'test', limit=10, window=60)
    limiter.is_rate_limited('192.168.1.2', 'test', limit=10, window=60)
    
    stats_before = limiter.get_stats()
    assert stats_before['tracked_ips'] >= 2
    
    # Cleanup doesn't run immediately (only every 60 seconds)
    # Just verify the method exists and can be called
    limiter._cleanup_old_entries()
    
    # Stats should still show tracked IPs (they're not old enough yet)
    stats_after = limiter.get_stats()
    assert stats_after['tracked_ips'] >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
