"""
Unit tests for APIForge modules
"""

import unittest
import json
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apiforge.config import ConfigManager, GlobalConfig
from apiforge.utils import generate_id, sanitize_filename, flatten_dict, merge_dicts
from apiforge.generator import MockGenerator
from apiforge.mock_engine import MockEngine, MockResponse, MockScenario
from apiforge.recorder import APIRecorder, Recording, RequestRecord, ResponseRecord


class TestConfigManager(unittest.TestCase):
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = GlobalConfig()
        self.assertEqual(config.version, "1.0.0")
        self.assertEqual(config.server.port, 8080)
        self.assertEqual(config.mock.latency_min, 0)
    
    def test_config_to_dict(self):
        """Test configuration serialization"""
        config = GlobalConfig()
        data = config.to_dict()
        self.assertIsInstance(data, dict)
        self.assertIn("server", data)
        self.assertIn("mock", data)


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_generate_id(self):
        """Test ID generation"""
        id1 = generate_id()
        id2 = generate_id()
        self.assertNotEqual(id1, id2)
        self.assertEqual(len(id1), 8)
        
        id_with_prefix = generate_id(prefix="test_")
        self.assertTrue(id_with_prefix.startswith("test_"))
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        dirty = "test<file>name:with*special|chars"
        clean = sanitize_filename(dirty)
        self.assertNotIn("<", clean)
        self.assertNotIn(">", clean)
        self.assertNotIn("*", clean)
    
    def test_flatten_dict(self):
        """Test dictionary flattening"""
        nested = {"a": {"b": {"c": 1}}, "d": 2}
        flat = flatten_dict(nested)
        self.assertIn("a.b.c", flat)
        self.assertEqual(flat["a.b.c"], 1)
    
    def test_merge_dicts(self):
        """Test dictionary merging"""
        base = {"a": 1, "b": {"c": 2}}
        updates = {"b": {"d": 3}, "e": 4}
        merged = merge_dicts(base, updates)
        self.assertEqual(merged["a"], 1)
        self.assertEqual(merged["b"]["c"], 2)
        self.assertEqual(merged["b"]["d"], 3)
        self.assertEqual(merged["e"], 4)


class TestMockGenerator(unittest.TestCase):
    """Test mock data generator"""
    
    def setUp(self):
        self.generator = MockGenerator()
    
    def test_generate_string_schema(self):
        """Test string schema generation"""
        schema = {"type": "string", "format": "email"}
        result = self.generator._generate_from_schema(schema)
        self.assertIsInstance(result, str)
        self.assertIn("@", result)
    
    def test_generate_object_schema(self):
        """Test object schema generation"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        result = self.generator._generate_from_schema(schema)
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
    
    def test_generate_array_schema(self):
        """Test array schema generation"""
        schema = {
            "type": "array",
            "items": {"type": "string"}
        }
        result = self.generator._generate_from_schema(schema)
        self.assertIsInstance(result, list)
    
    def test_generate_faker_data(self):
        """Test faker data generation"""
        name = self.generator.generate_faker_data("name")
        self.assertIsInstance(name, str)
        self.assertIn(" ", name)
        
        email = self.generator.generate_faker_data("email")
        self.assertIsInstance(email, str)
        self.assertIn("@", email)
    
    def test_generate_from_openapi(self):
        """Test OpenAPI specification generation"""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0"},
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        result = self.generator.generate_from_openapi(spec)
        self.assertIn("endpoints", result)
        self.assertIn("GET /users", result["endpoints"])


class TestMockEngine(unittest.TestCase):
    """Test mock engine"""
    
    def setUp(self):
        self.engine = MockEngine()
    
    def test_default_response(self):
        """Test default mock response"""
        response = self.engine.generate_response("/test", {})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.body)
    
    def test_add_scenario(self):
        """Test adding mock scenario"""
        scenario = MockScenario(
            name="test_scenario",
            conditions={"method": "GET"},
            response=MockResponse(status_code=200, body={"test": True})
        )
        self.engine.add_scenario("/test", scenario)
        self.assertIn("/test", self.engine.scenarios)
    
    def test_dynamic_values(self):
        """Test dynamic value generation"""
        result = self.engine.value_generator.generate("${uuid()}")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        
        result = self.engine.value_generator.generate("${random_int(min=1, max=10)}")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 10)


class TestAPIRecorder(unittest.TestCase):
    """Test API recorder"""
    
    def setUp(self):
        self.recorder = APIRecorder(storage_path="./test_recordings")
    
    def test_start_stop_recording(self):
        """Test recording start and stop"""
        recording = self.recorder.start_recording("test_recording", "Test description")
        self.assertIsNotNone(recording)
        self.assertEqual(recording.name, "test_recording")
        
        stopped = self.recorder.stop_recording()
        self.assertIsNotNone(stopped)
        self.assertEqual(stopped.name, "test_recording")
    
    def test_record_call(self):
        """Test recording API calls"""
        self.recorder.start_recording("test")
        
        request = RequestRecord(
            method="GET",
            url="http://example.com/api/test"
        )
        response = ResponseRecord(
            status_code=200,
            body={"success": True}
        )
        
        self.recorder.record_call(request, response)
        
        recording = self.recorder.stop_recording()
        self.assertEqual(len(recording.records), 1)


if __name__ == '__main__':
    unittest.main()
