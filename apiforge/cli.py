"""
CLI Interface for APIForge
Command-line interface for all APIForge features
"""

import sys
import os
import json
import click
from pathlib import Path
from typing import Optional

from apiforge import __version__
from apiforge.config import ConfigManager
from apiforge.server import MockServer, create_test_server
from apiforge.recorder import APIRecorder
from apiforge.generator import MockGenerator
from apiforge.mock_engine import MockEngine, MockResponse, MockScenario
from apiforge.utils import ensure_dir


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    """🚀 APIForge - AI-Powered API Mocking & Testing Toolkit
    
    Create mock APIs, record real requests, and generate test data with ease.
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = ConfigManager()


@cli.command()
@click.option('--host', default='127.0.0.1', help='Server host address')
@click.option('--port', default=8080, help='Server port')
@click.option('--config', '-c', type=click.Path(), help='Configuration file path')
@click.option('--scenarios', '-s', type=click.Path(exists=True), help='Mock scenarios file')
@click.pass_context
def serve(ctx, host, port, config, scenarios):
    """🖥️  Start the mock API server"""
    config_manager = ctx.obj.get('config')
    if config:
        config_manager = ConfigManager(config)
    
    server_config = config_manager.config.to_dict()
    
    click.echo(f"\n🎯 Starting APIForge Mock Server...")
    click.echo(f"   📍 Address: http://{host}:{port}")
    click.echo(f"   ⚙️  Config: {config or 'default'}")
    click.echo(f"   📂 Scenarios: {scenarios or 'none'}\n")
    
    server = MockServer(host=host, port=port, config=server_config)
    
    if scenarios:
        click.echo(f"📦 Loading scenarios from: {scenarios}")
        server.load_mock_scenarios(scenarios)
    
    try:
        server.start(blocking=True)
    except KeyboardInterrupt:
        click.echo("\n\n👋 Shutting down server...")
        server.stop()


@cli.group()
def mock():
    """🎭 Mock endpoint management commands"""
    pass


@mock.command('add')
@click.argument('endpoint')
@click.option('--status', default=200, help='HTTP status code')
@click.option('--body', '-b', help='Response body (JSON string or file path)')
@click.option('--delay', default=0, help='Response delay in milliseconds')
@click.option('--content-type', default='application/json', help='Content-Type header')
def add_mock(endpoint, status, body, delay, content_type):
    """➕ Add a mock endpoint"""
    if body and os.path.isfile(body):
        with open(body, 'r') as f:
            body = f.read()
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
    
    response = MockResponse(
        status_code=status,
        body=body,
        delay_ms=delay,
        headers={'Content-Type': content_type}
    )
    
    click.echo(f"✅ Added mock endpoint: {endpoint}")
    click.echo(f"   Status: {status}")
    click.echo(f"   Delay: {delay}ms")


@mock.command('list')
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table')
def list_mocks(format):
    """📋 List all mock endpoints"""
    click.echo("📋 Mock Endpoints:")
    click.echo("   (Use --scenarios option in 'serve' command to load scenarios)")
    click.echo("   Endpoint                    Status  Delay")
    click.echo("   -------------------------   ------  ------")


@mock.command('generate')
@click.argument('schema_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--count', '-n', default=1, help='Number of records to generate')
def generate_mock(schema_file, output, count):
    """🎲 Generate mock data from JSON schema"""
    with open(schema_file, 'r') as f:
        schema = json.load(f)
    
    generator = MockGenerator()
    
    for i in range(count):
        data = generator._generate_from_schema(schema)
        
        if output:
            output_path = Path(output)
            if count > 1:
                output_path = output_path.parent / f"{output_path.stem}_{i+1}{output_path.suffix}"
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            click.echo(f"✅ Generated: {output_path}")
        else:
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))


@cli.group()
def record():
    """📝 API recording commands"""
    pass


@record.command('start')
@click.argument('name')
@click.option('--description', '-d', default='', help='Recording description')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
def start_recording(name, description, output):
    """▶️  Start recording API requests"""
    recorder = APIRecorder(storage_path=output or './recordings')
    recorder.start_recording(name, description)
    click.echo(f"\n🎬 Recording started: {name}")
    click.echo(f"   📂 Output: {recorder.storage_path}")
    click.echo(f"   ⏹️  Use 'apiforge record stop' to stop recording")


@record.command('stop')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
def stop_recording(output):
    """⏹️  Stop recording"""
    recorder = APIRecorder(storage_path=output or './recordings')
    recording = recorder.stop_recording()
    
    if recording:
        click.echo(f"\n✅ Recording stopped: {recording.name}")
        click.echo(f"   📊 Records: {len(recording.records)}")
    else:
        click.echo("⚠️  No active recording to stop")


@record.command('list')
@click.option('--output', '-o', type=click.Path(), help='Recordings directory')
def list_recordings(output):
    """📜 List all recordings"""
    recorder = APIRecorder(storage_path=output or './recordings')
    recordings = recorder.list_recordings()
    
    if not recordings:
        click.echo("📭 No recordings found")
        return
    
    click.echo(f"\n📜 Found {len(recordings)} recording(s):\n")
    
    for rec in recordings:
        click.echo(f"   📁 {rec['name']}")
        click.echo(f"      Records: {rec['record_count']}")
        click.echo(f"      Created: {rec['metadata'].get('created_at', 'N/A')}")
        click.echo()


@record.command('export')
@click.argument('name')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'har', 'openapi']), default='json')
def export_recording(name, output, format):
    """📤 Export recording to different formats"""
    recorder = APIRecorder()
    recording = recorder.load_recording(name)
    
    if not recording:
        click.echo(f"❌ Recording not found: {name}")
        return
    
    if format == 'json':
        data = recording.to_dict()
    elif format == 'har':
        data = recorder.export_to_har(recording)
    elif format == 'openapi':
        data = recorder.export_to_openapi_examples(recording)
    
    output_path = output or f"{name}.{format}"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    click.echo(f"✅ Exported to: {output_path}")


@cli.group()
def generate():
    """🎲 Data generation commands"""
    pass


@generate.command('from-openapi')
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def generate_from_openapi(spec_file, output):
    """📄 Generate mock data from OpenAPI specification"""
    with open(spec_file, 'r') as f:
        spec = json.load(f)
    
    generator = MockGenerator()
    mocks = generator.generate_from_openapi(spec)
    
    if output:
        generator.save_to_file(mocks, output)
        click.echo(f"✅ Generated mocks saved to: {output}")
    else:
        click.echo(json.dumps(mocks, indent=2, ensure_ascii=False))


@generate.command('test-data')
@click.argument('schema_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--count', '-n', default=10, help='Number of records')
def generate_test_data(schema_file, output, count):
    """🧪 Generate test data records"""
    with open(schema_file, 'r') as f:
        schema = json.load(f)
    
    generator = MockGenerator()
    data = generator.generate_test_data(count, schema)
    
    if output:
        generator.save_to_file(data, output)
        click.echo(f"✅ Generated {count} test records to: {output}")
    else:
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))


@generate.command('faker')
@click.argument('data_type')
@click.option('--count', '-n', default=1, help='Number of values')
def generate_faker(data_type, count):
    """🎭 Generate fake data (name, email, phone, etc.)"""
    generator = MockGenerator()
    
    valid_types = ['name', 'first_name', 'last_name', 'email', 'phone', 'address',
                   'city', 'country', 'company', 'job', 'date', 'datetime', 'url',
                   'ipv4', 'uuid', 'text', 'sentence', 'paragraph']
    
    if data_type not in valid_types:
        click.echo(f"❌ Invalid data type. Valid types: {', '.join(valid_types)}")
        return
    
    for i in range(count):
        value = generator.generate_faker_data(data_type)
        click.echo(value)


@cli.group()
def config():
    """⚙️  Configuration management"""
    pass


@config.command('init')
@click.option('--output', '-o', type=click.Path(), default='apiforge.yaml')
def init_config(output):
    """📝 Create default configuration file"""
    default_config = {
        'version': '1.0.0',
        'log_level': 'INFO',
        'server': {
            'host': '127.0.0.1',
            'port': 8080,
            'debug': False,
            'cors_enabled': True
        },
        'mock': {
            'latency_min': 0,
            'latency_max': 0,
            'error_rate': 0.0,
            'error_codes': [400, 401, 403, 404, 500]
        },
        'recorder': {
            'storage_path': './recordings',
            'format': 'json',
            'auto_save': True
        },
        'generator': {
            'template_dir': './templates',
            'null_probability': 0.1,
            'preserve_types': True
        }
    }
    
    with open(output, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    click.echo(f"✅ Configuration file created: {output}")


@config.command('show')
def show_config():
    """👁️  Show current configuration"""
    config_manager = ConfigManager()
    click.echo(json.dumps(config_manager.config.to_dict(), indent=2))


@cli.command()
@click.argument('url')
@click.option('--method', '-X', default='GET', help='HTTP method')
@click.option('--data', '-d', help='Request body (JSON string or file)')
@click.option('--header', '-H', multiple=True, help='Custom headers')
def request(url, method, data, header):
    """🌐 Make a test request to any endpoint"""
    import urllib.request
    import urllib.parse
    
    headers = {}
    for h in header:
        if ':' in h:
            key, value = h.split(':', 1)
            headers[key.strip()] = value.strip()
    
    req_data = None
    if data:
        if os.path.isfile(data):
            with open(data, 'r') as f:
                req_data = f.read().encode()
        else:
            req_data = data.encode()
        headers['Content-Type'] = headers.get('Content-Type', 'application/json')
    
    req = urllib.request.Request(url, data=req_data, method=method, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode()
            click.echo(f"\n✅ {method} {url}")
            click.echo(f"   Status: {response.status}")
            click.echo(f"   Response:\n{body}")
    except Exception as e:
        click.echo(f"\n❌ Request failed: {e}")


@cli.command()
def info():
    """ℹ️  Show APIForge information"""
    click.echo(f"""
    ╔═══════════════════════════════════════════════╗
    ║                                               ║
    ║   🚀 APIForge - AI-Powered API Toolkit       ║
    ║                                               ║
    ║   Version: {__version__}                          ║
    ║   Author:  GitHub Incubator                  ║
    ║   License: MIT                                ║
    ║                                               ║
    ╚═══════════════════════════════════════════════╝
    
    Quick Start:
    
    1️⃣  Start mock server:
        apiforge serve --port 8080
    
    2️⃣  Add mock endpoints:
        apiforge mock add /api/users --body '{"users": []}'
    
    3️⃣  Generate test data:
        apiforge generate test-data schema.json --count 10
    
    4️⃣  Record API calls:
        apiforge record start my-recording
        # ... make API calls ...
        apiforge record stop
    
    Documentation: https://github.com/gitstq/APIForge
    """)


if __name__ == '__main__':
    cli()
