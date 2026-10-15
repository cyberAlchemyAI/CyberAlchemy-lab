"""Independent byte/signature audit followed by a parent-preserving partial proof."""
import argparse,ast,base64,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def raw_sha(raw):return hashlib.sha256(raw).hexdigest()
def sha(p):return raw_sha(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':sha(p)}
def parse(raw):
    def pairs(items):
        v={}
        for k,x in items:
            if k in v:raise ValueError('duplicate audit JSON key')
            v[k]=x
        return v
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite audit JSON')))
def digest(v):return raw_sha(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.open('x').write(json.dumps(v,indent=2,sort_keys=True)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);args=ap.parse_args()
    assert sha(HERE/'source-manifest.json')==args.source_sha256
    m=parse((HERE/'source-manifest.json').read_bytes());checks=[]
    def need(value,name):
        if not value:raise AssertionError(name)
        checks.append(name)
    for row in m['files']:need(sha(ROOT/row['path'])==row['sha256'],'exact source '+row['path'])
    parent=parse((ROOT/m['parent_receipt_binding']['path']).read_bytes())
    retained={r['path']:r['sha256'] for r in m['files']}
    for row in parent['files']:need(retained.get(row['path'])==row['sha256'],'parent retained '+row['path'])
    need(parent['result']=='PASS' and parent['task_complete'] is False,'original incomplete parent remains')
    selected=ROOT/m['selected_runtime_root'];totals={}
    for name,count in [('guards',76),('runtime',38),('custody',28),('schemas',12)]:
        report=parse((selected/'receipts/0001'/f'{name}.json').read_bytes())
        need(report['result']=='PASS' and report['tests_run']==report['expected']==count,'full '+name+' case count')
        need(report['sources_unchanged'],'fresh source closure '+name)
        need(report['authority_effect']=='none' and report['actual_owner_outcome'] is None,'candidate posture '+name)
        need(len(report['cases'])==count and len({r['test'] for r in report['cases']})==count
            and all(r['result']=='PASS' for r in report['cases']),'every method exactly once '+name)
        roots=report.get('owned_roots',[report.get('owned_correction_root')])
        need(all(r and r['removed'] and not Path(r['path']).exists() for r in roots),'actual owned cleanup '+name)
        totals[name]=count
    terminal=parse((ROOT/m['terminal_observations_binding']['path']).read_bytes())
    need(all(terminal['selected_exit_codes'][name]==0 for name in ['guards','runtime','custody','schemas','journey','coupling']),
        'every selected producer actual zero exit')
    coupling=(ROOT/m['coupling_log_binding']['path']).read_text();lines=coupling.splitlines()
    need(sum(line.startswith('test_') and line.endswith(' ... ok') for line in lines)==35,'all 35 inherited coupling methods')
    summary=parse(lines[-1].encode())
    need(summary=={'assertions_changed':False,'authority_effect':'none','errors':0,'failures':0,'result':'PASS','tests':35},'actual coupling terminal summary')
    totals['coupling']=35
    need(sum(totals.values())==189,'full 177 retained plus 12 new methods')
    adaptation=parse((selected/'regression-sources/adaptation.json').read_bytes())
    need(adaptation['original_assertions_changed'] is False,'original assertions retained')
    original_runtime=(ROOT/adaptation['original_runtime']['path']).read_text()
    for edit in adaptation['runtime_edits']:
        need(original_runtime.count(edit['before'])==edit['occurrences'],'exact original runtime locator anchor')
        original_runtime=original_runtime.replace(edit['before'],edit['after'])
    need(original_runtime==(selected/'regression-sources/test_runtime.py').read_text(),'runtime changed only declared host locators')
    original_custody=(ROOT/adaptation['original_custody']['path']).read_text()
    for edit in adaptation['custody_edits']:original_custody=original_custody.replace(edit['before'],edit['after'])
    need(original_custody==(selected/'regression-sources/test_custody.py').read_text(),'all prior raw custody assertions unchanged')
    historical=selected/'runtime/lab_runtime/historical_v2'
    historical_manifest=parse((selected/'runtime/lab_runtime/historical-v2-manifest.json').read_bytes())
    for row in historical_manifest['files']:
        need(sha(historical/row['path'])==row['sha256'],'exact captured historical code '+row['path'])
        if row['original_binding']:
            need(sha(ROOT/row['original_binding']['path'])==row['sha256'],'historical interpretation retains original code '+row['path'])
    need(historical_manifest['effect_scope']=='read-only original transaction replay; never successor writes','historical interpretation grants no successor write scope')
    journey=parse((selected/'receipts/0001/journey.json').read_bytes())
    need(journey['result']=='PASS' and len(journey['applied_corrections'])==10,'actual ten-member correction journey')
    need(journey['checks']==48 and len(journey['check_names'])==49
        and journey['check_names'][-1]=='owned store and signer removed',
        'retained journey pre-cleanup counter and final cleanup assertion explicitly reconciled')
    need(journey['owned_root']['removed'] and not Path(journey['owned_root']['path']).exists(),'actual correction signer/store cleanup')
    p=journey['original_proposal'];cores=journey['review_cores'];approval=journey['fixture_approval'];config=journey['fixture_configuration']
    signed={k:v for k,v in approval.items() if k!='signature'}
    expected_signed={'schema_version':'lab-runtime-approval/v2-candidate','store_id':config['store_id'],
        'owner_ref':config['owner_ref'],'scope_ref':p['scope_ref'],'policy_ref':p['policy_ref'],
        'challenge_route':p['challenge_route'],'source_snapshot_digest':p['source_snapshot_digest'],
        'expected_head':p['expected_head'],'proposal_digest':digest(p),'decision_core_digests':[digest(c) for c in cores],
        'approved_at':approval['approved_at'],'outcome':'authorize-exact-local-effects','configuration_digest':digest(config),
        'correction_profile_binding':config['correction_profile_binding'],'authorized_domain_scope_refs':config['authorized_domain_scope_refs']}
    need(signed==expected_signed,'independent closed exact signature input construction')
    need(approval['proposal_digest']==digest(p) and approval['decision_core_digests']==[digest(c) for c in cores],
        'original bytes enter exact full signed review')
    need(approval['configuration_digest']==digest(config)
        and approval['correction_profile_binding']==config['correction_profile_binding']==p['correction_profile_binding']
        and approval['authorized_domain_scope_refs']==config['authorized_domain_scope_refs'], 'independent scoped configuration binds signature')
    Ed25519PublicKey.from_public_bytes(bytes.fromhex(config['public_key'])).verify(bytes.fromhex(approval['signature']),encoded(signed))
    checks.append('independent actual Ed25519 signature verification')
    txraw=base64.b64decode(journey['transaction_original_base64'],validate=True);tx=parse(txraw)
    need(raw_sha(txraw)==journey['transaction_byte_sha256'],'actual original transaction bytes')
    need(digest({k:v for k,v in tx.items() if k!='digest'})==tx['digest']==journey['transaction_structural_digest'],'actual transaction structural seal')
    need(tx['proposal']==p and tx['decision_cores']==cores and tx['approval']==approval,'committed original proposal and full correction cores')
    need(p['schema_version']=='lab-runtime-reviewed-original-json-proposal/v2-candidate'
        and tx['schema_version']=='lab-runtime-reviewed-original-json-transaction/v2-candidate','distinct exact schema protocol families')
    need(tx['config_digest']==digest(config) and tx['previous_digest']==p['expected_head'],'exact configuration and predecessor')
    original_rows={r['version_ref']:r for r in journey['original_read_rows']}
    for target,core in zip(p['targets'],cores):
        raw=base64.b64decode(target['content']['data'],validate=True);row=original_rows[target['version_ref']]
        need(all(core[k]==target[k] for k in ['decision_ref','category','operation','version_ref'])
            and core['domain_scope_ref'] in config['authorized_domain_scope_refs'], 'independent target core and provisioned domain '+target['version_ref'])
        need(raw_sha(raw)==target['content']['byte_sha256']==row['source_binding']['sha256'],'actual target original byte identity '+target['version_ref'])
        need(digest(parse(raw))==digest(target['record']) and core['target_digest']==digest(target),'retained distinct parsed and full target digests '+target['version_ref'])
        need(base64.b64decode(row['original_base64'],validate=True)==raw and row['reader_report']['parsed_record_matches'],
            'canonical and captured source bridge byte parity '+target['version_ref'])
    need(journey['cold_read_exit_code']==0
        and base64.b64decode(journey['cold_original_base64'],validate=True)==base64.b64decode(p['targets'][0]['content']['data'],validate=True),
        'actual cold process original bytes')
    need(journey['retry']['idempotent'] and journey['retry']['transaction_digest']==tx['digest'],'exact historical retry')
    schemas=parse((selected/'receipts/0001/schemas.json').read_bytes())
    example=next(r for r in schemas['observations'] if 'original_schema_base64' in r)
    raw=base64.b64decode(example['original_schema_base64'],validate=True);sha_original=raw_sha(raw)
    need(sha_original==example['original_schema_sha256']==example['descriptor']['schema_sha256']
        ==example['contract']['schema_sha256']==example['schema_source_binding']['byte_sha256'],'actual original schema descriptor/contract/header parity')
    need(sha_original!=example['inherited_encoded_schema_sha256']==raw_sha(encoded(parse(raw))), 'original schema differs from inherited encoder')
    need(example['schema_source_binding']['selector']=='/proposal/schema_contents/'+example['schema_path'].replace('~','~0').replace('/','~1')+'/data',
        'exact escaped immutable schema source selector')
    need(any(r.get('episode')=='Actual cold exact schema retrieval' and r['exit_code']==0
        and base64.b64decode(r['returned_base64'],validate=True)==raw for r in schemas['observations']),'actual cold schema original bytes')
    need(journey['repository_admissions_applied']==0 and journey['actual_owner_outcome'] is None,'no actual owner or canonical effect inferred')
    audit={'schema_version':'lab-custody-correction-independent-audit/v1-candidate','result':'PASS','checks':len(checks),'check_names':checks,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'parent_files_retained':len(parent['files']),'method_counts':totals,'selected_methods':189,'independent_actual_fixture_signature_verified':True,
        'journey_check_counter_observation':{'retained_pre_cleanup_count':48,'actual_named_checks_including_cleanup':49,'frozen_report_rewritten':False},
        'source_manifest_binding':bind(HERE/'source-manifest.json'),'claim_ceiling':'Exact bounded storage and retained correction proof. Full API and original plan remain open.'}
    audit_path=HERE/'receipts/0001/audit.json';put(audit_path,audit)
    rows={r['path']:r for r in m['files']}
    for path in [HERE/'source-manifest.json',audit_path]:rows[bind(path)['path']]=bind(path)
    for row in rows.values():assert sha(ROOT/row['path'])==row['sha256']
    receipt={'schema_version':'lab-R03-exact-schema-correction-partial-proof/v1-candidate','result':'PASS',
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'checked_at':datetime.now(timezone.utc).isoformat(),'files':sorted(rows.values(),key=lambda r:r['path']),
        'parent_receipt_binding':m['parent_receipt_binding'],'selected_runtime_source_binding':m['selected_runtime_source_binding'],
        'independent_audit_binding':bind(audit_path),'audit_checks':len(checks),'method_counts':totals,'selected_methods':189,
        'parent_files_retained':len(parent['files']),'actual_public_api_operations':12,'remaining_original_api_operations':22,
        'original_public_api_operations':34,'closed_plan_criteria':35,'total_plan_criteria':46,
        'repository_admissions_applied':0,'private_keys_exported':False,'private_memory_exported':False,
        'selected_producers_terminal':True,'selected_owned_roots_removed':True,'remaining_obligations':m['remaining_obligations'],
        'claim_ceiling':'Original artifact/schema bytes now compose with unchanged correction, scoped configuration, signatures and coupling rules. Full API/body/privacy/binary/export/review/ontology integration and all original task acceptance remain; no completed Lab or actual owner admission.'}
    receipt_path=HERE/'receipts/R03-0018.json';put(receipt_path,receipt)
    print(json.dumps({'result':'PASS','checks':len(checks),'selected_methods':189,'files':len(rows),'parent_files_retained':len(parent['files']),'receipt_binding':bind(receipt_path)}),flush=True)
if __name__=='__main__':main()
