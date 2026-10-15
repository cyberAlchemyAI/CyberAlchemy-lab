"""Explicit O05/v2 current-native role; historical O05/v1 remains unchanged.

Only an independently selected scope and trusted private factory activate this
caller. Compatibility evidence concerns exact historical metadata event bytes,
not missing executable480, binary reproducible-build identity, or authority.
"""
import copy,datetime,hashlib,inspect,json,os,re,sys
from pathlib import Path
from .capture import capture_path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).parent
VERSION='lab-O05-build-scope/v2-candidate'
EXECUTION={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/ontology-installation-root-0001/execution-selection.json','sha256':'3b0c97b2b31363f6d344af10e2dde3281dbffb042a6746e67f0b9fe1795a3bf4'}
INPUTS={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/migration-native-role-compatibility-preparation-0002/input-selection.json','sha256':'7bd34f40555e99d7779bce8a693b8633b226b5e398a54f063c92f8a192aa9e99'}
HISTORICAL={'path':'implementation/lab-ontology/candidates/v1/migration/adapters/build-scope.json','sha256':'9f42e28db872ad237c0859d99614758e13c9016168c3c93704bb83fd3573b3ad'}
NATIVE='57416d01d3479238f9e76a967c0275f1af04466efeb130fc0125bcb94e3a3399'
OLD_NATIVE='480d421a438f712db930bb287d2ee1d5e4a0933e1336816defa28d6c284de9c3'
FACTORY_ORIGIN='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-lifecycle-recovery-adoption-0003/selected_store.py'
EXECUTOR_ORIGIN='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/ontology-native-execution-preparation-0001/native_executor.py'
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
    need(value['schema_version']=='lab-O05-native-byte-compatibility/v1-candidate'and value['authority_effect']=='none'
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

class MigrationExecutionContract:
    """Trusted bootstrap selects the new scope; public workflow data cannot."""
    def __init__(self,scope_binding,independent_sha256,store_factory):
        need(type(scope_binding)is dict and set(scope_binding)=={'path','sha256'}and scope_binding['sha256']==independent_sha256,'independently selected explicitv2 migration scope required')
        self.scope_binding=copy.deepcopy(scope_binding);self.scope=parse(bytes_for(scope_binding));self._seal=canonical(self.scope)
        self.factory=store_factory;self.guard()
    def guard(self):
        s=self.scope;closed(s,FIELDS)
        need(canonical(s)==self._seal and parse(bytes_for(self.scope_binding))==s,'selected migration scope mutated')
        need(s['schema_version']==VERSION and s['task']=='O05'and s['authority_effect']=='none'and s['actual_owner_outcome']is None,
             'explicitv2 migration scope/technical posture required')
        need(type(s['captured_at'])is str and type(s['output_root'])is str and all(type(s[k])is dict for k in('store_factory_selection_binding','technical_packet_binding','api_source_binding','api_profile_binding','compatibility_evidence_binding')),
             'migration scope remains inactive until actual current evidence/custody bindings exist')
        old=parse(bytes_for(HISTORICAL))
        need(s['predecessor_scope_binding']==HISTORICAL and s['historical_native_requirement']==old['native_executable']
             and old['native_executable']['sha256']==OLD_NATIVE,'historical480 requirement cannot be replaced')
        for name in('selection_binding','profile_binding'):
            need(s[name]==old[name],'original selected migration source/profile cannot be replaced')
        for flag in('source_execution_allowed','source_mutation_allowed','source_body_copy_allowed','private_body_export_allowed'):
            need(s[flag]is False,'source privacy/effect boundary changed')
        need(s['native_execution_selection_binding']==EXECUTION and s['input_selection_binding']==INPUTS,'unselected current-native compatibility inputs')
        input_guard();execution=parse(bytes_for(EXECUTION));role=execution['ontology_role']
        need(s['native_role']=={'sha256':NATIVE,'path':str(Path(execution['new_installation']['path'])/role['destination'])},'independently installed574 role required')
        need(type(self.factory).__name__=='StoreFactory'and Path(inspect.getsourcefile(type(self.factory)))==ROOT/FACTORY_ORIGIN
             and sys.modules[type(self.factory).__module__].StoreFactory is type(self.factory),'actual selected StoreFactory required')
        fsel=parse(bytes_for(s['store_factory_selection_binding']))
        need(fsel==self.factory.selection,'independently selected private factory descriptor differs')
        runtime=s['runtime_code_bindings'];need(type(runtime)is list and runtime and len({b['path']for b in runtime})==len(runtime),'unique explicit runtime code closure required')
        for b in runtime:bytes_for(b)
        required=[bind(HERE/n)for n in('migration.py','execution_contract.py','compatibility_probe.py','validate.py','cold_replay.py','import_guards.py','qualify.py','capture.py','private_io.py')]
        required += [bind(ROOT/FACTORY_ORIGIN),fsel['generation_module_binding'],fsel['original_store_binding'],
                     fsel['executor_class_binding']['code_binding'],fsel['boundary_class_binding']['code_binding']]
        need(all(b in runtime for b in required)and s['producer_binding']==bind(HERE/'migration.py'),'actual successor/runtime producer closure differs')
        executor=self.factory.executor
        need(type(executor).__name__=='SelectedOntologyExecutor'and Path(inspect.getsourcefile(type(executor)))==ROOT/EXECUTOR_ORIGIN
             and sys.modules[type(executor).__module__].SelectedOntologyExecutor is type(executor)
             and executor.pin==EXECUTION['sha256']and executor.raw==bytes_for(EXECUTION)
             and Path(executor.executable_path)==Path(s['native_role']['path'])and executor.executable_sha256==NATIVE,
             'actual selected574 executor capability differs')
        boundary=self.factory.boundary
        need(boundary.binding==s['technical_packet_binding']and parse(bytes_for(s['technical_packet_binding']))==boundary.packet,
             'independently selected technical packet differs')
        for name in('api_source_binding','api_profile_binding'):
            need(boundary.packet[name]==s[name],'current Source/profile technical join differs');bytes_for(s[name])
        self.factory.guard() # Includes original source, ABI1011, custody, technical boundary, real expiry.

        ev=evidence(parse(bytes_for(s['compatibility_evidence_binding'],private=True)),runtime_bindings=runtime)
        captured=utc(s['captured_at']);observed=utc(ev['captured_at'])
        need(observed<=captured<=datetime.datetime.now(datetime.timezone.utc),'current compatibility/scope observation order differs')
        output=Path(s['output_root'])
        need(not output.is_absolute()and '..'not in output.parts and output.as_posix()==s['output_root']
             and output.is_relative_to('implementation/lab-ontology/candidates/v1/migration/candidate')
             and not output.is_relative_to(Path(old['output_root']))
             and not Path(old['output_root']).is_relative_to(output),'explicit distinct successor output root required')
        return copy.deepcopy(s)
