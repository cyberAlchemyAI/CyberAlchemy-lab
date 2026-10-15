"""Preserve exact source, projection observations and the full original plan."""
from build import *
from datetime import datetime,timezone
PARENT=HERE.parent/'session-participation-v2/receipts/R03-0012.json'
PARENT_SHA='0fa9cb68bd8c6cc5e1a53ec9b40df4e25e2dadc1f1a14dd915b31135bb7cbf89'

def audit(pin,package_pin,audit_pin):
    require(sha((HERE/'audit-source-manifest.json').read_bytes())==audit_pin,'audit producer differs')
    for row in load(HERE/'audit-source-manifest.json')['files']:original(row)
    guard(pin);require(sha(PARENT.read_bytes())==PARENT_SHA,'exact predecessor proof differs')
    package_path=HERE/'packages/0001/manifest.json';require(sha(package_path.read_bytes())==package_pin,'exact mapped package differs')
    package=load(package_path);build_result=load(HERE/'packages/0001/build-result.json');checks=load(HERE/'receipts/checks.json')
    require(checks['result']==build_result['result']=='PASS' and checks['tests_run']==20 and checks['errors']==checks['failures']==0,'actual check scope differs')
    require(checks['source_sha256']==pin and checks['package_sha256']==package_pin,'checks belong to another source/package')
    for n in ['build-tool-terminal.json','checks-tool-terminal.json']:
        t=load(HERE/'receipts'/n);require(t['exit_code']==0 and t['terminal_observed'] is True,'actual producer terminal absent')
    require(build_result['node_count']==15 and build_result['edge_count']==10 and build_result['exact_governance_joins']==25,'actual native projection scope differs')
    parent=load(PARENT);files={};count=0
    def add(row):
        nonlocal count
        original(row);require(row['path'] not in files or files[row['path']]==row,'contradictory original binding');files[row['path']]=row;count+=1
    for row in parent['files']:add(row)
    add(binding(PARENT))
    for n in ['source-manifest.json','audit-source-manifest.json']:
        add(binding(HERE/n))
        for row in load(HERE/n)['files']:add(row)
    for root in [HERE,HERE.parent/'mapped-context-v1',HERE.parent/'mapped-context-v2',HERE.parent/'mapped-context-v3',HERE.parent/'mapped-context-v4',HERE.parent/'mapped-native-v1',HERE.parent/'mapped-native-v2']:
        for q in sorted(root.rglob('*')):
            if not q.is_file() or '__pycache__' in q.parts or q.name in ['audit-result.json','audit.stdout','audit.stderr','audit-tool-terminal.json','R03-0013.json']:continue
            add(binding(q))
    expected={r['path'] for r in package['files']}|{binding(package_path)['path']}
    actual={p.relative_to(ROOT).as_posix() for p in (HERE/'packages/0001').rglob('*') if p.is_file()}
    require(actual==expected,'mapped derived closure differs')
    mapping=load(HERE/'packages/0001/mapping.json')
    require(mapping['source_package_binding']==binding(reader.HERE/'packages/0001/manifest.json'),'different signed source package substituted')
    require(len(parent['supported_operations'])==7 and len(parent['remaining_operations'])==27,'original public API scope narrowed')
    value={k:v for k,v in parent.items() if k not in ['files','checks','observed_checks','claim_ceiling','recorded_at']}
    value.update(schema_version='lab-R03-same-cut-native-domain-projection-proof/v1-candidate',task='R03',result='PASS',task_complete=False,
        parent_binding=binding(PARENT),selected_mapped_projection_root=HERE.relative_to(ROOT).as_posix(),
        selected_mapped_projection_source_binding=binding(HERE/'source-manifest.json'),
        selected_mapped_projection_package_binding=binding(package_path),
        exact_domain_mapped_nodes=15,exact_declared_domain_mapped_edges=10,exact_native_governance_joins=25,
        mapped_native_source_cut=mapping['source_cut'],native_semantic_cursor=25,native_governance_cursor=25,
        mapped_native_projection_tests=20,mapped_projection_original_byte_binding_checks=count,
        native_domain_mapping_supplied=True,source_and_native_cursors_kept_distinct=True,
        context_or_ontology_views_generated=False,fresh_Session_participation_established=False,
        public_Session_API_calls_executed=0,session_API_operations_added=0,active_Agent_Sessions_created=0,
        native_selector_profile='test-complete-profile/v1',
        authority_effect='none',actual_owner_outcome=None,human_pilot_outcome=None,goal_complete=False,
        checks=[*parent['checks'],{'suite':'same-signed-cut-actual-native-domain-projection','test_count':20,'result':'PASS'},
            {'suite':'mapped-source-projection-and-original-plan-byte-closure','byte_binding_checks':count,'result':'PASS'}],
        observed_checks=parent['observed_checks']+20+count,files=sorted(files.values(),key=lambda row:row['path']),
        claim_ceiling='Retained seven public APIs and full original 46-task scope plus real fresh signed participation and fifteen original Artifact instances mapped to native nodes with ten declared closed Typed Relations mapped to native edges. Native event sealing, cold replay parity, exact governance joins, property profiles, original schemas/Definition witnesses and source cut are verified. The runtime read selector remains explicitly test-complete-profile/v1. Context/Ontology View carrier outputs, independent host permission/authentication, classified ephemeral Session resources and all four Context/Session public APIs remain incomplete. No admission, human pilot or complete plan inferred.',
        recorded_at=datetime.now(timezone.utc).isoformat())
    emit(HERE/'receipts/audit-result.json',{'result':'PASS','original_byte_binding_checks':count,'files':len(files),'source_sha256':pin,'package_sha256':package_pin,'authority_effect':'none','actual_owner_outcome':None})
    emit(HERE/'receipts/R03-0013.json',value)
    print(json.dumps({'result':'PASS','receipt':binding(HERE/'receipts/R03-0013.json'),'files':len(files),'byte_binding_checks':count,'task_complete':False}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);p.add_argument('--package-sha256',required=True);p.add_argument('--audit-sha256',required=True);a=p.parse_args();audit(a.source_sha256,a.package_sha256,a.audit_sha256)
