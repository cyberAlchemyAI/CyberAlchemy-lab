"""Register only verified composition; preserve authentic-policy and inherited closure requirements."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
 v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json')
 assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==61
 assert v['new_general_declarations']==49 and v['new_worked_control_declarations']==12
 assert len(v['records'])==140 and a['resolved_source_phase_pairs']==140
 assert a['result']=='import-resolution-audit-pass' and a['verification']==b(HERE/'verification.json')
 assert v['runtime_composed_cases']==34 and v['digest_capture_pipeline_composed']
 index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json')
 progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
 assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1620
 assert not index.get('digest_capture_packages') and seq['current_unit']=='K04'
 assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
 driver=N/'check_current_review.py';s=driver.read_text()
 marker="index.get('digest_packages', [])):";end='    assert len(declarations) == len(set(declarations))'
 assert s.count(marker)==s.count(end)==1
 readout=H/'execution/PROGRESS.md';old='making 1620 distinct verified candidate declarations in total.'
 assert readout.read_text().count(old)==1
 files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json',
  'candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md',
  'refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md',
  'independent_formalization':'FORMALIZATION.md','control_index':'control-index.json'}
 package={'unit':'K02-digest-capture','kind':'relation.addresses-intent','theorems':61,'general_declarations':49,'worked_control_declarations':12,
  'digest_capture_pipeline_composed':True,'digest_capture_exactness_proved':True,
  'digest_capture_all_input_catalog_exactness_proved':True,'digest_capture_envelope_order_retention_proved':True,
  'digest_capture_direct_refusal_meanings_proved':True,'capture_parse_digest_policy_adapters_implemented':True,
  'capture_remaining_policies_unchanged_proved':True,'configured_catalog_resource_guards_proved':True,
  'authenticated_digest_profile_selection_proved':False,'authenticated_capture_proved':False,
  'complete_source_refinement':False,'inherited_discharges':0}
 for key,name in files.items():package[key]=b(HERE/name)
 index['digest_capture_packages']=[package];index['digest_capture_candidate_theorems']=61
 index['total_distinct_new_candidate_theorems']=1681;save(N/'formal-preparation-index.json',index)
 seq['candidate_fragment_theorems']=1681;seq['candidate_digest_capture_packages']=1;save(N/'sequential-review.json',seq)
 progress['candidate_fragment_theorems']=1681;progress['digest_capture_candidate_theorems']=61;progress['candidate_digest_capture_packages']=1
 for key,name in files.items():progress['K02_digest_capture_'+key]=b(HERE/name)
 for value in progress.values():
  if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:
   value.update(b(ROOT/value['path']))
 save(H/'execution/plan.json',plan)
 s=s.replace(marker,"index.get('digest_packages', []) +\n                    index.get('digest_capture_packages', [])):")
 block='''        if package.get('digest_capture_pipeline_composed'):
            for key in ['digest_capture_pipeline_composed','digest_capture_exactness_proved',
                        'digest_capture_all_input_catalog_exactness_proved','digest_capture_envelope_order_retention_proved',
                        'digest_capture_direct_refusal_meanings_proved','capture_parse_digest_policy_adapters_implemented',
                        'capture_remaining_policies_unchanged_proved','capture_conditional_authentication_bridge_proved',
                        'configured_catalog_resource_guards_proved','whole_original_fixture_runtime_composition_checked']:
                assert proof[key] is True
            for key in ['authenticated_digest_profile_selection_proved','authenticated_capture_proved',
                        'authenticated_full_source_policy_realization_proved','JSON_schema_semantics_interpreter_proved',
                        'whole_K02_source_refinement_proved','external_standard_translation_reviewed','collision_freedom_proved',
                        'supported_resource_envelope_measured','public_outcome_classification_implemented',
                        'independent_checker_run','original_positive_kernel_hash_controls']:
                assert proof[key] is False
            assert proof['new_general_declarations']==49 and proof['new_worked_control_declarations']==12
            assert len(proof['records'])==140 and proof['runtime_composed_cases']==34
            read(ROOT/proof['context_pack']['path'])
            capture=read(ROOT/proof['source_capture']['path'])
            assert capture['profile_and_owner_review_roots_synthetic'] and not capture['authenticated_capture_proved']
            controls=read(ROOT/proof['control_index']['path'])
            assert len(controls['runtime_cases'])==34 and len(controls['kernel_control_declarations'])==12
            assert controls['profile_and_owner_review_roots_synthetic'] and not controls['original_positive_kernel_hash_controls']
            source=(ROOT/proof['sources'][-2]['path']).read_text()
            assert Path(proof['sources'][-2]['path']).stem=='DigestCaptureControls'
            for row in controls['original_fixtures']:
                original=(ROOT/row['original_bytes']['path']).read_bytes()
                assert len(original)==row['byte_count'] and hashlib.sha256(original).hexdigest()==row['computed_sha256']
                line='def '+row['kind']+'Capture : CandidateBindingCapture.Envelope := ⟨'+row['kind']+'Bytes,'+str(row['byte_count'])+',profile.ref,'+json.dumps(row['computed_sha256'])+'⟩'
                assert line in source
            for record in proof['records']:
                if Path(record['source']['path']).stem=='DigestCaptureRuntimeControls':
                    assert record['runtime_composed_cases']==34
                    assert (ROOT/record['log']['path']).read_text().strip().splitlines()==[row['expected_json'] for row in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['digest_capture_pipeline_composed'] and api['capture_parse_digest_policy_adapters_implemented']
            assert not api['N03_API_freeze'] and not api['authenticated_capture_proved']
'''
 s=s.replace(end,block+end);driver.write_text(s)
 total=round(sum(r['seconds'] for r in v['records']),3);maximum=max(r['seconds'] for r in v['records'])
 text='''

## Digest-checked original-byte capture and catalog integration

K02-digest-capture composes exact retained-byte record preparation with independent
SHA-256/profile/digest meaning. It checks count/envelope, digest, then source/frame
interpretation and retains the full submitted envelope. Ordered catalog preparation
checks every record/root without filtering, preserves their envelopes in order,
retains existing structural catalog obligations and interprets configured per-capture,
aggregate-byte and input-count guards. Unsupported profiles are refused even for empty
catalogs. Parse and digest policy adapters are implemented; profile ownership, Schema
and reviewed-entry predicates remain exactly the separate original requirements.

The package adds 61 declarations: 49 general results and 12 closed kernel controls.
Fresh isolated compilation and same-kernel replay contain 140 successful invocations
and 140 audited import resolutions. All 34 runtime composition cases pass in each
phase, including original resolution/role captures and catalogs, unchanged retained
bytes, same-count changes, truncation/appending, stale frames, unused bad roots,
resource guards and correctly hashed malformed/unsupported source data. Original
large-file positive hashes are runtime comparisons, not separately kernel-reduced
concrete digest controls. Candidate profile and review roots are synthetic.

The cumulative total is 1681 distinct candidate declarations. Elaboration/evaluation
and fresh compilation/replay total SECONDS seconds, with MAX seconds for the largest
invocation; these do not qualify an operational envelope. Authentic profile/issuer/
Schema/review realization, all nineteen complete source policies, independent checking,
standard translation, measured limits, all-kind theory and extension closure remain
open. All 263 inherited IDs remain pending, zero new discharges are claimed, and the
90 original discharges retain scope. K04 and global D01-D08 reviews remain pending.
N01 remains in progress; N02/N03 and all twenty tasks retain their completion gates.
The full objective remains active; no publication, deployment or promotion occurs.
'''.replace('SECONDS',str(total)).replace('MAX',str(maximum))
 readout.write_text(readout.read_text().replace(old,'and digest-capture/catalog integration adds 61, making 1681 distinct verified candidate declarations in total.')+text)
 print(json.dumps({'registered':'K02-digest-capture','new_declarations':61,'total_candidate_declarations':1681,'inherited_discharges':0}))
if __name__=='__main__':run()
