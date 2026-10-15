"""Independent audit of historical authenticated original-source Context delivery.

Verify recorded evidence without restoring any host policy, key, or Session.
"""
import argparse,ast,base64,hashlib,importlib.util,json,os,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator,FormatChecker
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
SELECTED=ROOT/'product/lab/release-candidates/v1/interface/custody-context-delivery-v1'
SOURCE=HERE/'custody-context-audit-source-0001.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':sha(p.read_bytes())}
def parse(raw):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('duplicate audit JSON key')
            d[k]=v
        return d
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite audit JSON')))
def load(p):return parse(p.read_bytes())
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def wire(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def instant(v):return datetime.fromisoformat(v.replace('Z','+00:00'))
def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True,mode=0o700);fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(v))
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);a=ap.parse_args()
    assert sha(SOURCE.read_bytes())==a.source_sha256;m=load(SOURCE);checks=[]
    def need(v,name):
        if not v:raise AssertionError(name)
        checks.append(name)
    for row in m['files']:need(bind(ROOT/row['path'])==row,'exact frozen input '+row['path'])
    rows={r['path']:r for r in m['files']};parent=load(ROOT/m['parent_receipt_binding']['path'])
    need(parent['result']=='PASS' and not parent['task_complete'],'retain incomplete original parent')
    for row in parent['files']:need(rows.get(row['path'])==row,'retain original parent file '+row['path'])
    terminal=load(ROOT/m['terminal_binding']['path'])
    need(terminal['selected_exit_codes']=={'build':0,'checks':0},'actual construction and checks terminal zero')
    old=methods(SELECTED.parent/'context-delivery-v3/run_checks.py');new=methods(SELECTED/'test_original_delivery.py')
    need(old==new and len(old)==38,'all38original Context test method ASTs unchanged')
    need(len(methods(SELECTED/'test_raw_delivery.py'))==8,'eight additional raw-source criteria')
    tests=load(SELECTED/'receipts/checks.json')
    need(tests['result']=='PASS' and tests['tests_run']==tests['expected_tests']==46,'all46 actual tests pass')
    need(len(tests['cases'])==len({r['test'] for r in tests['cases']})==46 and all(r['result']=='PASS' for r in tests['cases']),'all46 terminal case results exactly once')
    need(tests['source_sha256']==m['delivery_source_binding']['sha256'] and tests['package_sha256']==m['delivery_package_binding']['sha256'],'tests exact source and actual outputs')
    package=SELECTED/'packages/0001';manifest=load(package/'manifest.json')
    actual={p.relative_to(ROOT).as_posix() for p in package.rglob('*') if p.is_file()}
    need(actual=={r['path'] for r in manifest['files']}|{(package/'manifest.json').relative_to(ROOT).as_posix()},'closed actual Context derived fileset')
    for r in manifest['files']:need(bind(ROOT/r['path'])==r and (ROOT/r['path']).stat().st_mode&0o777==0o600,'private exact derived file '+r['path'])
    build=load(package/'build-result.json');policy=load(package/'host-permission-public.json');auth=load(package/'authentication-proof.json');trusted=load(package/'trusted-context.json')
    query=load(package/'request.json');delivery=load(package/'delivery.json');proof=load(package/'delivery-provenance.json');lesson=load(package/'lesson-selection.json')
    need(build['result']=='PASS' and build['actual_generated_artifact_carriers']==30 and build['ontology_nodes']==15 and build['ontology_edges']==10,'actual30carrier construction')
    root=Path(build['owned_host_root'])
    need(root.parent==Path('/tmp') and root.name.startswith('cal-R03-context-host-') and not root.exists() and build['owned_host_policy_and_transport_key_removed'],'owned host policy/key root actually removed')
    need(build['active_Agents_created']==build['public_API_operations_added']==0 and build['authority_effect']=='none' and build['actual_owner_outcome'] is None,'no activeAgent publicAPI or authority effect')
    need(set(auth)=={'challenge','signature'},'closed signed authentication envelope')
    challenge=auth['challenge'];policy_sha=sha((package/'host-permission-public.json').read_bytes())
    need(challenge['policy_sha256']==policy_sha==trusted['policy_bindings'][0]['sha256']==proof['authority_envelope_binding']['sha256'],'exact historical independent host policy original bytes')
    key=Ed25519PublicKey.from_public_bytes(base64.b64decode(policy['reader_public_key'],validate=True))
    key.verify(base64.b64decode(auth['signature'],validate=True),wire(challenge));checks.append('actual independently verified Ed25519 challenge signature')
    need(trusted['authentication_evidence_binding']['sha256']==sha((package/'authentication-proof.json').read_bytes()),'exact authenticated proof bytes')
    need(challenge['connection_ref']==trusted['connection_ref'] and challenge['host_instance_ref']==trusted['host_instance_ref'],'nonce proof connection and host binding')
    need(challenge['expires_at']==trusted['expires_at']==policy['expires_at'] and len(bytes.fromhex(challenge['nonce']))==32,'challenge expiry and32byte nonce')
    need(trusted['principal_ref']==policy['principal_ref']==proof['authenticated_principal_ref']==query['actor']['principal_ref'],'authenticated principal independent of public request')
    need(trusted['scope_refs']==[policy['scope_ref']] and trusted['authority_scope']=='operator-local' and not trusted['accept_client_supplied_authority_context'],'explicit scoped independently trusted transport')
    need(query['actor']=={k:trusted[k] for k in ['principal_ref','agent_instance_ref','session_ref','assignment_ref']}|{'role_assignment_refs':trusted['role_assignment_bindings']},'complete public actor equals independently authenticated actor')
    need(trusted['limits']=={'max_request_bytes':policy['max_input_bytes'],'max_response_bytes':policy['max_output_bytes'],'max_actions':1,'deadline':policy['expires_at']},'host input output action and expiry limits retained')
    need(trusted['policy_bindings'][1]=={'ref':m['authorization_binding']['path'],'sha256':m['authorization_binding']['sha256']},'exact existing scoped authorization evidence')
    need(trusted['role_assignment_bindings']==[] and all(trusted[k] is None for k in ['agent_instance_ref','assignment_ref','session_ref']),'operator proof grants no agent/session/owner role')
    need(policy['allowed_operations']==['context.get','session.open'] and policy['max_session_seconds']==900 and policy['authority_effect']=='none' and policy['actual_owner_outcome'] is None,'closed bounded construction host operations')
    need(query['budget']['max_actions']==0 and query['authority_effect']=='none','Context request is read only')
    need(delivery['request_binding']['sha256']==sha((package/'request.json').read_bytes()) and proof['verified_original_binding']['sha256']==sha((package/'delivery.json').read_bytes()),'original request and delivery byte custody')
    need(delivery['lesson_selection_binding']['sha256']==sha((package/'lesson-selection.json').read_bytes()),'exact lesson selection original bytes')
    need(proof['mapped_package_sha256']==tests['mapped_package_sha256']==m['mapped_package_binding']['sha256'],'exact native selected package')
    for k in ['assignment','work','coordination_context']:need(query[k]==proof[k],'exact requested participation tuple '+k)
    index=load(package/'artifact-index.json');need(len(index)==30 and len({r['artifact']['identity_ref'] for r in index})==30,'30distinct actual derived artifact instances')
    artifacts={r['artifact']['identity_ref']:(r,load(ROOT/r['original_binding']['path'])) for r in index}
    need([r['artifact'] for r in index]==proof['generated_artifact_refs'],'exact output index and provenance headers')
    kinds={}
    for r,b in artifacts.values():
        need(bind(ROOT/r['original_binding']['path'])==r['original_binding'] and sha((ROOT/r['original_binding']['path']).read_bytes())==r['artifact']['byte_sha256'],'actual derived header exactbody '+b['node_id'])
        need(r['artifact']['identity_ref']==b['node_id'] and r['artifact']['scope_ref']==b['scope_ref']==policy['scope_ref'],'actual derived identity/scope '+b['node_id'])
        kinds.setdefault(b['kind'],[]).append(b)
    need({k:len(v) for k,v in kinds.items()}=={'ontology-node':15,'ontology-edge':10,'ontology':1,'ontology-cut':1,'ontology-view':1,'context-request':1,'context-view':1},'all seven carrier families complete')
    cv=kinds['context-view'][0];ov=kinds['ontology-view'][0];cut=kinds['ontology-cut'][0];ontology=kinds['ontology'][0];cr=kinds['context-request'][0]
    need(delivery['context_view']==artifacts[cv['node_id']][0]['artifact'] and delivery['ontology_view']==artifacts[ov['node_id']][0]['artifact'],'delivery references actual Context/Ontology View bytes')
    need(delivery['expires_at']==proof['expires_at']==cv['expires_at']==ov['payload']['expires_at'],'same exact delivery/view expiry')
    generated=instant(cv['generated_at']);expires=instant(delivery['expires_at'])
    need(instant(policy['not_before'])<=generated<expires<=instant(policy['expires_at']) and expires<=instant(query['budget']['deadline']) and expires-generated<=timedelta(minutes=5),'historical delivery generated inside independent host window with five minute deadline')
    need(instant(cr['requested_at'])==generated==instant(ov['payload']['freshness_at']),'same actual generation time')
    need(delivery['posture']=='ready' and delivery['scope_enforced'] and delivery['gaps']==[] and delivery['authority_effect']=='none','recorded actual ready construction posture')
    spec=importlib.util.spec_from_file_location('_cal_context_independent_audit',SELECTED/'__init__.py',submodule_search_locations=[str(SELECTED)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    D=__import__(spec.name+'.build',fromlist=['preflight']);D.preflight(m['delivery_source_binding']['sha256'])
    need(D.reader is D.MAPPED.reader and D.records is D.MAPPED.records and D.EL is D.reader.adapter.eligibility,'consistent selected reader records and eligibility class objects')
    schemas=D.API.Schemas(D.API_PROFILE_PIN)
    need(schemas.protocol_valid('urn:cyberalchemy-lab:protocol:context-query:v1-candidate',query) and schemas.protocol_valid('urn:cyberalchemy-lab:protocol:context-delivery:v1-candidate',delivery),'current API original Context protocol schemas')
    mapping,native,_=D.selected_mapping(m['mapped_package_binding']['sha256']);checks.append('independent actual cold native process byte parity')
    need(proof['native_cut_digest']==sha(encoded(native['cut']))==cut['payload']['calculated_digest']==ov['payload']['cut_digest'],'exact native cut digest distinct from signed sourcecut')
    need(cut['payload']['semantic_cursor']==ov['payload']['semantic_cursor']==native['cut']['semantic_cursor']==native['governance_cursor']==25,'native25exact cut joins')
    need(cut['payload']['source_event_set_digest']==ov['payload']['source_event_set_digest']==native['cut']['source_event_set_digest'],'actual native event set digest')
    need(ov['payload']['cut_ref']==cut['node_id'] and set(ontology['node_refs'])==set(cut['payload']['node_refs'])=={b['node_id'] for b in kinds['ontology-node']},'complete native node ontology/cut/view closure')
    need(set(ontology['relation_refs'])==set(cut['payload']['edge_refs'])=={b['node_id'] for b in kinds['ontology-edge']},'complete native edge ontology/cut closure')
    need(cv['request_ref']==cr['node_id'] and cv['context_ref']==cr['context_ref'] and cv['context_version_ref']==cr['context_version_ref'],'Context request/view exact signed Context version linkage')
    events=[load(p) for p in sorted((D.MAPPED.HERE/'packages/0001/semantic').glob('*.json'))];governance=[load(p) for p in sorted((D.MAPPED.HERE/'packages/0001/governance').glob('*.json'))]
    need(len(proof['correspondence'])==len(proof['source_material_provenance'])==len(mapping['rows'])==25,'25full source/native/carrier correspondences')
    need(delivery['included_refs']==[r['artifact'] for r in mapping['rows']] and cr['selectors']==[r['version_ref'] for r in delivery['included_refs']],'exact25domain source selections')
    raw_count=0
    with D.reader.open_signed(D.SOURCE_PIN,D.SOURCE_PACKAGE) as source:
        need(source.source_cut==mapping['source_cut']==query['source_cut']==delivery['source_cut']==proof['source_cut']==lesson['source_cut'],'actual signed sourcecut shared across all outputs')
        need(source.source_cut['source_profile_sha256']==source.view.handle.manifest['profile_binding']['sha256']==trusted['source_profile_binding']['sha256'],'actual selected engine profile')
        period=load(ROOT/policy['period_binding']['path']);need(bind(ROOT/policy['period_binding']['path'])==policy['period_binding'],'exact original Assignment period binding')
        inherited=load(ROOT/period['inherited_validity_binding']['path'])
        need(period['not_before']==inherited['not_before'] and period['expires_at']==inherited['expires_at'],'absolute Assignment period never reset or extended')
        need(instant(period['not_before'])<=instant(policy['not_before'])<instant(policy['expires_at'])<=instant(period['expires_at']),'host window bounded by exact original Assignment interval')
        contracts=source.view.data['projection']['contracts']
        for r,b in artifacts.values():
            contract=contracts[r['artifact']['carrier_ref']];schema_path=ROOT/contract['schema_path']
            need(sha(schema_path.read_bytes())==contract['schema_sha256'] and contract['lifecycle_state']=='admitted-current','exact admitted original carrier schema '+b['kind'])
            Draft202012Validator(load(schema_path),format_checker=FormatChecker()).validate(b);checks.append('actual independent schema validation '+b['node_id'])
            D.EL.no_private_memory(b);checks.append('actual derived body privacy '+b['node_id'])
        node_for_subject={c['native_identity']['subject_id']:c['carrier_identity'] for c in proof['correspondence'] if c['native_identity']['subject_kind']=='node'}
        for row,event,g,cor,pv in zip(mapping['rows'],events,governance,proof['correspondence'],proof['source_material_provenance']):
            ar=row['artifact'];subject=source.view.subjects[ar['version_ref']];raw,locator,encoding,enclosing=D.reader.adapter.model.record_bytes(source.view,subject)
            need(ar==D.reader.adapter.model.artifact_ref(source.view,subject) and sha(raw)==ar['byte_sha256'],'actual signed original header/body '+ar['version_ref'])
            source.view.handle.operations.validate_record(subject['record'],subject['carrier_ref'],source.view.data['projection']);D.EL.no_private_memory(parse(raw))
            file_ref,sep,selector=locator.partition('#');material={'source_ref':file_ref,'selector':selector if sep else '#','sha256':enclosing}
            need(pv['artifact']==ar and pv['original_material']==material and pv['selected_body_encoding']==encoding and pv['selected_original_body_sha256']==sha(raw),'original enclosing/source selector versus selected body '+ar['version_ref'])
            if encoding==source.view.handle.custody.ENCODING:need(raw!=encoded(subject['record']),'original raw body differs from serializer '+ar['version_ref']);raw_count+=1
            state=event['complete_resulting_semantic_state'];sr={'semantic_event_id':event['event_id'],'semantic_event_digest':event['event_digest'],'semantic_cursor':event['semantic_cursor']}
            need(cor['native_identity']==row['subject_identity']==event['subject_identity'] and cor['semantic_event_ref']==sr==g['semantic_ref']==g['complete_resulting_governance_state']['semantic_ref'] and cor['governance_event_ref']==g['event_id'],'exact native/carrier semantic and governance join '+ar['version_ref'])
            body=artifacts[cor['carrier_identity']][1];payload=body['payload'];need(payload['replay_source'] is False and payload.get('semantic_event_ref',payload.get('governance_binding',{}).get('semantic_event_ref'))==sr,'carrier is derived exact event representation '+ar['version_ref'])
            if body['kind']=='ontology-node':
                need(payload['represented_subject']=={'kind':row['semantic_kind'],'ref':ar['identity_ref'],'version_ref':ar['version_ref'],'digest':ar['byte_sha256']},'represented original artifact tuple '+ar['version_ref'])
                need(payload['semantic_state']['semantic_components']==[c['component_id'] for c in state['semantic_components']] and payload['semantic_state']['semantic_definition_refs']==[w['version_ref'] for w in row['definition_witnesses']],'complete qualified component and Definition layers '+ar['version_ref'])
                need(payload['semantic_state']['typed_properties']==state['typed_properties']['values'],'native exact typed properties '+ar['version_ref'])
            else:
                p=subject['record']['payload'];need(payload['edge_mode']=='global-projection' and payload['local_interpretation'] is None and payload['closed_qualifiers']==p['qualifiers']==row['qualifiers'],'closed globally typed relation qualifiers '+ar['version_ref'])
                need(payload['global_typed_relation_binding']=={'typed_relation_digest':ar['byte_sha256'],'typed_relation_ref':ar['identity_ref'],'typed_relation_version_ref':ar['version_ref']},'exact original typed relation byte binding '+ar['version_ref'])
                need(payload['source_node_ref']==node_for_subject[state['source_node_id']] and payload['target_node_ref']==node_for_subject[state['target_node_id']] and payload['relation_type_ref']==row['closed_signature']['relation_kind_id'],'closed relation endpoints and signature '+ar['version_ref'])
                source.view.handle.operations.validate_relation(subject['record'],source.view.data['projection']);checks.append('independent actual typed endpoint validation '+ar['version_ref'])
        need(raw_count==23,'all23original raw bodies retained in Context provenance')
        need(cv['included_material']==[r['original_material'] for r in proof['source_material_provenance']],'Context materials exact sourcebody selectors')
        current_lessons=[s for s in source.view.subjects.values() if s['effective_state'] in D.reader.adapter.CURRENT and (contracts.get(s.get('carrier_ref'),{}).get('semantic_kind')=='operational-lesson' or s['kind']=='operational-lesson')]
        need(not current_lessons and D.current_lesson_subjects(source.view)==[] and lesson['current_catalog_lessons']==0 and lesson['selected_lesson_refs']==[],'complete declared carrier Lesson catalog zero independently verified')
        need(source.closure_report()==mapping['source_closure'] and len(source.view.subjects)==582,'full original582subjects accounted')
        implementation=load(SELECTED/'implementation-binding.json');need(implementation['code_binding']['sha256']==sha(D.reader.HERE.joinpath('reader.py').read_bytes()),'new original-source implementation code binding')
        need(implementation['entrypoint_ref']==D.reader.HERE.joinpath('reader.py').relative_to(ROOT).as_posix()+'#open_signed' and implementation['environment']==load(SELECTED/'source-manifest.json')['environment'],'exact implementation entrypoint and selected environment')
        need(load(SELECTED/'protocols/policy.json')['reference']==D.records.POLICY==period['period_ref'].replace('assignment-period','source-policy'),'new source policy declaration selected')
        source.guard();checks.append('independent actual signed source final guard')
    need(sum(len((ROOT/r['original_binding']['path']).read_bytes()) for r in index)<=min(query['budget']['max_output_bytes'],policy['max_output_bytes']),'actual30body output byte budget')
    need(delivery['excluded_refs']==query['exclusions']==ov['payload']['exclusions'],'explicit exclusions preserved')
    for row in m['files']:need(bind(ROOT/row['path'])==row,'unchanged final audit input '+row['path'])
    audit={'schema_version':'lab-original-source-context-independent-audit/v1-candidate','result':'PASS','checks':len(checks),'check_names':checks,'selected_methods':46,'original38assertions_preserved':True,'parent_files_retained':len(parent['files']),'source_manifest_binding':bind(SOURCE),'actual_generated_carriers':30,'exact_native_joins':25,'raw_source_bodies':23,'historical_nonce_signature_independently_verified':True,'owned_host_policy_key_root_removed':True,'saved_delivery_is_current_permission':False,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    audit_path=SELECTED/'receipts/independent-audit.json';put(audit_path,audit)
    for p in [SOURCE,audit_path]:rows[bind(p)['path']]=bind(p)
    receipt={'schema_version':'lab-R03-original-source-context-partial-proof/v1-candidate','result':'PASS','files':sorted(rows.values(),key=lambda r:r['path']),'checked_at':datetime.now(timezone.utc).isoformat(),'parent_receipt_binding':m['parent_receipt_binding'],'selected_context_source_binding':m['delivery_source_binding'],'selected_context_package_binding':m['delivery_package_binding'],'independent_audit_binding':bind(audit_path),'parent_files_retained':len(parent['files']),'audit_checks':len(checks),'selected_methods':46,'original38context_assertions_unchanged':True,'actual_generated_artifact_carriers':30,'exact_native_governance_joins':25,'raw_original_artifact_bodies_carried':23,'accounted_source_subjects':582,'context_and_ontology_views_generated':True,'historical_independent_transport_permission_verified':True,'owned_policy_and_transport_key_removed':True,'fresh_Session_participation_established':False,'actual_active_Agents_created':0,'actual_public_api_operations':12,'remaining_original_api_operations':22,'original_public_api_operations':34,'closed_plan_criteria':35,'total_plan_criteria':46,'selected_producers_terminal':True,'repository_admissions_applied':0,'private_keys_exported':False,'Session_memory_rehydrated':False,'authority_effect':'none','actual_owner_outcome':None,'human_pilot_outcome':None,'task_complete':False,'goal_complete':False,'remaining_obligations':m['remaining_obligations'],'claim_ceiling':'Actual historical Context/Ontology delivery from original signed source and exact native cut. New API source selection, full SQLite original-byte projection, ephemeral Session, remaining22public APIs and original46task acceptance remain. Single actual R08 follows complete S02.'}
    p=SELECTED/'receipts/R03-0021.json';put(p,receipt);print(json.dumps({'result':'PASS','checks':len(checks),'methods':46,'files':len(rows),'parent_files_retained':len(parent['files']),'receipt_binding':bind(p)}),flush=True)
if __name__=='__main__':main()
