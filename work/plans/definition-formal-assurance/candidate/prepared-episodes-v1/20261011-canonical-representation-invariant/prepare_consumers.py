"""Prepare post-typed CPRI consumer inspection;no source or frozen-input writes."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.canonical-representation-invariant')
script='''"""Exact CPRI Definition/scaffold,paired meanings and candidate kind-table observations."""
import ast,copy,json
from pathlib import Path
import build_candidate as b
import verify_candidate as a
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def pure(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==set(names);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns
def inspect(write=False):
 context=load('context.json');typed=load('types-logic-receipt.json');b.unchanged(typed['inputs']+typed['producer_results']+context['sources']);b.external_current(context);snap=b.snapshot();assert b.r.verify(snap,b.ROOT)['files']==201
 audit=b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261011-canonical-representation-invariant/typed-stage-audit-command-result.json';assert json.loads(audit.read_bytes())['exit_code']==0 and not audit.with_name('typed-stage-audit-stderr.txt').read_bytes()
 rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());current=[x for x in registry['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if context['source_selection']['version_ref'] in x['semantic_definition_refs']];generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2')
 paths={'registry':rp,'source':b.ROOT/context['source_selection']['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_Definition_schema':b.ROOT/generic['schema_path'],'normalization':b.ROOT/'docs/normalizations/0001-definition-migration-model/normalization.json','prototype_renderer':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/followups.py','typed_receipt':b.UNIT/'types-logic-receipt.json','typed_separate_audit':audit,'checker':b.UNIT/'inspect_carrier_consumers.py','prior_Lifetime_profile':b.BASE/'definitions/cal.definition.artifact-lifetime/authority-profile-checks.json','prior_Artifact_profile':b.BASE/'definitions/cal.definition.artifact/authority-profile-checks.json'}
 selections=[b.source_ref(snap,'cal.definition.'+n) for n in ['artifact','artifact-lifetime','canonical-representation-invariant']]
 for selected in selections:
  key=selected['definition_id'];q=b.ROOT/selected['path'];paths[key]=q;paths[key+'-projection']=q.with_name('DEFINITION.md');doc=json.loads(q.read_bytes());scaffold=b.ROOT/doc['evidence_refs'][0];paths[key+'-scaffold']=scaffold;paths[key+'-scaffold-projection']=scaffold.with_name('ARTIFACT.md')
 refs={key:b.ref(q) for key,q in paths.items()};docs={key:json.loads(q.read_bytes()) for key,q in paths.items() if q.suffix=='.json'};checks=[]
 def ck(name,ok):
  assert ok,name;checks.append({'check_id':name,'result':True})
 ck('frozen16-stage-separate-audit0',typed['result']=='PASS-for-typed-candidate-stage-only' and len(typed['inputs'])==16 and typed['full_delivery_sealed'] is False)
 ck('catalog143rows121current',len(registry['admitted_contracts'])==143 and len(current)==121)
 ck('no-direct-current-CPRI-carrier-binding',direct==[])
 ck('generic-Definition-v2-not-CPRI-instance',generic['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']] and generic['schema_sha256']==refs['current_Definition_schema']['sha256'])
 schema=docs['Definition_schema'];validator=b.c.Draft202012Validator(schema);gen=pure(paths['Definition_generator'],['esc','bullets','render']);render=pure(paths['prototype_renderer'],['render_target']);observations=[]
 for selected in selections:
  key=selected['definition_id'];doc=docs[key];prototype=docs[key+'-scaffold'];label='semantic.'+key.removeprefix('cal.definition.');row=next(x for x in snap['current_entries'] if x['definition_id']==key)
  ck(key+'-exact-current-C53',refs[key]=={'path':selected['path'],'sha256':selected['sha256']} and row['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and row['effective_state']=='admitted-current')
  ck(key+'-Definition-v1-valid',not list(validator.iter_errors(doc)))
  ck(key+'-normalized-identity-separate','identified by '+label in doc['voices']['scientific_formal']['normative_statement'] and prototype['target_id']==label)
  before=copy.deepcopy(doc);one=gen['render'](before).encode();two=gen['render'](before).encode();ck(key+'-two-pure-Definition-projections',one==two==paths[key+'-projection'].read_bytes() and before==doc)
  before=copy.deepcopy(prototype);p1=render['render_target'](before).encode();p2=render['render_target'](before).encode();ck(key+'-two-pure-scaffold-projections',p1==p2==paths[key+'-scaffold-projection'].read_bytes() and before==prototype)
  ck(key+'-prototype-not-instance-admission',prototype['status']=='prototype-scaffold' and prototype['authority_effect']=='none' and prototype['four_facets']['schema']['admitted_schema_ref'] is None)
  observations.append({'source':selected,'consumer_label':label,'outer_Definition_classification':doc['classification'],'normalized_scaffold_classification':prototype['normalized_contract'],'first_render_sha256':b.r.digest(one),'second_render_sha256':b.r.digest(two),'prototype_projection_sha256':b.r.digest(p1),'accepted_semantic_map_refs':[],'native_or_live_consumer_executed':False})
 cpri=docs['cal.definition.canonical-representation-invariant'];artifact=docs['cal.definition.artifact'];lifetime=docs['cal.definition.artifact-lifetime'];proto=docs['cal.definition.canonical-representation-invariant-scaffold'];f=cpri['voices']['scientific_formal'];nf=artifact['voices']['scientific_formal'];lf=lifetime['voices']['scientific_formal']
 ck('C12-invariant-normalized-contract-exact',proto['normalized_contract']==next(x for x in docs['normalization']['semantic_concepts'] if x['concept_id']=='semantic.canonical-representation-invariant') and proto['normalized_contract']['semantic_kind']=='invariant' and proto['normalized_contract']['carrier_ref']=='type.invariant')
 ck('C53-outer-Definition-carrier-vs-normalized-invariant',cpri['classification']['semantic_kind']=='definition' and cpri['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1' and proto['normalized_contract']['semantic_kind']=='invariant')
 ck('D51-sibling-formal-expression-exact-but-identities-distinct',f['formal_expression']==nf['formal_expression'] and cpri['definition_id']!=artifact['definition_id'] and cpri['source_refs']==artifact['source_refs'])
 ck('source-primary-Lifetime-ref-and-reverse-links',cpri['primary_consumer_refs']==['semantic.artifact-lifetime'] and lifetime['primary_consumer_refs']==['semantic.artifact','semantic.canonical-representation-invariant'])
 ck('kind-derived-durability-vs-instance-override-retained','inherits from its kind' in f['formal_expression'] and 'derived, not' in f['formal_expression'] and 'Assign durability per canonical-kind as a default' in lifetime['scope']['applicability'] and 'overridable per instance with an owner note' in lifetime['scope']['applicability'])
 ck('prior-Artifact-Lifetime-finding-retained',len(docs['prior_Lifetime_profile']['cross_definition_review_findings'])==1 and docs['prior_Lifetime_profile']['cross_definition_review_findings'][0]['finding_id']=='LIFE-CONSUMER-FINDING-001' and docs['prior_Lifetime_profile']['cross_definition_review_findings'][0]['status']=='unresolved')
 ck('current-body-and-C53-overlay-remain-separate','It is not admitted' in cpri['claim_ceiling'] and load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION')
 ck('future-L2-and-exact-L1-L2-support-not-current-execution','defined future level, not a currently available result' in f['normative_statement'] and 'valid L1 verifier receipt' in cpri['scope']['applicability'] and 'real L2 external' in cpri['scope']['applicability'])
 external=Path('/home/vlad_/projects/cyberAlchemy-v2/ontology/canonical-kinds/CANONICAL-KINDS.md');raw=external.read_bytes();table=raw.decode();external_ref={'absolute_path':str(external),'sha256':b.r.digest(raw)};sections=[]
 for name,start,end in [('candidate-kind-contract','# Canonical Kinds','## Instance Contract'),('frontmatter-rules','## Instance Contract','### Core contract'),('durability-override','### OQ-3.','### OQ-4.'),('unresolved-producers','### OQ-6.','### OQ-7.')]:
  i=table.index(start);j=table.find(end,i+len(start));assert j>i,(name,end);excerpt=table[i:j];sections.append({'section_id':name,'start_character':i,'end_character':j,'excerpt':excerpt,'excerpt_sha256':b.r.digest(excerpt.encode()),'authority_posture':'related-current-candidate-context-not-admitted-allowed-origin-source'})
 ck('external-table-explicit-candidate-unratified','Status: candidate' in table[:200] and 'Uncited by construction' in table and 'as ratified' in table[:650] and 'not closed yet' in table)
 ck('external-table-fine-coarse-rollup','fine artifact-types' in table and 'coarse **Tier-2**' in table and 'several canonical kinds' in table)
 ck('external-table-owner-note-carrier-open','The carrier for that override' in sections[2]['excerpt'] and 'Status: OPEN' in sections[2]['excerpt'])
 ck('external-table-six-missing-producers-open','six kinds can be canonical with no producer' in sections[3]['excerpt'] and 'Status: OPEN' in sections[3]['excerpt'])
 ck('external-table-filename-path-scope-retained','for the four kinds in scope' in sections[1]['excerpt'] and 'On conflict the filename wins' in sections[1]['excerpt'] and 'The path' in sections[1]['excerpt'])
 probes=[]
 def probe(name,mutate,expected):
  doc=copy.deepcopy(cpri);mutate(doc);before=copy.deepcopy(doc);errors=sorted('/'+('/'.join(map(str,e.absolute_path)))+': '+e.message for e in validator.iter_errors(doc));accepted=not errors;assert accepted==expected,(name,errors);one=gen['render'](doc).encode() if accepted else None;two=gen['render'](doc).encode() if accepted else None;assert one==two and before==doc;probes.append({'case_id':name,'schema_accepted':accepted,'expected_schema_acceptance':expected,'schema_errors':errors,'two_generated_projections_equal':True if accepted else None,'fixture_digest':b.ir.digest(doc),'actual_semantic_obligations_enforced':False,'accepted_semantic_map':False})
 probe('exact-selected-Definition',lambda x:None,True)
 for field in schema['required']:probe('missing-required-'+field,lambda x,field=field:x.pop(field),False)
 for field in ['definition_id','semantic_owner_ref','term']:probe('unresolved-nonempty-'+field,lambda x,field=field:x.update({field:'hyp:unresolved'}),True)
 for field in ['artifact_ref','machine_canonical_representations','process_origin','allowed_origins_source','origin_assurance','L1_receipt','L2_signature','identity_policy','kind_default_durability','effective_instance_durability']:probe('instance-field-not-Definition-'+field,lambda x,field=field:x.update({field:'hyp:unaccepted-map'}),False)
 probe('empty-source-selection-shape-valid',lambda x:x.update(source_refs=[]),True)
 probe('empty-consumer-list-shape-valid',lambda x:x.update(primary_consumer_refs=[]),True)
 for name,text in [('duplicate-representation-claim','hyp:two independent machine representations both define this artifact'),('current-L2-without-external-signature','hyp:actor-attested currently available without signature or policy'),('canonical-proves-execution-truth-authority','hyp:canonical classification proves actual execution,truth and authority'),('candidate-table-makes-producer-admitted','hyp:a row in the candidate kind table authenticates this producer')]:probe(name,lambda x,text=text:x['voices']['scientific_formal'].update(normative_statement=text),True)
 comparison=[];core=load('t.json')['payload'];compiled=load('static-ir.json');ids={x['symbol_id']:b.ir.qualified(core['source'],core['scope'],x['symbol_id']) for x in core['declarations']}
 def compare(name,mutate,expected):
  m=a.base_model();mutate(m);model=a.qualify(m,ids);e=v.Denotation(compiled['declarations'],model);tc=[{'clause_id':x['clause_id'],'truth':e.truth(x['formal_statement'])} for x in compiled['clauses'] if x['disposition']=='encoded'];pc=[{'population_id':x['population_id'],'truth':e.truth(x['statement'])} for x in compiled['populations'] if x['requirement']=='required'];T=all(x['truth'] for x in tc);I=all(x['truth'] for x in pc);assert (T,I)==expected,(name,T,I);comparison.append({'case_id':name,'model':model,'model_sha256':b.ir.digest(model),'T':T,'I':I,'clause_results':tc,'population_results':pc,'accepted_Lifetime_kind_durability_map':False,'whole_Lifetime_theory_imported':False})
 def different_fine_kind_defaults(m):
  a.setfn(m,'kindDurability','kindCoarse','durableOutside');a.setfn(m,'artifactDurability','aAuthority','durableOutside');m['predicates']['DurabilityDeclared'].append(['durableOutside']);a.refresh(m)
 compare('distinct-fine-kinds-same-coarse-authority-different-durability',different_fine_kind_defaults,(True,True))
 def override_derived_field(m):
  a.setfn(m,'artifactDurability','aDeclared','durableOutside');m['predicates']['DurabilityDeclared'].append(['durableOutside']);a.refresh(m)
 compare('instance-effective-override-cannot-silently-replace-derived-field',override_derived_field,(False,True))
 compare('projection-regeneration-does-not-grant-authority',lambda m:m['predicates']['RepresentationActualAuthority'].append(['aDeclared']),(True,True))
 findings=[
 {'finding_id':'CPRI-CONSUMER-FINDING-001','issue':'C12 normalized invariant/type.invariant scaffold and C53 outer Definition/v1 carrier have different classification axes;no direct current contract binds CPRI meaning. A scaffold is not a canonical artifact instance or accepted representation map.'},
 {'finding_id':'CPRI-CONSUMER-FINDING-002','issue':'Linked canonical-kind table is candidate,uncited and not closed,with six unresolved producers;D51 requires current owner-approved allowed origins and rejects unresolved/candidate producers. Candidate table prose is not an admitted allowed-origin source;exact process/version/producer and owner source correspondence remain pending.'},
 {'finding_id':'CPRI-CONSUMER-FINDING-003','issue':'CPRI and Artifact inherit kind-derived durability;Lifetime allows an owner-noted effective instance override. Fine/coarse granularity permits differing defaults but does not settle the effective override. Prior LIFE-CONSUMER-FINDING-001 remains unresolved;default/effective fields and owner precedence require an accepted map.'},
 {'finding_id':'CPRI-CONSUMER-FINDING-004','issue':'Definition schema and pure projection accept textual duplicate-machine,current unsupported L2,execution/truth/authority and candidate-producer claims. Closed Definition schema rejects instance origin/representation/receipt fields. Shape and regeneration do not enforce or accept this artifact-instance theory.'},
 {'finding_id':'CPRI-CONSUMER-FINDING-005','issue':'Declared,L1 integrity-bound and conditional future L2 support have no accepted source-to-receipt/statement/state/actor/policy/signature map in this review. A hypothetical linked future witness does not make actor attestation currently available or prove execution,truth,correctness or authority.'},
 {'finding_id':'CPRI-CONSUMER-FINDING-006','issue':'Candidate four-kind frontmatter assigns kind via filename or named session-path rule;CPRI prohibits directory placement establishing semantic type or authority. Distinguish a separately governed carrier-selection rule from unguided directory inference;scope,kind inclusion,authority independence and C53 overlay/body correspondence remain owner pending.'}]
 for x in findings:x.update(status='unresolved',accepted_map_refs=[])
 prior=load('../cal.definition.canonical-package-manifest/delivery-manifest.json');b.unchanged(prior['files']+typed['inputs']+list(refs.values()));b.external_current(context);assert b.r.digest(external.read_bytes())==external_ref['sha256']
 report={'schema_version':'definition-assurance-CPRI-carrier-consumer-inspection/v1-candidate','result':'PASS-exact-CPRI-shape-paired-meanings-and-related-candidate-kind-context','authority_effect':'none','source':context['source_selection'],'checks':checks,'check_count':len(checks),'selected_inputs':refs,'external_file_refs':[external_ref],'external_context_sections':sections,'current_registry_contracts':len(registry['admitted_contracts']),'admitted_current_contracts':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_current_Definition_ref':generic['artifact_type_ref'],'meaning_observations':observations,'shape_probes':probes,'shape_probe_count':len(probes),'shape_acceptances':sum(x['schema_accepted'] for x in probes),'typed_comparison_models':comparison,'typed_comparison_count':len(comparison),'accepted_semantic_map_refs':[],'unresolved_consumer_findings':findings,'isolated_pure_Definition_and_scaffold_helpers_executed':True,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'real_canonical_artifact_origin_receipt_signature_or_authority_created':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_inventory_refresh_complete':False,'claim_ceiling':'Exact selected source/scaffold shape,pure copied-fixture projections,paired consumer meanings and related current candidate table;three supplied CPRI-only comparison models. No accepted kind/default/effective/origin/receipt/carrier map,actual instance,owner fidelity or whole proof.'}
 if write:b.put('carrier-consumer-inspection.json',report)
 elif not b.r.same_json(report,load('carrier-consumer-inspection.json')):raise ValueError('Fresh CPRI consumer observations differ')
 return report
if __name__=='__main__':
 x=inspect('--write' in b.sys.argv);print(json.dumps({key:x[key] for key in ['result','check_count','shape_probe_count','shape_acceptances','typed_comparison_count','current_registry_contracts','admitted_current_contracts','direct_current_definition_binding_types','semantic_ready']},indent=2))
'''
ast.parse(script)
with (u/'inspect_carrier_consumers.py').open('x') as f:f.write(script)
capture='''from pathlib import Path
import sys,subprocess,json
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.canonical-representation-invariant';argv=[sys.executable,'-B',str(u/'inspect_carrier_consumers.py')]+(['--write'] if '--write' in sys.argv else []);r=subprocess.run(argv,cwd=root,capture_output=True);stem='carrier-inspection' if '--write' in sys.argv else 'fresh-carrier-inspection'
for key,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (u/(stem+'-'+key+'.txt')).open('xb') as f:f.write(raw)
with (u/(stem+'-command-result.json')).open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'},f,indent=2);f.write('\\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
'''
with (p/'capture_consumer.py').open('x') as f:f.write(capture)
print('Prepared post-typed CPRI exact consumer inspection;no frozen inputs modified.')
