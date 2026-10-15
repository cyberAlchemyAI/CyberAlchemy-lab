"""Actual selected replay and deterministic three-lens question materialization."""
import argparse
from datetime import datetime,timezone
from common import *
from selection import verify
from scope import governed_scope,native_source_scope
from model import Model
STATE='project-state:cyberalchemy-v2-to-lab-migration:decision-0072@candidate.1'
DECISION='recorded-decision:CAL-DECISION-0073-FIRST-GOVERNED-AGENT-WORK-EPISODE-ADMISSION'
CAPABILITY='product-capability:cyberalchemy-lab:governed-knowledge-lifecycle@foundation.1'
def request(scope,query,root,obligations,*,direction='outgoing',predicates=None,depth=4,nodes=100,edges=200):
    from contract import SCOPES
    return {'schema_version':'lab-three-lens-query/v1-candidate','query_id':query,'root':root,'scope_ref':scope,'admission_as_of':SCOPES[scope],
        'view':'historical' if scope=='historical-d73-slice' else 'current','direction':direction,'edge_selection':predicates or [],
        'limits':{'depth':depth,'nodes':nodes,'edges':edges},'obligations':obligations}
def cases(scope,model):
    if scope=='historical-d73-slice':
        return {'lifecycle':request(scope,'lifecycle-slice','Lifecycle',['current-state','separate-project-histories','state-admission','exact-predecessor-path']),
            'authority':request(scope,'authority-explanation',DECISION,['recorded-admission','exact-authorization','effect-scope']),
            'provenance':request(scope,'capability-provenance',CAPABILITY,['exact-lineage'],predicates=['relation.derives-from'],depth=1)}
    if scope=='d75-selected-source':
        return {'lifecycle-D75':request(scope,'lifecycle-slice','Lifecycle',['current-state','separate-project-histories','state-admission','exact-predecessor-path'])}
    first=next(v for v,e in sorted(model.p['subjects'].items()) if e['kind']=='ontology-node')
    return {'native-source-lineage':request(scope,'capability-provenance',first,['ontology-event-join'],direction='both',depth=2,nodes=200,edges=200)}
def run(scope_ref,out,pin):
    manifest=verify(pin);out=Path(out);require(out.is_relative_to(PACKAGE/'coverage'),'output outside declared candidate coverage root')
    out.mkdir(parents=True,exist_ok=False);checks=[]
    factory=native_source_scope() if scope_ref=='O05-source-interpretation' else governed_scope(scope_ref)
    with factory as scope:
        model=Model(scope);results={}
        for name,req in cases(scope_ref,model).items():
            response=model.query(req);repeat=model.query(copy.deepcopy(req));require(encoded(response)==encoded(repeat),'same-cut query nondeterministic')
            rows=response['coverage']['subject_rows'];require(len(rows)==len({r['version_ref'] for r in rows})==len(model.p['subjects']),'selected subject accounting omitted/duplicated')
            require(sum(response['coverage']['partition'].values())==len(rows),'mapped/unresolved/excluded partition incomplete')
            emit(out/(name+'.json'),response);results[name]={'response_binding':bind(out/(name+'.json')),'response_digest':digest(response),'status':response['result_status'],
                'counts':response['coverage']['partition'],'nodes':len(response['subjects']),'edges':len(response['connections']),'gaps':len(response['gaps'])}
            checks.append({'name':name+'-same-cut-determinism-and-partition','result':'PASS'})
        if scope_ref=='historical-d73-slice':
            values={k:load(ROOT/v['response_binding']['path']) for k,v in results.items()}
            require(values['lifecycle']['result_status']=='partial','D73 unresolved predecessor must remain partial')
            claim=next(v for v in values['lifecycle']['claims'] if v['obligation']=='current-state')
            require(claim['basis']['selected_state_ref']==STATE and claim['basis']['content_cursor']=='decision:0072','D73 current state/content epoch mismatch')
            histories=values['lifecycle']['source_snapshot']['histories'];require(histories['project-semantic-event-history']['cursor']==histories['project-governance-event-history']['cursor']==2,'D73 separate Project cursors differ')
            require(histories['ontology-semantic'] is None and histories['ontology-governance'] is None,'Project cursors collapsed into ontology events')
            require(values['authority']['result_status']=='complete' and values['provenance']['result_status']=='complete','recorded authority/one-hop lineage expected complete')
            require(any(g['kind']=='unresolved-global-connection' for g in values['lifecycle']['gaps']),'exact version gaps omitted')
            require(any(g['kind']=='unresolved-represented-revision' for g in values['lifecycle']['gaps']),'Project Node mismatch hidden')
            checks.append({'name':'three-original-written-C1-answers','result':'PASS'})
        if scope_ref=='O05-source-interpretation':
            require(len(model.scope.reconciliation)==140 and sum(v['disposition']=='block' for v in model.scope.reconciliation)==9,'original source dependency accounting incomplete')
            require(sum(v['mode']=='source-local-interpretation' for v in model.edges.values())==50,'exact fifty local ontology edges missing')
            require(sum('native_join' in v for v in model.nodes.values())==88,'exact ontology native event joins incomplete')
            require(model.histories()['ontology-semantic']['cursor']==model.histories()['ontology-governance']['cursor']==88,'native cursors collapsed/missing')
            require(model.histories()['project-semantic-event-history'] is None,'native cursor substituted for Project cursor')
            checks.append({'name':'actual-native-original-event-and-local-interpretation-joins','result':'PASS'})
        require(scope.guard()['state']=='current','sources drifted during actual question run')
    require(scope.closed,'query scope remains reusable after closure');verify(pin)
    emit(out/'result.json',{'result':'PASS','scope_ref':scope_ref,'selection_binding':pin,'questions':results,'checks':checks,
        'observed_at':datetime.now(timezone.utc).isoformat(),'closed_scope':True,'owned_query_stores_removed':True,
        'actual_owner_outcome':None,'authority_effect':'none','native_graph_acceleration_selected':False})
    return bind(out/'result.json')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('scope');parser.add_argument('output');parser.add_argument('selection_path');parser.add_argument('selection_sha256');args=parser.parse_args()
    print(json.dumps(run(args.scope,args.output,{'path':args.selection_path,'sha256':args.selection_sha256}),sort_keys=True))
