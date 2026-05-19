"""
Utility functions for APIForge
Common helper functions used across the project
"""

import os
import re
import json
import hashlib
import random
import string
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


def generate_id(prefix: str = "", length: int = 8) -> str:
    """Generate random ID with optional prefix"""
    chars = string.ascii_lowercase + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(length))
    return f"{prefix}{random_str}" if prefix else random_str


def generate_hash(data: Union[str, Dict, List]) -> str:
    """Generate MD5 hash from string or serializable data"""
    if isinstance(data, (dict, list)):
        data = json.dumps(data, sort_keys=True)
    return hashlib.md5(str(data).encode()).hexdigest()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'[\x00-\x1f]', '', filename)
    return filename.strip()


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if not"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json_file(filepath: Union[str, Path]) -> Optional[Dict]:
    """Load JSON file safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to load JSON file {filepath}: {e}")
        return None


def save_json_file(filepath: Union[str, Path], data: Any, indent: int = 2) -> bool:
    """Save data to JSON file safely"""
    try:
        ensure_dir(Path(filepath).parent)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON file {filepath}: {e}")
        return False


def merge_dicts(base: Dict, updates: Dict, deep: bool = True) -> Dict:
    """Merge two dictionaries"""
    result = base.copy()
    
    if deep:
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value, deep=True)
            else:
                result[key] = value
    else:
        result.update(updates)
    
    return result


def filter_dict(data: Dict, keys: List[str], exclude: bool = False) -> Dict:
    """Filter dictionary by keys"""
    if exclude:
        return {k: v for k, v in data.items() if k not in keys}
    return {k: v for k, v in data.items() if k in keys}


def flatten_dict(data: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(data: Dict, sep: str = '.') -> Dict:
    """Unflatten dictionary"""
    result = {}
    for key, value in data.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def parse_content_type(content_type: str) -> Optional[str]:
    """Parse content type and return format"""
    if 'application/json' in content_type:
        return 'json'
    elif 'application/xml' in content_type or 'text/xml' in content_type:
        return 'xml'
    elif 'text/plain' in content_type:
        return 'text'
    elif 'application/x-www-form-urlencoded' in content_type:
        return 'form'
    return None


def guess_json_type(value: Any) -> str:
    """Guess JSON schema type from Python value"""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "object"
    return "string"


def generate_fake_data(data_type: str, **kwargs) -> Any:
    """Generate fake data based on type"""
    from faker import Faker
    fake = Faker()
    
    generators = {
        'name': lambda: fake.name(),
        'email': lambda: fake.email(),
        'phone': lambda: fake.phone_number(),
        'address': lambda: fake.address(),
        'url': lambda: fake.url(),
        'ipv4': lambda: fake.ipv4(),
        'ipv6': lambda: fake.ipv6(),
        'date': lambda: fake.date().isoformat(),
        'datetime': lambda: fake.iso8601().isoformat(),
        'text': lambda: fake.text(max_nb_chars=kwargs.get('max_chars', 200)),
        'number': lambda: random.randint(kwargs.get('min', 1), kwargs.get('max', 100)),
        'float': lambda: random.uniform(kwargs.get('min', 0), kwargs.get('max', 100)),
        'boolean': lambda: random.choice([True, False]),
        'uuid': lambda: str(fake.uuid4()),
        'image': lambda: fake.image_url(width=kwargs.get('width', 800), height=kwargs.get('height', 600)),
    }
    
    return generators.get(data_type, generators['text'])()


def calculate_size_mb(filepath: Union[str, Path]) -> float:
    """Calculate file size in MB"""
    return Path(filepath).stat().st_size / (1024 * 1024)


def get_timestamp(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Get formatted timestamp"""
    return datetime.now().strftime(fmt)


def parse_duration(duration: str) -> int:
    """Parse duration string to seconds (e.g., '5s', '2m', '1h')"""
    units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    match = re.match(r'^(\d+)([smhd])$', duration.lower())
    if match:
        return int(match.group(1)) * units[match.group(2)]
    return 0


def mask_sensitive(data: str, pattern: str = None) -> str:
    """Mask sensitive information in string"""
    patterns = [
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '****-****-****-****'),  # Credit card
        (r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****'),  # SSN
        (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '***@***.***'),  # Email
        (r'bearer\s+[a-zA-Z0-9._-]+', 'Bearer ***'),  # Bearer token
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]+', 'api_key=***'),  # API key
    ]
    
    result = data
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    if pattern:
        result = re.sub(pattern, '***', result)
    
    return result


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def is_allowed(self) -> bool:
        """Check if request is allowed under rate limit"""
        now = datetime.now()
        self.requests = [req for req in self.requests if now - req < timedelta(seconds=self.window_seconds)]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
    
    def reset(self):
        """Reset rate limiter"""
        self.requests = []


def validate_openapi_spec(spec: Dict) -> List[str]:
    """Validate OpenAPI specification"""
    errors = []
    
    required_fields = ['openapi', 'info', 'paths']
    for field in required_fields:
        if field not in spec:
            errors.append(f"Missing required field: {field}")
    
    if 'openapi' in spec and not re.match(r'^3\.\d+\.\d+$', spec['openapi']):
        errors.append("Invalid OpenAPI version format")
    
    if 'paths' in spec and not isinstance(spec['paths'], dict):
        errors.append("'paths' must be an object")
    
    return errors
