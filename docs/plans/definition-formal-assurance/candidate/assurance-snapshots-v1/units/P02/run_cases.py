"""Create-only hand-derived theory records and actual search/replay evidence."""
import json
import sys
import tracemalloc
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
sys.path[:0]=[str(IMPL/'providers'),str(IMPL),str(IMPL/'tests')]
import finite as f
import test_A01 as fixtures


def make(extra=()):
    core=fixtures.payloads()['interpretation'];core['declarations']+=list(extra);subject=f.ir.compile_interpretation(core)
    return subject,{row['local_symbol_id']:row['canonical_id'] for row in subject['origins']}


def main():
    records=[];subject,ids=make();x={'op':'var','name':'x'};y={'op':'var','name':'y'}
    def pred(name,*args):return {'op':'pred','name':ids[name],'args':list(args)}
    def quant(op,body,var='x'):return {'op':op,'var':var,'sort':ids['Object'],'body':body}
    p=pred('P',x)
    exactly_one=quant('exists',{'op':'and','args':[p,quant('forall',{'op':'implies','left':pred('P',y),'right':{'op':'eq','left':y,'right':x}},'y')]})
    unmarked=quant('exists',{'op':'not','arg':p});population=quant('exists',p)
    def record(identity,subject,T,I,Q,cards,expected,derivation,mode='witness',budgets=None):
        result=f.search(subject,T,I,Q,cards,mode,budgets)
        if result['status']!=expected:raise ValueError('Unexpected controlled result: '+identity+' '+result['status'])
        replay=f.replay(subject,result,T,I,Q,cards,expected_mode=mode) if result['witness'] else {'result':'not-applicable','reason':'No witness result; bounded exhaustion requires its separate completeness interpretation.'}
        records.append({'case_id':identity,'source_kind':'synthetic-hand-derived-theory','subject':subject,'theory':T,'populations':I,'query':Q,'cardinalities':cards,'mode':mode,'hand_expected_status':expected,'independent_hand_derivation':derivation,'actual':result,'witness_replay':replay})
    record('one-marked-two-members',subject,[exactly_one],[population],unmarked,{ids['Object']:2},'witness-found','A two-member set with exactly one marked member has another unmarked member. The premise and population constrain one shared interpretation.')
    record('one-marked-two-members-bounded',subject,[exactly_one],[population],unmarked,{ids['Object']:2},'bounded-supported','There are four subsets of a two-member set; exactly two are singleton marked sets, and both leave one unmarked member.','bounded-validity')
    record('one-marked-one-member',subject,[exactly_one],[population],unmarked,{ids['Object']:1},'bounded-no-witness','Exactly one marked member in a singleton leaves no unmarked member. This says nothing about larger domains.')
    record('inhabited-not-universal-countermodel',subject,[],[population],quant('forall',p),{ids['Object']:2},'countermodel-found','A singleton marked subset of a two-member domain is inhabited and fails universal marking.','countermodel')
    scope=subject['input_core']['scope'];subject,ids=make([{'kind':'total-function','symbol_id':'next','scope':scope,'argument_sorts':['Object'],'result_sort':'Object','definedness_policy':None}]);nextx={'op':'fn','name':ids['next'],'args':[x]};twice={'op':'fn','name':ids['next'],'args':[nextx]}
    involution=quant('forall',{'op':'eq','left':twice,'right':x});no_fixed=quant('forall',{'op':'not','arg':{'op':'eq','left':nextx,'right':x}});truth={'op':'and','args':[]}
    record('fixed-point-free-involution-two',subject,[involution,no_fixed],[],truth,{ids['Object']:2},'witness-found','The swap map on a two-member set is total, its square is identity, and neither member is fixed.')
    record('fixed-point-free-involution-one',subject,[involution,no_fixed],[],truth,{ids['Object']:1},'bounded-no-theory-model','The only total singleton endofunction fixes its member, so no fixed-point-free involution exists at cardinality one; the two-member case prevents an unbounded inconsistency claim.')
    subject,ids=make([{'kind':'relation','symbol_id':'R','scope':scope,'argument_sorts':['Object']*9}]);cards={ids['Object']:3};false={'op':'or','args':[]}
    tracemalloc.start()
    try:
        result=f.search(subject,[],[],false,cards,budgets={'max_interpretations':512});_,peak=tracemalloc.get_traced_memory()
    finally:tracemalloc.stop()
    if result['status']!='resource-limit' or result['counts']['visited']!=512 or peak>=8_000_000:raise ValueError('Streaming resource control failed')
    records.append({'case_id':'factored-space-prefix','source_kind':'synthetic-resource-control','subject':subject,'theory':[],'populations':[],'query':false,'cardinalities':cards,'mode':'witness','hand_expected_status':'resource-limit','independent_hand_derivation':'A nine-argument relation over three-member carriers has 3^9=19683 tuples and 2^19683 extensions. Visiting 512 interpretations cannot exhaust this scope.','actual':result,'tracemalloc_peak_bytes':peak,'witness_replay':{'result':'not-applicable','reason':'Resource limit has no witness or absence evidence.'}})
    value={'schema_version':'definition-assurance-finite-worked-theories/v1-candidate','authority_effect':'none','whole_current_definition_translations':0,'records':records,'review_kind':'candidate-agent-controls with independent hand expectations; not independent source-owner review','claim_ceiling':'Actual searches and complete-witness replays of two hand-derived theories plus countermodel/resource controls. No generic correctness theorem, unbounded absence or current-definition fidelity.'}
    output=Path(__file__).resolve().parent/'worked-theories.json'
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'cases':len(records),'witness_replays':sum(row['witness_replay']['result']=='PASS' for row in records),'traced_peak_bytes':peak,'whole_definition_translations':0},indent=2))


if __name__=='__main__':main()
