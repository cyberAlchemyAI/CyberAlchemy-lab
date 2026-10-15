"""Prepare exact next source only after full Intent seal and separate audit."""
from pathlib import Path
import copy,hashlib,importlib.util,json
import jsonschema
root=Path.cwd();p=Path(__file__).resolve().parent
base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
for stem in ['full-delivery-seal','full-delivery-audit']:
    r=json.loads((p/(stem+'-command-result.json')).read_text());assert r['exit_code']==0 and not(p/r['stderr']).read_bytes()
assert not(base/'definitions/cal.definition.intent-resolution').exists(),'Native construction must be a separate next stage'
checks=[];refs=[]
def check(name,value):assert value,name;checks.append({'check_id':name,'result':True})
def bound(path):
    raw=path.read_bytes();refs.append({'path':str(path.relative_to(root)),'sha256':hashlib.sha256(raw).hexdigest()});return raw
snapshot=json.loads(bound(base/'current-snapshot.json'));rows=[r for r in snapshot['current_entries'] if r['definition_id']=='cal.definition.intent-resolution'];check('one-current-IntentResolution',len(rows)==1);row=rows[0]
raw=bound(root/row['path']);check('exact-source-digest',hashlib.sha256(raw).hexdigest()==row['sha256']=='cf84080dba84433926c7f11759057ca4277458152518aaa243d61a948e96c136');d=json.loads(raw)
check('exact-source-version',d['definition_id']+'@'+d['version']==row['version_ref']=='cal.definition.intent-resolution@1.0.0-candidate.1')
check('positive-current-C65-overlay',row['effective_state']=='admitted-current' and row['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION')
binding=next(r for r in snapshot['admission_decision_bindings'] if r['decision_ref']==row['admission_decision_ref']);decision_raw=bound(root/binding['path']);check('exact-current-C65-decision',hashlib.sha256(decision_raw).hexdigest()==binding['sha256']);decision=json.loads(decision_raw)
selected=[r for r in decision['admitted_definitions'] if r['definition_ref']==row['version_ref']];check('C65-exact-selected-row',len(selected)==1 and selected[0]['path']==row['path'] and selected[0]['sha256']==row['sha256'])
auth=decision['authorization'];check('C65-authorization-bound',hashlib.sha256(bound(root/auth['path'])).hexdigest()==auth['sha256'])
check('C65-owner-admitted',decision['status']=='owner-admitted');check('C65-no-types-or-consumers',decision['admission_result']['artifact_types_admitted']==decision['admission_result']['consumer_activations']==decision['admission_result']['relation_kinds_admitted']==0)
schema_raw=bound(root/'authority/artifact-types/definition/v1/schema.json');check('source-schema-digest',hashlib.sha256(schema_raw).hexdigest()==d['schema_digest']);schema=json.loads(schema_raw);jsonschema.validators.validator_for(schema)(schema).validate(d);check('Definition-schema-valid',True)
generator=root/'authority/artifact-types/definition/v1/generator.py';check('source-generator-digest',hashlib.sha256(bound(generator)).hexdigest()==d['source_direction']['generator_sha256']);spec=importlib.util.spec_from_file_location('next_definition_pure_projection',generator);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
before=copy.deepcopy(d);one=module.render(d);two=module.render(d);check('pure-render-repeatability',one==two and d==before);check('exact-stored-projection',one.encode()==bound((root/row['path']).with_name('DEFINITION.md')))
upstream=root/'.arcanum/ontology-vault/2026-10-05-lab-integrated-model.md';embedded=d['source_refs'][0];check('whole-file-upstream-source-digest',embedded['selector']=='whole-file' and hashlib.sha256(bound(upstream)).hexdigest()==embedded['content_sha256'])
check('embedded-source-posture-preserved',embedded['admission_posture']=='candidate-unadmitted' and embedded['source_admission_ref'] is None)
check('historical-candidate-source-ceiling-preserved','review only' in d['claim_ceiling'] and 'does not admit' in d['claim_ceiling'])
normative=d['voices']['scientific_formal'];check('exact-owner-decision-genus','attributable owner decision' in normative['normative_statement'] and 'one exact Intent' in normative['normative_statement'] and 'satisfaction test' in normative['normative_statement'])
check('separate-effects-boundary','authority_effect' in normative['formal_expression'] and 'separate admitted contracts' in d['boundaries'][1]);check('no-admitted-typed-relations-from-source-record',d['typed_relations']==[])
terms=['Intent','Product','Project','Goal','Research','Capability','Decision','Principal','Authority'];deps=[];unresolved=[]
for term in terms:
    matches=[r for r in snapshot['current_entries'] if r['term'].casefold()==term.casefold()]
    if len(matches)==1:
        match=matches[0];check('dependency-source-'+term,hashlib.sha256(bound(root/match['path'])).hexdigest()==match['sha256']);deps.append({k:match[k] for k in ['definition_id','version_ref','path','sha256','term']})
    else:unresolved.append({'label':term,'matching_current_entries':len(matches),'disposition':'requires-explicit-selection-no-name-equality-import'})
record={'schema_version':'IntentResolution-next-source-preparation/v1-candidate','authority_effect':'none','result':'PASS-for-exact-next-source-only','source':{k:row[k] for k in ['definition_id','version_ref','path','sha256']},'current_admission_ref':row['admission_decision_ref'],'checks':checks,'check_count':len(checks),'inputs':refs,'native_construction_started':False,'native_T_created':False,'source_fidelity':'pending','semantic_ready':False,'whole_definition_proof':None,'accepted_maps':[],'proposed_types_first':['IntentResolutionRef','ExactIntentRef','OwnerDecisionRef','AttributorRef','GovernedOutputRef','SatisfactionTestRef','ScopeRef'],'necessary_logic_to_review':['Selected resolution nominates one exact Intent, attributable owner decision, bounded scope and a declared satisfaction test.','At least one selected governed output is needed; the source example permits several outputs in one resolution.','Named Product, Project, Goal, Research and Capability are inclusive output roles; other governed outputs remain possible.','Selection and satisfaction-test nomination do not prove delivery, actual satisfaction or related output suitability.','No Implementation embedding, unrelated-work authorization or term-alone authority/effect inference.','No unique resolution per Intent, exhaustive output taxonomy, automatic instance admission or globally forced successor policy.'],'candidate_dependency_sources':deps,'unresolved_dependency_labels':unresolved,'source_relations_not_created':True,'next_stage':'Prepared candidate source account, qualified types, necessary guards and nonvacuous T/I controls before native authoring','original_episode_scope_preserved':{'identities':183,'versions':189,'source_files':201,'tasks':121,'planning_edges':511,'work_units':797,'frontiers':36}}
with(p/'next-IntentResolution-source-preparation.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps({'result':record['result'],'checks':len(checks),'source':record['source'],'dependency_sources':len(deps),'unresolved_labels':unresolved,'native_T_created':False,'semantic_ready':False}))
