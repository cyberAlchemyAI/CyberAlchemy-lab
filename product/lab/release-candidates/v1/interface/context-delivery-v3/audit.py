"""Independently bind the new carrier delivery to the retained full-plan proof."""
import argparse,hashlib,json,os
from pathlib import Path
from datetime import datetime,timezone
from jsonschema import Draft202012Validator,FormatChecker
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
PARENT=ROOT/'product/lab/release-candidates/v1/interface/mapped-context-v5/receipts/R03-0013.json'
PARENT_PIN='7d695e84acbbd21b847a1024f757e5c48a38d173c37275746895b1a39e3237b5'
MAPPED=HERE.parent/'mapped-context-v6'
MAPPED_PIN='a69fc59bf255a59d12e194e20d72419267782653addab2be5e1ad682d6e861b2'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
def require(v,message):
    if not v:raise ValueError(message)
def load(p):return json.loads(p.read_bytes())
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def emit(p,v):
    require(p.parent==HERE/'receipts','audit output escaped');p.parent.mkdir(exist_ok=True)
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(v))

def audit(source_pin,package_pin,audit_pin):
    files={};count=0
    def add(row):
        nonlocal count
        p=ROOT/row['path'];require(p.resolve().is_relative_to(ROOT) and not p.is_symlink(),'unsafe original source')
        require(sha(p.read_bytes())==row['sha256'],'original bytes differ: '+row['path'])
        require(row['path'] not in files or files[row['path']]==row,'conflicting original binding')
        files[row['path']]=row;count+=1
    ap=HERE/'audit-source-manifest.json';require(sha(ap.read_bytes())==audit_pin,'audit pin differs')
    for row in load(ap)['files']:add(row)
    add(binding(ap));require(sha(PARENT.read_bytes())==PARENT_PIN,'predecessor differs')
    parent=load(PARENT)
    for row in parent['files']:add(row)
    add(binding(PARENT))
    require(len(parent['supported_operations'])==7 and len(parent['remaining_operations'])==27,'original API scope narrowed')
    sp=HERE/'source-manifest.json';pp=HERE/'packages/0001/manifest.json'
    require(sha(sp.read_bytes())==source_pin and sha(pp.read_bytes())==package_pin,'selected delivery differs')
    for root in [HERE,MAPPED,HERE.parent/'context-delivery-v1',HERE.parent/'context-delivery-v2']:
        for p in sorted(root.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.name in ['audit-result.json','audit.stdout','audit.stderr','audit-tool-terminal.json','R03-0014.json']:continue
            add(binding(p))
    for p in [sp,MAPPED/'source-manifest.json']:
        for row in load(p)['files']:add(row)
    for p in [pp,MAPPED/'packages/0001/manifest.json']:
        m=load(p)
        for row in m['files']:add(row)
        expected={r['path'] for r in m['files']}|{binding(p)['path']}
        actual={q.relative_to(ROOT).as_posix() for q in p.parent.rglob('*') if q.is_file()}
        require(expected==actual,'derived package file closure differs')
    require(sha((MAPPED/'packages/0001/manifest.json').read_bytes())==MAPPED_PIN,'native mapping package differs')
    suites=[]
    for root,tests in [(MAPPED,20),(HERE,38)]:
        checks=load(root/'receipts/checks.json');build=load(root/'packages/0001/build-result.json')
        require(checks['result']==build['result']=='PASS' and checks['tests_run']==tests and checks['errors']==checks['failures']==0,'actual selected suite failed')
        require(checks['package_sha256']==sha((root/'packages/0001/manifest.json').read_bytes()) and checks['source_sha256']==sha((root/'source-manifest.json').read_bytes()),'checks select other bytes')
        for n in ['build-tool-terminal.json','checks-tool-terminal.json']:
            t=load(root/'receipts'/n);require(t['terminal_observed'] is True and t['exit_code']==0,'actual producer terminal absent')
        suites.append({'suite':root.name,'test_count':tests,'result':'PASS'})
    old=load(HERE.parent/'context-delivery-v2/receipts/checks.json')
    require(old['result']=='FAIL' and old['failures']==2 and old['errors']==10,'failed observations not preserved')
    index=load(HERE/'packages/0001/artifact-index.json');require(len(index)==30,'actual carrier count differs')
    kinds={}
    for row in index:
        add(row['original_binding']);raw=(ROOT/row['original_binding']['path']).read_bytes();body=json.loads(raw);ref=row['artifact']
        require(sha(raw)==ref['byte_sha256'] and body['node_id']==ref['identity_ref'],'carrier reference differs from exact output bytes')
        kind=body['kind'];version='v2' if kind=='ontology-node' else 'v1';schema=ROOT/'authority/artifact-types'/kind/version/'schema.json'
        add(binding(schema));Draft202012Validator(load(schema),format_checker=FormatChecker()).validate(body)
        require(ref['carrier_ref']=='cal.artifact-type.'+kind+'/'+version and body['authority_effect']=='none','carrier posture differs')
        kinds[kind]=kinds.get(kind,0)+1
    require(kinds=={'ontology-node':15,'ontology-edge':10,'ontology':1,'ontology-cut':1,'ontology-view':1,'context-request':1,'context-view':1},'carrier kind closure differs')
    delivery=load(HERE/'packages/0001/delivery.json');provenance=load(HERE/'packages/0001/delivery-provenance.json')
    require(delivery['posture']=='ready' and delivery['scope_enforced'] is True and len(delivery['included_refs'])==25,'historical delivery incomplete')
    require(provenance['verified_original_binding']['sha256']==sha((HERE/'packages/0001/delivery.json').read_bytes()),'delivery provenance differs')
    value={k:v for k,v in parent.items() if k not in ['files','checks','recorded_at','claim_ceiling']}
    value.update(schema_version='lab-R03-actual-context-ontology-delivery-proof/v1-candidate',result='PASS',task='R03',task_complete=False,
        parent_binding=binding(PARENT),selected_mapped_projection_root=MAPPED.relative_to(ROOT).as_posix(),
        selected_mapped_projection_source_binding=binding(MAPPED/'source-manifest.json'),selected_mapped_projection_package_binding=binding(MAPPED/'packages/0001/manifest.json'),
        selected_delivery_root=HERE.relative_to(ROOT).as_posix(),selected_delivery_source_binding=binding(sp),selected_delivery_package_binding=binding(pp),
        context_or_ontology_views_generated=True,generated_artifact_carriers=30,generated_carrier_counts=kinds,
        real_nonce_transport_authentication_verified=True,independent_current_host_permission_verified=True,
        recorded_delivery_expires_at=delivery['expires_at'],recorded_delivery_is_later_session_authority=False,
        protocol_object_isolation_verified=True,view_delivery_tests=38,new_mapped_projection_tests=20,
        active_Agent_Sessions_created=0,public_Session_API_calls_executed=0,session_API_operations_added=0,context_API_operations_added=0,
        authority_effect='none',actual_owner_outcome=None,human_pilot_outcome=None,goal_complete=False,
        checks=parent['checks']+suites+[{'suite':'actual-carrier-source-and-original-plan-byte-closure','byte_binding_checks':count,'result':'PASS'}],
        observed_checks=parent['observed_checks']+58+count,files=sorted(files.values(),key=lambda r:r['path']),
        claim_ceiling='Thirty actual schema-valid derived carriers from the retained signed participation cut and native rich-profile replay, with exact global Typed Relation projections, separate represented/representation Definitions, real one-use host authentication and independently current permission at recorded generation. Query and returned delivery snapshots do not alias trusted source state. Failed parent runs are retained. Delivery is historical, expires, and cannot confer later Agent or action authority. Seven public APIs remain implemented; all remaining 27 API handlers, classified ephemeral Session resources, human pilot, final package and exact R08 owner checkpoint remain obligations.',
        recorded_at=datetime.now(timezone.utc).isoformat())
    emit(HERE/'receipts/audit-result.json',{'result':'PASS','files':len(files),'original_byte_binding_checks':count,'authority_effect':'none','actual_owner_outcome':None})
    emit(HERE/'receipts/R03-0014.json',value)
    print(json.dumps({'result':'PASS','receipt':binding(HERE/'receipts/R03-0014.json'),'files':len(files),'byte_binding_checks':count,'task_complete':False}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);p.add_argument('--package-sha256',required=True);p.add_argument('--audit-sha256',required=True);a=p.parse_args();audit(a.source_sha256,a.package_sha256,a.audit_sha256)
