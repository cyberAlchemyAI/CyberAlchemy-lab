"""Bounded inert controls only; no full Source/installation guard or real packet."""
import hashlib,json,sys,types,uuid
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).resolve().parent
CAPTURE=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T35/full-learning-driver-0005/capture.py'
CAPTURE_PIN='979c76d1f974430044b7c266b09482a256bde8d03bac081c876728a2be49285c'

def run(pin):
    # Root independently selects this entry; same captured helper bytes execute
    # at their actual filename. No original runtime callback is replaced.
    raw=CAPTURE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=CAPTURE_PIN:raise ValueError('independent helper entry bytes differ')
    C=types.ModuleType('_cal_T35_input5_capture_'+uuid.uuid4().hex);C.__file__=str(CAPTURE);sys.modules[C.__name__]=C
    exec(compile(raw,str(CAPTURE),'exec'),C.__dict__)
    manifest=json.loads(C.read(HERE/'source-manifest.json',pin));by={r['path']:r for r in manifest['files']}
    own=['prepare.py','controls.py','expected-input-packet.schema.json','UNRESOLVED-EXPECTED-INPUT-PACKET.json']
    bodies={}
    for name in own:
        path=HERE/name;row=by[str(path.relative_to(ROOT))];bodies[name]=C.read(path,row['sha256'])
    controls=C.module('_cal_T35_input5_pure_controls_'+uuid.uuid4().hex,HERE/'controls.py',bodies['controls.py'])
    result=controls.check()
    for name in own:
        path=HERE/name;row=by[str(path.relative_to(ROOT))];C.require(C.read(path,row['sha256'])==bodies[name],'pure own input changed')
    C.read(HERE/'source-manifest.json',pin)
    return {'schema_version':'lab-T35-inputpreparer5-bounded-pure-qualification/v1-candidate','result':'PASS-bounded-inert-controls-only',
        'component_manifest_sha256':pin,'direct_own_input_rows':len(own),'coverage':'Four own input files entry/exit plus explicitly declared inert fixture adapter; no full inherited component/API Source/installed1010 guards.',
        'controls':result,'actual_Root_packet_or_private_config_preparation':False,'actual_API_import':False,'actual_native_lease_or_Runtime':False,
        'Source_API_selector_mutation':False,'empirical_margin_qualified':False,'authority_effect':'none','task_complete':False}

if __name__=='__main__':print(json.dumps(run(sys.argv[1]),sort_keys=True))
