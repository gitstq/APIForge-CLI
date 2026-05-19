"""
Mock Server for APIForge
Flask-based mock server for serving API responses
"""

import json
import time
import random
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread, Event
import socketserver
from urllib.parse import urlparse, parse_qs

from apiforge.mock_engine import MockEngine, MockResponse
from apiforge.recorder import APIRecorder, RequestRecord, ResponseRecord


logger = logging.getLogger(__name__)


class MockServerHandler(BaseHTTPRequestHandler):
    """HTTP request handler for mock server"""
    
    mock_engine: Optional[MockEngine] = None
    recorder: Optional[APIRecorder] = None
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        """Handle GET requests"""
        self._handle_request("GET")
    
    def do_POST(self):
        """Handle POST requests"""
        self._handle_request("POST")
    
    def do_PUT(self):
        """Handle PUT requests"""
        self._handle_request("PUT")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        self._handle_request("DELETE")
    
    def do_PATCH(self):
        """Handle PATCH requests"""
        self._handle_request("PATCH")
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self._send_response(200, {}, {"message": "OK"})
    
    def _handle_request(self, method: str):
        """Handle any HTTP request"""
        start_time = time.time()
        
        parsed_url = urlparse(self.path)
        endpoint = parsed_url.path
        query_params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed_url.query).items()}
        
        headers = {}
        for header, value in self.headers.items():
            headers[header] = value
        
        body = None
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                body = body.decode('utf-8')
        
        request_data = {
            "method": method,
            "path": endpoint,
            "headers": headers,
            "query": query_params,
            "body": body
        }
        
        if self.recorder:
            request_record = RequestRecord(
                method=method,
                url=f"http://{self.headers.get('Host', 'localhost')}{self.path}",
                headers=headers,
                query_params=query_params,
                body=body
            )
        
        response = self._generate_response(endpoint, request_data)
        
        if self.recorder:
            response_record = ResponseRecord(
                status_code=response.status_code,
                headers=response.headers,
                body=response.body,
                duration_ms=int((time.time() - start_time) * 1000)
            )
            self.recorder.record_call(request_record, response_record)
        
        self._send_response(response.status_code, response.headers, response.body)
    
    def _generate_response(self, endpoint: str, request_data: Dict) -> MockResponse:
        """Generate mock response"""
        if self.mock_engine:
            return self.mock_engine.generate_response(endpoint, request_data)
        
        return MockResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"message": "Mock response", "endpoint": endpoint}
        )
    
    def _send_response(self, status_code: int, headers: Dict, body: Any):
        """Send HTTP response"""
        self.send_response(status_code)
        
        for key, value in headers.items():
            self.send_header(key, value)
        
        if "Content-Type" not in headers:
            self.send_header("Content-Type", "application/json")
        
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        
        self.end_headers()
        
        if body is not None:
            if isinstance(body, (dict, list)):
                body_str = json.dumps(body, ensure_ascii=False)
            else:
                body_str = str(body)
            
            body_bytes = body_str.encode('utf-8')
            self.wfile.write(body_bytes)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Threaded HTTP server for handling concurrent requests"""
    allow_reuse_address = True
    daemon_threads = True


class MockServer:
    """Mock API server"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8080, config: Optional[Dict] = None):
        self.host = host
        self.port = port
        self.config = config or {}
        self.server: Optional[ThreadedHTTPServer] = None
        self.thread: Optional[Thread] = None
        self.stop_event = Event()
        
        self.mock_engine = MockEngine(self.config)
        self.recorder = APIRecorder(
            storage_path=self.config.get("recorder", {}).get("storage_path", "./recordings"),
            auto_save=self.config.get("recorder", {}).get("auto_save", True)
        )
        
        MockServerHandler.mock_engine = self.mock_engine
        MockServerHandler.recorder = self.recorder
    
    def add_mock_endpoint(self, path: str, response: MockResponse):
        """Add a mock endpoint"""
        self.mock_engine.set_fallback_response(path, response)
    
    def load_mock_scenarios(self, filepath: Union[str, Path]):
        """Load mock scenarios from file"""
        self.mock_engine.load_scenarios_from_file(filepath)
    
    def start(self, blocking: bool = True):
        """Start the mock server"""
        try:
            self.server = ThreadedHTTPServer((self.host, self.port), MockServerHandler)
            MockServerHandler.mock_engine = self.mock_engine
            MockServerHandler.recorder = self.recorder
            
            logger.info(f"Mock server starting on {self.host}:{self.port}")
            print(f"🚀 APIForge Mock Server running at http://{self.host}:{self.port}")
            print(f"📝 Recording requests: {self.config.get('recorder', {}).get('auto_save', True)}")
            print(f"⏹️  Press Ctrl+C to stop")
            
            if blocking:
                self.server.serve_forever()
            else:
                self.thread = Thread(target=self.server.serve_forever, daemon=True)
                self.thread.start()
        
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise
    
    def stop(self):
        """Stop the mock server"""
        if self.server:
            logger.info("Stopping mock server...")
            self.server.shutdown()
            self.server.server_close()
            print("\n✅ Mock server stopped")
    
    def get_url(self) -> str:
        """Get server URL"""
        return f"http://{self.host}:{self.port}"
    
    def is_running(self) -> bool:
        """Check if server is running"""
        return self.server is not None and self.thread is not None and self.thread.is_alive()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            "host": self.host,
            "port": self.port,
            "running": self.is_running(),
            "mock_engine": self.mock_engine.get_stats(),
            "recorder": self.recorder.get_stats()
        }


def create_test_server(port: int = 8080) -> MockServer:
    """Create a test mock server with default endpoints"""
    server = MockServer(port=port)
    
    server.add_mock_endpoint("/api/users", MockResponse(
        status_code=200,
        body={
            "users": [
                {"id": "1", "name": "John Doe", "email": "john@example.com"},
                {"id": "2", "name": "Jane Smith", "email": "jane@example.com"}
            ],
            "total": 2
        }
    ))
    
    server.add_mock_endpoint("/api/products", MockResponse(
        status_code=200,
        body={
            "products": [
                {"id": "1", "name": "Product A", "price": 29.99},
                {"id": "2", "name": "Product B", "price": 49.99}
            ]
        }
    ))
    
    server.add_mock_endpoint("/api/health", MockResponse(
        status_code=200,
        body={"status": "healthy", "timestamp": datetime.now().isoformat()}
    ))
    
    return server
