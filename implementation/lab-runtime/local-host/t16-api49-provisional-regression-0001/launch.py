"""Externally pin the selected T16 provisional worker before executing its bytes."""

import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RUNNER = HERE / 'run_bucket.py'
RUNNER_SHA = 'a8bc485fa0fa411eec93042935eb5f38a53774ab0f169ecb0ccc70751f3fdef9'

raw = RUNNER.read_bytes()
if hashlib.sha256(raw).hexdigest() != RUNNER_SHA:
    raise ValueError('T16 runner byte selection differs')
if len(sys.argv) != 3 or sys.argv[1] != '--bucket':
    raise ValueError('select one whole-class bucket')
namespace = {'__name__': '__main__', '__file__': str(RUNNER),
             '__selected_runner_sha__': RUNNER_SHA}
exec(compile(raw, str(RUNNER), 'exec', dont_inherit=True), namespace)
