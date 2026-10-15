"""Independent byte/custody audit and exact partial proof; never owner admission."""
from datetime import datetime,timezone
import argparse
import stat
from base import *

PARENT=HERE.parent/'operator-context-v4/receipts/R03-0011.json'
PARENT_SHA='410bbaa54fda5a3fdeb1a9cf3415998429d891c6567cbb9dbe7ce8b49f94fc37'

def audit(source_pin,package_pin,audit_pin):
    audit_manifest=HERE/'audit-source-manifest.json'
    require(sha(audit_manifest.read_bytes())==audit_pin,'independent audit producer pin differs')
    for row in load(audit_manifest)['files']: original(row)
    verify_source(source_pin)
    require(sha(PARENT.read_bytes())==PARENT_SHA,'original full partial proof differs')
    parent=load(PARENT);package=load(HERE/'packages/0001/manifest.json')
    require(sha((HERE/'packages/0001/manifest.json').read_bytes())==package_pin,'independent package pin differs')
    result=load(HERE/'packages/0001/build-result.json');checks=load(HERE/'receipts/checks.json')
    require(result['result']=='PASS' and checks['result']=='PASS' and checks['tests_run']==22 and checks['errors']==checks['failures']==0,'actual producer scope or result differs')
    for name in ['build-tool-terminal.json','checks-tool-terminal.json']:
        t=load(HERE/'receipts'/name);require(t['exit_code']==0 and t['terminal_observed'] is True,'actual terminal absent')
    require(checks['source_sha256']==source_pin and checks['package_sha256']==package_pin,'observations belong to another package')
    files={};count=0
    def add(row):
        nonlocal count
        original(row);require(row['path'] not in files or files[row['path']]==row,'contradictory evidence binding')
        files[row['path']]=row;count+=1
    for row in parent['files']:add(row)
    add(binding(PARENT))
    for name in ['source-manifest.json','audit-source-manifest.json']:
        add(binding(HERE/name))
        for row in load(HERE/name)['files']:add(row)
    for root in [HERE,HERE.parent/'operator-context-v6',HERE.parent/'session-participation-v1']:
        for p in sorted(root.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.name in ['audit-result.json','audit.stdout','audit.stderr','audit-tool-terminal.json','R03-0012.json']:continue
            add(binding(p))
    expected_paths={row['path'] for row in package['files']}|{binding(HERE/'packages/0001/manifest.json')['path']}
    actual_paths={p.relative_to(ROOT).as_posix() for p in (HERE/'packages/0001').rglob('*') if p.is_file()}
    require(expected_paths==actual_paths,'derived package exact file closure differs')
    for row in package['files']:
        original(row);p=ROOT/row['path'];require(stat.S_IMODE(p.stat().st_mode)==0o600,'protected source custody file mode differs')
    require(package['public_package_export_allowed'] is False and result['owned_store_and_key_removed'] is True and result['private_keys_exported'] is False,'private custody or key disposal differs')
    require(result['authored_current_artifacts']==11 and result['authored_current_typed_relations']==10 and result['independent_participation_decision_cores']==21,'actual source/relation cardinality differs')
    require(len(parent['supported_operations'])==7 and len(parent['remaining_operations'])==27,'original API obligations narrowed')
    value={k:v for k,v in parent.items() if k not in ['files','checks','observed_checks','claim_ceiling','recorded_at']}
    value.update(schema_version='lab-R03-fresh-signed-participation-proof/v1-candidate',task='R03',result='PASS',task_complete=False,
        parent_binding=binding(PARENT),selected_participation_root=HERE.relative_to(ROOT).as_posix(),
        selected_participation_source_binding=binding(HERE/'source-manifest.json'),selected_participation_package_binding=binding(HERE/'packages/0001/manifest.json'),
        selected_operator_source_adapter_root=(HERE.parent/'operator-context-v6').relative_to(ROOT).as_posix(),
        selected_source_adapter_binding=binding(HERE.parent/'operator-context-v6/source-manifest.json'),
        fresh_participation_artifacts=11,fresh_participation_typed_relations=10,fresh_participation_decision_cores=21,
        fresh_participation_original_source_tests=22,fresh_participation_original_byte_binding_checks=count,
        fresh_Profile_eligible_Assignment_materialized=True,actual_cryptographically_bound_Principal_Reference=True,
        fresh_current_Goal_and_Coordination_materialized=True,owned_participation_exact_retry=True,
        owned_participation_store_and_signing_key_removed=True,missing_current_source_carriers=[],
        selected_participation_uses_old_Agent_instance=False,
        native_domain_mapping_supplied=False,fresh_Session_participation_established=False,
        context_or_ontology_views_generated=False,public_Session_API_calls_executed=0,
        session_API_operations_added=0,active_Agent_Sessions_created=0,
        authority_effect='none',actual_owner_outcome=None,human_pilot_outcome=None,goal_complete=False,
        checks=[*parent['checks'],{'suite':'fresh-actual-signed-participation-original-source','test_count':22,'result':'PASS'},
            {'suite':'independent-source-byte-custody-and-original-plan-closure','byte_binding_checks':count,'result':'PASS'}],
        observed_checks=parent['observed_checks']+22+count,files=sorted(files.values(),key=lambda r:r['path']),
        claim_ceiling='Retained seven public APIs and original 46-task obligations plus actual fresh signed participant source branch. Eleven current artifacts and ten closed Typed Relations conform and cold replay preserves original bytes, exact retry and deleted owned signing keys. Actual same-cut native domain projection, generated Context/Ontology Views, independently authenticated eligible context consumption and all four Context/Session APIs remain incomplete. No owner admission, active Agent, human pilot or complete plan inferred.',
        recorded_at=datetime.now(timezone.utc).isoformat())
    emit(HERE/'receipts/audit-result.json',{'result':'PASS','original_byte_binding_checks':count,'files':len(files),'source_sha256':source_pin,'package_sha256':package_pin,'authority_effect':'none','actual_owner_outcome':None})
    emit(HERE/'receipts/R03-0012.json',value)
    print(json.dumps({'result':'PASS','receipt':binding(HERE/'receipts/R03-0012.json'),'files':len(files),'byte_binding_checks':count,'task_complete':False}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);p.add_argument('--package-sha256',required=True);p.add_argument('--audit-sha256',required=True);a=p.parse_args();audit(a.source_sha256,a.package_sha256,a.audit_sha256)
