"""
API Recorder for APIForge
Records and replays API requests/responses for testing and mocking
"""

import os
import json
import time
import gzip
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict
import logging
import re


logger = logging.getLogger(__name__)


@dataclass
class RequestRecord:
    """API request record"""
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: int = 0


@dataclass
class ResponseRecord:
    """API response record"""
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: int = 0


@dataclass
class APICallRecord:
    """Complete API call record with request and response"""
    id: str
    request: RequestRecord
    response: ResponseRecord
    matched: bool = False
    match_score: float = 0.0


class Recording:
    """Collection of API call records"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.records: List[APICallRecord] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "total_requests": 0,
            "unique_endpoints": set()
        }
    
    def add_record(self, record: APICallRecord):
        """Add a record to the recording"""
        self.records.append(record)
        self.metadata["total_requests"] += 1
        self.metadata["unique_endpoints"].add(record.request.url)
    
    def to_dict(self) -> Dict:
        """Convert recording to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "metadata": {
                **self.metadata,
                "unique_endpoints": list(self.metadata["unique_endpoints"])
            },
            "records": [asdict(r) for r in self.records]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Recording":
        """Create recording from dictionary"""
        recording = cls(data.get("name", ""), data.get("description", ""))
        recording.metadata = data.get("metadata", {})
        
        for record_data in data.get("records", []):
            request_data = record_data.get("request", {})
            response_data = record_data.get("response", {})
            
            request = RequestRecord(
                method=request_data.get("method", "GET"),
                url=request_data.get("url", ""),
                headers=request_data.get("headers", {}),
                query_params=request_data.get("query_params", {}),
                body=request_data.get("body"),
                timestamp=request_data.get("timestamp", ""),
                duration_ms=request_data.get("duration_ms", 0)
            )
            
            response = ResponseRecord(
                status_code=response_data.get("status_code", 200),
                headers=response_data.get("headers", {}),
                body=response_data.get("body"),
                timestamp=response_data.get("timestamp", ""),
                duration_ms=response_data.get("duration_ms", 0)
            )
            
            record = APICallRecord(
                id=record_data.get("id", ""),
                request=request,
                response=response,
                matched=record_data.get("matched", False),
                match_score=record_data.get("match_score", 0.0)
            )
            recording.records.append(record)
        
        return recording


