from dotenv import load_dotenv
import os
import pandas as pd
from pathlib import Path

# Load .env from project root explicitly (find parent of app/ directory)
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 5242880))
MAX_ROWS = int(os.getenv('MAX_ROWS', 100000))
MAX_COLUMNS = int(os.getenv('MAX_COLUMNS', 100))


def analyze(file_path: str, file_size: int | None = None) -> dict:
    """Analyze CSV file and return metrics.
    
    Args:
        file_path: Path to CSV file
        file_size: Optional file size in bytes for validation
    
    Returns:
        Dict with analysis results
    
    Raises:
        ValueError: If file violates limits or is invalid
    """
    # Validate file size before reading
    if file_size is not None and file_size > MAX_UPLOAD_SIZE:
        raise ValueError(f"File size ({file_size} bytes) exceeds limit of {MAX_UPLOAD_SIZE} bytes")
    
    try:
        # Read CSV with limits to prevent memory issues
        df = pd.read_csv(file_path, nrows=MAX_ROWS + 1)
    except Exception as e:
        raise ValueError(f"Invalid CSV file: {e}")
    
    # Validate row/column limits
    total_rows = len(df)
    total_columns = len(df.columns)
    
    if total_rows > MAX_ROWS:
        raise ValueError(f"Row count ({total_rows}) exceeds limit of {MAX_ROWS}")
    if total_columns > MAX_COLUMNS:
        raise ValueError(f"Column count ({total_columns}) exceeds limit of {MAX_COLUMNS}")
    
    # Count duplicate rows (exact duplicates across all columns)
    duplicate_rows = df.duplicated().sum()
    
    # Analyze each column
    column_analysis = []
    for column in df.columns:
        series = df[column].astype(str).str.strip()
        
        # Data type detection
        data_type = _infer_data_type(series)
        
        # Missing values (empty strings, NaN, 'nan')
        missing_mask = series.isna() | series.str.lower().isin(['', 'nan', 'null', 'none'])
        missing_count = missing_mask.sum()
        missing_percentage = (missing_count / total_rows * 100) if total_rows > 0 else 0.0
        
        column_analysis.append({
            'name': column,
            'data_type': data_type,
            'missing_count': int(missing_count),
            'missing_percentage': round(missing_percentage, 2)
        })
    
    return {
        'total_rows': total_rows,
        'total_columns': total_columns,
        'duplicate_rows': int(duplicate_rows),
        'column_analysis': column_analysis
    }


def _infer_data_type(series: pd.Series) -> str:
    """Infer data type for a series."""
    # Remove missing values for type detection
    non_null = series[~series.isna() & ~series.str.lower().isin(['', 'nan', 'null', 'none'])]
    
    if len(non_null) == 0:
        return 'string'  # All values missing, default to string
    
    # Try integer
    try:
        numeric = pd.to_numeric(non_null, errors='coerce')
        if (numeric.notna() & (numeric % 1 == 0)).all():
            return 'integer'
    except Exception:
        pass
    
    # Try float
    try:
        numeric = pd.to_numeric(non_null, errors='coerce')
        if numeric.notna().all():
            return 'float'
    except Exception:
        pass
    
    # Try boolean
    bool_values = {'true', 'false', 'yes', 'no', '1', '0'}
    if non_null.str.lower().isin(bool_values).all():
        return 'boolean'
    
    # Try date
    try:
        dates = pd.to_datetime(non_null, errors='coerce')
        if dates.notna().any():
            return 'date'
    except Exception:
        pass
    
    return 'string'
