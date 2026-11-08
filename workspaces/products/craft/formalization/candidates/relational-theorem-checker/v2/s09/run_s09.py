from pathlib import Path
import sys,copy,tempfile,time
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import shadow as h
s=h.s;r=h.r;HERE=Path(__file__).resolve().parent
import bounded_qualification as bounded
bounded.install(h)
sys.path.insert(0,str(s.BASE/'s07'));import fixtures as f
s.context('S09',[(s.BASE/'s06/recursive-workflow-audit.json','actual complete obligations and replay'),(s.BASE/'s07/mapping-audit.json','separately qualified direct/fixed contexts'),(s.BASE/'s08/docs-audit.json','human/readiness distinction'),(s.BASE/'s15/baseline.schema.json','exact immutable baseline'),(s.BASE/'s18/transition-controls.json','richer baseline meanings'),(s.V1/'workflow/application-adapter/task-acceptance.json','retained currentness and local cooperative posture')],[{'decision':'Snapshots and baseline registrations are immutable; a mutable HEAD is protected by a cooperative advisory lock and fresh checks','basis':'local candidate application, no authority effect'},{'decision':'Different Horn/mapped contexts remain individually named; no cross-epoch truth merging','basis':'exact contextual semantics'}])
store=Path(tempfile.mkdtemp(prefix='two-step-',dir=HERE/'runs'));build=store/'build';b=r.ext.c.fixture()
initial=h.initialize(b,store,build);results=[]
print('Initial baseline registered with split concrete proof stages',flush=True)
def check(name,ok):s.require(ok,'application control failed '+name);results.append({'name':name,'result':'pass'})
check('nonempty-baseline-independent-registration',bool(b['inference']['rules']) and initial['identity']==s.identity(b))
a=r.ext.example(b);p1=r.proposal(b,a,'shadow-edit-1');mappings=[f.example('delegation'),f.holds(f.example('inheritance'))];review1=h.review(p1,store,mappings,label='candidate-review');first=h.apply(review1,p1,store,mappings,build)
print('First shadow edit applied and successor registered',flush=True)
check('first-exact-baseline-applied',first['before']['identity']==s.identity(b) and first['after']['identity']==s.identity(a))
# Second extension builds on the first registered successor; the old rules are nonempty.
a2=copy.deepcopy(a);a2['inference']['predicates'].append({'id':'NextReview','version':'v2','sorts':['reference'],'role':'ordinary'});a2['producers'].append({'predicate':'NextReview','class':'derived-information','meaning':'derived-positive-horn'});a2['inference']['rules'].append({'id':'next-review','version':'v2','head':{'predicate':'NextReview','terms':[{'variable':'x'}]},'body':[{'predicate':'FreshReady','terms':[{'variable':'x'}]}]})
p2=r.proposal(a,a2,'shadow-edit-2');review2=h.review(p2,store,mappings,label='candidate-review');second=h.apply(review2,p2,store,mappings,build)
print('Second shadow edit applied and successor registered',flush=True)
check('second-fresh-before-state',second['before']['identity']==s.identity(a) and second['after']['identity']==s.identity(a2) and second['before']['registration']!=initial['registration'])
check('two-independent-successor-registrations',first['after']['registration']!=second['after']['registration'])
check('contexts-qualified-without-epoch-merging',len(second['mapped_results'])==2 and second['composition_policy'].startswith('individually'))
check('immutable-three-before-after-snapshots',len(list((store/'snapshots').glob('*.json')))==3)
check('complete-generated-obligations',all(len(x['qualification']['obligations'])==20 for x in [first,second]))
check('split-concrete-layout-identities',bounded.check_layout(first['qualification']) and bounded.check_layout(second['qualification']))
check('authority-remains-none',first['authority_effect']==second['authority_effect']=='none')
def negative(name,fn):
 try:fn();raise ValueError('hostile accepted '+name)
 except Exception as ex:s.require(not str(ex).startswith('hostile accepted'),'negative failed '+name);results.append({'name':name,'result':'pass','outcome':'blocked','reason':str(ex).splitlines()[0]})
