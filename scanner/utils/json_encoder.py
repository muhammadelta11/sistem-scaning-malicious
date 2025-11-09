"""
Custom JSON encoder untuk handle numpy types dan types lainnya yang tidak bisa di-serialize oleh JSON default.
"""

import json
from datetime import datetime, date
from decimal import Decimal

# Try to import numpy, jika tidak ada maka skip numpy handling
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


def convert_to_serializable(obj):
    """
    Convert object ke serializable format untuk JSON.
    Handle numpy types, datetime, Decimal, dll.
    
    Args:
        obj: Object yang akan di-convert
        
    Returns:
        Object yang sudah bisa di-serialize ke JSON
    """
    if isinstance(obj, dict):
        # Convert dictionary keys dan values
        return {str(k) if not isinstance(k, (str, int, float, bool, type(None))) else k: convert_to_serializable(v) 
                for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        # Convert list/tuple items
        return [convert_to_serializable(item) for item in obj]
    elif HAS_NUMPY:
        if isinstance(obj, np.integer):
            # Convert numpy int types (int64, int32, etc) ke Python int
            return int(obj)
        elif isinstance(obj, np.floating):
            # Convert numpy float types (float64, float32, etc) ke Python float
            return float(obj)
        elif isinstance(obj, np.bool_):
            # Convert numpy bool ke Python bool
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            # Convert numpy array ke list
            return obj.tolist()
    elif isinstance(obj, (datetime, date)):
        # Convert datetime/date ke ISO format string
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        # Convert Decimal ke float
        return float(obj)
    elif isinstance(obj, (set, frozenset)):
        # Convert set/frozenset ke list
        return list(obj)
    else:
        # Return as-is jika sudah serializable
        return obj


class NumpyJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder yang bisa handle numpy types.
    """
    
    def encode(self, obj):
        # Convert object terlebih dahulu
        obj = convert_to_serializable(obj)
        return super().encode(obj)
    
    def default(self, obj):
        # Handle types yang tidak bisa di-handle oleh JSONEncoder default
        if HAS_NUMPY:
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
        
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (set, frozenset)):
            return list(obj)
        return super().default(obj)


def json_dumps_safe(obj, **kwargs):
    """
    Safe JSON dumps yang bisa handle numpy types dan types lainnya.
    
    Args:
        obj: Object yang akan di-serialize
        **kwargs: Additional arguments untuk json.dumps
        
    Returns:
        JSON string
    """
    # Convert object terlebih dahulu
    obj = convert_to_serializable(obj)
    # Use custom encoder
    return json.dumps(obj, cls=NumpyJSONEncoder, **kwargs)

