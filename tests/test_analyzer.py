"""Unit tests for CSV analyzer functionality."""

import sys
from pathlib import Path

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


def test_infer_integer():
    """Test inference of integer type."""
    series = pd.Series(['1', '2', '3', '4', '5'])
    assert _infer_data_type(series) == 'integer'


def test_infer_float():
    """Test inference of float type."""
    series = pd.Series(['1.5', '2.7', '3.14', '4.0'])
    assert _infer_data_type(series) == 'float'


def test_infer_string():
    """Test inference of string type (default fallback)."""
    series = pd.Series(['hello', 'world', 'test'])
    assert _infer_data_type(series) == 'string'


def test_infer_boolean():
    """Test inference of boolean type."""
    series = pd.Series(['true', 'false', 'true'])
    assert _infer_data_type(series) == 'boolean'


def test_infer_all_missing_returns_string():
    """Test that all-missing series returns string type."""
    series = pd.Series(['', 'nan', 'null'])
    assert _infer_data_type(series) == 'string'