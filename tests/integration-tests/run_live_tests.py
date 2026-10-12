"""
Comprehensive live testing script for DataCheck API
Tests both local (http://127.0.0.1:5000) and production (https://irmakburkay.pythonanywhere.com)
"""

import requests
import json
from pathlib import Path
import time

# Test configuration
BASE_URL = "https://irmakburkay.pythonanywhere.com"  # Change to production URL to test live
SCENARIOS_DIR = Path(__file__).parent.parent / 'fixtures'  # CSV files are in tests/fixtures/

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_section(title):
    """Print section header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(msg):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    """Print error message."""
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    """Print info message."""
    print(f"{YELLOW}→{RESET} {msg}")

def test_health_endpoint():
    """Test 1: Health endpoint."""
    print_section("TEST 1: Health Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                print_success(f"Health check passed: {data}")
                return True
            else:
                print_error(f"Unexpected response: {data}")
                return False
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_index_page():
    """Test 2: Index page loads."""
    print_section("TEST 2: Index Page")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            if 'DataCheck' in response.text and 'CSV Quality Analyzer' in response.text:
                print_success("Index page loaded successfully")
                print_info(f"Page size: {len(response.text)} bytes")
                return True
            else:
                print_error("Index page missing expected content")
                return False
        else:
            print_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_csv_upload(scenario_name, csv_path, expected_features=None):
    """Test CSV upload and analysis."""
    print_section(f"TEST: {scenario_name}")
    
    if not csv_path.exists():
        print_error(f"File not found: {csv_path}")
        return False
    
    print_info(f"File: {csv_path.name}")
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'csv_file': (csv_path.name, f, 'text/csv')}
            data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'service': 'Basic CSV Analysis',
                'description': f'Testing {scenario_name}'
            }
            
            response = requests.post(
                f"{BASE_URL}/api/analyze",
                data=data,
                files=files,
                timeout=10
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # Basic validation
            if result.get('status') == 'success':
                print_success("Analysis completed successfully")
                
                # Extract analysis data
                analysis = result.get('analysis', {})
                request_id = result.get('request_id')
                
                print_info(f"Request ID: {request_id}")
                print_info(f"Filename: {analysis.get('filename')}")
                print_info(f"Total rows: {analysis.get('total_rows')}")
                print_info(f"Total columns: {analysis.get('total_columns')}")
                print_info(f"Duplicate rows: {analysis.get('duplicate_rows')}")
                
                # Check columns
                columns = analysis.get('columns', [])
                print_info(f"Columns analyzed: {len(columns)}")
                
                for col in columns:
                    col_info = [
                        f"  - {col['name']}:",
                        f"type={col['data_type']}",
                        f"unique={col.get('unique_count', 'N/A')}",
                        f"missing={col['missing_count']}({col['missing_percentage']}%)"
                    ]
                    
                    # Check for stats (NEW FEATURE)
                    if 'stats' in col:
                        stats = col['stats']
                        col_info.append(f"stats(min={stats['min']}, max={stats['max']}, mean={stats['mean']}, median={stats['median']})")
                    
                    # Check for date range (NEW FEATURE)
                    if 'date_range' in col:
                        dr = col['date_range']
                        col_info.append(f"range({dr['earliest']} to {dr['latest']})")
                    
                    print(" ".join(col_info))
                
                # Validate expected features
                if expected_features:
                    all_passed = True
                    for feature, expected in expected_features.items():
                        actual = analysis.get(feature)
                        if actual == expected:
                            print_success(f"Feature check: {feature} = {expected}")
                        else:
                            print_error(f"Feature check failed: {feature} expected {expected}, got {actual}")
                            all_passed = False
                    
                    if not all_passed:
                        return False
                
                # Test download endpoint
                print_info("Testing download endpoint...")
                download_response = requests.get(f"{BASE_URL}/api/download/{request_id}", timeout=5)
                if download_response.status_code == 200:
                    print_success("Download endpoint works")
                    report = download_response.json()
                    print_info(f"Report contains {len(report.get('column_analysis', []))} columns")
                else:
                    print_error(f"Download failed: HTTP {download_response.status_code}")
                
                return True
            else:
                print_error(f"Analysis failed: {result}")
                return False
        else:
            print_error(f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_validation_errors():
    """Test validation error handling."""
    print_section("TEST: Validation Errors")
    
    test_cases = [
        {
            'name': 'Missing name',
            'data': {'email': 'test@example.com', 'service': 'Basic CSV Analysis'},
            'expected_status': 400
        },
        {
            'name': 'Missing email',
            'data': {'name': 'Test', 'service': 'Basic CSV Analysis'},
            'expected_status': 400
        },
        {
            'name': 'Invalid email',
            'data': {'name': 'Test', 'email': 'not-an-email', 'service': 'Basic CSV Analysis'},
            'expected_status': 400
        },
        {
            'name': 'Missing service',
            'data': {'name': 'Test', 'email': 'test@example.com'},
            'expected_status': 400
        }
    ]
    
    all_passed = True
    for case in test_cases:
        try:
            # Create a minimal CSV file
            csv_content = "col1\nval1"
            files = {'csv_file': ('test.csv', csv_content, 'text/csv')}
            
            response = requests.post(
                f"{BASE_URL}/api/analyze",
                data=case['data'],
                files=files,
                timeout=5
            )
            
            if response.status_code == case['expected_status']:
                print_success(f"{case['name']}: Correctly returned HTTP {response.status_code}")
            else:
                print_error(f"{case['name']}: Expected {case['expected_status']}, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print_error(f"{case['name']}: Request failed - {e}")
            all_passed = False
    
    return all_passed

def test_edge_cases():
    """Test edge cases."""
    print_section("TEST: Edge Cases")
    
    all_passed = True
    
    # Test 1: Empty CSV (header only)
    print_info("Testing empty CSV (header only)...")
    try:
        csv_content = "col1,col2,col3\n"
        files = {'csv_file': ('empty.csv', csv_content, 'text/csv')}
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'service': 'Basic CSV Analysis'
        }
        
        response = requests.post(f"{BASE_URL}/api/analyze", data=data, files=files, timeout=5)
        
        if response.status_code == 400:
            result = response.json()
            if 'empty' in result.get('error', '').lower():
                print_success("Empty CSV correctly rejected with appropriate error")
            else:
                print_error(f"Wrong error message: {result.get('error')}")
                all_passed = False
        else:
            print_error(f"Expected 400, got {response.status_code}")
            all_passed = False
            
    except Exception as e:
        print_error(f"Test failed: {e}")
        all_passed = False
    
    # Test 2: Wrong file type
    print_info("Testing wrong file type...")
    try:
        files = {'csv_file': ('test.txt', 'not a csv', 'text/plain')}
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'service': 'Basic CSV Analysis'
        }
        
        response = requests.post(f"{BASE_URL}/api/analyze", data=data, files=files, timeout=5)
        
        if response.status_code == 400:
            result = response.json()
            if 'csv' in result.get('error', '').lower():
                print_success("Non-CSV file correctly rejected")
            else:
                print_error(f"Wrong error message: {result.get('error')}")
                all_passed = False
        else:
            print_error(f"Expected 400, got {response.status_code}")
            all_passed = False
            
    except Exception as e:
        print_error(f"Test failed: {e}")
        all_passed = False
    
    return all_passed

def test_sample_csv_download():
    """Test sample CSV download."""
    print_section("TEST: Sample CSV Download")
    try:
        response = requests.get(f"{BASE_URL}/sample-csv", timeout=5)
        if response.status_code == 200:
            if 'text/csv' in response.headers.get('Content-Type', ''):
                print_success("Sample CSV download works")
                print_info(f"File size: {len(response.content)} bytes")
                # Verify it's actually CSV content
                if b',' in response.content:
                    print_success("Content appears to be valid CSV")
                    return True
                else:
                    print_error("Content doesn't look like CSV")
                    return False
            else:
                print_error(f"Wrong content type: {response.headers.get('Content-Type')}")
                return False
        elif response.status_code == 404:
            print_info("Sample CSV not found (this is OK if file doesn't exist)")
            return True
        else:
            print_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_404_handler():
    """Test 404 error handler."""
    print_section("TEST: 404 Handler")
    try:
        response = requests.get(f"{BASE_URL}/this-page-does-not-exist", timeout=5)
        if response.status_code == 404:
            print_success("404 handler works")
            if '404' in response.text or 'not found' in response.text.lower():
                print_success("404 page has appropriate content")
                return True
            else:
                print_info("404 page exists but content not verified")
                return True
        else:
            print_error(f"Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print(f"\n{BLUE}╔══════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║{RESET}     DataCheck Live API Test Suite                         {BLUE}║{RESET}")
    print(f"{BLUE}╚══════════════════════════════════════════════════════════════╝{RESET}")
    print(f"\nTarget: {YELLOW}{BASE_URL}{RESET}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        'Health Endpoint': test_health_endpoint(),
        'Index Page': test_index_page(),
        'Scenario 1 - Numeric Stats': test_csv_upload(
            'Scenario 1: Numeric with Stats',
            SCENARIOS_DIR / 'scenario1_numeric.csv',
            {'total_rows': 5, 'total_columns': 4}
        ),
        'Scenario 2 - Date Ranges': test_csv_upload(
            'Scenario 2: Date Ranges',
            SCENARIOS_DIR / 'scenario2_dates.csv',
            {'total_rows': 5, 'total_columns': 4}
        ),
        'Scenario 3 - Mixed Types': test_csv_upload(
            'Scenario 3: Mixed Data Types',
            SCENARIOS_DIR / 'scenario3_mixed.csv',
            {'total_rows': 6, 'total_columns': 6}
        ),
        'Scenario 4 - Duplicates': test_csv_upload(
            'Scenario 4: Duplicate Detection',
            SCENARIOS_DIR / 'scenario4_duplicates.csv',
            {'total_rows': 6, 'duplicate_rows': 2}
        ),
        'Scenario 5 - Unique Counts': test_csv_upload(
            'Scenario 5: Unique Value Counts',
            SCENARIOS_DIR / 'scenario5_large_unique.csv',
            {'total_rows': 10, 'total_columns': 3}
        ),
        'Validation Errors': test_validation_errors(),
        'Edge Cases': test_edge_cases(),
        'Sample CSV Download': test_sample_csv_download(),
        '404 Handler': test_404_handler()
    }
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status} - {test_name}")
    
    print(f"\n{BLUE}{'─'*60}{RESET}")
    percentage = (passed / total * 100) if total > 0 else 0
    color = GREEN if percentage == 100 else YELLOW if percentage >= 80 else RED
    print(f"{color}Result: {passed}/{total} tests passed ({percentage:.1f}%){RESET}")
    print(f"{BLUE}{'─'*60}{RESET}\n")
    
    return passed == total

if __name__ == '__main__':
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Tests interrupted by user{RESET}\n")
        exit(1)
    except Exception as e:
        print(f"\n\n{RED}Fatal error: {e}{RESET}\n")
        exit(1)
