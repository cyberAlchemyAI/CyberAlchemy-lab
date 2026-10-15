"""Register verified candidate resource work without accepting semantics or completing the plan."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def run():
    proof=read(HERE/'verification.json');audit=read(HERE/'import-resolution-audit.json');shape=read(HERE/'schema-shape-audit.json')
    assert proof['result']=='candidate-fragment-pass' and proof['new_declaration_count']==55
    assert proof['new_general_declarations']==37 and proof['new_worked_control_declarations']==18
    assert len(proof['records'])==audit['resolved_source_phase_pairs']==176 and proof['runtime_composed_cases']==22
    assert audit['verification']==binding(HERE/'verification.json') and audit['result']=='import-resolution-audit-pass'
    assert shape['result']=='candidate-schema-shape-audit-pass' and len(shape['checks'])==25
    assert shape['api_contract']==binding(HERE/'candidate-api-contract.json')
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json')
    progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1794
    assert not index.get('evidence_resource_packages')
    assert seq['current_unit']=='K04' and seq['accepted_meaning_count']==4
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','candidate_api_contract':'candidate-api-contract.json','schema_shape_audit':'schema-shape-audit.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md','independent_formalization':'FORMALIZATION.md','control_index':'control-index.json'}
    package={'unit':'K02-evidence-resources','kind':'relation.addresses-intent','theorems':55,'general_declarations':37,'worked_control_declarations':18,'bounded_evidence_preparation_exact':True,'complete_source_refinement':False,'inherited_discharges':0}
    for key,name in files.items():package[key]=binding(HERE/name)
    driver=N/'check_current_review.py';source=driver.read_text()
    marker="index.get('profile_evidence_packages', [])):";end='    assert len(declarations) == len(set(declarations))'
    assert source.count(marker)==source.count(end)==1
    block='''        if package.get('bounded_evidence_preparation_exact'):
            for key in ['combined_authority_inclusive_budget_exact','numeric_guard_before_typed_decoding',
                        'decimal_power_exponents_bounded','bounded_evidence_preparation_exact',
                        'original_source_envelopes_retained','source_refusal_position_and_prefix_proved',
                        'local_data_refusal_meanings_exact']:
                assert proof[key] is True
            for key in ['real_authoritative_snapshot_provider','whole_K02_source_refinement_proved',
                        'independent_checker_run','supported_resource_envelope_measured','N03_API_freeze']:
                assert proof[key] is False
            assert proof['new_general_declarations']==37 and proof['new_worked_control_declarations']==18
            assert len(proof['records'])==176 and proof['runtime_composed_cases']==22
            read(ROOT/proof['context_pack']['path'])
            controls=read(ROOT/proof['control_index']['path'])
            assert len(controls['runtime_cases'])==22 and len(controls['imported_original_fixture_bindings'])==6
            assert controls['kernel_controls_are_typed_data_only'] and controls['huge_exponents_evaluated_only_through_preflight']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['numeric_eligibility_is_integrality']
            runtime=ROOT/proof['sources'][-1]['path'];assert runtime.stem=='ResourceRuntimeControls'
            assert re.findall(r'^#eval (.*)$',runtime.read_text(),re.M)==[row['expression'] for row in controls['runtime_cases']]
            for record in proof['records']:
                if Path(record['source']['path']).stem=='ResourceRuntimeControls':
                    assert record['runtime_composed_cases']==22
                    assert (ROOT/record['log']['path']).read_text().strip().splitlines()==[row['expected'] for row in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['N03_API_freeze'] and not api['configuration']['example_is_measured_policy']
            shape=read(ROOT/package['schema_shape_audit']['path'])
            assert shape['result']=='candidate-schema-shape-audit-pass' and len(shape['checks'])==25
            assert not shape['byte_decoder_equivalence_proved'] and not shape['measured_operational_policy']
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert matrix['inherited_discharges']==0
            for row in matrix['rows']:
                assert row['inherited_discharges']==0
                assert set(row.get('theorem_targets',[]))<=set(proof['new_declarations'])
'''
    source=source.replace(marker,"index.get('profile_evidence_packages', []) +\n                    index.get('evidence_resource_packages', [])):").replace(end,block+end)
    compile(source,str(driver),'exec')
    index['evidence_resource_packages']=[package];index['evidence_resource_candidate_theorems']=55;index['total_distinct_new_candidate_theorems']=1849
    seq['candidate_fragment_theorems']=1849;seq['candidate_evidence_resource_packages']=1
    progress['candidate_fragment_theorems']=1849;progress['evidence_resource_candidate_theorems']=55;progress['candidate_evidence_resource_packages']=1
    for key,name in files.items():progress['K02_evidence_resources_'+key]=binding(HERE/name)
    save(N/'formal-preparation-index.json',index);save(N/'sequential-review.json',seq)
    for v in progress.values():
        if isinstance(v,dict) and v.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:v.update(binding(ROOT/v['path']))
    save(H/'execution/plan.json',plan);driver.write_text(source)
    p=H/'execution/PROGRESS.md';text=p.read_text();old='making 1794 distinct verified candidate declarations in total.'
    assert text.count(old)==1
    text=text.replace(old,'and bounded evidence resource preparation adds 55, making 1849 distinct verified candidate declarations in total.')
    text+='''

Bounded evidence resource preparation

K02-evidence-resources adds 37 general declarations and 18 closed controls. All
176 fresh pinned compile/replay invocations, matching-phase import audits and 22
runtime controls in each phase pass. Authority bytes and its capture now count in
one combined aggregate/count/per-capture budget. Preserved numeric tokens are
checked before typed source decoding; exponent digit/magnitude and mantissa/token
bounds constrain the decimal powers used by the existing Nat evaluator. Huge
exponents in nested, unused and duplicate-key entries refuse through this guard.
Integral decimal/exponent spellings and negative zero retain their prior semantics.

The guarded entrypoint is equivalent to independent bounded prepared-data meaning,
retains all original envelopes, and exposes exact first-failed capture ordinal with
a checked prefix and actual numeric lexeme. Typed-data causes are profile absence,
authority-data absence and failed evidence joins; they are stage-level. One local
configuration schema passes 25 shape checks; this is not raw decoder equivalence.
The review and remaining implementation order are in the registered package.

Legacy unguarded functions remain callable; mandatory consumer integration is still
required. Preflight and legacy preparation reparse/rehash, operational time/memory
is unmeasured, and no actual authentic-root provider is realized. Same-kernel replay
is not independent checking. This component does not complete N01/N03/N14 or any
original inherited obligation. Four meanings remain accepted with K04 pending;
global D01-D08 assessments remain pending. All 263 inherited IDs remain pending,
all 90 original discharges retain scope, and only N00 is accepted (1/20). The full
41-kind/550-pair/seven-extension goal remains active and incomplete.
'''
    p.write_text(text)
    print('Registered K02-evidence-resources; 1849 distinct candidate declarations; zero inherited discharges.')
if __name__=='__main__':run()
