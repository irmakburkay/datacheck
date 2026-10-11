"""Unit tests for CSV analyzer functionality."""

import sys
from pathlib import Path
import tempfile
import pytest

# Add app directory to path to import analyzer directly
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

# Mock environment before importing
import os
os.environ['DATABASE_PATH'] = '/tmp/test.db'
os.environ['MAX_UPLOAD_SIZE'] = '5242880'
os.environ['MAX_ROWS'] = '100000'
os.environ['MAX_COLUMNS'] = '100'
os.environ['LOG_LEVEL'] = 'WARNING'

from analyzer import analyze, _infer_data_type
import pandas as pd


# ═══════════════════════════════════════════════════════════════════
# Type Inference Tests
# ═══════════════════════════════════════════════════════════════════

def test_infer_integer():
    """TC-U06: Test inference of integer type."""
    series = pd.Series(['1', '2', '3', '4', '5'])
    assert _infer_data_type(series) == 'integer'


def test_infer_float():
    """TC-U07: Test inference of float type."""
    series = pd.Series(['1.5', '2.7', '3.14', '4.0'])
    assert _infer_data_type(series) == 'float'


def test_infer_string():
    """TC-U08: Test inference of string type (default fallback)."""
    series = pd.Series(['hello', 'world', 'test'])
    assert _infer_data_type(series) == 'string'


def test_infer_boolean():
    """Test inference of boolean type."""
    series = pd.Series(['true', 'false', 'true'])
    assert _infer_data_type(series) == 'boolean'


def test_infer_boolean_yes_no():
    """Test inference of boolean type with yes/no values."""
    series = pd.Series(['yes', 'no', 'yes', 'no'])
    assert _infer_data_type(series) == 'boolean'


def test_infer_boolean_numeric():
    """Test inference of integer type with 0/1 values (numeric, not boolean)."""
    series = pd.Series(['0', '1', '1', '0'])
    # Note: 0 and 1 are treated as integers, not booleans
    # Boolean detection requires 'true'/'false', 'yes'/'no'
    assert _infer_data_type(series) == 'integer'


def test_infer_date():
    """Test inference of date type."""
    series = pd.Series(['2024-01-01', '2024-02-15', '2024-03-30'])
    assert _infer_data_type(series) == 'date'


def test_infer_all_missing_returns_string():
    """Test that all-missing series returns string type."""
    series = pd.Series(['', 'nan', 'null'])
    assert _infer_data_type(series) == 'string'


def test_infer_mixed_with_missing():
    """Test that type inference ignores missing values."""
    series = pd.Series(['1', '2', '', 'nan', '3'])
    assert _infer_data_type(series) == 'integer'


# ═══════════════════════════════════════════════════════════════════
# Full Analysis Tests
# ═══════════════════════════════════════════════════════════════════

def test_analyze_valid_csv():
    """TC-U01: Test analysis of valid CSV with known metrics."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('id,name,score\n')
        f.write('1,Alice,95.5\n')
        f.write('2,Bob,87.0\n')
        f.write('3,Charlie,92.3\n')
        temp_path = f.name
    
    try:
        result = analyze(temp_path)
        
        assert result['total_rows'] == 3
        assert result['total_columns'] == 3
        assert result['duplicate_rows'] == 0
        assert len(result['column_analysis']) == 3
        
        # Check column names
        col_names = [c['name'] for c in result['column_analysis']]
        assert col_names == ['id', 'name', 'score']
        
        # Check data types
        id_col = next(c for c in result['column_analysis'] if c['name'] == 'id')
        assert id_col['data_type'] == 'integer'
        assert id_col['missing_count'] == 0
        assert id_col['unique_count'] == 3
        
        score_col = next(c for c in result['column_analysis'] if c['name'] == 'score')
        assert score_col['data_type'] == 'float'
        assert 'stats' in score_col
        assert score_col['stats']['min'] == 87.0
        assert score_col['stats']['max'] == 95.5
        
    finally:
        os.unlink(temp_path)


def test_analyze_missing_values():
    """TC-U02: Test CSV with missing values."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('id,name,score\n')
        f.write('1,Alice,95.5\n')
        f.write('2,,\n')
        f.write('3,Charlie,92.3\n')
        f.write('4,Diana,\n')
        temp_path = f.name
    
    try:
        result = analyze(temp_path)
        
        assert result['total_rows'] == 4
        
        name_col = next(c for c in result['column_analysis'] if c['name'] == 'name')
        assert name_col['missing_count'] == 1
        assert name_col['missing_percentage'] == 25.0
        
        score_col = next(c for c in result['column_analysis'] if c['name'] == 'score')
        assert score_col['missing_count'] == 2
        assert score_col['missing_percentage'] == 50.0
        
    finally:
        os.unlink(temp_path)


