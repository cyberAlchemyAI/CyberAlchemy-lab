from pathlib import Path
import sys,copy,re
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import explain as e
s=e.s;HERE=Path(__file__).resolve().parent
s.context('S08',[(s.BASE/'s05/capability-manifest.json','actual transport scope'),(s.BASE/'s06/recursive-result.json','actual complete recursion result and query certificate'),(s.BASE/'s07/mapping-audit.json','actual stress/condition verdict scope'),(s.BASE/'s15/selected-profile.json','generic versus source-faithful classes'),(s.BASE/'s18/source-map.json','41 selected/deferred meanings'),(s.V1/'workflow/proof-verifier/Verifier.lean','same-kernel wording'),(s.PROPOSAL,'S08 explanation contract and pending S14 human review')],[{'decision':'Bound source and checked witness source before describing saved outcomes; readiness is unchanged','basis':'S08 currentness/explanation requirements'},{'decision':'Author usability walkthrough checks wrong-contract/scope explanation; actual human diagnostic review remains S14','basis':'machine/author/human statuses separate'}])
p=s.read(s.BASE/'s06/recursive-proposal.json');result=s.read(s.BASE/'s06/recursive-result.json');query=next(a for a in result['closure'] if a['predicate']['id']=='FreshReady');positive=e.describe(result,p,query)
wrong=copy.deepcopy(next(a for a in result['observations'] if a['predicate']['id']=='ConformsTo'));wrong['values'][-1]['value']='wrong-scope';negative=e.describe(result,p,wrong)
current=s.read(s.BASE/'s07/cases/inherited-potential-with-unknown-condition.json')['result'];potential=e.describe(current)
fixtures={'derived-query':positive,'wrong-scope':negative,'potential-only':potential,'unknown-resource':e.describe({'status':'unknown-resource','reason':'grounding budget'})}
results=[]
def check(name,ok):s.require(ok,'explanation failed '+name);results.append({'name':name,'result':'pass'})
check('source-and-rule-trace',positive['trace']['rule']['id']=='fresh-chain' and 'source observation' in str(positive['trace']))
check('wrong-scope-names-exact-query-and-lossy-unary','wrong-scope' in negative['text'] and 'unary' in negative['text'] and 'contract' in negative['text'])
check('potential-versus-active-fulfillment','1 potential norm(s), 0 active norm(s)' in potential['text'] and 'Fulfillment has not been established' in potential['text'])
check('resource-exhaustion-no-absence','No complete closure, absence or readiness' in fixtures['unknown-resource']['text'])
check('human-review-remains-pending',positive['human_review']=='pending' and 'fresh' in positive['readiness'])
changed=copy.deepcopy(result);changed['closure'].pop()
try:e.describe(changed,p);raise ValueError('changed explanation accepted')
except ValueError as ex:check('mismatched-checked-closure-refused','changed explanation accepted' not in str(ex))
links=[]
for name in ['CURRENT-STATUS.md','API.md']:
 for link in re.findall(r'\]\(([^)]+)\)',(HERE/name).read_text()):
  resolved=(HERE/link).resolve();s.require(resolved.is_file(),'broken documentation link '+link);links.append(s.binding(resolved))
check('all-current-document-links-resolve',bool(links))
s.write(HERE/'explanation-fixtures.json',fixtures)
s.write(HERE/'docs-audit.json',{'result':'pass','controls':results,'links':links,'usability_review':'author walkthrough: exact wrong scope named, unary loss explained, trace ends at source assertion/assessment; actual human meaning/diagnostic assessment pending S14','machine_author_human_authority_separate':True,'status_links':'live execution status consulted separately; no static whole-plan completion implied','authority_effect':'none'})
s.accept('S08',['Concrete source, exact rule substitution and wrong-scope blocked query explanation retain readiness.','Current docs link actual contracts/proofs/results and a live execution status; static guide states no whole-plan completion.','Historical/v1 accepted exports unchanged; actual human review stays pending.','Each explanation labels model/closure/query scope and source versus ordinary/root supplied truth; potential/active/fulfilled distinct.'],controls=results,extra_dependencies=[HERE/'explain.py'])
print('S08 accepted: '+str(len(results))+' explanation/currentness/link controls; actual human usability feedback pending S14.')
