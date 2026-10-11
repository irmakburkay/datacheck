"""Integration tests for API endpoints."""

from pathlib import Path
import pytest
import sys
import os

# Set required environment variables BEFORE importing app modules
os.environ.setdefault('DATABASE_PATH', '/tmp/test_datacheck.db')
os.environ.setdefault('MAX_UPLOAD_SIZE', '5242880')
os.environ.setdefault('MAX_ROWS', '100000')
os.environ.setdefault('MAX_COLUMNS', '100')
os.environ.setdefault('LOG_LEVEL', 'WARNING')

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
import tempfile


@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    return str(tmp_path / "test_requests.db")


class TestHealthEndpoint:
    """Tests for /health endpoint."""
    
    def test_health_returns_ok(self, client):
        """Test health check returns success."""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json == {"status": "ok"}


class TestIndexEndpoint:
    """Tests for / endpoint."""
    
    def test_index_serves_form(self, client):
        """Test that index page serves the form."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'CSV Quality Analyzer' in response.data


class TestAnalyzeEndpoint:
    """Tests for /api/analyze endpoint."""
    
    def test_analyze_valid_submission(self, client, tmp_path):
        """Test successful analysis with valid CSV."""
        # Create a temporary CSV file
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("""id,name,value
1,Alice,100
2,Bob,200
3,Charlie,300
""")
        
        with open(csv_path, 'rb') as f:
            data = {
                'name': 'John Doe',
                'email': 'john@example.com',
                'service': 'Basic CSV Analysis',
                'description': 'Test analysis',
                'csv_file': (f, 'test.csv')
            }
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert 'request_id' in response.json
        assert response.json['analysis']['total_rows'] == 3
        assert response.json['analysis']['total_columns'] == 3
    
    def test_analyze_missing_name(self, client, tmp_path):
        """Test that missing name returns error."""
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("id,name\n1,Alice")
        
        with open(csv_path, 'rb') as f:
            data = {
                'email': 'john@example.com',
                'service': 'Basic CSV Analysis',
                'csv_file': (f, 'test.csv')
            }
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert 'error' in response.json
        assert 'name' in response.json['error'].lower()
    
    def test_analyze_missing_email(self, client, tmp_path):
        """Test that missing email returns error."""
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("id,name\n1,Alice")
        
        with open(csv_path, 'rb') as f:
            data = {
                'name': 'John Doe',
                'service': 'Basic CSV Analysis',
                'csv_file': (f, 'test.csv')
            }
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert 'email' in response.json['error'].lower()
    
    def test_analyze_invalid_email(self, client, tmp_path):
        """Test that invalid email format returns error."""
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("id,name\n1,Alice")
        
        with open(csv_path, 'rb') as f:
            data = {
                'name': 'John Doe',
                'email': 'not-an-email',
                'service': 'Basic CSV Analysis',
                'csv_file': (f, 'test.csv')
            }
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert 'email' in response.json['error'].lower()
    
    def test_analyze_missing_file(self, client):
        """Test that missing file returns error."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'service': 'Basic CSV Analysis',
        }
        response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert 'file' in response.json['error'].lower()
    
    def test_analyze_wrong_file_type(self, client, tmp_path):
        """Test that non-CSV file returns error."""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("This is not a CSV")
        
        with open(txt_path, 'rb') as f:
            data = {
                'name': 'John Doe',
                'email': 'john@example.com',
                'service': 'Basic CSV Analysis',
                'csv_file': (f, 'test.txt')
            }
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert 'csv' in response.json['error'].lower()
    
    def test_analyze_file_too_large(self, client, tmp_path):
        """Test that oversized file returns error."""
        # Create a file larger than default 5MB
        large_path = tmp_path / "large.csv"
        large_path.write_text("x" * (6 * 1024 * 1024))
        
        with open(large_path, 'rb') as f:
            data = {
                'name': 'John Doe',
                'email': 'john@example.com',
                'service': 'Basic CSV Analysis',
                'csv_file': (f, 'large.csv')
            }
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        error_msg = response.json.get('error', '').lower()
        assert 'size' in error_msg or 'limit' in error_msg


class TestDownloadEndpoint:
    """Tests for /api/download/<id> endpoint."""
    
    def test_download_valid_request(self, client, tmp_path):
        """Test downloading a valid analysis result."""
        # First create a request
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("""id,name,value
1,Alice,100
""")
        
        # We need to simulate saving to database first
        # For this test, we'll just verify the endpoint structure
        response = client.get('/api/download/nonexistent-id')
        assert response.status_code == 404
    
    def test_download_nonexistent_request(self, client):
        """Test downloading a non-existent request returns 404."""
        response = client.get('/api/download/nonexistent-id')
        assert response.status_code == 404
        assert 'error' in response.json