"""
Mock Generator for APIForge
Generates mock data and responses from OpenAPI specs and templates
"""

import json
import re
import random
import string
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)


class MockGenerator:
    """Generates mock data and API responses from specifications"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.null_probability = self.config.get("generator", {}).get("null_probability", 0.1)
        self.preserve_types = self.config.get("generator", {}).get("preserve_types", True)
    
    def generate_from_openapi(self, spec: Dict) -> Dict[str, Any]:
        """Generate mock responses from OpenAPI specification"""
        generated = {
            "endpoints": {},
            "schemas": {}
        }
        
        paths = spec.get("paths", {})
        components = spec.get("components", {})
        schemas = components.get("schemas", {})
        
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    endpoint_key = f"{method.upper()} {path}"
                    
                    generated["endpoints"][endpoint_key] = {
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", ""),
                        "parameters": self._generate_parameters(operation.get("parameters", [])),
                        "requestBody": self._generate_request_body(operation.get("requestBody")),
                        "responses": self._generate_responses(operation.get("responses", {}), schemas)
                    }
        
        for schema_name, schema in schemas.items():
            generated["schemas"][schema_name] = self._generate_from_schema(schema, schemas)
        
        return generated
    
    def _generate_parameters(self, parameters: List[Dict]) -> Dict[str, Any]:
        """Generate mock parameter values"""
        result = {}
        
        for param in parameters:
            name = param.get("name", "")
            param_in = param.get("in", "query")
            schema = param.get("schema", {})
            
            if param_in == "query":
                result[name] = self._generate_from_schema(schema)
            elif param_in == "path":
                result[name] = self._generate_from_schema(schema)
            elif param_in == "header":
                result[name] = self._generate_from_schema(schema)
        
        return result
    
    def _generate_request_body(self, request_body: Optional[Dict]) -> Any:
        """Generate mock request body"""
        if not request_body:
            return None
        
        content = request_body.get("content", {})
        
        if "application/json" in content:
            json_content = content["application/json"]
            schema = json_content.get("schema", {})
            example = json_content.get("example")
            
            if example:
                return example
            
            return self._generate_from_schema(schema)
        
        return None
    
    def _generate_responses(self, responses: Dict, schemas: Dict) -> Dict[str, Any]:
        """Generate mock responses"""
        result = {}
        
        for status_code, response in responses.items():
            content = response.get("content", {})
            
            if "application/json" in content:
                json_content = content["application/json"]
                schema = json_content.get("schema", {})
                example = json_content.get("example")
                
                if example:
                    result[status_code] = {"body": example}
                else:
                    result[status_code] = {"body": self._generate_from_schema(schema, schemas)}
            else:
                result[status_code] = {"body": {"message": f"Response for status {status_code}"}}
        
        return result
    
    def _generate_from_schema(self, schema: Dict, schemas: Optional[Dict] = None) -> Any:
        """Generate mock data from JSON schema"""
        if not schema:
            return None
        
        schema_type = schema.get("type")
        
        if schema.get("$ref"):
            ref_name = schema["$ref"].split("/")[-1]
            if schemas and ref_name in schemas:
                return self._generate_from_schema(schemas[ref_name], schemas)
            return {"id": self._generate_id()}
        
        if schema_type == "object":
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            result = {}
            
            for prop_name, prop_schema in properties.items():
                if prop_name in required or random.random() > self.null_probability:
                    result[prop_name] = self._generate_from_schema(prop_schema, schemas)
            
            return result
        
        if schema_type == "array":
            items = schema.get("items", {})
            min_items = schema.get("minItems", 1)
            max_items = schema.get("maxItems", 5)
            count = random.randint(min_items, max_items)
            
            return [self._generate_from_schema(items, schemas) for _ in range(count)]
        
        if schema_type == "string":
            return self._generate_string_value(schema)
        
        if schema_type == "integer" or schema_type == "number":
            return self._generate_number_value(schema)
        
        if schema_type == "boolean":
            return random.choice([True, False])
        
        if schema_type == "null":
            return None
        
        return None
    
    def _generate_string_value(self, schema: Dict) -> str:
        """Generate string value based on format"""
        format_type = schema.get("format", "")
        enum_values = schema.get("enum", [])
        
        if enum_values:
            return random.choice(enum_values)
        
        min_length = schema.get("minLength", 1)
        max_length = schema.get("maxLength", 100)
        length = random.randint(min_length, max_length)
        
        if format_type == "date":
            return datetime.now().strftime("%Y-%m-%d")
        elif format_type == "date-time":
            return datetime.now().isoformat()
        elif format_type == "email":
            return self._generate_email()
        elif format_type == "uri" or format_type == "url":
            return self._generate_url()
        elif format_type == "ipv4":
            return self._generate_ipv4()
        elif format_type == "uuid":
            return self._generate_uuid()
        elif format_type == "password":
            return "*" * length
        else:
            return self._generate_random_string(length)
    
    def _generate_number_value(self, schema: Dict) -> Union[int, float]:
        """Generate number value based on constraints"""
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 1000)
        multiple_of = schema.get("multipleOf", 1)
        
        value = random.uniform(minimum, maximum)
        
        if schema.get("type") == "integer":
            value = int(value)
            if multiple_of > 1:
                value = (value // multiple_of) * multiple_of
        
        return value
    
    def _generate_id(self) -> str:
        """Generate random ID"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    def _generate_email(self) -> str:
        """Generate random email"""
        username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
        domains = ["gmail.com", "outlook.com", "yahoo.com", "github.com", "example.com"]
        return f"{username}@{random.choice(domains)}"
    
    def _generate_url(self) -> str:
        """Generate random URL"""
        paths = ["api", "users", "products", "orders", "data", "items"]
        return f"https://example.com/{random.choice(paths)}/{self._generate_id()}"
    
    def _generate_ipv4(self) -> str:
        """Generate random IPv4 address"""
        return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
    
    def _generate_uuid(self) -> str:
        """Generate UUID-like string"""
        return f"{self._generate_id()}-{self._generate_id()}-{self._generate_id()}-{self._generate_id()[:12]}"
    
    def _generate_random_string(self, length: int) -> str:
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits + " ", k=length))
    
    def generate_faker_data(self, data_type: str, **kwargs) -> Any:
        """Generate data using Faker library patterns (without Faker dependency)"""
        generators = {
            "name": lambda: self._generate_name(),
            "first_name": lambda: self._generate_first_name(),
            "last_name": lambda: self._generate_last_name(),
            "email": lambda: self._generate_email(),
            "phone": lambda: self._generate_phone(),
            "address": lambda: self._generate_address(),
            "city": lambda: self._generate_city(),
            "country": lambda: self._generate_country(),
            "company": lambda: self._generate_company(),
            "job": lambda: self._generate_job(),
            "date": lambda: self._generate_date(),
            "datetime": lambda: self._generate_datetime(),
            "url": lambda: self._generate_url(),
            "ipv4": lambda: self._generate_ipv4(),
            "uuid": lambda: self._generate_uuid(),
            "text": lambda: self._generate_text(kwargs.get("max_chars", 200)),
            "sentence": lambda: self._generate_sentence(),
            "paragraph": lambda: self._generate_paragraph(),
        }
        
        return generators.get(data_type, generators["text"])()
    
    def _generate_name(self) -> str:
        """Generate full name"""
        return f"{self._generate_first_name()} {self._generate_last_name()}"
    
    def _generate_first_name(self) -> str:
        """Generate first name"""
        names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eric", "Fiona", 
                 "George", "Helen", "Ivan", "Julia", "Kevin", "Linda", "Michael", "Nancy"]
        return random.choice(names)
    
    def _generate_last_name(self) -> str:
        """Generate last name"""
        names = ["Smith", "Doe", "Brown", "Jones", "Wilson", "Taylor", "Anderson", 
                 "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia"]
        return random.choice(names)
    
    def _generate_phone(self) -> str:
        """Generate phone number"""
        return f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
    
    def _generate_address(self) -> str:
        """Generate address"""
        street_num = random.randint(100, 9999)
        streets = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St"]
        return f"{street_num} {random.choice(streets)}"
    
    def _generate_city(self) -> str:
        """Generate city name"""
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
                  "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
        return random.choice(cities)
    
    def _generate_country(self) -> str:
        """Generate country name"""
        countries = ["United States", "Canada", "United Kingdom", "Germany", "France",
                     "Japan", "Australia", "Brazil", "China", "India"]
        return random.choice(countries)
    
    def _generate_company(self) -> str:
        """Generate company name"""
        prefixes = ["Tech", "Global", "United", "Advanced", "Smart", "Digital"]
        suffixes = ["Corp", "Inc", "Solutions", "Systems", "Labs", "Group"]
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"
    
    def _generate_job(self) -> str:
        """Generate job title"""
        titles = ["Developer", "Manager", "Engineer", "Designer", "Analyst", "Director"]
        return f"{random.choice(titles)}"
    
    def _generate_date(self) -> str:
        """Generate random date"""
        days_offset = random.randint(0, 365)
        date = datetime.now() - timedelta(days=days_offset)
        return date.strftime("%Y-%m-%d")
    
    def _generate_datetime(self) -> str:
        """Generate random datetime"""
        days_offset = random.randint(0, 365)
        date = datetime.now() - timedelta(days=days_offset)
        return date.isoformat()
    
    def _generate_text(self, max_chars: int) -> str:
        """Generate random text"""
        return self._generate_paragraph(max_chars)
    
    def _generate_sentence(self) -> str:
        """Generate random sentence"""
        words = ["The", "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
                 "This", "is", "sample", "text", "for", "testing", "purposes"]
        return ' '.join(random.choices(words, k=random.randint(5, 12))).capitalize() + '.'
    
    def _generate_paragraph(self, max_chars: int = 200) -> str:
        """Generate random paragraph"""
        sentences = [self._generate_sentence() for _ in range(random.randint(3, 6))]
        text = ' '.join(sentences)
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        return text
    
    def generate_test_data(self, count: int, schema: Dict) -> List[Dict]:
        """Generate multiple test data records"""
        return [self._generate_from_schema(schema) for _ in range(count)]
    
    def save_to_file(self, data: Any, filepath: Union[str, Path]):
        """Save generated data to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved generated data to: {filepath}")
