"""Register source-format preparation without claiming theorem or provider discharge."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
N,H,ROOT=HERE.parents[1],HERE.parents[3],HERE.parents[9]
def binding(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def read(path):return json.loads(path.read_text())
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def run():
    proof=read(HERE/'verification.json')
    assert proof['result']=='candidate-complete-body-controls-pass'
    assert proof['profile_count']==proof['positive_body_count']==7
    assert proof['runtime_case_count']==308 and proof['required_top_level_field_counterexamples']==115
    assert proof['nested_required_counterexamples']==26 and proof['array_constraint_counterexamples']==83
    assert proof['scalar_regex_whitespace_exhaustion_count']==1112064 and proof['regex_runtime_comparison_count']==221
    assert proof['new_general_theorems']==proof['inherited_discharges']==0
    index,seq,plan=read(N/'formal-preparation-index.json'),read(N/'sequential-review.json'),read(H/'execution/plan.json')
    progress=next(task for task in plan['tasks'] if task['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1947
    assert not index.get('payload_provider_preparations')
    assert seq['current_unit']=='K04' and seq['accepted_meaning_count']==4
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','profile_manifest':'profile-manifest.json',
           'independent_formalization':'FORMALIZATION.md','pattern_formalization':'PATTERN-FORMALIZATION.md',
           'candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md',
           'next_implementation_plan':'NEXT-IMPLEMENTATION.md','source_policy_gap_map':'source-policy-gap-map.json',
           'component_completion_audit':'component-completion-audit.json'}
    driver=N/'check_current_review.py';source=driver.read_text()
    marker='    assert len(declarations) == len(set(declarations))'
    assert source.count(marker)==1
    source=source.replace(marker,"    for preparation in index.get('payload_provider_preparations', []):\n        proof=read(ROOT/preparation['verification']['path'])\n        assert proof['result']=='candidate-complete-body-controls-pass'\n        assert proof['profile_count']==proof['positive_body_count']==7\n        assert proof['runtime_case_count']==len(proof['runtime_cases'])==308\n        assert len({case['id'] for case in proof['runtime_cases']})==308\n        assert all(case['observed']==case['expected'] for case in proof['runtime_cases'])\n        for case in proof['runtime_cases']:\n            if case['required_schema_keyword']:\n                assert case['observed']=='schema' and case['required_schema_keyword'] in {item['keyword'] for item in case['detail']}\n        assert proof['required_top_level_field_counterexamples']==115\n        assert proof['nested_required_counterexamples']==len(proof['nested_required_paths'])==26\n        assert proof['array_constraint_counterexamples']==len(proof['array_constraint_paths'])==83\n        assert proof['scalar_regex_whitespace_exhaustion_count']==1112064\n        assert proof['regex_runtime_comparison_count']==221 and len(proof['observed_python_ecmascript_differences'])==19\n        assert proof['exact_two_pinned_pattern_forms_implemented']\n        assert proof['new_general_theorems']==proof['inherited_discharges']==0\n        for flag in ['general_lean_decoder_correspondence_proved','general_json_schema_semantics_proved',\n                     'regex_dialect_correspondence_proved','owned_profile_admission_proved',\n                     'approved_kind_specific_payload_decoders_realized','real_authoritative_source_provider',\n                     'integrated_into_lean_full_entrypoint','all_eighteen_remaining_source_policies_realized',\n                     'independent_checker_run','supported_resource_envelope_measured','N01_accepted']:\n            assert proof[flag] is False\n        manifest=read(ROOT/preparation['profile_manifest']['path'])\n        assert {row['kind'] for row in manifest['profiles']}=={'intent','agent-assignment','goal','product','product-capability','project','research-inquiry'}\n        required=set()\n        for row in manifest['profiles']:\n            artifact,schema=read(ROOT/row['artifact']['path']),read(ROOT/row['schema']['path'])\n            assert artifact['schema_digest']==row['schema']['sha256']\n            assert artifact['schema_ref']==row['schema_ref'] and artifact['artifact_type_ref']==row['artifact_type_ref']\n            assert artifact['status']==row['source_status']=='candidate-unadmitted'\n            assert artifact['instance_contract']['identity_field']==row['identity_field']\n            assert row['identity_field']==('goal_id' if row['kind']=='goal' else 'node_id')\n            assert set(row['required_fields'])==set(schema['required'])\n            assert row['all_top_level_fields']==sorted(schema['properties'])\n            required.update((row['kind'],field) for field in schema['required'])\n        assert required=={tuple(path) for path in proof['required_top_level_field_paths']} and len(required)==115\n        assert not manifest['owned_profile_admission'] and not manifest['authenticity_proved']\n        api=read(ROOT/preparation['candidate_api_contract']['path'])\n        for flag in ['caller_AST_allowed','caller_schema_definition_allowed','caller_approval_boolean_allowed',\n                     'body_trimming_allowed','source_identity_and_owner_inferred_from_strings',\n                     'general_lean_decoder_correspondence_proved','owned_profile_admission_proved',\n                     'integrated_into_lean_full_entrypoint','N03_API_freeze']:\n            assert api[flag] is False\n        assert api['original_candidate_status_preserved'] and api['inherited_discharges']==0\n        gaps=read(ROOT/preparation['source_policy_gap_map']['path'])\n        assert gaps['remaining_slot_count']==len(gaps['rows'])==18\n        prior=read(ROOT/gaps['original_remaining_policy_map']['path'])\n        assert {row['slot'] for row in gaps['rows']}=={row['slot'] for row in prior['rows']}\n        assert all(row['status']=='provider-realization-incomplete' and not row['inherited_discharge'] for row in gaps['rows'])\n        assert not gaps['all_original_source_policy_providers_realized'] and not gaps['unconditional_original_source_interpretation_proved']\n        completion=read(ROOT/preparation['component_completion_audit']['path'])\n        assert completion['result']=='source-format-prototype-implemented-with-formal-and-authority-gaps'\n        assert completion['new_general_theorems']==completion['inherited_discharges']==0 and not completion['N01_accepted']\n    assert len(index.get('payload_provider_preparations', []))==seq.get('candidate_payload_format_providers',0)==progress.get('candidate_payload_format_providers',0)\n"+marker)
    source=source.replace("checked[node['path']] = binding(path)['sha256']","checked[node['path']] = hashlib.sha256(path.read_bytes()).hexdigest()")
    compile(source,str(driver),'exec')
    completion={'task':'N01','unit':HERE.name,'result':'source-format-prototype-implemented-with-formal-and-authority-gaps',
                'verification':binding(HERE/'verification.json'),'review':binding(HERE/'MODEL-REVIEW.md'),
                'api':binding(HERE/'candidate-api-contract.json'),'remaining_policy_map':binding(HERE/'source-policy-gap-map.json'),
                'requirements':[{'id':'seven-complete-original-source-formats','status':'implemented-and-exercised'},
                                {'id':'exact-original-schema-references-and-identities','status':'implemented-and-exercised'},
                                {'id':'pinned-ecmascript-pattern-semantics','status':'implemented-and-runtime-compared'},
                                {'id':'complete-general-lean-decoder-correspondence','status':'incomplete'},
                                {'id':'actual-owned-profile-admission-and-authentic-source','status':'incomplete'},
                                {'id':'full-entrypoint-and-mandatory-consumers','status':'incomplete'},
                                {'id':'independent-proof-checking-and-measured-limits','status':'incomplete'}],
                'new_general_theorems':0,'inherited_discharges':0,'N01_accepted':False,'authority_effect':'none'}
    save(HERE/'component-completion-audit.json',completion)
    package={'unit':HERE.name,'kind':'relation.addresses-intent','new_general_theorems':0,
             'inherited_discharges':0,'complete_source_refinement':False}
    package.update({key:binding(HERE/name) for key,name in files.items()})
    index['payload_provider_preparations']=[package]
    seq['candidate_payload_format_providers']=1
    progress['candidate_payload_format_providers']=1
    progress.update({'K02_complete_payload_'+key:binding(HERE/name) for key,name in files.items()})
    save(N/'formal-preparation-index.json',index);save(N/'sequential-review.json',seq)
    changed={str((N/name).relative_to(ROOT)) for name in ['formal-preparation-index.json','sequential-review.json']}
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in changed:value.update(binding(ROOT/value['path']))
    save(H/'execution/plan.json',plan);driver.write_text(source)
    progress_path=H/'execution/PROGRESS.md';text=progress_path.read_text()
    text+='\n\nComplete seven-kind payload source-format preparation\n\nK02-complete-payload-provider preserves all original body fields and exact schema\nreferences across Intent, Assignment, Goal, Product, Capability, Project and Inquiry.\nGoal uses goal_id; the other six use node_id. Three v1 artifact directories retain\ntheir actual v2 review schema references. All source types remain candidate-unadmitted.\n\nThe prototype passes 308 runtime controls: seven full original positive bodies,\n115 required top-level field omissions, 26 nested omissions, 83 array constraint\ncases and original hostile/byte/profile/digest cases. The two original regex forms\nare interpreted explicitly under ECMAScript; 221 runtime comparisons and all\n1,112,064 Unicode scalar whitespace checks pass. This fixes Python digit/anchor/\nwhitespace differences without altering schemas. Runtime comparison is not an\nindependent proof checker, and no new general theorem is claimed.\n\nA heterogeneous proved Lean Decoder and exact raw-AST/Python/Lean correspondence,\nactual owner admission, source issuance/identity/roles, all eighteen non-parser\npolicies and full-entrypoint/consumer integration remain required. All 263 inherited\nobligations remain open, 90 original discharges retain scope, and the candidate theorem\ncount stays 1947. K04 and global reviews remain pending; the full plan stays active.\n'
    progress_path.write_text(text)
    print('Registered seven complete payload-format preparations; 308 controls; 1947 theorems unchanged; no discharges.')
if __name__=='__main__':run()
