"""Actual inspected layouts, typed diagnostics and hostile display controls."""
from pathlib import Path
import copy
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p04.explain import describe,certificate_trace,classify_query,bound_read
from v3.p03.context import C,QualificationContext
sys.path.insert(0,str(BASE/'execution'))
import support as s
controls=[]
def check(name,condition):s.require(condition,'control failed '+name);controls.append({'name':name,'result':'pass'})
def negative(name,fn):
    try:fn()
    except Exception as e:controls.append({'name':name,'result':'pass','expected':'rejected','reason':str(e).splitlines()[0]});return
    raise AssertionError('unexpected acceptance '+name)

def adapt(proposal_path,payload_path,layout,name):
    request=s.read(BASE/'p01/request-fixture.json');request['proposal']=s.read(proposal_path);request['layout']=layout
    payload=s.read(payload_path);tag=lambda b:{'kind':'repo',**b}
    sys.path.insert(0,str(BASE/'p02'));import evidence as e
    manifest={'schema':'relational.proof-manifest/v3','identity':e.expected_identity(request),'change_class':'rule-only','witness':{'layout':layout,'modules':[{'role':role,'module':m['module'],'source':tag(m['source']),'olean':tag(m['olean'])} for role,m in zip(['combined'] if layout=='combined' else ['data','typed','closure','expansion'],payload['evidence']['actual'])]},'obligations':[o['id'] for o in C.required_inventory('rule-only')],'general':tag(payload['evidence']['general']['submission_source']),'projection':tag(payload['evidence']['projection'][0]['source']),'dependencies':tag(payload['evidence']['dependencies']),'bound_result':tag(s.binding(payload_path)),'generator':tag(s.binding(BASE/'p02/proof_layout.py')),'authority_effect':'none'}
    result={'schema':'relational.qualification-result/v3','status':'qualified-candidate','request_identity':C.identity(request),'run_id':'historical-inspection-fixture-'+name,'manifest':manifest,'claims':[{'kind':k,'model_class':payload['model_class'],'query_scope':payload['closure_scope'],'change_class':'rule-only','source_profile':request['source_profile'],'truth_assumptions':e.TRUTH_ASSUMPTIONS,'evidence_mode':'fresh-invocation-at-creation'} for k in ['complete-closure','model-expansion']],'resource_report':{'enforcement':'advisory','outcome':'completed','events':[{'kind':'scope','detail':'Exact wrapper of recorded original qualification, not a new fresh qualification.'}],'policy_identity':C.identity(request['resource_policy'])},'payload':tag(s.binding(payload_path)),'complete_closure':True,'application_authorized':False,'authority_effect':'none'}
    s.write(HERE/'fixtures'/(name+'-request.json'),request);s.write(HERE/'fixtures'/(name+'-result.json'),result)
    return request,result,payload

request=s.read(BASE/'p03/cli-request.json');result=s.read(BASE/'p03/cli-result.json');payload=bound_read(result['payload'])
context=QualificationContext(HERE/'inspection-runs',request['resource_policy'])
query=next(a for a in payload['closure'] if a['predicate']['id']=='ContractReady')
positive=describe(request,result,query,context)
check('actual-staged-rich-positive',positive['outcome']=='present' and len(positive['trace']['nodes'])==4)
check('exact-rule-slot-substitutions',all(n['substitution'] and n['rule']['hash'] for n in positive['trace']['nodes'] if n['kind']=='apply'))
check('exact-source-target-scope-kind-leaves',len(positive['supports'])==2 and {s['atom']['predicate']['id'] for s in positive['supports']}=={'ConformsTo','TargetKind'})
check('explanation-never-creates-replay-event',not context.live_event(result) and not positive['application_authorized'])
s.write(HERE/'positive-explanation.json',positive)

combined_req,combined_result,combined_payload=adapt(s.V2/'s06/recursive-proposal.json',s.V2/'s06/recursive-result.json','combined','combined')
combined_query=next(a for a in combined_payload['closure'] if a['predicate']['id']=='FreshReady')
combined=describe(combined_req,combined_result,combined_query)
check('actual-combined-inspected-positive',combined['outcome']=='present' and combined['trace']['nodes'])
s.write(HERE/'combined-explanation.json',combined)

wrong_req,wrong_result,wrong_payload=adapt(s.V2/'s13/wrong-scope-unseeded-fresh-cycle-proposal.json',s.V2/'s13/wrong-scope-unseeded-fresh-cycle-result.json','staged','wrong-scope')
absent=describe(wrong_req,wrong_result,query)
check('well-typed-complete-wrong-scope-cycle-absent',absent['outcome']=='absent-in-complete-profile' and absent['trace'] is None)
s.write(HERE/'wrong-scope-explanation.json',absent)