def test_analyze_duplicates():
    """TC-U03: Test CSV with duplicate rows."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('name,department,score\n')
        f.write('Alice,Engineering,95\n')
        f.write('Bob,Sales,87\n')
        f.write('Alice,Engineering,95\n')  # Exact duplicate
        f.write('Charlie,Marketing,92\n')
        f.write('Alice,Engineering,95\n')  # Another duplicate
        temp_path = f.name
    
    try:
        result = analyze(temp_path)
        
        assert result['total_rows'] == 5
        assert result['duplicate_rows'] == 2  # 2 duplicate rows (not counting the first occurrence)
        
    finally:
        os.unlink(temp_path)


def test_analyze_empty_csv_raises_error():
    """TC-U04: Test that empty CSV (no data rows) raises error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('id,name,score\n')  # Header only
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError) as exc_info:
            analyze(temp_path)
        assert 'empty' in str(exc_info.value).lower()
    finally:
        os.unlink(temp_path)


def test_analyze_malformed_csv_raises_error():
    """TC-U05: Test that malformed CSV raises error."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
        f.write(b'\x89PNG\r\n\x1a\n')  # PNG header bytes
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError) as exc_info:
            analyze(temp_path)
        assert 'invalid' in str(exc_info.value).lower()
    finally:
        os.unlink(temp_path)


def test_analyze_file_too_large():
    """TC-U09: Test that oversized file raises error."""
    # Create a large temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('col1,col2\n')
        # Write enough data to exceed 5MB
        for i in range(200000):
            f.write(f'{i},{"x" * 50}\n')
        temp_path = f.name
    
    try:
        file_size = os.path.getsize(temp_path)
        with pytest.raises(ValueError) as exc_info:
            analyze(temp_path, file_size=file_size)
        assert 'size' in str(exc_info.value).lower() and 'exceeds' in str(exc_info.value).lower()
    finally:
        os.unlink(temp_path)


def test_analyze_too_many_rows():
    """Test that CSV exceeding row limit raises error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('id,value\n')
        # Write just over the limit
        for i in range(100002):
            f.write(f'{i},val{i}\n')
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError) as exc_info:
            analyze(temp_path)
        assert 'row' in str(exc_info.value).lower() and 'exceeds' in str(exc_info.value).lower()
    finally:
        os.unlink(temp_path)


def test_analyze_too_many_columns():
    """Test that CSV exceeding column limit raises error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        # Create 101 columns
        header = ','.join([f'col{i}' for i in range(101)])
        f.write(header + '\n')
        f.write(','.join(['1'] * 101) + '\n')
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError) as exc_info:
            analyze(temp_path)
        assert 'column' in str(exc_info.value).lower() and 'exceeds' in str(exc_info.value).lower()
    finally:
        os.unlink(temp_path)


def test_analyze_numeric_stats():
    """Test that numeric columns include statistical metrics."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('id,score\n')
        f.write('1,10\n')
        f.write('2,20\n')
        f.write('3,30\n')
        f.write('4,40\n')
        temp_path = f.name
    
    try:
        result = analyze(temp_path)
        
        score_col = next(c for c in result['column_analysis'] if c['name'] == 'score')
        assert 'stats' in score_col
        assert score_col['stats']['min'] == 10.0
        assert score_col['stats']['max'] == 40.0
        assert score_col['stats']['mean'] == 25.0
        assert score_col['stats']['median'] == 25.0
        
    finally:
        os.unlink(temp_path)


