"""Cold driver executable-pin causal checks without a native Session."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DRIVER = ROOT / 'implementation/lab-runtime/local-host/t03-api33-native-v4-learning-0010/run_full.py'
spec = importlib.util.spec_from_file_location('_cal_t03_v10_driver_pins', DRIVER)
selected = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selected)
if not selected.selected_executables_current():
    raise ValueError('actual selected executables differ')
names = ('API_SHA','PROFILE_SHA','PROVIDER_SHA','LIFECYCLE_SHA','MARGIN_SHA','MATERIALS_SHA')
for name in names:
    old = getattr(selected,name)
    setattr(selected,name,'0'*64)
    try:
        if selected.selected_executables_current():
            raise ValueError('mutated executable pin accepted: '+name)
    finally:
        setattr(selected,name,old)
if not selected.selected_executables_current():
    raise ValueError('restored selected executable pins failed')
print(json.dumps({'selected_executables_current':True,'causal_wrong_pin_refusals':len(names),
                  'selected_driver_sha256':selected.sha(DRIVER)},sort_keys=True))
