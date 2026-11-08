#!/usr/bin/env python3
"""Check functional structure, contracts and copy boundary; no runtime execution."""
from pathlib import Path
import argparse,hashlib,json,re,stat
from jsonschema import Draft202012Validator

P=Path(__file__).resolve().parent;Q=P/'proposed';LAB=P.parents[2];U=LAB.parent/'cyberAlchemy-v2'
def sha(data):return hashlib.sha256(data).hexdigest()
def load(path):return json.loads(path.read_text())
def need(ok,message):
 if not ok:raise ValueError(message)
def pointer(value,path):
 for key in path.lstrip('/').split('/') if path else []:value=value[int(key)] if isinstance(value,list) else value[key]
 return value

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--write-report',action='store_true');args=parser.parse_args()
 m=load(P/'IMPORT.json');checks=[];errors=[]
 def run(name,fn):
  try:checks.append(dict(id=name,status='pass',detail=fn()))
  except Exception as e:checks.append(dict(id=name,status='fail',detail=str(e)));errors.append(name+': '+str(e))
 rows=m['payload'];targets={r['target']:r for r in rows};actual={str(f.relative_to(Q)):f for f in Q.rglob('*') if f.is_file() or f.is_symlink()}
 def boundary():
  need(m['scope']=='entire-craft-import' and m['selection_policy']=='retain-structure-and-functional-material; exclude-evidence-only-files','Wrong selection policy')
  need(set(actual)==set(targets) and len(targets)==len(rows)==m['payload_file_count'],'Prepared tree differs from whole-import allowlist')
  need(all(not f.is_symlink() for f in actual.values()),'Unreviewed symlink in prepared payload')
  for target,row in targets.items():
   need(row['source']=='proposed/'+target,'Target/source mapping changed')
   need(row['role'] and 'evidence-only' not in row['role'],'File lacks a functional role')
   data=actual[target].read_bytes();need(len(data)==row['bytes'] and sha(data)==row['sha256'],'Prepared file changed: '+target)
   need(not set(Path(target).parts).intersection({'node_modules','__pycache__'}),'Installed dependency/cache imported: '+target)
   # A schema, verifier, proof-engine module or test fixture may legitimately use
   # evidence terminology. Reject observed outputs, not their functional inputs.
   if row['role'] not in {'implementation-source','test-source','test-fixture','runtime-schema'}:
    need(not set(Path(target).parts).intersection({'receipts','validation-receipts','runs','run-history'}),'Saved execution/receipt directory imported: '+target)
    need(Path(target).name not in {'RESULT.md','REPORT.md','VALIDATION.json','TEST-RESULT.json','PROOF.json','CONNECTED-PROOF.json','validation.json','execution.json','product-test.json','release-test.json'},'Observed result record imported')
   if row['role']=='runtime-configuration' and target.endswith('.json'):
    try:value=load(actual[target])
    except Exception:value=None
    if isinstance(value,dict):need(value.get('result') not in ['pass','fail','PASS','FAIL'] and value.get('status') not in ['pass','fail','PASS','FAIL'],'Observed result disguised as runtime configuration')
   need(not any(part in {'specified-first-order-logic-framework','sfol-test-closure'} for part in Path(target).parts),'Standalone SFOL feature restored')
   if 'mode' in row:need(stat.S_IMODE(actual[target].stat().st_mode)==row['mode'],'Functional executable/file mode lost: '+target)
  need(m['evidence_only_files']==m['source_snapshot_files']==m['standalone_sfol_packages']==0,'Excluded data count changed')
  need(not m['active_import_performed'] and not m['runtime_tests_executed'],'Preparation promoted to execution')
  return dict(files=len(rows),bytes=sum(r['bytes'] for r in rows),evidence_only_files=0,selection='functional role, not smallest file count')
 def structure():
  for area in ['product','project','work','authority','ontology','architecture','implementation','docs']:need('craft/'+area+'/README.md' in targets,'Missing concept home: '+area)
  for target in ['craft/product/product-thesis.record.json','craft/work/goals/craft-orodi-integration/goal.json','craft/authority/method-bindings/craft/method-binding.json','craft/ontology/packages/product-bridge/sources.json','craft/ontology/packages/orodi-bridge/schemas/orodi-ontology.schema.json']:
   need(target in targets,'Functional record/contract removed as evidence: '+target)
  return 'Detailed concept homes and functional records retained'
 def native_contracts():
  specs=[('craft/product/product.json','product-identity/v2'),('craft/project/project.json','project-identity/v1'),('craft/work/goals/establish-craft-product-feature/goal.json','goal/v1'),('craft/work/goals/craft-orodi-integration/goal.json','goal/v1'),('craft/ontology/identity-graph.json','identity-graph/v1'),('craft/authority/method-bindings/craft/method-binding.json','method-binding/v1')]
  for target,kind in specs:Draft202012Validator(load(LAB/'authority/artifact-types'/kind/'schema.json')).validate(load(Q/target))
  orodi=load(Q/'craft/work/goals/craft-orodi-integration/goal.json');need(all(isinstance(x,str) for x in orodi['success_conditions']),'Goal contains achieved-condition evidence instead of acceptance definitions')
  return dict(existing_carrier_schemas=len(specs),goal_assessments_copied=0)
 def capabilities():
  cat=load(Q/'craft/product/capabilities/catalog.json');families=cat['families'];ids=[]
  need(len(families)==14 and {f['family'] for f in families}>={'generation','profiles','tde','evf','orodi'},'Required capability family lost')
  cap_schema=Draft202012Validator(load(LAB/'authority/artifact-types/product-capability/v1/schema.json'))
  realization_schema=Draft202012Validator(load(LAB/'authority/artifact-types/capability-realization-binding/v2/schema.json'))
  bindings_checked=0
  for family in families:
   base=Q/'craft/product/capabilities';data=load(base/family['path']);records=data[family['record_collection']] if family['record_collection'] else [data]
   need([r['node_id'] for r in records]==family['capability_ids'],'Capability catalog membership drift')
   home=base/family['family']
   contracts={r['contract_id']:r for r in load(home/'contracts.json')['contracts']}
   policies={r['policy_id']:r for r in load(home/'policies.json')['policies']}
   realizations={r['node_id']:r for r in load(home/'realizations.json')['bindings']}
   obligations={r['capability_ref']:r for r in load(home/'obligations.json')['registries']}
   for r in records:
    cap_schema.validate(r);ids.append(r['node_id'])
    need(set(r['input_contract_refs']+r['output_contract_refs'])<=set(contracts),'Dangling functional input/output contract')
    need(set(r['context_policy_refs'])<=set(policies),'Dangling context policy')
    need(bool(r['realization_binding_refs']) and set(r['realization_binding_refs'])<=set(realizations),'Missing/dangling realization binding')
    need(r['node_id'] in obligations,'Acceptance obligations dropped')
    need(r['evidence_refs']==r['revision_history']==r['successor_refs']==[],'Historical evidence/history populated in restored candidate')
    for ref in r['realization_binding_refs']:
     binding=realizations[ref];realization_schema.validate(binding);bindings_checked+=1
     need(binding['capability_ref']==r['node_id'] and binding['binding_state']=='candidate' and binding['adoption_decision_ref'] is None,'Binding promoted beyond prepared candidate')
     need(binding['contract']=={k:r[k] for k in ['input_contract_refs','output_contract_refs','context_policy_refs']},'Realization contract differs from capability')
     path,_,selector=binding['capability_version_ref'].partition('#');subject=pointer(load(Q/path),selector)
     need(subject['node_id']==r['node_id'],'Capability version reference does not resolve')
     for realization in binding['realization_refs']:need(realization['realization_ref'] in targets and realization['contract_ref'] in targets,'Realization points to missing component binding')
  need(len(ids)==len(set(ids))==37,'Capability description omitted or duplicated')
  return dict(families=14,native_product_capability_contracts=37,native_realization_bindings=bindings_checked,functional_contract_policy_and_component_references='closed',shared_runtime_qualification='not-inferred')
 def current_sources():
  changes=0
  for row in m['source_preservation_checks']:
   root=LAB if row['root']=='lab' else U;source=root/row['path'];prepared=Q/row['target']
   need(source.is_file() and sha(source.read_bytes())==row['sha256'],'Selected current source changed: '+str(source))
   need(sha(prepared.read_bytes())==row['prepared_sha256'],'Prepared source/link binding changed: '+row['target'])
   if row['binding_changes_only']:
    need(prepared.suffix=='.md','Non-document source silently rewritten');changes+=1
  staged=fixtures=0
  for target,row in targets.items():
   if not row.get('current_source'):continue
   ref=row['current_source'];root=LAB if ref['root']=='lab' else U;source=root/ref['path'];prepared=Q/target
   need(source.is_file() and sha(source.read_bytes())==ref['sha256'],'Restored current implementation source changed: '+str(source));staged+=1
   if prepared.read_bytes()!=source.read_bytes():
    if row.get('binding_change_kind')=='tsconfig-extends-relocation-only':
     original=load(source);current=load(prepared);current['extends']=original['extends'];need(current==original,'Build configuration changed beyond extends binding')
    else:need(prepared.suffix=='.md' and row.get('prepared_binding_changes'),'Restored source silently changed')
   if row['role']=='test-fixture':need(prepared.read_bytes()==source.read_bytes(),'Test fixture source/digest changed');fixtures+=1
  return dict(current_definition_sources=len(m['source_preservation_checks']),restored_implementation_and_work_files=staged,byte_preserved_test_fixtures=fixtures,documents_with_link_rebindings=changes,historical_source_snapshots=0)
 def models():
  total_nodes=total_relations=bridges=0
  for name,expected,schema_path in [('product-bridge',(50,76),'schema/ontology-package.schema.json'),('orodi-bridge',(27,34),'schemas/orodi-ontology.schema.json')]:
   base=Q/'craft/ontology/packages'/name;nodes=load(base/'nodes.json')['nodes'];relations=load(base/'relations.json')['relations'];schema=load(base/schema_path)
   need((len(nodes),len(relations))==expected,'Native source graph coverage changed')
   node_ids={n['node_id']:n for n in nodes};need(len(node_ids)==len(nodes),'Native IDs collapsed')
   for kind,records in [('node',nodes),('relation',relations)]:
    validator=Draft202012Validator({'$schema':schema['$schema'],'$defs':schema['$defs'],'$ref':'#/$defs/'+kind})
    for record in records:validator.validate(record)
   for edge in relations:
    need(edge['from'] in node_ids and edge['to'] in node_ids,'Native relation endpoint missing')
    if edge['branch']=='bridge':
     bridges+=1;need(edge['evidence']['business_refs'] and edge['evidence']['system_refs'],'Bridge verification requirements lost')
   total_nodes+=len(nodes);total_relations+=len(relations)
  identity=load(Q/'craft/ontology/identity-graph.json');need(len(identity['nodes'])==len(identity['relations'])==5,'Admitted identity base replaced with unselected successor')
  return dict(native_graph_nodes=total_nodes+5,native_graph_relations=total_relations+5,bridge_definitions=bridges,current_source_pin_status='requires-reconciliation; not refreshed by this check')
 def consumer():
  mf=load(Q/'craft/ontology/application/source-manifest.json');need(set(mf)=={'schema_version','authority_effect','roots','packages'} and mf['schema_version']=='cal-source-runtime-manifest/v1' and mf['roots']=={'craft':'.'},'Wrong consumer manifest contract')
  need(len(mf['packages'])==3,'Registry mapping omitted')
  n=e=docs=0;keys=set()
  def source(ref):
   need(set(ref)=={'root','path','sha256'} and ref['root']=='craft','Wrong Source contract')
   path=Path(ref['path']);need(not path.is_absolute() and '..' not in path.parts,'Unsafe consumer source path')
   f=Q/'craft'/path;need(f.is_file() and sha(f.read_bytes())==ref['sha256'],'Consumer input missing or stale: '+str(path));return f
  for pkg in mf['packages']:
   need(set(pkg)=={'package_key','ontology_id','profile','owner','source_status','nodes','relations','endpoint_aliases','documents'},'Wrong Package contract')
   need(pkg['package_key']=='pkg-'+sha(('craft:'+pkg['profile']['path']).encode()) and pkg['package_key'] not in keys,'Package identity mismatch');keys.add(pkg['package_key'])
   profile=load(source(pkg['profile']));need(profile.get('ontology_id',profile.get('package_id'))==pkg['ontology_id'],'Profile identity mismatch')
   need(not pkg['endpoint_aliases'],'Unreviewed cross-package aliases')
   ids=set();ends=[]
   for kind in ['nodes','relations']:
    r=pkg[kind];need(set(r)=={'source','selector','id_field','type_field','source_field','target_field','direction_map'},'Wrong Registry contract')
    records=pointer(load(source(r['source'])),r['selector']);need(isinstance(records,list),'Bad source selector')
    seen=set()
    for record in records:
     rid=record[r['id_field']];need(isinstance(rid,str) and rid and rid not in seen,'Invalid registry identity');seen.add(rid)
     need(isinstance(record[r['type_field']],str),'Invalid registry type mapping')
     if kind=='nodes':ids.add(rid);n+=1
     else:ends.append((record[r['source_field']],record[r['target_field']]));e+=1;need(r['direction_map'].get(record.get('direction','directed')) in ['directed','symmetric'],'Unmapped direction')
   need(all(a in ids and b in ids for a,b in ends),'Consumer endpoint closure failed')
   for ref in pkg['documents']:source(ref);docs+=1
  need((n,e)==(82,115),'Consumer graph totals changed')
  views=load(Q/'craft/ontology/views/inputs/index.json')['views'];need(len(views)==9,'Input-view definition missing')
  for row in views:
   view=load(Q/row['path']);need(view['proof_record_files_selected']==0,'Evidence data selected')
   for path in view['input_paths']:need(path in targets,'Input-view dependency absent: '+path)
  return dict(registry_packages=3,nodes=n,relations=e,functional_supporting_documents=docs,input_view_definitions=9,consumer_plan_executed=False)
 def external_components():
  binding=load(Q/'craft/implementation/bindings.json');roots={name:(LAB/'craft/implementation'/relative).resolve() for name,relative in binding['roots'].items()};components={}
  for row in binding['components']:
   ref=load(Q/row['path']);need(ref['component_id']==row['component_id'],'Component index mismatch');components[ref['component_id']]=ref
   f=roots[ref['root']]/ref['path'];need(f.is_file() and sha(f.read_bytes())==ref['manifest_sha256'],'Shared/external current component changed')
   if ref['copy_files']:
    need('prepared_source_root' in ref and (Q/ref['prepared_source_root']).is_dir(),'Component has no restored source home')
   else:need(ref['access']=='read-only-reference','Shared runtime access changed')
  need(len(components)==18 and {'system-integration','architecture-conformance','operational-resilience','alchlang-extensions'}<=set(components),'Functional component binding omitted')
  need(components['core']['version']==components['alchlang']['peer_dependencies']['@domainspec-v2/cli']==components['ai-profiles']['peer_dependencies']['@domainspec-v2/cli'],'Core peer mismatch')
  return dict(components=len(components),runtime_tests_executed=False,relocation_or_host_qualification=False)
 def restored_inputs():
  roles=[r['role'] for r in rows]
  need(roles.count('implementation-source')>1000 and roles.count('test-source')>1000 and roles.count('test-fixture')>500,'Implementation/test restoration reduced to placeholders')
  for target in ['craft/implementation/cli/package.json','craft/implementation/alchlang/package.json','craft/implementation/profiles/ai/package.json','craft/implementation/test-derivation-engine/src/index.ts','craft/implementation/system-integration/compiler/system-integration-v1.mjs','craft/implementation/config/tsconfig.base.json','craft/implementation/cli/profiles/node-http-shared-ports-v1/entry.tpl']:
   need(target in targets,'Required functional source/build/template input missing: '+target)
  build=load(Q/'craft/implementation/build-inputs.json')
  for ref in build['tsconfig_bindings']:
   cfg=load(Q/ref['path']);need(cfg['extends']==ref['final_extends'],'Build input binding does not match configuration')
   final=(LAB/ref['path']).parent/cfg['extends'];final=final.resolve()
   if isinstance(ref['target_input'],str):need(final==LAB/ref['target_input'] and ref['target_input'] in targets,'Local build input does not resolve after relocation')
   else:
    source=U/ref['target_input']['path'];need(final==source and source.is_file() and sha(source.read_bytes())==ref['source_input_sha256'],'Shared build input does not resolve')
  work=load(Q/'craft/work/tasks/source-tasks.json')['tasks'];need(len(work)==114 and len({(r['plan'],r['task_id']) for r in work})==114,'Current source plan/task definitions incomplete')
  for task in work:need(task['definition_path'] in targets and task['status_is_fresh_runtime_acceptance'] is False,'Source task missing or treated as fresh acceptance')
  return dict(implementation_sources=roles.count('implementation-source'),test_sources=roles.count('test-source'),fixtures=roles.count('test-fixture'),current_source_tasks=len(work),build_input_bindings=len(build['tsconfig_bindings']))
 def apply_plan():
  plan=load(P/'APPLY.json');need(not plan['executed'] and not plan['delete_existing_files'] and not plan['historical_backups_imported'],'Apply plan changed execution/deletion boundary')
  current={t for t in targets if (LAB/t).exists()};need(current=={r['target'] for r in plan['existing_targets']},'Existing target coverage changed')
  for row in plan['existing_targets']:
   need(sha((LAB/row['target']).read_bytes())==row['expected_current_sha256'] and targets[row['target']]['sha256']==row['candidate_sha256'],'Collision precondition/candidate changed')
   need(not row['automatic_blind_overwrite'] and row['action'] in ['replace-navigation-preserving-live-entrypoints','review-and-apply-current-reference-rebinding','keep-identical'],'Unresolved blind overwrite')
  need('craft/tsconfig.base.json' in plan['must_keep_existing_paths'] and 'craft/tsconfig.base.json' not in targets,'Legacy runtime build configuration would be overwritten')
  return dict(existing_targets=len(current),blind_overwrites=False,executed=False)
 def navigation():
  links=0
  docs=[Q/t for t,r in targets.items() if t.endswith('.md') and r['role']!='test-fixture']
  for f in [P/'PLAN.md',*docs]:
   for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',f.read_text()):
    if re.match(r'[A-Za-z][A-Za-z0-9+.-]*:',link) or link.startswith('#'):continue
    need((f.parent/link.split('#')[0]).exists(),'Broken reader link: '+str(f)+': '+link);links+=1
   # Current source documents may intentionally use Markdown hard line breaks.
   # Preserve those bytes; enforce authored proposal formatting separately.
   if f==P/'PLAN.md' or not targets[str(f.relative_to(Q))].get('current_source'):
    need(all(line.rstrip()==line for line in f.read_text().splitlines()),'Trailing Markdown whitespace: '+str(f))
  return dict(reader_links=links)
 for name,fn in [('functional-copy-boundary',boundary),('restored-concept-structure',structure),('identity-and-goal-contracts',native_contracts),('capability-coverage',capabilities),('current-functional-source-bindings',current_sources),('native-ontology-models',models),('application-input-contract',consumer),('current-external-components',external_components),('restored-functional-implementation-and-work',restored_inputs),('explicit-apply-collision-handling',apply_plan),('reader-navigation',navigation)]:run(name,fn)
 report=dict(status='fail' if errors else 'pass',scope='Structured functional Craft proposal with restored source/contracts/work; evidence-only records excluded',payload_files=len(rows),payload_bytes=sum(r['bytes'] for r in rows),evidence_only_files=0,source_snapshot_files=0,standalone_sfol_packages=0,legacy_named_compatibility_inputs=len(m['restoration']['legacy_named_dependency_files']),checks=checks,errors=errors,source_readiness='requires-source-pin-path-reconciliation',application_readiness='requires-named-consumer-and-host-runtime-qualification',runtime_tests_executed=False,active_import_performed=False)
 if args.write_report:(P/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({key:report[key] for key in ['status','payload_files','payload_bytes','evidence_only_files','source_readiness','application_readiness','errors']}));raise SystemExit(bool(errors))

if __name__=='__main__':main()
