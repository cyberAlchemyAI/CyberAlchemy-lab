"""Exact installed runtime, complete real dependency guard, component controls."""
import hashlib,json,os,runpy,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
HERE=ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0002'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
sys.path[:0]=[str(INSTALL/'deps'),str(HERE)]
import composite as C
raw_files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}
started=time.time();selection={'selection':{'path':C.DEPENDENCY_SELECTION,'sha256':C.DEPENDENCY_SHA},'installation':str(INSTALL)}
count=C.dependency_guard(selection)
import capture_checks,checks
capture_checks.main('capture-evidence-0002.json')
checks.checks('focused-evidence-0002.json')
assert C.dependency_guard(selection)==count==1010
assert raw_files=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}
out=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/revision-0002/qualification-0001.json'
value={'schema_version':'lab-T06-revision-qualification/v2-candidate','result':'PASS','started_at_unix':started,'finished_at_unix':time.time(),'environment':{'interpreter':str(INSTALL/'bin/python'),'python':sys.version.split()[0],'isolated':sys.flags.isolated,'no_site':sys.flags.no_site,'no_bytecode':sys.dont_write_bytecode,'selected_loader':str(INSTALL/'lib/abi/ld-linux-x86-64.so.2')},'dependency_input_count':1010,'fresh_dependency_entry_exit':'PASS','component_files_entry_exit':raw_files,'actual_full34_construction':False,'task_complete':False,'authority_effect':'none'}
fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'wb') as s:s.write(json.dumps(value,indent=2,sort_keys=True).encode()+b'\n')
print(json.dumps({'result':'PASS','qualification':str(out)}),flush=True)
