"""Record exact scope hypothesis and retained validation candidate; no task closure."""
import hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v46';TYPED=BASE/'typed-extension-preparation-v11'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 assert bind(API/'source-manifest.json')['sha256']=='db77ca7aa91fe4d8b5e25f2f23b4b32610a40f83dfd20ab6bcf50fcd06326118'
 assert bind(TYPED/'source-manifest.json')['sha256']=='56a9db7a496302d1811d55df2c217dadef01af9ee6b60889e7771e8b103f8674'
 checks=load(TYPED/'receipts/checks-0001.json');terminal=load(RUN/'typed-extension-wire144-terminal-0001.json')
 assert checks['result']=='PASS' and checks['actual_tests']==144 and checks['errors']==checks['failures']==0 and terminal['actual_exit_code']==0
 signed=load(RUN/'typed-actual-source-comparison-0010.json');post=signed['actual_preimage_candidate_postimage'];scope=post['scope_preparation']
 assert signed['result']=='BOUND-POSTIMAGE-PASS' and signed['original_reader_guarded_exit_completed']
 assert len(signed['actual_public_predecessor_binding']['predecessors'])==4
 assert scope['actual_scope_refusal']=='target outside authorized scope' and scope['configuration_status']=='hypothetical-unprovisioned'
 assert not post['operational_preparation_ready'] and not post['runtime_admission_authorized'] and not scope['actual_runtime_grant']
 assert signed['genuine_semantic_review_provided'] is False and signed['actual_public_calls']==signed['actual_transactions_written']==0
 failed=load(BASE/'api-v45/receipts/failure-checks.json')
 assert failed['tests_run']==18 and failed['result']=='FAIL' and len(failed['cases'])==18
 counts={kind:sum(c['result']==kind for c in failed['cases']) for kind in ['PASS','FAIL','ERROR']};assert counts=={'PASS':16,'FAIL':2,'ERROR':0}
 assert load(RUN/'API45-failure18-terminal-0001.json')['actual_exit_code']==1
 assert load(RUN/'API45-failure18-cleanup-evidence-0001.json')['result']=='PASS'
 assert load(RUN/'API46-freeze-terminal-0001.json')['actual_exit_code']==0
 typed_rows={r['path']:r for r in load(TYPED/'source-manifest.json')['files']}
 for p in [TYPED/'source-manifest.json',TYPED/'receipts/checks-0001.json',RUN/'typed-extension-wire144-terminal-0001.json',RUN/'typed-extension-wire144-0001.log']:
  r=bind(p);typed_rows[r['path']]=r
 for r in typed_rows.values():assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
 proof=TYPED/'receipts/proof-0001.json'
 put(proof,{'schema_version':'lab-typed-extension-scope-preparation-proof/v1-candidate','result':'PASS','actual_cases':144,'retained_predecessor_test_methods':128,'new_scope_preparation_cases':16,'actual_terminal_exit_code':0,
  'source_binding':bind(TYPED/'source-manifest.json'),'checks_binding':bind(TYPED/'receipts/checks-0001.json'),'terminal_binding':bind(RUN/'typed-extension-wire144-terminal-0001.json'),'files':[typed_rows[k] for k in sorted(typed_rows)],
  'all_prospective_original_backend_checks':True,'exact_schema_target_and_core_bytes_checked':True,'actual_scope_refusal_preserved':True,'hypothetical_configuration_unprovisioned':True,'operational_preparation_ready':False,'actual_runtime_grant':False,'actual_transactions_written':0,'actual_public_calls':0,'current_public_handler_qualified':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,
  'claim_ceiling':'Complete144 pure checks. The separate signed-source diagnostic checks an exact synthetic coupled hypothesis; no actual scope grant, public dispatcher, Actor, semantic review or admission.'})
 governance=RUN/'GOVERNANCE-BOUNDARY-REVIEW-0002.md'
 text='''# Candidate construction and final admission boundary\n\nThe existing candidate development authorization permits implementation, full\nverification and owned isolated development episodes. Continue that work and\npresent the complete S02 package for the sole R08 owner admission decision.\n\n## Current findings\n\nTyped v11 passes all144 checks. The exact selected signed replay passes complete\ncatalog and four predecessor bindings, then checks a complete coupled hypothetical\npostimage under a separately frozen synthetic diagnostic profile. The original\nruntime still refuses `target outside authorized scope`; its actual configuration,\npublic headers and semantic body bytes stay unchanged. The hypothetical\nconfiguration is unprovisioned and operational preparation remains false.\nThis diagnostic profile supplies no genuine semantic review or scoped grant.\n\nAPI45 full failure18 finished:16 PASS,2 FAIL,0 ERROR. Cases12 and15 fail.\nCase12 delivers indeterminate after the real deadline instead of the expected\nconflict. Case15 loses its required failed structural validation report. All18\nregistered owned fixture cleanup paths completed; failures remain retained.\nAPI46 is frozen with a narrowly conditional known-validation evidence fix after\ncomplete exact core verification. All293 original methods and34 contracts remain\nunchanged; original clocks,900-second bound and source/policy/journal predicates\nremain. Runtime verification of this successor is outstanding. CPU measurement\nof unchanged original case12 remains a diagnostic, not normal timing qualification.\n\n## Decisions and evidence still required\n\n- R05 needs genuine participant evidence. Automated fixtures cannot establish it.\n- R06 and R07 must review the complete candidate and its unresolved boundaries.\n- S02 must freeze the complete package and validation evidence before R08.\n- R08 requires an actual owner decision bound to that reviewed package.\n- Real typed operations require independently scoped permission and authenticated\n  Actor/current source integration; a semantic domain supplies no transaction grant.\n- Activation, deployment, existing store effects and external effects require\n  their applicable authority. Candidate construction authorizes none of them.\n\nNo additional owner admission checkpoint is introduced during construction.\nOriginal tests, currentness checks and task prerequisites remain required.\n'''
 with governance.open('x') as f:f.write(text)
 parent=BASE/'api-v45/receipts/R03-0080.json';previous=load(parent);rows={r['path']:r for r in previous['files']}
 for manifest in [API/'source-manifest.json',TYPED/'source-manifest.json']:
  for r in load(manifest)['files']:rows[r['path']]=r
  r=bind(manifest);rows[r['path']]=r
 extras=[parent,proof,governance,Path(__file__).resolve(),RUN/'authorization.json',RUN/'API45-failure18-terminal-0001.json',RUN/'API45-failure18-cleanup-evidence-0001.json',BASE/'api-v45/receipts/failure-checks.json',BASE/'api-v45/receipts/failure-wire.json',RUN/'current-API45-failure18-0001.log',RUN/'API45-failure15-validation-finding-0001.json',RUN/'typed-scope-diagnostic-profile-0001.json',RUN/'typed-scope-diagnostic-profile-envelope-0001.json',RUN/'build-typed-scope-diagnostic-profile-0001.py',RUN/'freeze-typed-extension-scope-v11-0001.py',RUN/'typed-extension-v11-freeze-terminal-0001.json',RUN/'context-R03-typed-scope-preparation-v11.json',RUN/'typed-scope-authoring-positive-0001.log',RUN/'typed-scope-authoring-positive-terminal-0001.json',RUN/'inspect-typed-actual-source-0010.py',RUN/'typed-actual-source-comparison-0010.json',RUN/'typed-actual-source-comparison-0010.log',RUN/'typed-actual-source-comparison-terminal-0010.json',RUN/'API46-freeze-terminal-0001.json',RUN/'API46-freeze-0001.log',RUN/'profile-API45-failure12-0001.py']
 # Bind the CPU runner, but never freeze its live appendable output as a result.
 for p in extras:
  r=bind(p);rows[r['path']]=r
 for r in typed_rows.values():rows[r['path']]=r
 for p in (BASE/'api-v45/receipts/per-call-observations').glob('*.json'):
  r=bind(p);rows[r['path']]=r
 for r in rows.values():assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
 remaining=[
  'Qualify all21 original outstanding operations;16 authored handlers do not establish runtime qualification.',
  'Measure and repair actual deadline delivery without changing original900-second bound, clocks or source/policy guards.',
  'Run original incomplete-core case14 and failed-schema evidence case15 against frozen API46; then every sequential full original runtime suite and refusal/cleanup criterion.',
  'Integrate typed.extension.prepare with authenticated current source, Actor, independently scoped permission and original durable journal/retry/recovery.',
  'Replace synthetic diagnostic targets/profile with genuinely reviewed complete typed extension package and its exact independently selected operational authority.',
  'Implement governed internal endpoint and specialized canonical authority resolvers.',
  'Complete genuine R05 participant evidence, R06, R07 and S02 before the sole actual R08 owner decision.',
  'Actual owner outcomes and independently scoped authorization remain required before A01-A04 effects.']
 receipt={**previous,'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'parent_progress_binding':bind(parent),'files':[rows[k] for k in sorted(rows)],
  'change':'Typed-v11 complete144 PASS and exact signed replay hypothetical coupled scope postimage PASS. API45 full failure18 FAIL16/2; cleanup PASS. API46 freezes conditional known structural refusal retention with unchanged293 methods/34 contracts; successor runtime verification outstanding.',
  'typed_source_resolver_proof_binding':bind(proof),'pure_typed_wire_full_cases':144,'typed_retained_predecessor_test_methods':128,'typed_predecessor_full_suite_result':'PASS','typed_exact_scope_preparation_cases':16,
  'actual_signed_candidate_postimage_observation':bind(RUN/'typed-actual-source-comparison-0010.json'),'scope_preparation_profile_binding':bind(RUN/'typed-scope-diagnostic-profile-0001.json'),'genuine_semantic_review_provided':False,'operational_scope_grant':False,
  'current_public_suite_observation_binding':bind(BASE/'api-v45/receipts/failure-checks.json'),'current_full_suites':[],'completed_API45_full_failure_suite_binding':bind(BASE/'api-v45/receipts/failure-checks.json'),'completed_API45_full_failure_counts':counts,'completed_API45_full_failure_exit_code':1,'current_full_public_suite_verdict':None,'API46_successor_runtime_verification_executed':False,
  'API45_cleanup_evidence_binding':bind(RUN/'API45-failure18-cleanup-evidence-0001.json'),'known_validation_retention_static_binding':bind(RUN/'API46-retained-validation-static-0001.json'),'governance_boundary_review_binding':bind(governance),
  'remaining_obligations':remaining,'whole_API_qualified':False,'task_complete':False,'goal_complete':False,'actual_owner_outcome':None,'authority_effect':'none',
  'claim_ceiling':'Scoped candidate progress only. Full144 pure checks and exact signed preimage hypothetical postimage pass; full API45 failure suite has2 retained failures, API46 runtime unqualified. No genuine semantic review, operational grant, admission or owner outcome.'}
 path=API/'receipts/R03-0081.json';put(path,receipt)
 print(json.dumps({'result':'PASS','progress_binding':bind(path),'typed_proof_binding':bind(proof),'bound_files':len(rows),'whole_API_qualified':False,'task_complete':False}),flush=True)
if __name__=='__main__':main()