for name,modify,expected in [
    ('unknown-predicate',lambda q:q['predicate'].update(id='Unselected'),'outside-profile'),
    ('wrong-version',lambda q:q['predicate'].update(version='unselected-version'),'outside-profile'),
    ('wrong-predicate-digest',lambda q:q['predicate'].update(hash='0'*64),'outside-profile'),
    ('wrong-arity',lambda q:q['values'].append(q['values'][0]),'invalid-query'),
    ('wrong-sort',lambda q:q['values'].__setitem__(0,{'kind':'scope','value':'static'}),'invalid-query'),
    ('undeclared-reference',lambda q:q['values'][0].update(version='unknown-revision'),'outside-profile'),
    ('malformed-reference',lambda q:q['values'][0].pop('version'),'invalid-query'),
]:
    q=copy.deepcopy(query);modify(q);out=describe(request,result,q,context);check(name,out['outcome']==expected)
scope_query=copy.deepcopy(next(a for a in payload['closure'] if a['predicate']['id']=='ConformsTo'))
scope_query['values'][-1]['value']='undeclared-scope'
check('undeclared-scope-never-proved-absent',describe(request,result,scope_query,context)['outcome']=='outside-profile')

timeout=s.read(s.check(s.read(BASE/'p03/observed-timeout.json')['result']))
incomplete=describe(request,timeout,query,context)
check('timeout-never-proved-absent',incomplete['outcome']=='incomplete' and incomplete['trace'] is None)
s.write(HERE/'incomplete-explanation.json',incomplete)
limited=describe(request,result,query,context,trace_nodes=1)
check('bounded-trace-omissions-explicit',limited['outcome']=='present' and limited['trace']['truncated'] and limited['trace']['omitted_indices'] and len(limited['trace']['nodes'])==1)
small=describe(request,result,query,context,output_bytes=1024)
check('output-byte-limit-withholds-claim',small['outcome']=='incomplete' and len(json.dumps(small).encode())<=1024)

ordinary=next((step['conclusion'] for step in payload['certificates'] if step['kind']=='base' and not any(support['atom']==step['conclusion'] for support in payload['supports'])),None)
if ordinary is not None:
    leaf=describe(request,result,ordinary,context)
    check('supplied-base-truth-explicit',leaf['trace']['nodes'][0]['leaf'] in ['supplied-truth','independent-root'])
else:
    # Separate trace primitive control; no kernel qualification is fabricated.
    synthetic=copy.deepcopy(payload);synthetic['supports']=[]
    declaration=next(p for p in synthetic['normal_form']['predicates'] if p['id']=='BaselineSignal')
    supplied_atom={'predicate':{k:declaration[k] for k in ['id','version','hash']},'values':[synthetic['normal_form']['domain'][0]]}
    synthetic['certificates']=[{'kind':'base','conclusion':supplied_atom}]
    supplied,_=certificate_trace(synthetic,synthetic['certificates'][0]['conclusion'],256)
    check('supplied-leaf-rendering-primitive',supplied['nodes'][0]['leaf']=='supplied-truth')

bad=copy.deepcopy(result);bad['manifest']['witness']['modules'].pop()
negative('truncated-split-evidence-rejects',lambda:describe(request,bad,query,context))
changed=copy.deepcopy(payload);changed['supports'][0]['witness']['assertion_id']='other-assertion';path=HERE/'fixtures/changed-support.json';s.write(path,changed)
bad=copy.deepcopy(result);bad['payload']={'kind':'repo',**s.binding(path)};bad['manifest']['bound_result']=bad['payload']
negative('changed-source-support-rejects',lambda:describe(request,bad,query,context))
for name,index in [('forward',len(payload['certificates'])),('cycle',len(payload['certificates'])-1)]:
    changed=copy.deepcopy(payload);changed['certificates'][-1]['indices'][0]=index
    negative(name+'-certificate-trace-rejects',lambda changed=changed:certificate_trace(changed,query,256))

mapped=[]
for name in ['unknown-potential','active-origin','expired-delegation']:
    record=s.read(s.V2/'s13'/(name+'.json'));out=describe(record['request'],record['result'])
    check('mapped-source-inspected-'+name,out['inspection']=='recorded-current' and not out['application_authorized'])
    s.write(HERE/(name+'-explanation.json'),out);mapped.append(out)
