from pathlib import Path
import sys,json,copy,re
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import adapter as a
s=a.s;HERE=Path(__file__).resolve().parent
s.context('S05',[(s.BASE/'s17/preflight-bounds.json','early envelope ceilings'),(s.BASE/'s18/source-map.json','selected and deferred source meanings'),(s.BASE/'s15/selected-profile.json','fixed selected producer/catalog/toolchain profile'),(s.BASE/'s02/fresh-replay-audit.json','independent exact general projector targets'),(s.BASE/'s16/SupportedObservations.lean','observation-to-source correspondence'),(s.V1/'input/decoder.py','v1 strict source-to-Lean tested boundary'),(s.V1/'references/resolver.py','exact version/reference resolver')],[{'decision':'Strict v2 transport is a tested boundary; each projected finite inventory is kernel checked against universal projector','basis':'source meanings independent from Python decoder'},{'decision':'Projection readiness stays pending full obligations; selected F0 subgraph cannot claim unselected whole-graph semantics','basis':'explicit source coverage ceiling'}])
b=a.c.fixture();request=a.request(b);s.write(HERE/'projection-request.json',request)
result=a.project(request,HERE/'build');s.write(HERE/'projection-result.json',result)
results=[]
def ctrl(name,fn,pos=False):
 try:out=fn();s.require(pos,'accepted hostile '+name);results.append({'name':name,'result':'pass','outcome':'checked'})
 except Exception as ex:
  if pos:raise
  s.require(not str(ex).startswith('accepted hostile'),'failed control '+name);results.append({'name':name,'result':'pass','outcome':'blocked','reason':str(ex).splitlines()[0]})
def mutate(fn):
 q=copy.deepcopy(request);fn(q);return a.project(q,HERE/'build')
ctrl('rich-source-inventory-kernel-agreement',lambda:s.require(result['status']=='observed' and not result['unhandled_kinds'],'unexpected projection'),True)
ctrl('v1-receipt-v2-request-substitution',lambda:mutate(lambda q:q.update(schema='relational.projection-request/v1')))
ctrl('caller-shrunken-catalog',lambda:mutate(lambda q:q.update(catalog_identity='0'*64)))
ctrl('wrong-rich-arity',lambda:mutate(lambda q:next(p for p in q['baseline']['inference']['predicates'] if p['id']=='ConformsTo').update(sorts=['reference'])))
ctrl('wrong-rich-sort',lambda:mutate(lambda q:next(p for p in q['baseline']['inference']['predicates'] if p['id']=='TargetKind').update(sorts=['scope','text'])))
ctrl('caller-injected-conformance',lambda:mutate(lambda q:q['baseline']['inference']['facts'].append({'predicate':'Conforms','terms':[q['baseline']['inference']['domain'][0]]})))
ctrl('caller-injected-kind',lambda:mutate(lambda q:q['baseline']['inference']['facts'].append({'predicate':'TargetKind','terms':[q['baseline']['inference']['domain'][0],next(v for v in q['baseline']['inference']['domain'] if v['kind']=='text')]})))
ctrl('sealed-constant-head',lambda:mutate(lambda q:q['baseline']['inference']['rules'].append({'id':'forgery','version':'v2','head':{'predicate':'Conforms','terms':[{'constant':q['baseline']['inference']['domain'][0]}]},'body':[]})))
ctrl('altered-assessment-binding',lambda:mutate(lambda q:q['baseline']['graph']['assessments'][0].update(accepted=False)))
ctrl('wrong-source-target-version',lambda:mutate(lambda q:q['baseline']['graph']['assertions'][0]['target'].update(version='wrong')))
ctrl('missing-domain-kind-literal',lambda:mutate(lambda q:q['baseline']['inference'].update(domain=[v for v in q['baseline']['inference']['domain'] if not(v['kind']=='text' and v['value']==q['baseline']['graph']['nodes'][0]['kind'])])))
ctrl('preallocation-budget-refusal',lambda:mutate(lambda q:q['baseline']['inference']['domain'].extend([{'kind':'text','value':str(n)} for n in range(100)])))
ctrl('duplicate-json-keys',lambda:a.decode('{"schema":"one","schema":"two"}'))
ctrl('nonfinite-json',lambda:a.decode('{"x":NaN}'))
ctrl('excessive-json-depth',lambda:a.decode('['*100+'0'+']'*100))
ctrl('dangling-support-edge',lambda:a.support_check(b,[{**r,'witness':{**r['witness'],'assertion_id':'absent'}} if r['witness']['kind']=='conformance' else r for r in result['supports']]))
ctrl('missing-support-inventory',lambda:a.support_check(b,result['supports'][1:]))
ctrl('stale-context-support',lambda:a.support_check(b,[{**r,'context_identity':'0'*64} for r in result['supports']]))
ctrl('sealed-semantic-alias',lambda:mutate(lambda q:q['baseline']['producers'][-1].update(meaning='member-conformance')))
# Multiple assertion supports remain separate while the atom inventory deduplicates.
more=copy.deepcopy(b);edge=copy.deepcopy(next(e for e in more['graph']['assertions'] if e['kind']=='relation.conforms-to'));edge['id']='second-support';more['graph']['assertions'].append(edge)
multi=a.project(a.request(more),HERE/'build');s.write(HERE/'multiple-support-result.json',multi)
ctrl('multiple-supports-one-observation',lambda:s.require(len(multi['facts'])==len(result['facts']) and len(multi['supports'])==len(result['supports'])+2,'support multiplicity lost'),True)
migration=s.read(s.BASE/'s18/migration-after.json');migrated=a.project(a.request(migration),HERE/'build');s.write(HERE/'migration-projection-result.json',migrated)
ctrl('richer-new-target-scope-kind-projection',lambda:s.require(len(migrated['facts'])>len(result['facts']),'migration not projected'),True)
# A wrong Python candidate inventory is checked as false in the kernel.
bad=a.predict(b);bad['facts']=bad['facts'][1:];path=HERE/'build/ProjectionMismatch.lean';path.write_text(a.witness_source(bad,False));negative=s.compile_modules(HERE/'build',[('ProjectionMismatch',path)])
ctrl('differential-missing-fact-kernel-rejection',lambda:s.require(bool(negative),'missing kernel rejection'),True)
# Full build source/binary manifest rejects drift, then original bytes are restored.
p=HERE/'build/dependency-build.json';original=p.read_bytes();changed=s.read(p);changed['modules'][0]['source']['sha256']='0'*64
try:
 s.write(p,changed);ctrl('stale-import-build-reuse',lambda:a.project(request,HERE/'build'))
