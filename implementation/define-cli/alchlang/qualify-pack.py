"""Exact byte-port witness; fixture-owned inputs, no native Lab authority."""
import base64
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root.parent / 'standalone'))
from define_core import call
spec = importlib.util.spec_from_file_location('define_pack_port', root / 'runtime/pack-port.py')
port = importlib.util.module_from_spec(spec)
spec.loader.exec_module(port)
source = json.loads(subprocess.check_output([sys.executable, '-B', str(root / 'runtime/examples/request.py'), 'user-journey']))
request = port.request(json.load(sys.stdin))
assert request == source['request'], 'actual User Journey request changed'

def invoke(operation, params):
    result = call({'api_version': 'define.api/v1', 'id': 'modular-model-qualification', 'operation': operation, 'params': params})
    assert result['outcome'] in ('prepared', 'prepared-with-gaps'), result['diagnostics']
    return result['data']

raw = json.dumps(request, ensure_ascii=False, separators=(',', ':'))
capture = invoke('capture', {'request_utf8': raw, 'inputs': source['members'], 'permit_retention': True})
prepared = invoke('prepare', {'request_utf8': raw, 'capture_utf8': capture['capture_utf8'], 'inputs': capture['inputs']})
materialized = invoke('materialize', {'package_members': prepared['package_members']})
restored = invoke('reconstruct', {'package_members': prepared['package_members']})
assert restored['package_members'] == prepared['package_members']
body = base64.b64decode(materialized['members']['definitions/000/definition.json'])
from hashlib import sha256
expected = '693045f6c86f0faa8b168d072e473bbb48f1e75cb71d440fc559c7440f147fe7'
assert sha256(body).hexdigest() == expected
print(json.dumps({'definition_sha256': expected, 'package_members': len(prepared['package_members']),
                  'reconstructed_exactly': True, 'materialized_definition_v2': True,
                  'pack_status': prepared['pack']['status'], 'authority_effect': 'none'}))
