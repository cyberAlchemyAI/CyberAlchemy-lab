"""Combine complete public export and owner-routing evidence; retain full scope."""
import argparse
import base64
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v25'
SOURCE=RUN/'public-file-export-qualification-source-0001.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def compact(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def bind(path):return {'path':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),'sha256':sha(path.read_bytes())}
def put(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);args=parser.parse_args()
    assert sha(SOURCE.read_bytes())==args.source_sha256
    frozen=json.loads(SOURCE.read_bytes());rows={r['path']:r for r in frozen['files']}
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    checks=json.loads((API/'receipts/file-export-checks.json').read_bytes())
    terminal=json.loads((RUN/'file-export-api-terminal-0002.json').read_bytes())
    assert checks['result']=='PASS' and checks['tests_run']==134 and terminal['result']=='PASS' and terminal['exit_code']==0
    assert len(checks['cases'])==len({r['test'] for r in checks['cases']})==134 and all(r['result']=='PASS' for r in checks['cases'])
    counts=Counter(r['test'].split('.')[-3] for r in checks['cases'])
    assert dict(counts)=={'test_file_exports':24,'test_export_kernel':24,'test_guarded_reads':17,'test_preparation_corrected':47,'test_metadata_scope':22},counts
    wire=json.loads((API/'receipts/file-export-wire.json').read_bytes())
    nonce_count=0
    for witness in wire['public_nonce_witnesses']:
        if 'signed_nonce_proof' not in witness:continue
        policy=witness['public_policy'];proof=witness['signed_nonce_proof']
        Ed25519PublicKey.from_public_bytes(base64.b64decode(policy['reader_public_key'],validate=True)).verify(base64.b64decode(proof['signature'],validate=True),compact(proof['challenge']))
        context=witness['authentication_reply']['context']
        assert context['principal_ref']==policy['principal_ref'] and context['agent_instance_ref'] is None and context['assignment_ref'] is None and context['session_ref'] is None
        assert policy['allowed_operations']==(['lab.status','catalog.get','artifact.inspect','artifact.query','change.prepare','change.validate','operation.inspect','projection.refresh','files.materialize'] if policy['schema_version']=='lab-local-export-candidate-policy/v1-candidate' else ['lab.status','catalog.get','artifact.inspect','artifact.query','change.prepare','change.validate','operation.inspect','projection.refresh'])
        nonce_count+=1
    assert nonce_count==27
    assert any(e.get('actual_stdio') and e['reply'].get('kind')=='result' and e['reply']['message']['posture']=='published' for e in wire['events'])
    audit=json.loads((RUN/'public-file-export-independent-observations-0001.json').read_bytes())
    audit_terminal=json.loads((RUN/'public-file-export-audit-terminal-0001.json').read_bytes())
    assert audit['result']=='PASS' and audit['checks']==26 and audit_terminal['exit_code']==0
    positives=[e for e in audit['observations'] if e.get('call',{}).get('operation')=='files.materialize' and e['reply'].get('kind')=='result']
    assert {e['call']['message']['mode'] for e in positives}=={'byte-exact','rendered'} and all(e['actual_stdio'] for e in positives)
    owner=json.loads((ROOT/'product/lab/release-candidates/v1/interface/owner-coverage-v1/receipts/checks-0001.json').read_bytes())
    owner_audit=json.loads((RUN/'owner-coverage-independent-observations-0001.json').read_bytes())
    assert owner['result']=='PASS' and owner['tests_run']==35 and owner_audit['result']=='PASS' and owner_audit['checks']==217
    assert not owner['current_governing_coverage_verified'] and not owner_audit['current_owner_authority_verified']
    profile=json.loads((API/'contract-profile.json').read_bytes());catalog=json.loads((ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json').read_bytes())
    implemented=profile['implemented_operations'];original=[o['operation'] for o in catalog['operations']]
    assert len(set(implemented))==13 and len(set(original))==34 and set(implemented)<=set(original)
    remaining=[o for o in original if o not in implemented];assert len(remaining)==21
    report=RUN/'R03-PUBLIC-EXPORT-AND-OWNER-COVERAGE-RESULT-0001.md'
    with report.open('x') as stream:
        stream.write('# Public file export qualified; owner review construction continues\n\n')
        stream.write('Candidate progress: **35/46 criteria, 13/34 APIs, 21 APIs remaining**. Current Agent/Session qualification and complete S02/R08 remain pending. No owner outcome or canonical admission occurred.\n\n')
        stream.write('## Complete actual evidence\n\n- API25 full 134-case suite passed: 24 public export, 24 kernel, 17 guarded read, 47 preparation and 22 metadata cases.\n- Fresh-process independent actual stdio export audit passed 26 checks. Original body bytes, renderer, publication markers, retries, deleted-output refusal and cleanup were observed.\n- All 27 recorded signed nonce witnesses verify against their explicit local policies. These policies grant no Agent participation or owner authority.\n- Required-owner compiler passed 35 cases over 42 original cores and 21 scopes; independent audit passed 217 checks. Separate role voices and exact legacy recognition are preserved. Current governing coverage remains an explicit blocking gap.\n\n')
        stream.write('## Preserved failures and limits\n\nAPI24 full 134-case failure is retained. New bounded participation source production succeeded with fresh keys and a separate fixed episode identity; its initial source-byte test used an incorrect Store receiver. Full corrected source checks are separate work. The original expired Assignment, historical source interpretation, old Session evidence and every original plan requirement remain intact. No current Agent qualification is inferred from export or source construction.\n\n')
        stream.write('## Next\n\nFinish the corrected new-source checks, integrate new Context/Ontology Views and independently provision current Session permission. Integrate the review compiler with independently current governing requirements and implement all remaining public operations. Complete S02 and present the exact complete package at the sole final R08 checkpoint.\n')
    for path in [SOURCE,report]:row=bind(path);rows[row['path']]=row
    parent=ROOT/'product/lab/release-candidates/v1/interface/api-v23/receipts/R03-0023.json'
    receipt={'schema_version':'lab-R03-public-export-and-owner-coverage-partial-proof/v1-candidate','result':'PASS','checked_at':datetime.now(timezone.utc).isoformat(),'files':sorted(rows.values(),key=lambda r:r['path']),
             'parent_receipt_binding':bind(parent),'qualification_source_binding':bind(SOURCE),'report_binding':bind(report),'closed_plan_criteria':35,'total_plan_criteria':46,'qualified_public_api_operations':13,'original_public_api_operations':34,'remaining_original_api_operations':21,'implemented_operations':implemented,'remaining_operations':remaining,
             'public_file_export_qualified':True,'complete134_suite_terminal_binding':bind(RUN/'file-export-api-terminal-0002.json'),'public_file_export_complete_suite_proof_binding':bind(RUN/'file-export-api-proof-0001.json'),'public_file_export_independent_audit_proof_binding':bind(RUN/'public-file-export-audit-proof-0001.json'),'full_suite_cases':134,'independent_export_checks':26,'verified_nonce_witnesses':nonce_count,
             'owner_coverage_compiler_proof_binding':bind(ROOT/'product/lab/release-candidates/v1/interface/owner-coverage-v1/receipts/proof-0001.json'),'owner_coverage_independent_audit_proof_binding':bind(RUN/'owner-coverage-audit-proof-0001.json'),'owner_coverage_suite_cases':35,'owner_coverage_independent_checks':217,'current_governing_owner_coverage_verified':False,'current_owner_authority_verified':False,'current_Agent_qualified':False,'historical_twelve_handler_evidence_retained':True,'original_Assignment_renewed':False,'Session_memory_rehydrated':False,'private_keys_exported':False,'repository_admissions_applied':0,'human_pilot_outcome':None,
             'remaining_obligations':['All21remainingpublicAPIs and complete original46criteria.','Genuinely new current Agent/Session source, mapped/context/ontology delivery, independent permissions and full relevant regression; expired original Assignment unchanged.','Public proposal.review and independently current governing role/scope coverage.','Complete S02, actual human/pilot requirements, sole finalR08 owner checkpoint and original admitted operational obligations.'],
             'claim_ceiling':'Public export candidate qualification plus exact proposed owner-routing compiler. Historical Session evidence retained; current Agent, governing role coverage, owner outcome and whole plan completion are not inferred.','authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    out=API/'receipts/R03-0024.json';put(out,receipt)
    print(json.dumps({'result':'PASS','receipt_binding':bind(out),'files':len(rows),'qualified_public_api_operations':13,'remaining_public_operations':21,'closed_plan_criteria':35,'goal_complete':False}),flush=True)
if __name__=='__main__':main()