negative('old-baseline-review-reuse-after-first-edit',lambda:h.validate_review(review1,p1,store,mappings))
# A current no-change review lets drift controls run before any expensive replay.
p3=r.proposal(a2,a2,'current-drift-controls');v=h.review(p3,store,mappings,label='candidate-review')
drift=copy.deepcopy(mappings);drift[1]['evaluations'][0]['key']['epoch']+=1;negative('condition-epoch-review-to-apply-drift',lambda:h.validate_review(v,p3,store,drift))
policy=copy.deepcopy(v);policy['runtime_bindings'][0]['sha256']='0'*64;policy['review_identity']=s.identity({k:x for k,x in policy.items() if k!='review_identity'});negative('verifier-policy-drift',lambda:h.validate_review(policy,p3,store,mappings))
mutated=copy.deepcopy(p3);mutated['after']['graph']['nodes'][0]['content_identity']='0'*64;negative('same-reference-content-substitution',lambda:h.review(mutated,store,mappings))
source=copy.deepcopy(p3);source['after']['source_bindings'][0]['sha256']='0'*64;negative('source-byte-binding-drift',lambda:h.review(source,store,mappings))
# Inject an external pointer write before the final comparison; immutable snapshots remain.
headPath=store/'HEAD.json';original=headPath.read_bytes()
try:s.write(headPath,initial);negative('noncooperating-pointer-change-before-check',lambda:h.validate_review(v,p3,store,mappings))
finally:headPath.write_bytes(original)
check('post-drift-current-head-retained',h.head(store)==second['after'])
oldAttempt=HERE/'runs/two-step-mutg0kru'
if oldAttempt.is_dir():
 oldHead=s.read(oldAttempt/'HEAD.json');s.require(oldHead['identity']==s.identity(a),'resource attempt published second edit')
 s.write(HERE/'resource-exhaustion-audit.json',{'status':'unknown-resource','stage':'second-successor-registration','observed':'subprocess.TimeoutExpired after 60 seconds; combined concrete witness module','retained_head':s.binding(oldAttempt/'HEAD.json'),'second_edit_published':False,'mitigation':'same independent declarations/proofs split into data, typed checks, closure and expansion compilation modules under unchanged stage ceiling','weakened_statement':False,'authority_effect':'none'})
 results.append({'name':'resource-limit-retains-before-state-and-blocks-second-edit','result':'pass','outcome':'unknown-resource'})
s.write(HERE/'application-qualification.json',{'result':'pass','applications':[first,second],'controls':results,'store':str(store.relative_to(s.ROOT)),'locking_limits':first['locking_limits'],'all_writes_candidate_only':True,'human_review':'pending','authority_effect':'none'})
s.write(HERE/'baseline-registration-qualification.json',{'result':'pass','registrations':[initial,first['after'],second['after']],'required_inventory':[o['id'] for o in r.ext.c.obligations('register')],'method':'Fresh independent identity-extension complete qualification for each exact snapshot; no receipt transplant','controls':results,'authority_effect':'none'})
s.accept('S09',['Two actual supported edits have separately replayed exact before-state registrations and complete current obligation outcomes.','Condition/context/source/policy/pointer drift controls block; authority effect is none.','Local advisory-lock limits and noncooperating final check/rename race are explicit; postcheck reports indeterminate and snapshots remain.','Same-reference substitution and original review/baseline receipt reuse reject.'],controls=results,extra_dependencies=[HERE/'shadow.py',HERE/'bounded_qualification.py',HERE/'resource-exhaustion-audit.json']+[s.ROOT/x[k]['path'] for x in [initial,first['after'],second['after']] for k in ['snapshot','registration']])
print('S09 accepted: two fresh candidate shadow edits; '+str(len(results))+' drift/registration controls.')
