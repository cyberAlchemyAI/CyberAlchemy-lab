"""Exact C66 source/projection/account/query observations; no accepted fidelity inferred."""
import ast,copy,json
import build_candidate as b
import verify_candidate as a
import verifier as v
def verify(write=False):
 context=a.load('context.json');b.unchanged(context['sources']);b.external_current(context);snapshot=b.snapshot();assert b.r.verify(snapshot,b.ROOT)['files']==201
 source=context['source_selection'];doc=json.loads((b.ROOT/source['path']).read_bytes());refs={};checks=[]
 def check(name,ok):assert ok,name;checks.append({'check_id':name,'result':True})
 def select(name,path):refs[name]=b.ref(path);return json.loads(path.read_bytes())
 registry=select('definition-registry',b.ROOT/'authority/definitions/registry.json')
 check('exact-current-C66-source',source==b.source_ref(snapshot,'cal.definition.capability-realization-binding') and registry['current_lookup'][source['definition_id']]==source['version_ref'])
 decision_path=b.ROOT/'docs/decisions/0066-definition-specialization-resolution-admission/decision.json';decision=select('C66-decision',decision_path);auth_path=b.ROOT/decision['authorization']['path'];select('C66-authorization',auth_path)
 check('exact-positive-C66-owner-admission',decision['status']=='owner-admitted' and refs['C66-authorization']['sha256']==decision['authorization']['sha256'] and any(x['definition_ref']==source['version_ref'] and x['path']==source['path'] and x['sha256']==source['sha256'] for x in decision['admitted_definitions']))
 gp=b.ROOT/'authority/artifact-types/definition/v1/generator.py';sp=b.ROOT/'authority/artifact-types/definition/v1/schema.json';refs['Definition-generator']=b.ref(gp);schema=select('Definition-schema',sp);refs['source']=b.ref(b.ROOT/source['path']);projection=(b.ROOT/source['path']).with_name('DEFINITION.md');refs['source-projection']=b.ref(projection)
 check('source-declared-schema-and-generator-bytes',doc['schema_digest']==refs['Definition-schema']['sha256'] and doc['source_direction']['generator_sha256']==refs['Definition-generator']['sha256'])
 check('source-whole-Definition-schema',not list(b.c.Draft202012Validator(schema).iter_errors(doc)))
 nodes=[x for x in ast.parse(gp.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in ['esc','bullets','render']];namespace={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(gp),'exec'),namespace)
 before=copy.deepcopy(doc);one=namespace['render'](doc).encode();two=namespace['render'](doc).encode();check('exact-two-pure-projections',one==two==projection.read_bytes() and doc==before)
 check('23source-units-live',len(b.co.inventory(doc))==23)
 check('candidate-upstream-posture-preserved',doc['source_refs'][0]['admission_posture']=='candidate-unadmitted' and doc['source_refs'][0]['source_admission_ref'] is None and doc['source_refs'][0]['content_sha256']=='9e80895df1887113cfc407de6ed4d11f6cd37d4ac10857389ee060e1139c9f36')
 core=a.load('t.json')['payload'];typed=a.load('static-ir.json');packet=a.load('correspondence.json');account=b.co.check(packet,snapshot)
 check('exact-complete-source-account',account['character_accounting_complete'] and account==a.load('correspondence-check.json') and len(core['clauses'])==23)
 check('14encoded6explanatory3deferred',sum(x['disposition']=='encoded' for x in core['clauses'])==14 and sum(x['disposition']=='explanatory' for x in core['clauses'])==6 and sum(x['disposition']=='deferred' for x in core['clauses'])==3)
 queries=a.load('query-policy.json')['queries'];query_by_id={q['query_id']:q for q in queries};check('33exact-independent-queries',queries==b.query_specs() and len(queries)==33 and all(q['selected_in_T'] is False for q in queries))
 ids={d['symbol_id']:b.ir.qualified(core['source'],core['scope'],d['symbol_id']) for d in core['declarations']};model=a.qualify(a.base_model(),ids);e=v.Denotation(typed['declarations'],model)
 check('source-qualified-baseline-T-and-I',all(e.truth(x['formal_statement']) for x in typed['clauses'] if x['disposition']=='encoded') and all(e.truth(x['statement']) for x in typed['populations'] if x['requirement']=='required'))
 source_obligations=a.load('source-query-obligation.json')['obligations'];clauses={x['clause_id']:x for x in core['clauses']};texts=dict(b.co.string_leaves(doc))
 for number,row in enumerate(source_obligations,1):
  clause=clauses[row['clause_id']];excerpt=texts[row['selector']][row['start_character']:row['end_character']];q=query_by_id[row['query_id']]
  check('source-query-'+str(number),row['source']==source and excerpt==row['excerpt'] and b.r.digest(excerpt.encode())==row['excerpt_sha256']==clause['excerpt_sha256'] and row['actual_outcome_target_in_T'] is False and row['necessary_declaration_guard_in_T']==(clause['disposition']=='encoded') and e.truth(v.renamed(q['target'],ids)) is False and e.truth(v.renamed(q['witness_condition'],ids)) is True)
 check('no-target-premise-or-whole-theory-import',not core['assumptions'] and not packet['assumption_links'] and a.load('comparison-selection.json')['comparison_assembled_into_primary_T'] is False)
 for name in ['context.json','t.json','static-ir.json','correspondence.json','query-policy.json','source-query-obligation.json','verify_source_checks.py']:refs[name]=b.ref(b.UNIT/name)
 b.unchanged(context['sources']+list(refs.values()));b.external_current(context)
 report={'schema_version':'definition-assurance-CRB-source-checks/v1-candidate','authority_effect':'none','result':'PASS-exact-current-C66-CRB-source-and-query-correspondence','source':source,'checks':checks,'selected_inputs':refs,'source_units':23,'projection_bytes':len(one),'projection_sha256':b.r.digest(one),'current_registry_admission_ref':'CAL-DECISION-0066-DEFINITION-SPECIALIZATION-RESOLUTION-ADMISSION','source_body_upstreams':doc['source_refs'],'source_query_obligations':len(source_obligations),'accepted_source_map':False,'actual_Binding_adopted_deployed_conformant_or_authorized':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False}
 if write:b.put('source-checks.json',report)
 else:assert b.r.same_json(report,a.load('source-checks.json')),'Fresh source checks differ'
 return report
if __name__=='__main__':
 result=verify('--write' in b.sys.argv);print(json.dumps({'result':result['result'],'checks':len(result['checks']),'source_units':23,'query_obligations':result['source_query_obligations'],'semantic_ready':False},indent=2))