class APIRecorder:
    """Records API requests and responses for later replay"""
    
    def __init__(self, storage_path: str = "./recordings", auto_save: bool = True):
        self.storage_path = Path(storage_path)
        self.auto_save = auto_save
        self.current_recording: Optional[Recording] = None
        self.recordings: Dict[str, Recording] = {}
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """Ensure storage directory exists"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def start_recording(self, name: str, description: str = "") -> Recording:
        """Start a new recording session"""
        self.current_recording = Recording(name, description)
        logger.info(f"Started recording: {name}")
        return self.current_recording
    
    def stop_recording(self) -> Optional[Recording]:
        """Stop the current recording session"""
        if self.current_recording:
            recording = self.current_recording
            self.recordings[recording.name] = recording
            
            if self.auto_save:
                self.save_recording(recording)
            
            logger.info(f"Stopped recording: {recording.name} ({len(recording.records)} records)")
            self.current_recording = None
            return recording
        return None
    
    def record_call(self, request: RequestRecord, response: ResponseRecord):
        """Record an API call"""
        if not self.current_recording:
            logger.warning("No active recording session")
            return
        
        record_id = self._generate_record_id(request)
        record = APICallRecord(
            id=record_id,
            request=request,
            response=response
        )
        self.current_recording.add_record(record)
    
    def _generate_record_id(self, request: RequestRecord) -> str:
        """Generate unique ID for a request record"""
        content = f"{request.method}:{request.url}:{request.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def save_recording(self, recording: Optional[Recording] = None, filepath: Optional[Path] = None):
        """Save recording to file"""
        recording = recording or self.current_recording
        if not recording:
            return
        
        filepath = filepath or (self.storage_path / f"{self._sanitize_filename(recording.name)}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(recording.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved recording to: {filepath}")
    
    def load_recording(self, name_or_path: Union[str, Path]) -> Optional[Recording]:
        """Load recording from file"""
        if not str(name_or_path).endswith('.json'):
            name_or_path = self.storage_path / f"{self._sanitize_filename(name_or_path)}.json"
        
        name_or_path = Path(name_or_path)
        
        if not name_or_path.exists():
            logger.error(f"Recording file not found: {name_or_path}")
            return None
        
        with open(name_or_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        recording = Recording.from_dict(data)
        self.recordings[recording.name] = recording
        return recording
    
    def list_recordings(self) -> List[Dict[str, Any]]:
        """List all saved recordings"""
        recordings = []
        
        for filepath in self.storage_path.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                recordings.append({
                    "name": data.get("name", filepath.stem),
                    "description": data.get("description", ""),
                    "file": str(filepath),
                    "metadata": data.get("metadata", {}),
                    "record_count": len(data.get("records", []))
                })
            except Exception as e:
                logger.warning(f"Failed to load recording {filepath}: {e}")
        
        return sorted(recordings, key=lambda x: x["metadata"].get("created_at", ""), reverse=True)
    
    def delete_recording(self, name: str) -> bool:
        """Delete a recording"""
        filepath = self.storage_path / f"{self._sanitize_filename(name)}.json"
        
        if filepath.exists():
            filepath.unlink()
            if name in self.recordings:
                del self.recordings[name]
            logger.info(f"Deleted recording: {name}")
            return True
        
        return False
    
    def find_matching_record(self, request: RequestRecord, recording: Optional[Recording] = None) -> Optional[APICallRecord]:
        """Find a matching record in recording for given request"""
        recording = recording or self.current_recording
        if not recording:
            return None
        
        best_match = None
        best_score = 0.0
        
        for record in recording.records:
            score = self._calculate_match_score(request, record.request)
            
            if score > best_score:
                best_score = score
                best_match = record
        
        if best_match and best_score > 0.5:
            return best_match
        
        return None
    
    def _calculate_match_score(self, req1: RequestRecord, req2: RequestRecord) -> float:
        """Calculate match score between two requests"""
        score = 0.0
        total_weight = 0.0
        
        weights = {
            "method": 1.5,
            "url": 2.0,
            "headers": 1.0,
            "query_params": 1.0,
            "body": 1.5
        }
        
        if req1.method == req2.method:
            score += weights["method"]
        total_weight += weights["method"]
        
        if req1.url == req2.url:
            score += weights["url"]
        total_weight += weights["url"]
        
        header_match = len(set(req1.headers.items()) & set(req2.headers.items())) / max(len(req1.headers), 1)
        score += header_match * weights["headers"]
        total_weight += weights["headers"]
        
        query_match = len(set(req1.query_params.items()) & set(req2.query_params.items())) / max(len(req1.query_params), 1)
        score += query_match * weights["query_params"]
        total_weight += weights["query_params"]
        
        if req1.body == req2.body:
            score += weights["body"]
        total_weight += weights["body"]
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize recording name for use as filename"""
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = re.sub(r'[\x00-\x1f]', '', name)
        return name.strip() or "recording"
    
    def export_to_har(self, recording: Optional[Recording] = None) -> Dict:
        """Export recording to HAR format"""
        recording = recording or self.current_recording
        if not recording:
            return {}
        
        har_entries = []
        for record in recording.records:
            entry = {
                "startedDateTime": record.request.timestamp,
                "time": record.response.duration_ms,
                "request": {
                    "method": record.request.method,
                    "url": record.request.url,
                    "httpVersion": "HTTP/1.1",
                    "headers": [{"name": k, "value": v} for k, v in record.request.headers.items()],
                    "queryString": [{"name": k, "value": v} for k, v in record.request.query_params.items()],
                    "bodySize": len(str(record.request.body)) if record.request.body else 0
                },
                "response": {
                    "status": record.response.status_code,
                    "statusText": "",
                    "httpVersion": "HTTP/1.1",
                    "headers": [{"name": k, "value": v} for k, v in record.response.headers.items()],
                    "content": {
                        "size": len(str(record.response.body)) if record.response.body else 0,
                        "mimeType": record.response.headers.get("Content-Type", "application/json"),
                        "text": str(record.response.body) if record.response.body else ""
                    },
                    "bodySize": len(str(record.response.body)) if record.response.body else 0
                }
            }
            har_entries.append(entry)
        
        return {
            "log": {
                "version": "1.2",
                "creator": {
                    "name": "APIForge",
                    "version": "1.0.0"
                },
                "entries": har_entries
            }
        }
    
    def export_to_openapi_examples(self, recording: Optional[Recording] = None) -> Dict:
        """Export recording to OpenAPI examples format"""
        recording = recording or self.current_recording
        if not recording:
            return {}
        
        endpoints = defaultdict(lambda: {"get": {}, "post": {}, "put": {}, "delete": {}, "patch": {}})
        
        for record in recording.records:
            method = record.request.method.lower()
            if method not in endpoints[record.request.url]:
                endpoints[record.request.url][method] = {
                    "request": {
                        "headers": record.request.headers,
                        "params": record.request.query_params,
                        "body": record.request.body
                    },
                    "response": {
                        "status": record.response.status_code,
                        "body": record.response.body
                    }
                }
        
        return dict(endpoints)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get recorder statistics"""
        total_records = sum(len(r.records) for r in self.recordings.values())
        unique_urls = set()
        
        for recording in self.recordings.values():
            for record in recording.records:
                unique_urls.add(record.request.url)
        
        return {
            "total_recordings": len(self.recordings),
            "total_records": total_records,
            "unique_endpoints": len(unique_urls),
            "storage_path": str(self.storage_path),
            "current_recording": self.current_recording.name if self.current_recording else None
        }
