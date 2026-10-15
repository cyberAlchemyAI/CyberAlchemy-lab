"""Verify original artifact tuples through qualified native projection and joins."""
import argparse,ast,hashlib,importlib.util,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
SELECTED=ROOT/'product/lab/release-candidates/v1/interface/custody-mapped-context-v2'
SOURCE=HERE/'custody-mapping-audit-source-0001.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':sha(p.read_bytes())}
def parse(raw):
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('duplicate independent mapping audit JSON key')
            result[k]=v
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite audit JSON')))
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True,mode=0o700);fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(v))
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);a=ap.parse_args();assert sha(SOURCE.read_bytes())==a.source_sha256;m=parse(SOURCE.read_bytes());checks=[]
    def need(value,name):
        if not value:raise AssertionError(name)
        checks.append(name)
    for row in m['files']:need(bind(ROOT/row['path'])==row,'exact frozen independent mapper input '+row['path'])
    parent=parse((ROOT/m['parent_receipt_binding']['path']).read_bytes());rows={r['path']:r for r in m['files']}
    need(parent['result']=='PASS' and parent['task_complete'] is False,'original full parent remains incomplete')
    for row in parent['files']:need(rows.get(row['path'])==row,'retain exact original proof '+row['path'])
    terminal=parse((ROOT/m['terminal_binding']['path']).read_bytes())
    need(terminal['selected_exit_codes']=={'build':0,'checks':0},'actual mapper/check producers exited zero')
    old=methods(SELECTED.parent/'mapped-context-v6/run_checks.py');new=methods(SELECTED/'test_original_mapping.py')
    need(old==new and len(old)==20,'all20currentoriginalmapping method ASTs unchanged')
    cases=parse((SELECTED/'receipts/checks.json').read_bytes())
    need(cases['result']=='PASS' and cases['tests_run']==cases['expected_tests']==29,'all29mappingmethods passed')
    need(len(cases['cases'])==len({r['test'] for r in cases['cases']})==29 and all(r['result']=='PASS' for r in cases['cases']),'all29methodterminal results exactly once')
    need(cases['source_sha256']==m['mapper_source_binding']['sha256'] and cases['package_sha256']==m['mapper_package_binding']['sha256'],'checks select exact source/derived output')
    package=SELECTED/'packages/0001';manifest=parse((package/'manifest.json').read_bytes());mapping=parse((package/'mapping.json').read_bytes());native=parse((package/'native-output.json').read_bytes())
    actual={p.relative_to(ROOT).as_posix() for p in package.rglob('*') if p.is_file()};expected={r['path'] for r in manifest['files']}|{(package/'manifest.json').relative_to(ROOT).as_posix()}
    need(actual==expected and len(manifest['files'])==len({r['path'] for r in manifest['files']}),'exact derived mapper file closure')
    for row in manifest['files']:need(bind(ROOT/row['path'])==row and (ROOT/row['path']).stat().st_mode&0o777==0o600,'private exact original mapped output '+row['path'])
    build=parse((package/'build-result.json').read_bytes())
    need(build['result']=='PASS' and build['node_count']==15 and build['edge_count']==10 and build['exact_governance_joins']==25 and build['cold_native_replay_byte_parity'],'actual full15node10edge25join build')
    events=[parse(p.read_bytes()) for p in sorted((package/'semantic').glob('*.json'))];gov=[parse(p.read_bytes()) for p in sorted((package/'governance').glob('*.json'))]
    need(len(events)==len(gov)==len(mapping['rows'])==25,'complete mapped event/row family count')
    need(mapping['semantic_cursor']==mapping['governance_cursor']==native['cut']['semantic_cursor']==native['governance_cursor']==25,'native semantic/governance cursors explicit')
    native_subjects={n['identity']['subject_id']:n for n in native['cut']['subjects']};need(len(native_subjects)==25 and len(native['governed_nodes'])==15,'native25subjects/15qualifiednodes')
    need(mapping['source_name']=='custody-participation' and mapping['source_cut']['commit_sequence']==2,'newsourceindependentHEAD coordinate remains2')
    need(mapping['projection_is_host_permission'] is False and mapping['native_representation_is_artifact_instance'] is False and mapping['context_or_ontology_view_carriers_generated'] is False and mapping['active_Agents_created']==mapping['public_API_operations_added']==0,'no permission/artifactidentity/liveAgent/publicAPI collapse')
    need(mapping['source_closure']['accounted_subjects']==len(mapping['projection_dispositions'])==582 and mapping['source_closure']['included_current_instances']==29,'full582subject29currentdomain source closure')
    need(len(mapping['source_closure']['instance_bound_assignments'])==1,'exact prior instanceAssignment diagnostic retained')
    spec=importlib.util.spec_from_file_location('_cal_custody_mapping_independent',SELECTED/'__init__.py',submodule_search_locations=[str(SELECTED)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    builder=__import__(spec.name+'.build',fromlist=['guard']);builder.guard(m['mapper_source_binding']['sha256'])
    output=builder.call([package/'semantic',package/'governance',package/'request.json'])
    need(output==(package/'native-output.json').read_bytes(),'actual third independent native coldprocess byte parity')
    by_version={r['artifact']['version_ref']:r for r in mapping['rows']};nodes={v:r for v,r in by_version.items() if r['subject_identity']['subject_kind']=='node'};raw_count=0;observations=[]
    with builder.reader.open_signed(builder.SOURCE_PIN,builder.PACKAGE_PIN) as source:
        need(mapping['source_cut']==source.source_cut and mapping['source_package_binding']==bind(builder.reader.HERE/'packages/0001/manifest.json'),'actual verified rawsourcepackage/cut selection')
        need(mapping['source_cut']['source_profile_sha256']==source.view.handle.manifest['profile_binding']['sha256'],'actual selected executable profile supplies source cut')
        need(mapping['source_closure']==source.closure_report(),'allsource dispositions/diagnostics independently verified')
        profile=source.view.data['projection']['contracts']['cal.artifact-type.ontology-node/v2'];ontologydefs=set(profile['semantic_definition_refs'])
        for row,event,g in zip(mapping['rows'],events,gov):
            artifact=row['artifact'];identity=row['subject_identity'];s=source.view.subjects[artifact['version_ref']]
            raw,locator,encoding,enclosing=builder.reader.adapter.model.record_bytes(source.view,s)
            need(artifact==builder.reader.adapter.model.artifact_ref(source.view,s) and sha(raw)==artifact['byte_sha256'],'actual original ArtifactReference '+artifact['version_ref'])
            need(row['origin']=={'source_locator':locator,'encoding':encoding,'enclosing_source_sha256':enclosing},'exact original location/bodyencoding/enclosing hash '+artifact['version_ref'])
            need(identity['subject_id']==identity['subject_kind']+':'+sha(encoded(artifact)) and identity['ontology_id']==builder.ONTOLOGY,'declared native headeridentity distinct from bodybytes '+artifact['version_ref'])
            state=event['complete_resulting_semantic_state'];n=native_subjects[identity['subject_id']]
            need(state==n['semantic_state'] and identity==event['subject_identity']==n['identity'],'actual native replay state and identity '+artifact['version_ref'])
            need(event['event_id']==n['source_event_id'] and event['event_digest']==n['source_event_digest'] and event['semantic_cursor']==n['source_cursor'],'native source event identity/digest/cursor '+artifact['version_ref'])
            need(state['typed_properties']['values']['record_sha256']==sha(raw) and state['typed_properties']['values']['mapping_sha256']==sha((SELECTED/'policy.json').read_bytes()),'actual rawbody and mappingpolicy properties '+artifact['version_ref'])
            semantic_ref={'semantic_event_id':event['event_id'],'semantic_event_digest':event['event_digest'],'semantic_cursor':event['semantic_cursor']}
            need(g['semantic_ref']==g['complete_resulting_governance_state']['semantic_ref']==semantic_ref,'independent exact native governance join '+artifact['version_ref'])
            gs=g['complete_resulting_governance_state'];need(gs['authority_effect']=='none' and gs['promotion_state_or_handle']=='not-promoted' and gs['candidate_or_maturity_status']=='candidate','candidate governance cannot promote or authorize '+artifact['version_ref'])
            if encoding==source.view.handle.custody.ENCODING:
                need(raw!=encoded(s['record']),'raw body not inherited serializer '+artifact['version_ref']);raw_count+=1
            if identity['subject_kind']=='node':
                need(ontologydefs <= {w['version_ref'] for w in row['definition_witnesses']},'current ontologyrepresentation Definition witnesses '+artifact['version_ref'])
                components=state['semantic_components'];need(len(components)==2 and components[0]['type_ref']=='cal.artifact-type.ontology-node/v2' and components[1]['type_ref']==artifact['carrier_ref'],'representation and representedcarrier components '+artifact['version_ref'])
                need(all(c['definition_ref'] in state['semantic_definition_refs'] for c in components),'qualified component Definition references '+artifact['version_ref'])
                contract=source.view.data['projection']['contracts'][artifact['carrier_ref']]
                need(row['schema_binding']=={'ref':contract['schema_path'],'sha256':contract['schema_sha256']} and sha((ROOT/contract['schema_path']).read_bytes())==contract['schema_sha256'],'exact source carrier schema '+artifact['version_ref'])
                for witness in row['definition_witnesses']:
                    path=ROOT/witness['source_locator'];need(sha(path.read_bytes())==witness['selected_original_sha256']==witness['enclosing_source_sha256'],'actual original Definition witness '+witness['version_ref']+' for '+artifact['version_ref'])
                observations.append({'artifact':artifact,'native_identity':identity,'original_body_encoding':encoding,'schema_binding':row['schema_binding'],'qualified_components':components})
            else:
                p=s['record']['payload'];sig,b=builder.reader.adapter.model.signature(source.view,p['relation_kind_ref'])
                need(b==row['signature_binding'] and sha((ROOT/b['ref']).read_bytes())==b['sha256'] and row['closed_signature']==sig['payload'],'actual closed relation signature '+artifact['version_ref'])
                need(row['axis_ref']==sig['payload']['axis_id'] and row['qualifiers']==p['qualifiers'] and state['typed_properties']['values']['qualifiers_sha256']==sha(encoded(p['qualifiers'])),'axis and qualifiers remain distinct exact witnesses '+artifact['version_ref'])
                for field in ['source','target']:
                    end=p[field];node=nodes[end['version_ref']]
                    need(row[field]==end and node['artifact']['identity_ref']==end['ref'] and node['semantic_kind']==end['kind'],'exact declared '+field+' endpoint tuple '+artifact['version_ref'])
                    need(state[field+'_node_id']==node['subject_identity']['subject_id'],'native '+field+' endpoint node representation '+artifact['version_ref'])
                source.view.handle.operations.validate_relation(s['record'],source.view.data['projection']);checks.append('actual current relation validation '+artifact['version_ref'])
        need(raw_count==23,'all23actualrawbodiesenter nativeproperties')
        need(len(mapping['projection_dispositions'])==len({r['version_ref'] for r in mapping['projection_dispositions']})==len(source.view.subjects),'every source subject accounted exactly once')
        need({r['version_ref'] for r in mapping['projection_dispositions'] if r['disposition']=='mapped-exact-context-representation'}==set(by_version),'exact projection inclusion set')
        for d in mapping['source_closure']['instance_bound_assignments']:need(d['assignment']['version_ref'] not in by_version,'oldinstance diagnostic remains outside newparticipantmapping')
    for row in m['files']:need(bind(ROOT/row['path'])==row,'unchanged final mapper input '+row['path'])
    audit={'schema_version':'lab-original-source-qualified-native-independent-audit/v1-candidate','result':'PASS','checks':len(checks),'check_names':checks,
        'selected_methods':29,'original20assertions_preserved':True,'source_manifest_binding':bind(SOURCE),'parent_files_retained':len(parent['files']),
        'native_nodes':15,'native_edges':10,'exact_governance_joins':25,'rawbodyproperties':23,'accounted_source_subjects':582,'actual_independent_cold_native_process':True,
        'actual_qualified_node_observations':observations,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    audit_path=SELECTED/'receipts/independent-audit.json';put(audit_path,audit)
    for p in [SOURCE,audit_path]:rows[bind(p)['path']]=bind(p)
    receipt={'schema_version':'lab-R03-original-source-qualified-native-partial-proof/v1-candidate','result':'PASS','files':sorted(rows.values(),key=lambda r:r['path']),
        'checked_at':datetime.now(timezone.utc).isoformat(),'parent_receipt_binding':m['parent_receipt_binding'],'selected_mapped_projection_source_binding':m['mapper_source_binding'],
        'selected_mapped_projection_package_binding':m['mapper_package_binding'],'independent_audit_binding':bind(audit_path),'parent_files_retained':len(parent['files']),
        'audit_checks':len(checks),'selected_methods':29,'original20mapping_assertions_unchanged':True,'exact_domain_mapped_nodes':15,'exact_declared_domain_mapped_edges':10,'exact_native_governance_joins':25,
        'raw_original_artifact_bodies_carried':23,'accounted_source_subjects':582,'current_domain_source_instances':29,'latest_ontology_representation_carrier_qualification_retained':True,
        'native_domain_mapping_supplied':True,'context_or_ontology_views_generated':False,'fresh_Session_participation_established':False,'actual_active_Agents_created':0,
        'actual_public_api_operations':12,'remaining_original_api_operations':22,'original_public_api_operations':34,'closed_plan_criteria':35,'total_plan_criteria':46,
        'selected_producers_terminal':True,'repository_admissions_applied':0,'private_keys_exported':False,'Session_memory_rehydrated':False,
        'authority_effect':'none','actual_owner_outcome':None,'human_pilot_outcome':None,'task_complete':False,'goal_complete':False,'remaining_obligations':m['remaining_obligations'],
        'claim_ceiling':'Actual qualified native mapping preserves exact original source and current ontology semantics. Current independent host permission/generatedContext/OntologyView/ephemeralSession/full publicAPI and original46task acceptance remain. Single actual R08 follows completeS02.'}
    p=SELECTED/'receipts/R03-0020.json';put(p,receipt);print(json.dumps({'result':'PASS','checks':len(checks),'methods':29,'files':len(rows),'parent_files_retained':len(parent['files']),'receipt_binding':bind(p)}),flush=True)
if __name__=='__main__':main()
