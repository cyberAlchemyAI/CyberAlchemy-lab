"""Explicit827 bounded probe evidence; historical full migration scopes unchanged.

Only an independently selected scope and trusted private factory activate this
caller. Compatibility evidence concerns exact historical metadata event bytes,
not missing executable480, binary reproducible-build identity, or authority.
"""
import copy,datetime,hashlib,inspect,json,os,re,sys
from pathlib import Path
from .capture import capture_path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).parent
VERSION='lab-O05-827-bounded-probe/v1-candidate'
EXECUTION={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/ontology-installation-root-0002/execution-selection.json','sha256':'3b67921318a8d9153f798c91d954e015bda51846608ded31cb6c8cc189806c10'}
INPUTS={'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-remaining-qualification-preparation-0001/migration827/input-selection.json', 'sha256': '3a112182f931f3ebf23a5ba81da53a994669de8e713aa79ee49ae49297f69870'}
HISTORICAL={'path':'implementation/lab-ontology/candidates/v1/migration/adapters/build-scope.json','sha256':'9f42e28db872ad237c0859d99614758e13c9016168c3c93704bb83fd3573b3ad'}
NATIVE='82713671f1c1271f92b7ae675ccee531c0ee972828e25899c0c19e64015025f6'
OLD_NATIVE='480d421a438f712db930bb287d2ee1d5e4a0933e1336816defa28d6c284de9c3'
FACTORY_ORIGIN='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-store-guard-composition-preparation-0001/selected_store.py'
EXECUTOR_ORIGIN='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/ontology-native-execution-preparation-0002/native_executor.py'
FIELDS=set('schema_version task authority_effect actual_owner_outcome predecessor_scope_binding historical_native_requirement selection_binding profile_binding source_execution_allowed source_mutation_allowed source_body_copy_allowed private_body_export_allowed captured_at capture_meaning output_root native_role native_execution_selection_binding input_selection_binding producer_binding runtime_code_bindings store_factory_selection_binding technical_packet_binding api_source_binding api_profile_binding compatibility_evidence_binding'.split())

def need(value,message):
    if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def parse(raw):
    def pairs(rows):
        d={}
        for k,v in rows:need(k not in d,'duplicate contract key');d[k]=v
        return d
    def bad(_):raise ValueError('nonfinite contract value')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)
def closed(v,fields):need(type(v)is dict and set(v)==set(fields),'closed migration execution contract required')
def bytes_for(b,*,private=False):
    closed(b,{'path','sha256'});p=Path(b['path'])
    need(type(b['path'])is str and p.as_posix()==b['path'] and '..'not in p.parts and '\\'not in b['path']
         and re.fullmatch('[0-9a-f]{64}',b['sha256']),'canonical exact binding required')
    need(p.is_absolute()==private,'explicit private evidence or relative public source binding required')
    p=p if private else ROOT/p
    need(not private or not p.is_relative_to(ROOT),'private evidence must remain outside repository')
    raw=capture_path(p,expected_sha256=b['sha256'],maximum=32*1024*1024,required_uid=os.getuid()if private else None)
    if private:need((p.stat().st_mode&0o777)==0o600,'private selected evidence must be600')
    return raw
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(capture_path(p,maximum=32*1024*1024))}
def utc(value):
    d=datetime.datetime.fromisoformat(value)
    need(d.utcoffset()==datetime.timedelta(0),'pinned UTC observation required');return d

def input_guard():
    value=parse(bytes_for(INPUTS))
    need(value['historical_full_proof_status']=='REFUSED'and value['historical_missing_inputs']==25
         and value['binary_source_rebuild_identity_claimed']is False,'historical proof ceiling changed')
    for b in value['inputs']:
        raw=bytes_for({k:b[k]for k in('path','sha256')});need(len(raw)==b['size_bytes'],'selected public input size differs')
    return value

def evidence(value,*,runtime_bindings):
    """Derive compatibility from exact raw child streams and event byte maps."""
    closed(value,{'schema_version','authority_effect','actual_owner_outcome','execution_selection_binding','historical_scope_binding',
                  'input_selection_binding','probe_module_binding','captured_at','historical_archive_binding','event_bytes','observations'})
    need(value['schema_version']=='lab-O05-native-byte-compatibility/v2-candidate'and value['authority_effect']=='none'
         and value['actual_owner_outcome']is None,'compatibility cannot confer authority')
    need(value['execution_selection_binding']==EXECUTION and value['historical_scope_binding']==HISTORICAL
         and value['input_selection_binding']==INPUTS,'compatibility input/role selection differs')
    need(value['probe_module_binding']==bind(HERE/'compatibility_probe.py')
         and value['probe_module_binding']in runtime_bindings,'actual selected compatibility producer differs')
    archive_binding=next({k:r[k]for k in('path','sha256')}for r in parse(bytes_for(INPUTS))['inputs']
        if r['path']=='implementation/lab-ontology/candidates/v1/migration/candidate/0001/native.snapshot')
    need(value['historical_archive_binding']==archive_binding,'unselected historical native metadata archive')
    archive=parse(bytes_for(archive_binding))
    need(archive['native_executable_sha256']==OLD_NATIVE and archive['semantic_cursor']==archive['governance_cursor']==88,
         'historical native requirement or full cursor changed')
    import base64
    families={k:[]for k in('semantic','governance')};event_bytes={}
    for family in families:
        for i in range(1,89):
            name=f'{family}/{i:08d}-ontology-{family}:O05:{i}.json';r=archive['files'][name]
            raw=base64.b64decode(r['base64_original_bytes'],validate=True)
            need(sha(raw)==r['sha256'],'historical exact event bytes differ')
            families[family].append(parse(raw));event_bytes[name]=sha(raw)
    need(set(archive['files'])==set(event_bytes) and value['event_bytes']==event_bytes,'complete176 original event byte set required')
    rows=value['observations'];need(type(rows)is list and [r['mode']for r in rows]==['read','seal','append','read'],'complete ordered native observations required')
    for row in rows:
        closed(row,{'mode','returncode','request_binding','stdout_binding','stderr_binding','files_before','files_after'})
        need(row['returncode']==0,'native compatibility child refused')
        stdout=bytes_for(row['stdout_binding'],private=True);bytes_for(row['stderr_binding'],private=True)
        result=parse(stdout)
        if row['mode']=='seal':
            request=parse(bytes_for(row['request_binding'],private=True))
            expected=copy.deepcopy(families)
            for events in expected.values():
                for event in events:event['event_digest']='0'*64
            need(request==expected and result==families,'current native seal differs from original full typed events')
            need(row['files_before']==row['files_after']=={},'seal observation has unexpected event stores')
        elif row['mode']=='append':
            need(parse(bytes_for(row['request_binding'],private=True))==families and result=={'result':'PASS','authority_effect':'none'}
                 and row['files_before']=={} and row['files_after']==event_bytes,'current append did not preserve exact176 event bytes')
        else:
            need(row['request_binding']is None and row['files_before']==row['files_after']==event_bytes,'cold replay mutated or dropped original events')
            need(result['result']==result['checkpoint_parity']=='PASS'and result['authority_effect']=='none'
                 and result['semantic_events']==families['semantic']and result['governance_events']==families['governance'],
                 'current native full replay/cursor/parity differs')
    # Both independently loaded cuts and rich governed projections must agree.
    need(bytes_for(rows[0]['stdout_binding'],private=True)==bytes_for(rows[3]['stdout_binding'],private=True),
         'restored-original and newly appended full cold projections differ')
    utc(value['captured_at'])
    return value
