"""Real typed native events, sealed and reduced by the actual Rust runtime."""
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from lab_runtime.common import byte_digest,digest,encoded,load,loads,require
from native_reader import NativePins,NativeReadStore,closure


def seal(executable,body):
    with TemporaryDirectory(prefix='lab-context-seal-fixture-') as temp:
        path=Path(temp)/'events.json';path.write_bytes(encoded(body))
        process=subprocess.run([str(executable),'seal-fixture',str(path)],capture_output=True,timeout=30)
    require(process.returncode==0,'native fixture sealing failed: '+process.stderr.decode()[:1000])
    return loads(process.stdout)


def fixture(root,executable,snapshot):
    semantic=root/'semantic';governance=root/'governance';semantic.mkdir();governance.mkdir()
    contract=snapshot['contracts']['cal.artifact-type.ontology-node/v2'];def_ref=contract['semantic_definition_refs'][0]
    definition=snapshot['subjects'][def_ref]
    # Exact Definition bytes are retained, independently from native event digests.
    definition_digest=definition['source']['sha256']
    identity=lambda kind,name:{'subject_id':name,'ontology_id':'lab-c08-native-fixture','subject_kind':kind,'type_ref':'test-node-type/v1' if kind=='node' else 'test-relation-type/v1'}
    properties={'profile_ref':'test-empty-profile/v1','values':{}}
    events=[]
    for cursor,(kind,name) in enumerate([('node','native-context-input'),('node','native-context-output'),('relation','native-context-connection')],1):
        i=identity(kind,name)
        if kind=='node':
            state={'identity':i,'lifecycle':'active','label':name,'definition_or_claim':'A bounded native ontology fixture node; it represents no domain Artifact instance.','scope':'C08 isolated native replay proof','semantic_components':[], 'semantic_definition_refs':[{'definition_id':definition['identity'],'selector_sha256':definition_digest}],'typed_properties':properties,'use_obligations':[],'forbidden_collapse':[],'profile_ref':'test-empty-profile/v1'}
        else:
            state={'identity':i,'lifecycle':'active','source_node_id':'native-context-input','target_node_id':'native-context-output','direction':'directed','typed_properties':properties,'forbidden_collapse':[]}
        events.append({'source_kind':'canonical_event','event_family':'semantic','event_id':'semantic-'+name,'event_digest':'0'*64,'stream_id':'semantic:lab-c08-native-fixture:'+kind+':'+name,'subject_identity':i,'previous_event_digest':None,'semantic_cursor':cursor,'complete_resulting_semantic_state':state})
    events=seal(executable,{'semantic':events,'governance':[]})['semantic']
    gov=[]
    for cursor,event in enumerate(events,1):
        ref={'semantic_event_id':event['event_id'],'semantic_event_digest':event['event_digest'],'semantic_cursor':event['semantic_cursor']}
        state={'semantic_ref':ref,'provenance':[{'source_ref':definition['source']['path'],'relation':'derived-from','operation':'isolated-fixture','owner_route':'candidate-repository-review','posture':'candidate'}],'owner_route':'candidate-repository-review','candidate_or_maturity_status':'candidate','promotion_state_or_handle':'not-promoted','authority_kind_and_posture':{'kind':'candidate','posture':'non-authoritative'},'authority_effect':'none','evidence_confidence':{'scheme_ref':'test-confidence/v1','level':'supported'},'commitment_confidence':{'scheme_ref':'test-confidence/v1','level':'experimental'},'challenge_contract':{'challenge_response':'Review exact input bytes and native replay.','valid_challenge_modes':['owner_review'],'contradiction_edges':[],'validation_edges':[],'owner_route':'candidate-repository-review','resolution_gate':'candidate-conformance','blocking_questions':[],'challenge_residue_route':'candidate-repository-review'},'residue':[],'conflicts':[],'drift_owner':'candidate-repository-review','invalidation_route':'candidate-repository-review'}
        gov.append({'source_kind':'canonical_event','event_family':'governance','event_id':'governance-'+event['subject_identity']['subject_id'],'event_digest':'0'*64,'stream_id':event['stream_id'].replace('semantic:','governance:',1),'semantic_ref':ref,'governance_cursor':cursor,'previous_event_digest':None,'complete_resulting_governance_state':state})
    gov=seal(executable,{'semantic':[],'governance':gov})['governance']
    for directory,family,field in [(semantic,events,'semantic_cursor'),(governance,gov,'governance_cursor')]:
        for event in family:(directory/f"{event[field]:08}-{event['event_id']}.json").write_bytes((json.dumps(event,ensure_ascii=False,separators=(",",":"))+"\n").encode())
    request={'selector_ref':'candidate-c08-native-selection','selector':{'semantic_cursor':3,'required_subject_set':[e['subject_identity'] for e in events],'governance_join_policy':'require-exact','intended_use':'candidate-c08-context','projection_profile':'test-complete-profile/v1'},'governance_cursor':3}
    raw=encoded(request);(root/'request.json').write_bytes(raw)
    process=subprocess.run([str(executable),str(semantic),str(governance),str(root/'request.json')],capture_output=True,timeout=30)
    require(process.returncode==0,'native fixture replay failed: '+process.stderr.decode()[:2000])
    output=loads(process.stdout)
    files=lambda path:digest({n:byte_digest(v) for n,v in closure(path).items()})
    pins=NativePins(byte_digest(Path(executable).read_bytes()),files(semantic),files(governance),byte_digest(raw),3,3,digest(output))
    adapter=NativeReadStore(semantic,governance,request,executable,pins)
    adapter.read()
    return adapter
