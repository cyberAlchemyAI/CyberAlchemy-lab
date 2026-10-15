"""Fresh selected-runtime check using the unchanged original inventory guard."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INSTALL = ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
assert Path(sys.executable) == INSTALL/'bin/python'
selection_path = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
raw = selection_path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
selected = json.loads(raw)
control_path = ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/control.py'
control_raw = control_path.read_bytes()
assert hashlib.sha256(control_raw).hexdigest() == '4e9351138e5fa27a3f0c99f72264e5fab63e00a686fcb8c63fdd558b87a84692'
spec = importlib.util.spec_from_file_location('_Root_original_strict_installation_check', control_path)
control = importlib.util.module_from_spec(spec)
exec(compile(control_raw, str(control_path), 'exec', dont_inherit=True), control.__dict__)
expected = {r['destination']: {'sha256':r['sha256'], 'size_bytes':r['size_bytes'], 'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in selected['inputs']}
expected.update(selected['wheel_members'])
expected['lib/abi/ld-linux-x86-64.so.2']['mode'] = 0o755
assert len(expected) == 1010
assert control.installed(INSTALL, expected) == 1010
assert control_path.read_bytes() == control_raw
assert selection_path.read_bytes() == raw
print(json.dumps({'result':'PASS-original-strict-selected-installation', 'selected_rows':1010, 'original_guard_changed':False, 'Lab_or_API_imported':False, 'authority_effect':'none', 'task_complete':False}, sort_keys=True))
