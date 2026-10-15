"""Own pure-control result capture only; never load native/API/Source modules."""
import json,os,runpy,sys
from pathlib import Path
HERE=Path(__file__).absolute().parent
result=runpy.run_path(str(HERE/'controls.py'),run_name='_owned_guard_composition_controls')['main']()
assert 'ctypes'not in sys.modules
result['ctypes_imported']=False
with(HERE/'controls-result.json').open('x')as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps(result,sort_keys=True))
