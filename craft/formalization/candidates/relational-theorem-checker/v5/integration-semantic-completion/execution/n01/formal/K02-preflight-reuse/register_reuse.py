"""Register exact reuse refinement while disclosing the dependency reuse method."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def run():
    proof=read(HERE/'verification.json');audit=read(HERE/'import-resolution-audit.json')
    assert proof['result']=='candidate-fragment-pass' and proof['new_declaration_count']==23
    assert proof['new_general_declarations']==23 and proof['new_worked_control_declarations']==0
    assert len(proof['records'])==audit['resolved_source_phase_pairs']==12 and proof['runtime_composed_cases']==22
    assert len(proof['reused_dependencies'])==176 and proof['local_dependency_rebuild'] is False
    assert audit['verification']==binding(HERE/'verification.json') and audit['result']=='import-resolution-audit-pass'
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json')
    progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1849
    assert not index.get('preflight_reuse_packages') and seq['current_unit']=='K04' and seq['accepted_meaning_count']==4
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md','independent_formalization':'FORMALIZATION.md','control_index':'control-index.json','context_pack':'context-pack.json'}
    package={'unit':'K02-preflight-reuse','kind':'relation.addresses-intent','theorems':23,'general_declarations':23,'worked_control_declarations':0,'reusable_entry_equal_guarded':True,'complete_source_refinement':False,'inherited_discharges':0}
    for k,f in files.items():package[k]=binding(HERE/f)
    driver=N/'check_current_review.py';source=driver.read_text();marker="index.get('evidence_resource_packages', [])):";end='    assert len(declarations) == len(set(declarations))'
    assert source.count(marker)==source.count(end)==1
    block='''        if package.get('reusable_entry_equal_guarded'):
            assert proof['reusable_entry_equal_guarded'] is True
            assert proof['new_general_declarations']==23 and proof['new_worked_control_declarations']==0
            assert len(proof['records'])==12 and proof['runtime_composed_cases']==22
            assert proof['local_dependency_rebuild'] is False
            assert not proof['supported_resource_envelope_measured'] and not proof['real_authoritative_snapshot_provider']
            assert not proof['live_consumer_integration'] and not proof['N03_API_freeze']
            prior=read(ROOT/proof['prior_verification']['path'])
            prior_audit=read(ROOT/proof['prior_import_audit']['path'])
            assert prior['result']=='candidate-fragment-pass' and prior_audit['verification']==proof['prior_verification']
            expected_reused=Counter((row['phase'],row['source']['path'],row['olean']['sha256']) for row in prior['records'])
            actual_reused=Counter((row['phase'],row['source']['path'],row['prior_output']['sha256']) for row in proof['reused_dependencies'])
            assert expected_reused==actual_reused and len(proof['reused_dependencies'])==176
            for row in proof['reused_dependencies']:
                assert row['prior_output']['sha256']==row['reused_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==(ROOT/package['verification']['path']).parent/row['phase']
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['resolved_source_phase_pairs']==12 and audit['verification']==package['verification']
            controls=read(ROOT/proof['control_index']['path'])
            assert len(controls['runtime_cases'])==22 and not controls['real_authoritative_snapshot_provider']
            runtime=ROOT/proof['sources'][-1]['path'];assert runtime.stem=='ReuseRuntimeControls'
            assert re.findall(r'^#eval (.*)$',runtime.read_text(),re.M)==[row['expression'] for row in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='ReuseRuntimeControls':
                    assert row['runtime_composed_cases']==22
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and matrix['inherited_discharges']==0
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['live_consumer_integration'] and not api['N03_API_freeze']
'''
    source=source.replace(marker,"index.get('evidence_resource_packages', []) +\n                    index.get('preflight_reuse_packages', [])):").replace(end,block+end);compile(source,str(driver),'exec')
    out=H/'execution/PROGRESS.md';text=out.read_text();old='making 1849 distinct verified candidate declarations in total.';assert text.count(old)==1
    text=text.replace(old,'and certified preflight reuse adds 23, making 1872 distinct verified candidate declarations in total.')
    text+='''

Certified preflight reuse

K02-preflight-reuse adds 23 general declarations and proves the reusable entrypoint
returns exactly the same full BoundedOutcome as the prior guarded entrypoint for
all inputs/configurations. This includes every refusal, source index/numeric token
and prepared stage. Certified inputs retain independently specified envelope,
digest, scalar-byte and numeric meanings; typed preparation consumes retained ASTs
without repeating byte parsing or digest evaluation. Original input ordering and
every duplicate occurrence are preserved. Every capture is preflighted before
any typed decoding on this entrypoint.

All 12 fresh new-module compile/replay invocations and import audits pass, with
46 axiom inspections and 22 runtime cases in each phase. The 88 unchanged dependency
modules were not rebuilt: exact source/output bindings to their registered prior
compile/replay phases were verified and reused. This method is explicitly disclosed
and is neither a fresh dependency rebuild nor independent checking. Peak memory
with retained ASTs and whole-process time remain unmeasured.

The consumer inventory finds candidate APIs/proofs/controls, not a live application
cutover target. Legacy unguarded functions remain callable. Actual authentic-root
and remaining full-source policies, mandatory consumers, all-kind/theory closure,
independent checking, all seven extensions, measured limits and final actual use
assessment remain required. All 263 inherited IDs remain open, all 90 original
discharges retain scope, and K04/global policies remain pending. Only N00 is accepted;
the complete plan remains active and incomplete with 1872 candidate declarations.
'''
    index['preflight_reuse_packages']=[package];index['preflight_reuse_candidate_theorems']=23;index['total_distinct_new_candidate_theorems']=1872
    seq['candidate_fragment_theorems']=1872;seq['candidate_preflight_reuse_packages']=1
    progress['candidate_fragment_theorems']=1872;progress['preflight_reuse_candidate_theorems']=23;progress['candidate_preflight_reuse_packages']=1
    for k,f in files.items():progress['K02_preflight_reuse_'+k]=binding(HERE/f)
    save(N/'formal-preparation-index.json',index);save(N/'sequential-review.json',seq)
    for v in progress.values():
        if isinstance(v,dict) and v.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:v.update(binding(ROOT/v['path']))
    save(H/'execution/plan.json',plan);driver.write_text(source);out.write_text(text)
    print('Registered preflight reuse; 1872 candidate declarations; zero inherited discharges.')
if __name__=='__main__':run()
