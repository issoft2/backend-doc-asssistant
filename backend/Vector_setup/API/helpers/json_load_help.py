import json
from typing import List, Any

def safe_json_loads(value: str, default: List[str]) -> List[str]:
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default
    
    
def safe_json_dumps(obj: Any, default=list) -> str:
    """Safely serialize to JSON string, handles UUID/int coercion."""
    try:
        # Coerce to strings (handles UUID, int, etc.)
        serializable = [str(item) for item in obj] if isinstance(obj, (list, tuple)) else str(obj)
        return json.dumps(serializable)
    except (TypeError, ValueError) as e:
        print(f"JSON serialization failed: {e}, using default")
        return json.dumps(default)    