finally:p.write_bytes(original)
legacy=a.c.legacy.baseline();ctrl('retained-v1-source-fixture',lambda:s.require(a.c.legacy.r.resolve(legacy['graph'],legacy['registry'])['status']=='supported','v1 regression'),True)
manifest={'schema':'relational.capability-manifest/v2','profile_identity':b['profile_identity'],'catalog_identity':b['catalog_identity'],'transport_bindings':[s.binding(HERE/name) for name in ['request.schema.json','support.schema.json','adapter.py','projection-adapter.py']],'required_general_proofs':s.binding(s.BASE/'s02/fresh-replay-audit.json'),'producer_proofs':s.binding(s.BASE/'s16/sealed-producer-controls.json'),'resource_contract':s.binding(s.BASE/'s17/preflight-bounds.json'),'selected_source_map':s.binding(s.BASE/'s18/source-map.json'),'supported':'exact F0 conformance/context/kind observations and all support witnesses; recursive/stress integration follows separate obligations','claim_ceiling':'Tested transport plus kernel-checked finite projection; external assessment truth and host/hash/compiler trust explicit','authority_effect':'none'}
s.write(HERE/'capability-manifest.json',manifest)
s.write(HERE/'transport-audit.json',{'result':'pass','controls':results,'positive_evidence':[s.binding(HERE/name) for name in ['projection-result.json','multiple-support-result.json','migration-projection-result.json']],'negative_projection_evidence':negative,'build_evidence':s.binding(HERE/'build/dependency-build.json'),'adapter_equivalence':'tested differential boundary; no universal JSON decoder equivalence theorem','v1_fixture_unchanged':[s.binding(s.V1/'demonstrations/l0/input.json'),s.binding(s.V1/'registry/normalized-registry.json')],'authority_effect':'none'})
s.accept('S05',['Finite rich/multiple-support/migrated projections compile kernel witnesses; false missing-fact inventory also compiles as rejection.','Missing/dangling/stale support or profile identity blocks; projection alone cannot issue readiness.','JSON decoding, normalization and source-to-Lean generation remain tested trust boundaries; same pinned kernel checked instances.','Sealed seed/head/alias, profile/catalog/import substitution and preallocation ceilings reject.'],controls=results,extra_dependencies=[HERE/'adapter.py',HERE/'projection-request.json',HERE/'projection-result.json',HERE/'multiple-support-result.json',HERE/'migration-projection-result.json',HERE/'build/dependency-build.json'])
print('S05 accepted: strict v2 projection transport and '+str(len(results))+' hostile/context controls.')
