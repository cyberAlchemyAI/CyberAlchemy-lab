"""Actual signed domain source -> actual sealed native event projection."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
import sys
sys.path.insert(0,str(HERE.parent/'session-participation-v2'))
import reader
import records
from base import ROOT,sha,encoded,load,require,binding,original
import json
import subprocess
import tempfile
import copy
import argparse
import time

SOURCE_PIN='f82b3813bc9b674c3f018997414f33a918b4d625fa85f0a36c8ff41e1978f368'
PACKAGE_PIN='95479689686c63590d8e98960a297455f9d3fa053ae11847d0c7d3965a1b2ad3'
EXE=Path('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader')
EXE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
PROFILE='lab-governed-subject-properties/v1-candidate'
EDGE_PROFILE='lab-governed-connection-properties/v1-candidate'
ONTOLOGY='ontology:R03-fresh-participation-domain-projection'

def native_bytes(value):
    return (json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def emit(p,value,raw=None):
    require(p.is_relative_to(HERE/'packages') or p.is_relative_to(HERE/'receipts'),'mapped output boundary escaped')
    p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    import os
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(value) if raw is None else raw)

def guard(pin):
    require(sha((HERE/'source-manifest.json').read_bytes())==pin,'mapped producer pin differs')
    for b in load(HERE/'source-manifest.json')['files']:original(b)
    require(EXE.is_file() and not EXE.is_symlink() and sha(EXE.read_bytes())==EXE_SHA,'selected native executable differs')

def call(args):
    require(sha(EXE.read_bytes())==EXE_SHA,'native executable changed before invocation')
    p=subprocess.run([str(EXE),*map(str,args)],capture_output=True,timeout=30)
    require(p.returncode==0,'actual native process rejected: '+p.stderr.decode(errors='replace')[:2000])
    require(sha(EXE.read_bytes())==EXE_SHA,'native executable changed after invocation')
    return p.stdout

def seal(body):
    with tempfile.TemporaryDirectory(prefix='cal-R03-domain-seal-') as tmp:
        p=Path(tmp)/'input.json';p.write_bytes(encoded(body));raw=call(['seal-fixture',p])
    return json.loads(raw)

def build(pin):
    guard(pin);started=time.monotonic();out=HERE/'packages/0001';require(not out.exists(),'mapped package already exists');out.mkdir(parents=True,mode=0o700)
    mapping_sha=sha((HERE/'policy.json').read_bytes());model=reader.adapter.model
    with reader.open_signed(SOURCE_PIN,PACKAGE_PIN) as source:
        view=source.view;proj=view.data['projection']
        ids=[records.PRINCIPAL,records.PRINCIPAL_REFERENCE,records.GOAL,records.WORK,records.INTENT,records.PROFILE,
            records.ASSIGNMENT,records.COORDINATION,records.CONTEXT,records.CAPABILITY,records.IMPLEMENTATION,
            source.sources.scope_ref,'product:cyberalchemy-lab',proj['state']['node_id'],records.PRODUCT_CAPABILITY]
        current={}
        for identity in ids:
            rows=[s for s in view.subjects.values() if s['identity']==identity and s['effective_state'] in reader.adapter.CURRENT]
            require(len(rows)==1,'exact current mapped source unresolved: '+identity);current[identity]=rows[0]
        require(len(current)==15,'exact fifteen source nodes required')
        require(current[records.COORDINATION]['record']['intended_uses']==[load(HERE/'policy.json')['intended_use_binding']['original_Coordination_Context_value']],'declared source/native intended-use binding differs')
        relations=[s for s in view.subjects.values() if s['identity'].startswith('typed-relation:'+records.PREFIX+':') and s['effective_state'] in reader.adapter.CURRENT]
        require(len(relations)==10,'exact ten original Typed Relations required')
        events=[];rows=[];by_version={}
        def ref(s):
            view.handle.operations.validate_record(s['record'],s['carrier_ref'],proj)
            raw,locator,encoding,enclosing=model.record_bytes(view,s)
            reader.adapter.eligibility.no_private_memory(json.loads(raw))
            return model.artifact_ref(view,s),{'source_locator':locator,'encoding':encoding,'enclosing_source_sha256':enclosing}
        def identity(s,kind):
            a,origin=ref(s);uid=kind+':'+sha(encoded(a))
            return a,origin,{'subject_id':uid,'ontology_id':ONTOLOGY,'subject_kind':kind,
                'type_ref':'protocol:R03-exact-artifact-node/v1' if kind=='node' else 'protocol:R03-exact-typed-connection/v1'}
        def event(i,state):
            return {'source_kind':'canonical_event','event_family':'semantic','event_id':'semantic:'+i['subject_id'],
                'event_digest':'0'*64,'stream_id':'semantic:'+ONTOLOGY+':'+i['subject_kind']+':'+i['subject_id'],
                'subject_identity':i,'previous_event_digest':None,'semantic_cursor':len(events)+1,'complete_resulting_semantic_state':state}
        for s in current.values():
            a,origin,i=identity(s,'node');c=proj['contracts'][s['carrier_ref']];definitions=[];witnesses=[]
            for version in c['semantic_definition_refs']:
                d=proj['subjects'][version];sb=d['source']
                require(not sb.get('selector') and 'store_id' not in sb,'Definition witness needs an explicit selector adapter')
                raw=reader.adapter.source.original({'path':sb['path'],'sha256':sb['sha256']})
                require(json.loads(raw)==d['record'],'selected Definition original bytes differ')
                locator=sb['path'];encoding='original-file-bytes';enclosing=sb['sha256']
                definitions.append({'definition_id':d['identity'],'selector_sha256':sha(raw)})
                witnesses.append({'version_ref':d['version_ref'],'identity_ref':d['identity'],'selected_original_sha256':sha(raw),
                    'source_locator':locator,'encoding':encoding,'enclosing_source_sha256':enclosing})
            require(definitions,'mapped carrier has no selected semantic Definition')
            represented=view.handle.mapping.subject_kind(s,proj)
            props={'profile_ref':PROFILE,'values':{'carrier_ref':a['carrier_ref'],'carrier_kind':c['semantic_kind'],
                'represented_kind':represented,'identity_ref':a['identity_ref'],'version_ref':a['version_ref'],
                'record_sha256':a['byte_sha256'],'schema_sha256':c['schema_sha256'],'mapping_sha256':mapping_sha}}
            state={'identity':i,'lifecycle':'active','label':s['record'].get('name',s['identity']),
                'definition_or_claim':'Candidate ontology representation of exact original Artifact instance '+a['version_ref'],
                'scope':source.sources.scope_ref,'semantic_components':[{'component_id':i['subject_id']+':domain',
                    'type_ref':'protocol:R03-exact-domain-component/v1','definition_ref':definitions[0]}],
                'semantic_definition_refs':definitions,'typed_properties':props,
                'use_obligations':[{'obligation_id':i['subject_id']+':exact-source',
                    'requirement':'Retain exact signed source tuple, selected original bytes and schema; independently verify current permission.',
                    'applies_to_use':'Read current scoped Project State'}],
                'forbidden_collapse':[{'left_ref':i['subject_id'],'right_ref':'protocol:exact-artifact-reference:'+sha(encoded(a)),
                    'context':'Ontology representation and represented Artifact instance','intended_use':'protocol:R03-read-current-scoped-project-state'},
                    {'left_ref':'protocol:R03-candidate-projection','right_ref':'protocol:R03-current-host-permission',
                    'context':'Projection is not admission or host permission','intended_use':'protocol:R03-read-current-scoped-project-state'}],
                'profile_ref':PROFILE}
            events.append(event(i,state));by_version[a['version_ref']]=i
            rows.append({'subject_identity':i,'artifact':a,'origin':origin,'semantic_kind':represented,
                'definition_witnesses':witnesses,'schema_binding':{'ref':c['schema_path'],'sha256':c['schema_sha256']}})
        for s in sorted(relations,key=lambda s:s['version_ref']):
            view.handle.operations.validate_relation(s['record'],proj);a,origin,i=identity(s,'relation');p=s['record']['payload']
            signature,b=model.signature(view,p['relation_kind_ref'])
            for endpoint in [p['source'],p['target']]:
                require(endpoint['version_ref'] in by_version,'mapped edge endpoint is outside exact node closure')
                target=next(r for r in rows if r['artifact']['version_ref']==endpoint['version_ref'])
                require(target['artifact']['identity_ref']==endpoint['ref'] and target['semantic_kind']==endpoint['kind'],'mapped typed endpoint tuple differs')
            props={'profile_ref':EDGE_PROFILE,'values':{'relation_kind_ref':p['relation_kind_ref'],'relation_version_ref':a['version_ref'],
                'source_version_ref':p['source']['version_ref'],'target_version_ref':p['target']['version_ref'],
                'record_sha256':a['byte_sha256'],'qualifiers_sha256':sha(encoded(p['qualifiers'])),'mapping_sha256':mapping_sha}}
            state={'identity':i,'lifecycle':'active','source_node_id':by_version[p['source']['version_ref']]['subject_id'],
                'target_node_id':by_version[p['target']['version_ref']]['subject_id'],'direction':'directed',
                'typed_properties':props,'forbidden_collapse':[
                    {'left_ref':i['subject_id'],'right_ref':'protocol:exact-artifact-reference:'+sha(encoded(a)),'context':'Native edge represents declared Typed Relation',
                        'intended_use':'protocol:R03-read-current-scoped-project-state'},
                    {'left_ref':p['relation_kind_ref'],'right_ref':signature['payload']['axis_id'],
                        'context':'Predicate signature and orthogonal axis remain distinct','intended_use':'protocol:R03-read-current-scoped-project-state'}]}
            events.append(event(i,state));rows.append({'subject_identity':i,'artifact':a,'origin':origin,'signature_binding':b,
                'axis_ref':signature['payload']['axis_id'],'closed_signature':signature['payload'],
                'source':p['source'],'target':p['target'],'qualifiers':p['qualifiers']})
        semantic=seal({'semantic':events,'governance':[]})['semantic'];governance=[]
        for cursor,(e,row) in enumerate(zip(semantic,rows),1):
            sr={'semantic_event_id':e['event_id'],'semantic_event_digest':e['event_digest'],'semantic_cursor':e['semantic_cursor']}
            state={'semantic_ref':sr,'provenance':[{'source_ref':row['origin']['source_locator'],
                'relation':'derived-from','operation':'exact-signed-candidate-projection','owner_route':'protocol:R03-controlled-candidate-review','posture':'candidate'}],
                'owner_route':'protocol:R03-controlled-candidate-review','candidate_or_maturity_status':'candidate','promotion_state_or_handle':'not-promoted',
                'authority_kind_and_posture':{'kind':'candidate','posture':'non-authoritative'},'authority_effect':'none',
                'evidence_confidence':{'scheme_ref':'protocol:R03-original-byte-native-replay-confidence','level':'supported'},
                'commitment_confidence':{'scheme_ref':'protocol:R03-candidate-commitment','level':'experimental'},
                'challenge_contract':{'challenge_response':'Verify signed source cut, exact tuple, original bytes and native event joins.',
                    'valid_challenge_modes':['owner_review'],'contradiction_edges':[],'validation_edges':[],
                    'owner_route':'protocol:R03-controlled-candidate-review','resolution_gate':'protocol:R03-candidate-projection-review',
                    'blocking_questions':[],'challenge_residue_route':'protocol:R03-controlled-candidate-review'},
                'residue':[],'conflicts':[],'drift_owner':'protocol:R03-controlled-candidate-review','invalidation_route':'protocol:R03-controlled-candidate-review'}
            governance.append({'source_kind':'canonical_event','event_family':'governance','event_id':'governance:'+e['subject_identity']['subject_id'],
                'event_digest':'0'*64,'stream_id':e['stream_id'].replace('semantic:','governance:',1),'semantic_ref':sr,
                'governance_cursor':cursor,'previous_event_digest':None,'complete_resulting_governance_state':state})
        governance=seal({'semantic':[],'governance':governance})['governance']
        for folder,family,field in [('semantic',semantic,'semantic_cursor'),('governance',governance,'governance_cursor')]:
            for e in family:emit(out/folder/(str(e[field]).zfill(8)+'.json'),None,raw=native_bytes(e))
        request={'selector_ref':'protocol:R03-exact-same-cut-domain-context','selector':{'semantic_cursor':25,
            'required_subject_set':[e['subject_identity'] for e in semantic],'governance_join_policy':'require-exact',
            'intended_use':'protocol:R03-read-current-scoped-project-state','projection_profile':'test-complete-profile/v1'},'governance_cursor':25}
        emit(out/'request.json',request)
        first=call([out/'semantic',out/'governance',out/'request.json']);second=call([out/'semantic',out/'governance',out/'request.json'])
        require(first==second,'actual cold native replay metadata differs')
        output=json.loads(first);require(output['authority_effect']=='none' and output['cut']['semantic_cursor']==25 and output['governance_cursor']==25,'native replay cut differs')
        require(len(output['governed_nodes'])==15,'native actual governed node count differs')
        emit(out/'native-output.json',None,raw=first)
        mapping={'schema_version':'lab-same-signed-cut-native-domain-mapping/v1-candidate','source_cut':copy.deepcopy(source.source_cut),
            'source_package_binding':binding(reader.HERE/'packages/0001/manifest.json'),'policy_binding':binding(HERE/'policy.json'),
            'semantic_cursor':25,'governance_cursor':25,'rows':rows,'authority_effect':'none','actual_owner_outcome':None,
            'native_seal_processes':2,'actual_cold_native_read_processes':2,'native_domain_mapping_supplied':True,
            'context_or_ontology_view_carriers_generated':False,'public_API_operations_added':0,'active_Agents_created':0}
        emit(out/'mapping.json',mapping);source.guard();guard(pin)
    result={'result':'PASS','node_count':15,'edge_count':10,'exact_governance_joins':25,'cold_native_replay_byte_parity':True,
        'same_signed_source_cut':True,'source_sha256':pin,'duration_seconds':time.monotonic()-started,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    emit(out/'build-result.json',result)
    manifest={'schema_version':'lab-mapped-context-package/v1-candidate','files':[binding(p) for p in sorted(out.rglob('*')) if p.is_file()],
        'source_manifest_binding':binding(HERE/'source-manifest.json'),'authority_effect':'none','actual_owner_outcome':None}
    emit(out/'manifest.json',manifest);print(json.dumps({'result':'PASS','package_binding':binding(out/'manifest.json'),'node_count':15,'edge_count':10}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();build(a.source_sha256)
