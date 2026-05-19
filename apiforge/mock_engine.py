"""
Mock Engine for APIForge
Handles mock response generation, scenario simulation, and dynamic responses
"""

import re
import time
import random
import json
import hashlib
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


@dataclass
class MockResponse:
    """Mock response definition"""
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    delay_ms: int = 0
    content_type: str = "application/json"


@dataclass
class MockScenario:
    """Mock scenario definition"""
    name: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    response: MockResponse = field(default_factory=MockResponse)
    probability: float = 1.0


class DynamicValueGenerator:
    """Generate dynamic values for mock responses"""
    
    def __init__(self):
        self._generators = {}
        self._register_default_generators()
    
    def _register_default_generators(self):
        """Register default value generators"""
        self.register("uuid", lambda: self._generate_uuid())
        self.register("timestamp", lambda: self._timestamp())
        self.register("date", lambda: self._date())
        self.register("datetime", lambda: self._datetime())
        self.register("random_int", lambda opts: random.randint(opts.get("min", 1), opts.get("max", 100)))
        self.register("random_float", lambda opts: round(random.uniform(opts.get("min", 0), opts.get("max", 100)), 2))
        self.register("random_choice", lambda opts: random.choice(opts.get("choices", ["a", "b", "c"])))
        self.register("incremental_id", lambda: self._incremental_id())
        self.register("email", lambda: self._fake_email())
        self.register("name", lambda: self._fake_name())
        self.register("url", lambda: self._fake_url())
        self.register("ip", lambda: self._fake_ip())
    
    def register(self, name: str, generator: Callable):
        """Register a custom value generator"""
        self._generators[name] = generator
    
    def generate(self, spec: Union[str, Dict]) -> Any:
        """Generate value based on specification"""
        if isinstance(spec, str):
            return self._generate_from_string(spec)
        elif isinstance(spec, dict):
            return self._generate_from_dict(spec)
        return spec
    
    def _generate_from_string(self, spec: str) -> Any:
        """Generate value from string specification"""
        if spec.startswith("${") and spec.endswith("}"):
            spec = spec[2:-1]
        
        parts = spec.split("(", 1)
        generator_name = parts[0]
        args = {}
        
        if len(parts) > 1 and parts[1].endswith(")"):
            args_str = parts[1][:-1]
            args = self._parse_args(args_str)
        
        if generator_name in self._generators:
            return self._generators[generator_name](args)
        
        return spec
    
    def _generate_from_dict(self, spec: Dict) -> Any:
        """Generate value from dict specification"""
        if "$type" in spec:
            type_name = spec["$type"]
            args = {k: v for k, v in spec.items() if k != "$type"}
            if type_name in self._generators:
                return self._generators[type_name](args)
        
        if "$expr" in spec:
            return self._evaluate_expression(spec["$expr"])
        
        return spec
    
    def _parse_args(self, args_str: str) -> Dict:
        """Parse function arguments string"""
        args = {}
        parts = args_str.split(",")
        for part in parts:
            part = part.strip()
            if "=" in part:
                key, value = part.split("=", 1)
                key = key.strip()
                value = value.strip()
                try:
                    args[key] = json.loads(value)
                except json.JSONDecodeError:
                    args[key] = value.strip('"\'')
        return args
    
    def _evaluate_expression(self, expr: str) -> Any:
        """Evaluate simple expression"""
        try:
            return eval(expr, {"random": random, "time": time, "datetime": datetime})
        except Exception as e:
            logger.warning(f"Failed to evaluate expression '{expr}': {e}")
            return None
    
    def _generate_uuid(self) -> str:
        return str(hashlib.uuid4())
    
    def _timestamp(self) -> int:
        return int(datetime.now().timestamp())
    
    def _date(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")
    
    def _datetime(self) -> str:
        return datetime.now().isoformat()
    
    def _incremental_id(self) -> int:
        if not hasattr(self, "_counter"):
            self._counter = 0
        self._counter += 1
        return self._counter
    
    def _fake_email(self) -> str:
        username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
        domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'github.com']
        return f"{username}@{random.choice(domains)}"
    
    def _fake_name(self) -> str:
        first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana"]
        last_names = ["Smith", "Doe", "Brown", "Jones", "Wilson", "Taylor"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _fake_url(self) -> str:
        paths = ["api", "users", "products", "orders", "data"]
        return f"https://example.com/{random.choice(paths)}/{random.randint(1, 1000)}"
    
    def _fake_ip(self) -> str:
        return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"


class MockEngine:
    """Main mock engine for generating and managing mock responses"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.value_generator = DynamicValueGenerator()
        self.scenarios: Dict[str, List[MockScenario]] = {}
        self.fallback_responses: Dict[str, MockResponse] = {}
        self._setup_default_scenarios()
    
    def _setup_default_scenarios(self):
        """Setup default mock scenarios"""
        default_response = MockResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"message": "Mock response", "status": "success"}
        )
        self.fallback_responses["default"] = default_response
    
    def add_scenario(self, endpoint: str, scenario: MockScenario):
        """Add a mock scenario for an endpoint"""
        if endpoint not in self.scenarios:
            self.scenarios[endpoint] = []
        self.scenarios[endpoint].append(scenario)
    
    def set_fallback_response(self, endpoint: str, response: MockResponse):
        """Set fallback response for endpoint"""
        self.fallback_responses[endpoint] = response
    
    def generate_response(self, endpoint: str, request_data: Dict) -> MockResponse:
        """Generate mock response based on endpoint and request data"""
        if endpoint in self.scenarios:
            for scenario in self.scenarios[endpoint]:
                if self._check_conditions(scenario.conditions, request_data):
                    if random.random() <= scenario.probability:
                        return self._apply_delay(scenario.response)
        
        if endpoint in self.fallback_responses:
            return self._apply_delay(self.fallback_responses[endpoint])
        
        return self._apply_delay(self.fallback_responses["default"])
    
    def _check_conditions(self, conditions: Dict, request_data: Dict) -> bool:
        """Check if conditions match request data"""
        for key, value in conditions.items():
            if key.startswith("header."):
                header_name = key[7:]
                if request_data.get("headers", {}).get(header_name) != value:
                    return False
            elif key.startswith("query."):
                query_param = key[6:]
                if request_data.get("query", {}).get(query_param) != value:
                    return False
            elif key == "method":
                if request_data.get("method") != value:
                    return False
            elif key == "body_field":
                if value not in request_data.get("body", {}):
                    return False
            else:
                if request_data.get(key) != value:
                    return False
        return True
    
    def _apply_delay(self, response: MockResponse) -> MockResponse:
        """Apply configured delay to response"""
        delay = response.delay_ms
        if self.config.get("mock", {}).get("latency_min", 0) > 0:
            min_delay = self.config["mock"]["latency_min"]
            max_delay = self.config["mock"].get("latency_max", min_delay)
            delay = random.randint(min_delay, max_delay)
        
        if delay > 0:
            time.sleep(delay / 1000)
        
        return response
    
    def generate_from_template(self, template: Union[Dict, List], context: Optional[Dict] = None) -> Any:
        """Generate response from template with dynamic values"""
        context = context or {}
        
        if isinstance(template, list):
            return [self.generate_from_template(item, context) for item in template]
        
        if isinstance(template, dict):
            result = {}
            for key, value in template.items():
                result[key] = self.generate_from_template(value, context)
            return result
        
        if isinstance(template, str):
            if "${" in template:
                return self.value_generator.generate(template)
            return template
        
        return template
    
    def generate_error_response(self, error_code: Optional[int] = None) -> MockResponse:
        """Generate error response"""
        if error_code is None:
            error_codes = self.config.get("mock", {}).get("error_codes", [400, 401, 403, 404, 500])
            error_code = random.choice(error_codes)
        
        error_messages = {
            400: {"error": "Bad Request", "message": "The request was invalid or cannot be served."},
            401: {"error": "Unauthorized", "message": "Authentication is required."},
            403: {"error": "Forbidden", "message": "You do not have permission to access this resource."},
            404: {"error": "Not Found", "message": "The requested resource was not found."},
            500: {"error": "Internal Server Error", "message": "An unexpected error occurred."},
        }
        
        return MockResponse(
            status_code=error_code,
            headers={"Content-Type": "application/json"},
            body=error_messages.get(error_code, {"error": "Unknown Error"})
        )
    
    def load_scenarios_from_file(self, filepath: Union[str, Path]):
        """Load mock scenarios from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for endpoint, scenarios_data in data.items():
            if not isinstance(scenarios_data, list):
                scenarios_data = [scenarios_data]
            
            for scenario_data in scenarios_data:
                scenario = self._parse_scenario_data(scenario_data)
                self.add_scenario(endpoint, scenario)
    
    def _parse_scenario_data(self, data: Dict) -> MockScenario:
        """Parse scenario data to MockScenario object"""
        response_data = data.get("response", {})
        response = MockResponse(
            status_code=response_data.get("status_code", 200),
            headers=response_data.get("headers", {"Content-Type": "application/json"}),
            body=response_data.get("body"),
            delay_ms=response_data.get("delay_ms", 0),
            content_type=response_data.get("content_type", "application/json")
        )
        
        return MockScenario(
            name=data.get("name", "unnamed"),
            conditions=data.get("conditions", {}),
            response=response,
            probability=data.get("probability", 1.0)
        )
    
    def save_scenarios_to_file(self, filepath: Union[str, Path]):
        """Save mock scenarios to JSON file"""
        data = {}
        for endpoint, scenarios in self.scenarios.items():
            scenarios_data = []
            for scenario in scenarios:
                scenarios_data.append({
                    "name": scenario.name,
                    "conditions": scenario.conditions,
                    "probability": scenario.probability,
                    "response": {
                        "status_code": scenario.response.status_code,
                        "headers": scenario.response.headers,
                        "body": scenario.response.body,
                        "delay_ms": scenario.response.delay_ms,
                        "content_type": scenario.response.content_type
                    }
                })
            data[endpoint] = scenarios_data
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def clear_scenarios(self):
        """Clear all mock scenarios"""
        self.scenarios.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get mock engine statistics"""
        return {
            "total_scenarios": sum(len(s) for s in self.scenarios.values()),
            "endpoints_with_scenarios": len(self.scenarios),
            "fallback_responses": len(self.fallback_responses),
            "registered_generators": len(self.value_generator._generators)
        }
