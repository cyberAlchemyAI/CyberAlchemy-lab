"""Independent exact-source, admission, projection, correspondence and countermodel checks."""
import ast,json,re
from pathlib import Path
import build_candidate as b
import verifier as v
import verify_candidate as models
def load(name):return json.loads((b.UNIT/name).read_bytes())
def verify(write=False):
 context=load('context.json');snap=b.snapshot();b.unchanged(context['sources']);b.external_current(context);assert b.r.verify(snap,b.ROOT)['files']==201
 source=context['source_selection'];doc=b.co.source_document(snap,source);core=load('t.json')['payload'];packet=load('correspondence.json');checks=[]
 def check(name,condition):
  if not condition:raise ValueError('Source check failed: '+name)
  checks.append({'check_id':name,'result':'PASS-for-exact-candidate-check'})
 check('exact-current-CoordinationContext-source',source==b.source_ref(snap,'cal.definition.coordination-context') and source['sha256']=='547a714a9552f83985de78b2ce228421f5102c40cacf8c1edfb48ef46366a8aa')
 decision=json.loads((b.ROOT/'docs/decisions/0018-definition-and-ctx00-promotion/decision.json').read_bytes())
 check('C18-positive-admission-eight-selected-definitions',decision['status']=='owner-admitted' and len(decision['admitted_definitions'])==8 and any(row['definition_id']==source['definition_id'] and row['sha256']==source['sha256'] for row in decision['admitted_definitions']))
 check('historical-candidate-lifecycle-preserved',doc['classification']['lifecycle_posture_ref']=='CAL-LIFECYCLE-DEFINITION-V1:candidate-authored')
 schema=json.loads((b.ROOT/'authority/artifact-types/definition/v1/schema.json').read_bytes());check('authoritative-Definition-schema',not list(b.c.Draft202012Validator(schema).iter_errors(doc)))
 generator=b.ROOT/'authority/artifact-types/definition/v1/generator.py';namespace={};nodes=[node for node in ast.parse(generator.read_bytes()).body if isinstance(node,ast.FunctionDef) and node.name in ['esc','bullets','render']];exec(compile(ast.Module(body=nodes,type_ignores=[]),str(generator),'exec'),namespace)
 projection=(b.ROOT/source['path']).with_name('DEFINITION.md');check('pure-generated-human-projection',namespace['render'](doc).encode()==projection.read_bytes())
 scientific=doc['voices']['scientific_formal'];check('source-fourteen-coordinate-tuple',scientific['formal_expression'].split(';')[0]=='CoordinationContext = (id, product_ref, project_ref?, goal_ref?, purpose, consumer_refs, intended_uses, subject_scope, source_policy_refs, bounded_context_refs, owner_ref, lifecycle, revision_history, challenge_route)')
 check('source-exact-Product-and-optional-cardinality','|product_ref|=1; |project_ref|<=1; |goal_ref|<=1;' in scientific['formal_expression'])
 check('source-material-change-successor-condition',scientific['formal_expression'].endswith('MaterialAnchorChange => SuccessorRequired.'))
 check('source-bounded-context-version-notation',scientific['notation']==[{'symbol':'bounded_context_refs','meaning':'Explicit references to separately owned Bounded Context versions.'}])
 check('source-containment-and-directory-boundaries',scientific['boundary_conditions']==['It references Bounded Contexts but never becomes one by containment.','Directory placement cannot supply identity or ownership.'])
 check('source-view-identity-boundary',doc['boundaries'][1]=='A source view changing does not mutate the durable coordination identity.')
 c17=json.loads((b.ROOT/'docs/decisions/0017-ctx00-source-admission/decision.json').read_bytes());admissions=json.loads((b.ROOT/'authority/decisions/source-admission/ctx00-context-metamodel/v1/admissions.json').read_bytes())
 check('C17-positive-decision-with-seven-scoped-uses',c17['status']=='owner-admitted' and len(admissions['admissions'])==7 and admissions['status']=='candidate-unadmitted')
 check('two-exact-external-selections',len(context['external_sources'])==len(doc['source_refs'])==2)
 for observed,reference in zip(context['external_sources'],doc['source_refs']):
  data=Path(observed['absolute_path']).read_bytes();admission=next(row for row in admissions['admissions'] if row['admission_id']==reference['source_ref'])
  if observed['selector']=='CAV2-D66':
   lines=data.splitlines(keepends=True);start=next(i for i,line in enumerate(lines) if line.startswith(b'## CAV2-D66:'));end=next((i for i in range(start+1,len(lines)) if lines[i].startswith(b'## ')),len(lines));selected=b''.join(lines[start:end])
   check('D66-semantic-evidence-not-whole-file-import',admission['selector_kind']=='markdown-h2-block-v1' and admission['boundary_class']=='private-external-semantic-evidence' and 'Does not establish a context hierarchy.' in admission['non_effects'])
  else:
   selected=data;check('ContextPackage-explanatory-use-not-package-import',admission['selector_kind']=='whole-file-v1' and admission['boundary_class']=='private-external-explanatory-evidence' and 'Does not import the source context package.' in admission['non_effects'])
  check('selected-byte-identity-'+reference['source_ref'],b.r.digest(selected)==observed['selected_sha256']==reference['content_sha256']==admission['selected_sha256'])
  check('source-admission-reference-'+reference['source_ref'],reference['source_admission_ref']==c17['decision_id'] and reference['admission_posture']=='admitted')
  check('external-current-byte-binding-'+reference['source_ref'],b.r.digest(data)==observed['sha256'])
 check('exact-source-unit-inventory',packet['source_units']==b.co.inventory(doc))
 account=b.co.check(packet,snap,required_dependencies=[row['version_ref'] for row in core['depends_on']],required_conflicts=[row['finding_id'] for row in packet['source_precedence']['conflicts']])
 check('complete-character-account-with-dependencies-and-findings',account==load('correspondence-check.json') and account['character_accounting_complete'])
 check('no-target-assumptions-or-accepted-fidelity',not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending' and packet['source_precedence']['review_ref'] is None and packet['review_packet']['review_status']=='pending')
 check('all-source-owner-findings-preserved',[row['description'] for row in packet['source_precedence']['conflicts']]==b.LOSSES and all(row['status']=='unresolved' for row in packet['source_precedence']['conflicts']))
 check('source-and-composed-IR-agree',load('static-ir.json')==b.ir.compile_interpretation(core,snap) and packet['interpretation']==core)
 stack=[row['formal_statement'] for row in core['clauses'] if row['disposition']=='encoded']
 while stack:
  value=stack.pop()
  if isinstance(value,dict):
   check_name=value.get('name','')
   if value.get('op')=='pred' and any(check_name.startswith(prefix+'Actual') for prefix in ['Context','AnchorChange','SourceViewChange']):raise ValueError('Actual target selected in theory')
   stack.extend(value.values())
  elif isinstance(value,list):stack.extend(value)
 check('actual-outcome-predicates-absent-from-T',True)
 model=load('model-controls.json');cases={row['case_id']:row for row in model['results']}
 check('complete-authored-control-denominator',len(cases)==model['control_count']==len(models.controls())==198)
 for name in ['positive-fourteen-coordinates-optional-anchors-boundaries-material-changes-and-views','same-principal-can-own-independent-boundaries','absent-Project-unused-binding-may-be-empty','absent-Goal-unused-binding-may-be-empty','unselected-Project-reference-may-be-undeclared','unselected-Goal-reference-may-be-undeclared','no-materiality-unused-successor-binding-aNonmaterial','no-materiality-unused-successor-binding-aNoChange']:
  check(name,cases[name]['primary_theory_satisfied'] is cases[name]['required_population_satisfied'] is True)
 for name in ['aProduct','aProject','aGoal','aPurpose']:
  check('material-successor-counterexample-'+name,cases['material-inplace-successor-'+name]['primary_theory_satisfied'] is False)
  check('materiality-not-all-anchor-differences-'+name,cases['materiality-flag-removed-'+name]['primary_theory_satisfied'] is True and cases['materiality-flag-removed-'+name]['required_population_satisfied'] is False)
 for name in ['second-Product-link','second-Project-link','second-Goal-link','missing-explicit-boundary-link','extra-boundary-link-outside-collection','missing-independent-boundary-ownership','source-view-change-mutates-coordination-identity']:
  check(name,cases[name]['primary_theory_satisfied'] is False)
 check('malformed-model-rejections-retain-original-bounds',sum(row['status']=='rejected-model-structure' for row in model['results'])==8 and v.MAX_STEPS==100000 and v.TIMEOUT==30)
 queries=load('query-policy.json')['queries'];check('all-query-targets-independent',queries==b.query_specs() and len(queries)==32)
 typed=load('static-ir.json');ids={row['symbol_id']:b.ir.qualified(core['source'],core['scope'],row['symbol_id']) for row in core['declarations']};model_base=models.qualify(models.base_model(),ids);countermodels={row['query_id']:row for row in model['nonentailment_countermodels']};composed=b.ir.compose([typed])
 for query in queries:
  target=v.renamed(query['target'],ids);witness=v.renamed(query['witness_condition'],ids);b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness);denotation=v.Denotation(typed['declarations'],model_base)
  check('independent-countermodel-'+query['query_id'],query['selected_in_T'] is False and denotation.truth(target) is False and denotation.truth(witness) is True and countermodels[query['query_id']]['model']==model_base)
 texts=dict(b.co.string_leaves(doc));obligations=load('source-query-obligation.json')['obligations'];by_clause={row['clause_id']:row for row in core['clauses']}
 for obligation in obligations:
  clause=by_clause[obligation['clause_id']];excerpt=texts[obligation['selector']][obligation['start_character']:obligation['end_character']]
  assert obligation['source']==source and excerpt==obligation['excerpt'] and b.r.digest(excerpt.encode())==obligation['excerpt_sha256']==clause['excerpt_sha256'] and obligation['query_id'] in countermodels and obligation['actual_outcome_target_in_T'] is False
 check('exact-span-query-obligations',bool(obligations) and {row['clause_id'] for row in obligations}=={row['clause_id'] for row in core['clauses'] if row['disposition']!='explanatory'})
 prior=load('../cal.definition.capability-realization-binding/delivery-manifest.json') if (b.UNIT.parent/'cal.definition.capability-realization-binding/delivery-manifest.json').exists() else json.loads((b.BASE/'definitions/cal.definition.capability-realization-binding/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']);b.external_current(context)
 bindings=[b.ref(b.UNIT/name) for name in ['build_candidate.py','verify_candidate.py','verify_source_checks.py']]
 report={'schema_version':'definition-assurance-CoordinationContext-source-checks/v1-candidate','status':'PASS-exact-CoordinationContext-source-conditions','authority_effect':'none','checks':checks,'source_query_obligations':len(obligations),'projection_bytes':len(projection.read_bytes()),'checker_bindings':bindings,'source':source,'source_fidelity':'pending','semantic_ready':False,'accepted_source_map':False,'actual_Context_created_owned_or_authorized':False,'whole_definition_proof':False,'prior_candidate_files_preserved':len(prior['files'])}
 if write:b.put('source-checks.json',report)
 elif report!=load('source-checks.json'):raise ValueError('Fresh source checks differ')
 return report
if __name__=='__main__':
 report=verify('--write' in b.sys.argv);print(json.dumps({'result':report['status'],'checks':len(report['checks']),'source_query_obligations':report['source_query_obligations'],'semantic_ready':False},indent=2))
