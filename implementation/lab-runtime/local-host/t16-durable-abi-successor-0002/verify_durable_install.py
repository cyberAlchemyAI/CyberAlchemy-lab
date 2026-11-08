"""Read-only exact durable ABI closure verification after the API69 focus."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import stat
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
INSTALL = Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001')
sys.path.insert(0, str(ROOT / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001'))
deps = importlib.import_module('closure_hardened_0003')
selection_path = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
selection, _ = deps.load_selection(selection_path, '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835')
expected = deps.verify_installed(INSTALL, selection)
receipt = json.loads((INSTALL / 'installation.json').read_bytes())
st = INSTALL.stat()
identity = [st.st_dev, st.st_ino, st.st_uid, stat.S_IMODE(st.st_mode)]
assert len(expected) == 1010
assert identity == receipt['identity']
assert not list(INSTALL.rglob('*.pyc'))
assert not list(INSTALL.rglob('__pycache__'))
print(json.dumps({'result': 'PASS', 'verified_payload_files': len(expected),
                  'installation': str(INSTALL), 'identity': identity,
                  'receipt_sha256': hashlib.sha256((INSTALL / 'installation.json').read_bytes()).hexdigest(),
                  'bytecode_files': 0, 'bytecode_directories': 0,
                  'authority_effect': 'none'}, sort_keys=True))
