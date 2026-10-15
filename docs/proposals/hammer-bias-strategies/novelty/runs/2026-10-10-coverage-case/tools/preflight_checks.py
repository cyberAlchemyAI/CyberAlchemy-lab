"""Meaningful guards for the known identity/reference failures; no scored writes."""
import copy, importlib.util, json
from pathlib import Path

P=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('coverage_runtime',P/'tools/coverage_runtime.py')
R=importlib.util.module_from_spec(s);s.loader.exec_module(R)
T=R.T
checks=[]
def good(name,fn):
    fn();checks.append({'id':name,'status':'pass'})
def bad(name,fn):
    try:fn()
    except (ValueError,KeyError,TypeError,StopIteration):checks.append({'id':name,'status':'pass'});return
    raise AssertionError(name+' was incorrectly accepted')
value=R.read(P/'inputs/fresh-case-and-archive.v1.json')
good('fresh_case_schema',lambda:R.validate_case(value))
c=R.case();allowed=T.case_refs(c);ref=sorted(allowed)[0]
assert (P/'outputs').is_dir()
assert not list((P/'outputs').glob('*.json'))
checks.append({'id':'actual_scored_parent_empty','status':'pass'})
for j in R.jobs():
    base=(P/'prompts/base'/(j['job_id']+'.txt')).read_text()
    assert 'Use python3 as the available interpreter' in base
    assert 'CONDITION_ID='+json.dumps(j['condition'])+'\n' in base
    literal=T.literal_prompt(j,base.encode(),R.output(j['job_id']),{'case':c}).decode()
    assert T.source_registry(c)==sorted(allowed)
    assert 'ALLOWED_SOURCE_REFS_JSON:\n'+json.dumps(sorted(allowed),ensure_ascii=False)+'\n' in literal
checks.append({'id':'ten_uniform_literal_identity_and_registry_headers','status':'pass'})
concern={'job_id':'NX-INV','case_id':'NX','role':'INV','dependency':'stipulated dependency','surviving_outcome':'valued function','predictions':[{'account':'one','when':'probe','result':'first'},{'account':'two','when':'probe','result':'second'}],'source_refs':[ref],'unknowns':[]}
good('valid_concern_schema',lambda:T.validate_output(R.job('NX-INV'),concern,c))
for wrong in ('NX','A1','job_id'):
    v=copy.deepcopy(concern);v['source_refs']=[wrong]
    bad('reject_nonfact_ref_'+wrong,lambda v=v:T.validate_output(R.job('NX-INV'),v,c))
st={'job_id':'NX-B-stage1','case_id':'NX','policy':'B','core':[{'id':'K1','text':'core','source_refs':[ref]}],'residue':[{'id':'Z1','text':'residue','source_refs':[ref]}],'tension':{'account_a':'one','account_b':'two','prediction_a':'first','prediction_b':'second'}}
good('valid_exact_B_machine_policy',lambda:T.validate_output(R.job('NX-B-stage1'),st,c))
v=copy.deepcopy(st);v['policy']='S05'
bad('reject_human_method_as_machine_policy',lambda:T.validate_output(R.job('NX-B-stage1'),v,c))
v=copy.deepcopy(st);v['core'][0]['text']='word '*650
bad('enforce_stage600_normalized_words',lambda:T.validate_output(R.job('NX-B-stage1'),v,c))
st2={'job_id':'NX-B-stage2','case_id':'NX','summary':[{'id':'S1','text':'summary','source_refs':[ref]}],'residue':[{'id':'Z1','text':'residue','source_refs':[ref]}]}
good('stage2_both_source_bound_branches',lambda:T.validate_output(R.job('NX-B-stage2'),st2,c))
zero={'job_id':'NX-B-builder','case_id':'NX','cards':[],'no_opening_reason':'No distinct feasible opening survived.'}
good('valid_explicit_zero_opening',lambda:T.validate_output(R.job('NX-B-builder'),zero,c,['S1']))
card={'id':'C1','anchor':'required function','mutation':'change one dependency','construction':'feasible operation','rival':'ordinary operation','probe':'one contrasting observation','prediction_candidate':'first result','prediction_rival':'second result','defeat':'absence of difference','resources':[c['resources'][0]['id']],'source_refs':[ref],'residue_refs':['S1'],'burden':'finite work','unknowns':[]}
b={'job_id':'NX-B-builder','case_id':'NX','cards':[card],'no_opening_reason':None}
good('summary_only_received_supplement_ID',lambda:T.validate_output(R.job('NX-B-builder'),b,c,['S1']))
v=copy.deepcopy(b);v['cards'][0]['residue_refs']=['Z1']
bad('reject_unreceived_residue_reference',lambda:T.validate_output(R.job('NX-B-builder'),v,c,['S1']))
v=copy.deepcopy(b);v['cards']=[dict(card,id='C'+str(i)) for i in range(3)]
bad('builder_maximum_two_cards',lambda:T.validate_output(R.job('NX-B-builder'),v,c,['S1']))
packet={'job_id':'NX-review1','case_id':'NX','units':[{'unit_id':'U1','status':'valid'},{'unit_id':'U2','status':'gated'}],'cards':[{'card_id':'Q1','unit_id':'U1'}],'archive':[{'id':'A1'},{'id':'A2'},{'id':'A3'}]}
review={'job_id':'NX-review1','case_id':'NX','units':[{'unit_id':'U1','status':'valid','reason':'valid declaration'},{'unit_id':'U2','status':'gated','reason':'missing predecessor'}],'cards':[dict(card_id='Q1',unit_id='U1',reason='test coverage',**{a:None for a in T.RUBRIC['axes']})],'archive_pairs':[{'card_id':'Q1','archive_id':'A'+str(i),'relation':'unknown','reason':'uncertainty retained'} for i in (1,2,3)],'candidate_pairs':[]}
good('complete_review_and_unknowns',lambda:T.validate_review(review,packet))
v=copy.deepcopy(review);v['archive_pairs'].pop()
bad('reject_missing_archive_pair',lambda:T.validate_review(v,packet))
v=copy.deepcopy(review);v['units'][1]['status']='valid'
bad('reject_gated_relabel_as_valid',lambda:T.validate_review(v,packet))
print(json.dumps({'verdict':'pass','checks':checks,'actual_native_calls_added':0,'scored_outputs_written':0},indent=2))
