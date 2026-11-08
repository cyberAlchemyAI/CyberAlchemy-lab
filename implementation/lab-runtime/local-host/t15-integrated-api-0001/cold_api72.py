"""Cold exact integrated API source/profile guard in the durable selected ABI."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
INSTALL = Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001')
sys.path.insert(0, str(INSTALL / 'deps'))
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v72-t15-native-resolution-0001'
SOURCE = 'add6fb7b5b33a52f3cdbfc3afe1af88ac8a8468165bc684b9872077799f88bc1'
PROFILE = '3f23e8cb7508e3dc411b6e3ded7dc730c91ad341b816f5e12548a1b7dee81df2'
sys.path.insert(0, str(API.parent))
started = time.monotonic()
guard = importlib.import_module(API.name + '.guard')
guard.verify(SOURCE)
P = importlib.import_module(API.name + '.protocol')
schemas = P.Schemas(PROFILE)
schemas.guard()
grant = importlib.import_module(API.name + '.agent_challenge_grant')
records, period = grant.source_records()
cut = grant.native_cut()
result = {'result': 'PASS-cold-source-schemas-grant',
          'source_sha256': SOURCE, 'profile_sha256': PROFILE,
          'current_contest_input_kinds': sorted(records),
          'source_cut': cut, 'source_expires_at': period['expires_at'],
          'elapsed_seconds': round(time.monotonic()-started, 3),
          'live_integrated_Session_observed': False,
          'live_integrated_Agent_challenge_observed': False,
          'full345_qualified': False, 'authority_effect': 'none'}
print(json.dumps(result, sort_keys=True))
