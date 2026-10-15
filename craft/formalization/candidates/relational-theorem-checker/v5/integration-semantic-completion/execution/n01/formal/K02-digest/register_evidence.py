"""Register exact digest proofs; never imply authentic profile choice or inherited closure."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
 v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json')
 assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==61
 assert v['new_general_declarations']==48 and v['new_worked_control_declarations']==13
 assert len(v['records'])==16 and a['resolved_source_phase_pairs']==16
 assert a['result']=='import-resolution-audit-pass' and a['verification']==b(HERE/'verification.json')
 assert v['runtime_digest_cases']==51 and v['runtime_submitted_capture_cases']==8
 index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json')
 progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
 assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1559
 assert not index.get('digest_packages') and seq['current_unit']=='K04'
 assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
 driver=N/'check_current_review.py';s=driver.read_text()
 marker="index.get('byte_binding_packages', [])):";end='    assert len(declarations) == len(set(declarations))'
 assert s.count(marker)==s.count(end)==1
 readout=H/'execution/PROGRESS.md';old='making 1559 distinct verified candidate declarations in total.'
 assert readout.read_text().count(old)==1
 files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json',
  'candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md',
  'refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md',
  'independent_formalization':'FORMALIZATION.md','runtime_control_index':'runtime-control-index.json'}
 package={'unit':'K02-digest','kind':'relation.addresses-intent','theorems':61,'general_declarations':48,'worked_control_declarations':13,
  'digest_algorithm_realized':True,'digest_independent_meaning_exactness_proved':True,
  'digest_algorithm_domain_totality_proved':True,'digest_hex_representation_proved':True,
  'digest_full_profile_ref_equality_proved':True,'digest_outcome_exactness_proved':True,
  'digest_capture_pipeline_composed':False,'authenticated_digest_profile_selection_proved':False,
  'authenticated_capture_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
 for key,name in files.items():package[key]=b(HERE/name)
 index['digest_packages']=[package];index['digest_candidate_theorems']=61
 index['total_distinct_new_candidate_theorems']=1620;save(N/'formal-preparation-index.json',index)
 seq['candidate_fragment_theorems']=1620;seq['candidate_digest_packages']=1;save(N/'sequential-review.json',seq)
 progress['candidate_fragment_theorems']=1620;progress['digest_candidate_theorems']=61;progress['candidate_digest_packages']=1
 for key,name in files.items():progress['K02_digest_'+key]=b(HERE/name)
 for value in progress.values():
  if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:
   value.update(b(ROOT/value['path']))
 save(H/'execution/plan.json',plan)
 s=s.replace(marker,"index.get('byte_binding_packages', []) +\n                    index.get('digest_packages', [])):")
 block='''        if package.get('digest_algorithm_realized'):
            for key in ['digest_algorithm_realized','digest_independent_meaning_exactness_proved',
                        'digest_algorithm_domain_totality_proved','digest_hex_representation_proved',
                        'digest_full_profile_ref_equality_proved','digest_outcome_exactness_proved']:
                assert proof[key] is True
            for key in ['digest_capture_pipeline_composed','authenticated_digest_profile_selection_proved',
                        'authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'external_standard_translation_reviewed','NIST_FIPS_validated','collision_freedom_proved',
                        'supported_resource_envelope_measured','independent_checker_run']:
                assert proof[key] is False
            assert proof['new_general_declarations']==48 and proof['new_worked_control_declarations']==13
            assert len(proof['records'])==16 and proof['runtime_digest_cases']==51 and proof['runtime_submitted_capture_cases']==8
            read(ROOT/proof['context_pack']['path'])
            capture=read(ROOT/proof['source_capture']['path'])
            assert capture['profile_reference_is_synthetic'] and not capture['authenticated_expected_profile']
            controls=read(ROOT/proof['runtime_control_index']['path'])
            assert len(controls['cases'])==51 and len(controls['refusal_cases'])==8
            assert not controls['independent_proof_checker']
            for case in controls['cases']:
                data=bytes.fromhex(case['input_hex'])
                assert len(data)==case['byte_length'] and hashlib.sha256(data).hexdigest()==case['expected_sha256']
                if case.get('original_bytes'):assert data==(ROOT/case['original_bytes']['path']).read_bytes()
            for record in proof['records']:
                if Path(record['source']['path']).stem=='DigestRuntimeControls':
                    assert record['runtime_digest_cases']==51 and record['runtime_submitted_capture_cases']==8
                    expected=[json.dumps(c['expected_sha256']) for c in controls['cases']]+[c['expected'] for c in controls['refusal_cases']]
                    assert (ROOT/record['log']['path']).read_text().strip().splitlines()==expected
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['digest_algorithm_realized'] and api['digest_independent_meaning_exactness_proved']
            assert not api['N03_API_freeze'] and not api['authenticated_capture_proved']
'''
 s=s.replace(end,block+end);driver.write_text(s)
 total_seconds=sum(r['seconds'] for r in v['records']);max_seconds=max(r['seconds'] for r in v['records'])
 text='''

## Exact byte digest formalization and evaluator

K02-digest implements SHA-256 for retained original byte lists. Its independent
padding, lossless ordered partition, schedule, round, feed-forward, message and
canonical hex meanings precede implementation. End-to-end soundness/completeness,
algorithm-domain totality and lowercase 64-character output are proved. Profile
checking compares the complete submitted RevisionRef against the candidate expected
profile, and distinct profile/domain/budget/format/mismatch outcomes have exact meanings.

The package adds 61 declarations: 48 general results and 13 kernel controls.
Two fresh phases contain 16 invocations and IMPORTS verified import resolutions.
Runtime comparisons pass 51 inputs and eight unchanged/altered submitted-digest cases
in each phase. This includes both original binding fixture byte files. The cumulative
total is 1620 distinct candidate declarations. Compilation and runtime-control
elaboration/evaluation total SECONDS seconds, with MAX seconds for the largest
invocation; these are not a qualified operational envelope.

Expected profile selection remains unauthenticated. Capture/catalog composition,
Schema/review/issuer providers, all nineteen full-source policies, external-standard
translation, runtime qualification and mandatory independent checking remain open.
All 263 inherited IDs remain pending, zero new inherited discharges are claimed,
and all 90 original discharges retain scope. K04 remains the pending one-by-one
meaning review. N01 stays in progress and N02/N03 remain unadmitted. The objective
remains the full seven-extension and 41-kind plan.
'''.replace('IMPORTS',str(a['resolved_source_phase_pairs'])).replace('SECONDS',str(round(total_seconds,3))).replace('MAX',str(max_seconds))
 readout.write_text(readout.read_text().replace(old,'and exact byte digest work adds 61, making 1620 distinct verified candidate declarations in total.')+text)
 print(json.dumps({'registered':'K02-digest','new_declarations':61,'total_candidate_declarations':1620,'inherited_discharges':0}))
if __name__=='__main__':run()