def test_analyze_date_range():
    """Test that date columns include date range."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('event,date\n')
        f.write('Start,2024-01-15\n')
        f.write('Middle,2024-06-20\n')
        f.write('End,2024-12-31\n')
        temp_path = f.name
    
    try:
        result = analyze(temp_path)
        
        date_col = next(c for c in result['column_analysis'] if c['name'] == 'date')
        assert date_col['data_type'] == 'date'
        assert 'date_range' in date_col
        assert date_col['date_range']['earliest'] == '2024-01-15'
        assert date_col['date_range']['latest'] == '2024-12-31'
        
    finally:
        os.unlink(temp_path)


def test_analyze_unique_counts():
    """Test that unique value counts are calculated."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('category,value\n')
        f.write('A,100\n')
        f.write('A,200\n')
        f.write('B,300\n')
        f.write('B,400\n')
        temp_path = f.name
    
    try:
        result = analyze(temp_path)
        
        category_col = next(c for c in result['column_analysis'] if c['name'] == 'category')
        assert category_col['unique_count'] == 2  # A and B
        
        value_col = next(c for c in result['column_analysis'] if c['name'] == 'value')
        assert value_col['unique_count'] == 4  # All unique
        
    finally:
        os.unlink(temp_path)


# ═══════════════════════════════════════════════════════════════════
# Fixture-based Tests
# ═══════════════════════════════════════════════════════════════════

def test_fixture_valid_basic():
    """Test analysis of valid_basic.csv fixture."""
    fixture_path = Path(__file__).parent / 'fixtures' / 'valid_basic.csv'
    if not fixture_path.exists():
        pytest.skip("Fixture file not found")
    
    result = analyze(str(fixture_path))
    
    assert result['total_rows'] == 10
    assert result['total_columns'] == 11
    assert result['duplicate_rows'] == 0


def test_fixture_missing_values():
    """Test analysis of missing_values.csv fixture."""
    fixture_path = Path(__file__).parent / 'fixtures' / 'missing_values.csv'
    if not fixture_path.exists():
        pytest.skip("Fixture file not found")
    
    result = analyze(str(fixture_path))
    
    # Check that missing values are detected
    assert result['total_rows'] == 10
    # At least one column should have missing values
    has_missing = any(c['missing_count'] > 0 for c in result['column_analysis'])
    assert has_missing


def test_fixture_duplicates():
    """Test analysis of duplicates.csv fixture."""
    fixture_path = Path(__file__).parent / 'fixtures' / 'duplicates.csv'
    if not fixture_path.exists():
        pytest.skip("Fixture file not found")
    
    result = analyze(str(fixture_path))
    
    assert result['duplicate_rows'] == 2


def test_fixture_header_only():
    """Test analysis of header_only.csv fixture."""
    fixture_path = Path(__file__).parent / 'fixtures' / 'header_only.csv'
    if not fixture_path.exists():
        pytest.skip("Fixture file not found")
    
    with pytest.raises(ValueError) as exc_info:
        analyze(str(fixture_path))
    assert 'empty' in str(exc_info.value).lower()


def test_fixture_malformed():
    """Test analysis of malformed.csv fixture."""
    fixture_path = Path(__file__).parent / 'fixtures' / 'malformed.csv'
    if not fixture_path.exists():
        pytest.skip("Fixture file not found")
    
    with pytest.raises(ValueError) as exc_info:
        analyze(str(fixture_path))
    assert 'invalid' in str(exc_info.value).lower()


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])