"""Cold exact selection of the v11 invocation-scope margin helper."""
from __future__ import annotations

import importlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = 'api-integration-v33-t03-one-lesson-native-v4-invocation-scope-0002'
spec = importlib.util.spec_from_file_location('t03_v11_margin', HERE / 'margin.py')
margin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(margin)
importlib.import_module(PACKAGE)
diagnostic = margin.DiagnosticMargin(PACKAGE)
try:
    result = diagnostic.public_receipt()
finally:
    diagnostic.close()
result['private_configuration_removed'] = not diagnostic.root.exists()
result['runtime_executed'] = False
result['lesson_applied'] = False
result['lesson_assessed'] = False
if not result['private_configuration_removed']:
    raise ValueError('diagnostic private configuration remained')
print(json.dumps(result,sort_keys=True))