check('potential-does-not-activate-with-unknown-condition',len(mapped[0]['potential_norms'])==1 and mapped[0]['active_norms']==[])
check('active-norm-not-fulfillment-or-admission',len(mapped[1]['active_norms'])==1 and mapped[1]['fulfilled']=='not-established' and mapped[1]['admission']=='not-derived')
check('exact-expiry-delegation-verdict',mapped[2]['verdict']=='no' and mapped[2]['delegation']['snapshot']['epoch']==10)
record=s.read(s.V2/'s13/active-origin.json');bad=copy.deepcopy(record['result']);bad['active_norms']=[]
negative('mapped-active-display-transplant-rejects',lambda:describe(record['request'],bad))
bad=copy.deepcopy(record['result']);bad['typed_result']['facts'][0]['edge']['scope']='other-scope';bad['potential_norms']=bad['typed_result']['facts'];bad['active_norms']=bad['typed_result']['facts']
negative('mapped-origin-scope-transplant-rejects',lambda:describe(record['request'],bad))
bad=copy.deepcopy(record['result']);bad['fulfilled']='established'
negative('mapped-fulfillment-upgrade-rejects',lambda:describe(record['request'],bad))

(HERE/'worked-examples.md').write_text('''# Query and relation explanations\n\nThe public `describe` API first inspects the exact saved source/witness evidence. This is recorded-current inspection, not a fresh replay or application authorization. Both actual combined and staged layouts use the same API. The combined and wrong-scope test envelopes adapt exact historical v2 qualifications; they do not issue new fresh qualifications.\n\n## Exact positive relation\n\n`ContractReady(capability:reviewer@v1)` follows from `ContractReview` and its exact rule substitution. Its two source leaves are `ConformsTo(capability:reviewer@v1, contract:review@v1, static)` and `TargetKind(contract:review@v1, contract)`. The conformance leaf retains its member assertion and assessment token; the kind leaf retains the target node. Accepted assessment truth is supplied. See [the staged trace](positive-explanation.json). The older unary Conforms fact loses target and scope, so it cannot select this contract/scope by itself.\n\n## Absence and typing\n\nThe wrong-scope case asks for other-scope, which is in the finite domain but has no matching conformance observation. Its unseeded positive cycle does not derive ContractReady. [The explanation](wrong-scope-explanation.json) says absent-in-complete-profile. The new theorem proves that this diagnostic entails AtomValid, completed closure and nonmembership. Given closure adequacy, it excludes derivation from these fixed supplied facts. It does not assert falsity in every generic model, which may contain extra truths.\n\nUnknown predicate identity/version/digest or an undeclared domain value is outside-profile. A known predicate with wrong arity/sorts or a malformed atom is invalid-query. An exhausted computation is incomplete and never proves absence. Trace rendering can be truncated while the inspected closure remains complete; omitted indices stay visible. Output overflow instead emits an incomplete rendering result without an absence/application claim.\n\n## Mapped semantic relations\n\n[Unknown condition](unknown-potential-explanation.json) retains a potential inherited norm but activates none. [Positive condition](active-origin-explanation.json) activates the exact norm and retains its binding/contract/subject/scope origin. Activation does not establish fulfillment or admission. Active require/forbid conflicts have separate paired origins; they do not enable arbitrary conclusions.\n\n[Expired direct delegation](expired-delegation-explanation.json) returns no at epoch 10 for period [0,10). Its exact agent, principal, delegation revision, action and scope remain visible. The profile does not implement chains.\n\nThe mapped reader regenerates the exact concrete checked witness and checks current source/compiled dependencies. It does not render ancillary typed transport certificate fields that the witness does not bind. Supplied roots, condition evaluations and policy/gate truth remain explicit assumptions. No same-kernel replay is an independent checker, and no explanation changes readiness.\n''')
s.write(HERE/'explanation-controls.json',{'result':'pass','controls':controls,'formal_statements':s.binding(HERE/'query-kernel-evidence.json'),'actual_timeout':s.read(BASE/'p03/observed-timeout.json')['result'],'method':'Actual current combined/staged and mapped witnesses plus the actual observed timeout inspected; trace primitive fixtures are explicitly separate from new qualification.','authority_effect':'none'})
s.accept('P04',[
    'One public describe API inspects actual combined and staged evidence before reading closure/certificates; mapped variants inspect exact regenerated concrete witnesses and their dependencies.',
    'Independent query definitions/theorems compile; identity/version/digest, arity/sorts/domain and incomplete-result controls never report unsupported or malformed requests as proved absent.',
    'Positive traces retain exact rule-slot substitutions and all supports for displayed source leaves; bounded trace/output controls and mapped potential/active/conflict/fulfillment/delegation distinctions pass.'
],controls,extra=[HERE/'QuerySemantics.lean',HERE/'build/QuerySemantics.lean',HERE/'build/QuerySemantics.olean',HERE/'query-kernel-evidence.json',HERE/'mapping_worker.py',HERE/'build_schemas.py',HERE/'run_p04.py',HERE/'explanation-controls.json']+list(HERE.glob('*-explanation.json'))+list((HERE/'fixtures').glob('*.json')))
print('P04 accepted with '+str(len(controls))+' controls')
