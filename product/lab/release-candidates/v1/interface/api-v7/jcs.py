"""Independently pinned RFC 8785 codec; artifact/wire bytes are never rewritten."""
import importlib
import sys
from pathlib import Path
import source_bridge as source

HERE=Path(__file__).resolve().parent
WHEEL=HERE/'dependencies/rfc8785-0.1.4-py3-none-any.whl'
WHEEL_SHA='520d690b448ecf0703691c76e1a34a24ddcd4fc5bc41d589cb7c58ec651bcd48'

def guard():
    source.require(WHEEL.is_file() and not WHEEL.is_symlink() and source.sha(WHEEL.read_bytes())==WHEEL_SHA,'JCS codec bytes differ')
    for name in ('rfc8785','rfc8785._impl'):
        if name in sys.modules:
            source.require(str(sys.modules[name].__file__).startswith(str(WHEEL)+'/'),'unselected JCS codec module')

guard()
sys.path.insert(0,str(WHEEL))
try:codec=importlib.import_module('rfc8785')
finally:sys.path.remove(str(WHEEL))
guard()

def dumps(value):
    guard();raw=codec.dumps(value);guard();return raw

def fingerprint(call,context):
    return source.sha(dumps({'api_version':call['schema_version'],'operation':call['operation'],
        'authenticated_principal_ref':context['principal_ref'],'authority_scope':context['authority_scope'],
        'selected_scope_refs':context['scope_refs'],'source_profile_binding':context['source_profile_binding'],
        'expected_source_cut':call['expected_source_cut'],'message':call['message']}))

def namespace(operation,key,context):
    return source.sha(dumps({'principal_ref':context['principal_ref'],'authority_scope':context['authority_scope'],
        'selected_scope_refs':context['scope_refs'],'operation':operation,'idempotency_key':key}))
