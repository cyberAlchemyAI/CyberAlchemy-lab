from pathlib import Path
import ast
p=Path(__file__).resolve().parent;root=Path.cwd();base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions';u=base/'cal.definition.artifact-type-resolution';prev=base/'cal.definition.artifact-type-request'
code='''"""Exact Resolution consumer observations; isolated pure functions and fixture copies only."""
import ast,copy,json,types
import build_candidate as b

def inspect(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes());typed=json.loads((b.UNIT/'types-logic-receipt.json').read_bytes());b.unchanged(typed['inputs']+typed['producer_results']+context['sources']);b.external_current(context)
 ap=b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261011-artifact-type-resolution/typed-stage-audit-command-result.json';assert json.loads(ap.read_bytes())['exit_code']==0
 paths={'current_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','legacy_registry':b.ROOT/'authority/artifact-types/candidates/0001-artifact-surface-foundation/registry.json','legacy_schema':b.ROOT/'authority/artifact-types/artifact-type-registry/v1/schema.json','shared_validator':b.ROOT/'tooling/validators/artifact_surface_candidate_2.py','typed_receipt':b.UNIT/'types-logic-receipt.json','checker':b.UNIT/'inspect_carrier_consumers.py','typed_separate_audit':ap}
 refs={n:b.ref(q) for n,q in paths.items()};registry=json.loads(paths['current_registry'].read_bytes());legacy=json.loads(paths['legacy_registry'].read_bytes());schema=json.loads(paths['legacy_schema'].read_bytes());validator=b.c.Draft202012Validator(schema);checks=[]
 def ck(n,ok):
  assert ok,n;checks.append({'check_id':n,'result':True})
 ck('frozen16-typed-stage-separately-audited',typed['result']=='PASS-for-typed-candidate-stage-only' and len(typed['inputs'])==16 and typed['full_delivery_sealed'] is False)
 ck('exact-shared-validator-bound',refs['shared_validator']['sha256']=='09df79ea7a251eb2836619749b2d1e5a6a51ef392a627639366ce271dae8eee1')
 ck('legacy-registry-schema-valid',not list(validator.iter_errors(legacy)))
 ck('legacy-entry-lifecycle-domain-admitted-only',schema['$defs']['entry']['properties']['lifecycle_state']['enum']==['admitted-current','admitted-historical'])
 ck('legacy25current22historical3',len(legacy['entries'])==25 and sum(x['lifecycle_state']=='admitted-current' for x in legacy['entries'])==22 and sum(x['lifecycle_state']=='admitted-historical' for x in legacy['entries'])==3)
 selected=[];snap=b.snapshot();resolution=context['source_selection']['version_ref']
 for row in registry['admitted_contracts']:
  if row['lifecycle_state']!='admitted-current' or resolution not in row['semantic_definition_refs']:continue
  a=b.ROOT/row['artifact_path'];s=b.ROOT/row['schema_path'];doc=json.loads(a.read_bytes());refs[row['artifact_type_ref']+'-artifact']=b.ref(a);refs[row['artifact_type_ref']+'-schema']=b.ref(s)
  ck('exact-current-contract-'+row['artifact_type_ref'],row['artifact_sha256']==b.ref(a)['sha256'] and row['schema_sha256']==b.ref(s)['sha256']==doc['schema_digest'])
  ck('exact-current-meaning-list-'+row['artifact_type_ref'],doc['semantic_definition_refs']==row['semantic_definition_refs'])
  meanings=[]
  for binding in doc['semantic_definition_bindings']:
   src=next(x for x in snap['current_entries'] if x['version_ref']==binding['definition_ref']);ref=b.ref(b.ROOT/binding['path']);refs[binding['definition_ref']]=ref;ck('exact-meaning-'+row['artifact_type_ref']+'-'+binding['definition_ref'],ref['sha256']==binding['sha256']==src['sha256'] and src['effective_state']=='admitted-current');meanings.append({'binding':binding,'effective_state':src['effective_state'],'accepted_map':False})
  did=row['admission_decision_ref'];decision_path='docs/decisions/0068-artifact-type-registry-v2-admission/decision.json' if '/v2' in row['artifact_type_ref'] else 'docs/decisions/0070-definition-complete-lab-model-admission/decision.json'
  q=b.ROOT/decision_path;decision=json.loads(q.read_bytes());refs[did]=b.ref(q);ck('owner-admitted-overlay-'+row['artifact_type_ref'],decision['decision_id']==did and decision['status']=='owner-admitted' and doc['status']=='candidate-unadmitted' and doc['authority_effect']=='none')
  selected.append({'artifact_type_ref':row['artifact_type_ref'],'admission_overlay':did,'embedded_status':doc['status'],'meanings':meanings})
 ck('two-current-direct-carriers',sorted(x['artifact_type_ref'] for x in selected)==['cal.artifact-type.artifact-type-registry/v2','cal.artifact-type.artifact-type-request/v1'])
 result_disc='cyberalchemy-lab-artifact-type-resolution-result/v1';result_contracts=[x['artifact_type_ref'] for x in registry['admitted_contracts'] if x['instance_discriminator']['value']==result_disc]
 ck('result-discriminator-not-registered-among143-contracts',len(registry['admitted_contracts'])==143 and result_contracts==[])
 wrapper=b.ROOT/'authority/artifact-types/artifact-type-request/v1/candidates/0002-executable-surface/validate.py';refs['Request_wrapper']=b.ref(wrapper);ck('current-Request-wrapper-explicitly-legacy-routed','authority/artifact-types/candidates/0001-artifact-surface-foundation/registry.json' in wrapper.read_text())
 tree=ast.parse(paths['shared_validator'].read_bytes());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['pointer_get','resolve']];ck('exact-two-pure-functions-selected',len(nodes)==2 and all(not isinstance(n,ast.Call) or not isinstance(n.func,ast.Name) or n.func.id not in ['open','dump','load','sha'] for x in nodes for n in ast.walk(x)))
 helper=types.ModuleType('_pure_Resolution');helper.__dict__.update(Any=object);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['shared_validator']),'exec'),helper.__dict__)
 current=next(x for x in legacy['entries'] if x['lifecycle_state']=='admitted-current');historical=next(x for x in legacy['entries'] if x['lifecycle_state']=='admitted-historical');assert current['instance_discriminator']['path']==historical['instance_discriminator']['path']=='/schema_version'
 probes=[]
 def probe(n,doc,expected_matches,r=legacy,path='fixture/subject.json'):
  before=copy.deepcopy((r,doc));one=helper.resolve(r,doc,path);two=helper.resolve(r,doc,path);state='resolved' if len(expected_matches)==1 else 'ambiguous' if expected_matches else 'unresolved';ck('probe-'+n,one==two and (r,doc)==before and one['matches']==sorted(expected_matches) and one['match_count']==len(expected_matches) and one['outcome']==state and one['authority_effect']=='none' and one['registry_id']==r['registry_id'] and one['inference_exclusions']==['directory','filename','extension','nearest-name']);probes.append({'case_id':n,'registry_schema_valid':not list(validator.iter_errors(r)),'registry_digest':b.ir.digest(r),'artifact_digest':b.ir.digest(doc),'result':one,'accepted_semantic_map':False});return one
 unknown={'schema_version':'fixture:unknown:v1'}
 probe('unknown-zero',unknown,[])
 probe('unknown-explicit-reference',{'classification':{'artifact_type_ref':'fixture:unregistered/v1'},**unknown},[])
 probe('candidate-unregistered-explicit',{'classification':{'artifact_type_ref':'fixture:candidate/v1'},**unknown},[])
 probe('explicit-current',{'classification':{'artifact_type_ref':current['artifact_type_ref']},**unknown},[current['artifact_type_ref']])
 hist=probe('explicit-historical',{'classification':{'artifact_type_ref':historical['artifact_type_ref']},**unknown},[historical['artifact_type_ref']]);ck('historical-state-exactly-recorded',hist['matched_entries'][0]['lifecycle_state']=='admitted-historical')
 disc={'schema_version':current['instance_discriminator']['value']};probe('discriminator-current',disc,[current['artifact_type_ref']])
 probe('historical-discriminator-only-ineligible',{'schema_version':historical['instance_discriminator']['value']},[])
 both={'classification':{'artifact_type_ref':current['artifact_type_ref']},**disc};dedup=probe('both-routes-deduplicate-by-type',both,[current['artifact_type_ref']]);ck('both-evidence-routes-retained',len(dedup['evidence'])==2 and dedup['match_count']==1)
 probe('historical-explicit-versus-current-disc-conflict',{'classification':{'artifact_type_ref':historical['artifact_type_ref']},**disc},[historical['artifact_type_ref'],current['artifact_type_ref']])
 moved=probe('directory-filename-extension-nearest-name-invariance',both,[current['artifact_type_ref']],path='moved/nearest-name/file.unrelated');ck('moved-result-identity-fields-do-not-change-match-set',all(moved[k]==dedup[k] for k in dedup if k!='artifact_path') and moved['artifact_path']!=dedup['artifact_path'])
 invalid_subject={'schema_version':current['instance_discriminator']['value'],'authority_effect':'invented-authority','classification':{'artifact_type_ref':current['artifact_type_ref']}};probe('carrier-invalidity-does-not-become-type-admission',invalid_subject,[current['artifact_type_ref']])
 bad_registry=copy.deepcopy(legacy);entry=copy.deepcopy(current);entry.update(artifact_type_ref='fixture:candidate/v1',lifecycle_state='candidate-unadmitted');bad_registry['entries'].append(entry);errors=sorted('/'+('/'.join(map(str,e.absolute_path)))+': '+e.message for e in validator.iter_errors(bad_registry));ck('injected-candidate-is-outside-declared-registry-schema',bool(errors))
 bad=probe('out-of-schema-candidate-explicit-robustness-only',{'classification':{'artifact_type_ref':entry['artifact_type_ref']},**unknown},[entry['artifact_type_ref']],bad_registry);ck('out-of-schema-result-records-candidate-with-none-effect',bad['matched_entries'][0]['lifecycle_state']=='candidate-unadmitted' and bad['authority_effect']=='none');candidate_probe={'registry_schema_valid':False,'schema_errors':errors,'helper_does_not_self_validate_registry':True,'source_compliant_input_violation_established':False,'scope':'Robustness observation on an out-of-schema in-memory fixture only;schema responsibility must be mapped.'}
 before=copy.deepcopy(registry)
 try:helper.resolve(registry,unknown,'fixture/subject.json');raw={'result':'unexpected-success'}
 except KeyError as e:raw={'exception':'KeyError','missing_key':e.args[0],'result':'raw-v2-unsupported-by-legacy-pure-helper'}
 ck('raw-current-v2-entries-shape-unsupported',raw.get('missing_key')=='entries' and registry==before and 'entries' not in registry)
 ck('pointer-escape-and-missing-value-observations',helper.pointer_get({'a/b':{'x~y':'value'}},'/a~1b/x~0y')=='value' and helper.pointer_get({},'/absent') is None)
 findings=[{'finding_id':'RES-CONSUMER-FINDING-001','issue':'Exact pure resolver expects legacy entries; raw current v2 admitted_contracts/descriptors registry raises KeyError entries. Current Request wrapper retains legacy registry path;accepted current registry routing map remains pending.'},{'finding_id':'RES-CONSUMER-FINDING-002','issue':'Explicit reference admission eligibility is delegated to the legacy registry schema. Injected candidate entry resolves only on an out-of-schema fixture;this is a robustness observation,not a compliant-input definition violation. Validation responsibility and accepted input domain remain pending.'},{'finding_id':'RES-CONSUMER-FINDING-003','issue':'Structured result uses resolution-result/v1 discriminator;none of143admitted contracts registers it. Whether it is an auxiliary observation or a governed canonical artifact requires an accepted result/type/lifecycle map;absence alone is no admission defect.'},{'finding_id':'RES-CONSUMER-FINDING-004','issue':'Current Registry-v2 and Request-v1 carriers bind current Resolution meaning yet retain candidate body posture. C68/C70 admitted overlays do not establish activation of the shared resolver product code or acceptance of this formalization.'}]
 for x in findings:x.update(status='unresolved',accepted_map_refs=[])
 prior=json.loads((b.BASE/'definitions/cal.definition.artifact-type-request/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+typed['inputs']+list(refs.values()));b.external_current(context)
 report={'schema_version':'definition-assurance-Resolution-carrier-consumer-inspection/v1-candidate','result':'PASS-for-qualified-exact-consumer-observations-and-isolated-pure-resolver-fixtures','authority_effect':'none','source':context['source_selection'],'checks':checks,'check_count':len(checks),'selected_inputs':refs,'direct_current_carriers':selected,'pure_lookup_probes':probes,'pure_lookup_probe_count':len(probes),'legacy_registry_entries':25,'legacy_current_entries':22,'legacy_historical_entries':3,'current_registry_admitted_contracts':143,'result_discriminator':result_disc,'registered_result_contract_refs':result_contracts,'out_of_schema_candidate_probe':candidate_probe,'raw_current_v2_helper_observation':raw,'accepted_semantic_map_refs':[],'unresolved_consumer_findings':findings,'package_validator_entrypoint_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'live_consumer_or_resolver_executed':False,'isolated_pure_resolver_functions_executed':True,'real_subject_type_result_or_authority_created':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_inventory_refresh_complete':False,'claim_ceiling':'Pure fixture lookup observations and exact source/carrier bindings. No operational resolver execution,accepted registry-version map,product activation,canonical result admission or source-owner fidelity.'}
 if write:b.put('carrier-consumer-inspection.json',report)
 elif not b.r.same_json(report,json.loads((b.UNIT/'carrier-consumer-inspection.json').read_bytes())):raise ValueError('Fresh Resolution consumer inspection differs')
 return report
if __name__=='__main__':
 x=inspect('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['result','check_count','pure_lookup_probe_count','legacy_registry_entries','legacy_current_entries','legacy_historical_entries','current_registry_admitted_contracts','semantic_ready']},indent=2))
'''
ast.parse(code)
with (u/'inspect_carrier_consumers.py').open('x') as f:f.write(code)
code='''from pathlib import Path
import subprocess,sys,json
root=Path.cwd();unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact-type-resolution';argv=[sys.executable,'-B',str(unit/'inspect_carrier_consumers.py'),'--write'];r=subprocess.run(argv,cwd=root,capture_output=True)
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (unit/('carrier-inspection-'+k+'.txt')).open('xb') as f:f.write(raw)
with (unit/'carrier-inspection-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'carrier-inspection-stdout.txt','stderr':'carrier-inspection-stderr.txt'},f,indent=2);f.write('\\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
'''
ast.parse(code)
with (p/'capture_consumer.py').open('x') as f:f.write(code)
print('Prepared exact isolated Resolution consumer checker.')
