"""Read-only source schema/render/lookup checks; never invoke the canonical receipt-writing validator."""
import copy
import json
import types
import build_candidate as b

def table_rows(raw,id,version,path,sha=None):
 rows=[];header=None
 for line in raw.decode().splitlines():
  if not line.startswith('|'):continue
  cells=[cell.strip().strip('`') for cell in line.strip('|').split('|')]
  if 'ID' in cells and 'Version' in cells:header=cells;continue
  if header is None or len(cells)!=len(header):continue
  row=dict(zip(header,cells))
  if row.get('ID')==id and row.get('Version')==version:rows.append(row)
 if len(rows)!=1:return []
 selected=rows[0]
 if selected.get('Path',selected.get('Candidate path'))!=path or sha is not None and selected.get('Digest')!=sha:return []
 return rows

def verify(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes())
 for reference in context['sources']:
  if b.ref(b.ROOT/reference['path'])!=reference:raise ValueError('Changed initial selected bytes')
 snap=b.snapshot();source=json.loads((b.UNIT/'t.json').read_bytes())['payload']['source'];document=b.co.source_document(snap,source);b.r.verify(snap,b.ROOT)
 folder=b.ROOT/'authority/definitions/candidates/0013-integrated-lab-definition-model';paths={'schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','registry':b.ROOT/'authority/definitions/registry.json','index':b.ROOT/'authority/definitions/DEFINITIONS-INDEX.md','proposed_registry':folder/'registry-postimage.json','proposed_index':folder/'DEFINITIONS-INDEX.md','source_projection':(b.ROOT/source['path']).with_name('DEFINITION.md'),'checker':b.UNIT/'verify_source_checks.py'};selected={name:b.ref(path) for name,path in paths.items()};raws={name:b.r.read_bytes(b.ROOT,reference['path']) for name,reference in selected.items()}
 if any(b.r.digest(raws[name])!=reference['sha256'] for name,reference in selected.items()):raise ValueError('Capture race')
 schema=b.r.parse(raws['schema'],'definition-schema');b.c.Draft202012Validator.check_schema(schema);errors=list(b.c.Draft202012Validator(schema).iter_errors(document))
 module=types.ModuleType('_bound_definition_generator');module.__file__=str(paths['generator']);exec(compile(raws['generator'],str(paths['generator']),'exec'),module.__dict__)
 before=copy.deepcopy(document);first=module.render(document).encode();second=module.render(document).encode()
 if document!=before:raise ValueError('Bound renderer mutated its input')
 registry=b.r.parse(raws['registry'],'live-registry');proposal=b.r.parse(raws['proposed_registry'],'proposed-registry');id=source['definition_id'];version=source['version_ref'].split('@',1)[1];selected_entries=[row for row in registry['entries'] if row['definition_id']==id and row['version']==version];proposed_entries=[row for row in proposal['entries'] if row['definition_id']==id and row['version']==version]
 checks=[{'check_id':'source-schema-digest-current','result':document['schema_digest']==selected['schema']['sha256']},{'check_id':'source-generator-digest-current','result':document['source_direction']['generator_sha256']==selected['generator']['sha256']},{'check_id':'source-Definition-v1-schema-valid','result':not errors},{'check_id':'two-render-exact-byte-equality','result':first==second},{'check_id':'bound-source-projection-parity','result':first==raws['source_projection']},{'check_id':'source-once-in-proposed-registry','result':len(proposed_entries)==1 and proposed_entries[0]['path']==source['path'] and proposed_entries[0]['sha256']==source['sha256']},{'check_id':'source-once-in-proposed-index','result':len(table_rows(raws['proposed_index'],id,version,source['path'],source['sha256']))==1},{'check_id':'source-once-in-current-registry','result':len(selected_entries)==1 and selected_entries[0]['path']==source['path'] and selected_entries[0]['sha256']==source['sha256'] and registry['current_lookup'][id]==source['version_ref']},{'check_id':'source-once-in-current-index','result':len(table_rows(raws['index'],id,version,source['path']))==1}]
 core=json.loads((b.UNIT/'t.json').read_bytes())['payload'];queries=json.loads((b.UNIT/'query-policy.json').read_bytes())['queries'];formal=document['voices']['scientific_formal']['formal_expression']
 checks += [{'check_id':'exact-source-identity-and-current-admission','result':document['definition_id']==source['definition_id']=='cal.definition.challenge-contract' and selected_entries[0]['lifecycle_state']=='admitted' and selected_entries[0]['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION'},
 {'check_id':'printed-positive-and-nonentailment-vocabulary-preserved','result':formal=='ChallengeContract(x) => governed_identity_or_record(x) and bounded_scope(x); ChallengeContract(x) =/=> authority_effect(x).'},
 {'check_id':'duplicate-genus-and-route-exclusions-accounted','result':sum(x['disposition']=='encoded' and x['forms']==['genus-differentia'] for x in core['clauses'])==3 and sum(x['disposition']=='encoded' and x['formal_statement']==b.ROUTE_EXCLUSION for x in core['clauses'])==4},
 {'check_id':'nonentailment-targets-not-primary-assumptions','result':not core['assumptions'] and len(queries)==20 and all(x['selected_in_T'] is False for x in queries) and any(x['query_id']=='filing-does-not-entail-ActualSuspended' for x in queries) and any(x['query_id']=='filing-does-not-entail-ActualReversed' for x in queries)},
 {'check_id':'historical-candidate-wording-not-source-interpretation-admission','result':document['claim_ceiling'].startswith('This candidate defines Challenge Contract for review only.') and core['source_fidelity']=='pending'}]
 if not all(row['result'] for row in checks):raise ValueError(json.dumps(checks))
 for name,path in paths.items():
  if b.ref(path)!=selected[name]:raise ValueError('Closing selected-input drift')
 b.r.verify(snap,b.ROOT)
 report={'schema_version':'definition-assurance-ChallengeContract-source-checks/v1-candidate','status':'PASS-for-exact-source-schema-render-and-lookup-checks','authority_effect':'none','semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'source':source,'selected_inputs':selected,'checks':checks,'schema_errors':[{'path':list(error.path),'message':error.message} for error in errors],'first_render_sha256':b.r.digest(first),'second_render_sha256':b.r.digest(second),'projection_bytes':len(first),'current_registry_entry_lifecycle':selected_entries[0]['lifecycle_state'],'current_registry_admission_ref':selected_entries[0]['admission_decision_ref'],'source_inner_claim_ceiling':document['claim_ceiling'],'claim_ceiling':'Fourteen actual read-only checks on one source record with pinned schema/generator and exact proposed/current lookup bytes. Two renders do not prove generic determinism. Existing source registry admission is not fidelity approval or promotion of this formal interpretation; source historical candidate wording is preserved.'}
 if write:
  for name,raw in [('source-render-1.md',first),('source-render-2.md',second)]:
   with (b.UNIT/name).open('xb') as stream:stream.write(raw)
  b.put('source-checks.json',report)
 else:
  if not b.r.same_json(report,json.loads((b.UNIT/'source-checks.json').read_bytes())) or first!=(b.UNIT/'source-render-1.md').read_bytes() or second!=(b.UNIT/'source-render-2.md').read_bytes():raise ValueError('Fresh source check differs')
 return report

def main():
 result=verify('--write' in b.sys.argv);print(json.dumps({'result':result['status'],'checks':len(result['checks']),'render_bytes':result['projection_bytes'],'render_sha256':result['first_render_sha256'],'current_registry_entry_lifecycle':result['current_registry_entry_lifecycle'],'source_fidelity':'pending','semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
