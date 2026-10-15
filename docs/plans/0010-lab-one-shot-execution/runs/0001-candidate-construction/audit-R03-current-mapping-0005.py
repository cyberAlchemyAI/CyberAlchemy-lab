"""Independent source-original/native replay and complete disposition audit."""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
SOURCE=RUN/'current-mapping-audit-source-0005.json'
MAPPED=ROOT/'product/lab/release-candidates/v1/interface/current-mapped-context-v4'
PRODUCER=MAPPED.parent/'current-participation-v5'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}
def encode(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def pointer(value,selector):
    for token in selector.split('/')[1:]:
        token=token.replace('~1','/').replace('~0','~')
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value
def main():
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);args=p.parse_args()
    assert sha(SOURCE.read_bytes())==args.source_sha256,'independent audit source differs'
    frozen=json.loads(SOURCE.read_bytes())
    def guard():
        for row in frozen['files']:assert bind(ROOT/row['path'])==row,row['path']
    guard();checks=[]
    def need(value,label):
        assert value,label
        checks.append(label)
    package=MAPPED/'packages/0001';mapping=json.loads((package/'mapping.json').read_bytes())
    native_input=json.loads((MAPPED/'source-manifest.json').read_bytes())['selected_native_executable']
    exe=Path(native_input['path']);need(exe.is_file() and not exe.is_symlink() and sha(exe.read_bytes())==native_input['sha256'],'independently selected actual native executable')
    result=subprocess.run([str(exe),str(package/'semantic'),str(package/'governance'),str(package/'request.json')],capture_output=True,timeout=30)
    need(result.returncode==0 and result.stdout==(package/'native-output.json').read_bytes(),'third actual cold native replay byte parity')
    need(sha(exe.read_bytes())==native_input['sha256'],'actual native executable unchanged')
    native=json.loads(result.stdout)
    name='_cal_current_mapping_independent_producer_v4'
    spec=importlib.util.spec_from_file_location(name,PRODUCER/'__init__.py',submodule_search_locations=[str(PRODUCER)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    B=__import__(name+'.base',fromlist=['*']);C=__import__(name+'.cold',fromlist=['*']);R=__import__(name+'.records',fromlist=['*'])
    original_period=PRODUCER.parent/'custody-participation-v1/packages/0001/period.json';old_raw=original_period.read_bytes()
    previous_period=PRODUCER.parent/'current-participation-v4/packages/0001/period.json';previous_raw=previous_period.read_bytes()
    events=[json.loads(p.read_bytes()) for p in sorted((package/'semantic').glob('*.json'))]
    gov=[json.loads(p.read_bytes()) for p in sorted((package/'governance').glob('*.json'))]
    with C.open_source(frozen['producer_source_binding']['sha256'],frozen['producer_package_binding']['sha256']) as cold:
        owned_root=cold.root;subjects=cold.data['projection']['subjects'];contracts=cold.data['projection']['contracts']
        need(mapping['source_cut']==B.cut(cold),'independent whole signed source cut equals mapping cut')
        need(mapping['source_package_binding']==bind(PRODUCER/'packages/0001/manifest.json'),'independent source package binding')
        need(mapping['source_closure']['accounted_subjects']==len(subjects),'full signed source accounting')
        dispositions=mapping['projection_dispositions']
        need(len(dispositions)==len(subjects) and {r['version_ref'] for r in dispositions}==set(subjects),'complete signed582subject disposition bijection')
        rows=mapping['rows'];nodes=[r for r in rows if r['subject_identity']['subject_kind']=='node'];edges=[r for r in rows if r['subject_identity']['subject_kind']=='relation']
        need(len(rows)==25 and len(nodes)==15 and len(edges)==10 and len(events)==len(gov)==25,'exact15node10edge25join closure')
        need({r['version_ref'] for r in dispositions if r['disposition']=='mapped-exact-context-representation'}=={r['artifact']['version_ref'] for r in rows},'exact selected and retained disposition distinction')
        need(native['cut']['semantic_cursor']==native['governance_cursor']==25 and cold.data['head']['sequence']==2,'native cursors and source sequence remain separate')
        byver={r['artifact']['version_ref']:r for r in nodes};original_count=0
        for row,event,governance in zip(rows,events,gov):
            artifact=row['artifact'];subject=subjects[artifact['version_ref']];locator=subject['source']
            enclosing=cold.originals[locator['path']] if 'store_id' in locator else (ROOT/locator['path']).read_bytes()
            if locator.get('encoding')==cold.handle.custody.ENCODING:
                content=pointer(json.loads(enclosing),locator['record_selector'].removesuffix('/record'))['content']
                raw=base64.b64decode(content['data'],validate=True);original_count+=1
                need(raw!=encode(subject['record']),'authored encoding preserved '+subject['version_ref'])
            elif locator.get('selector'):raw=encode(pointer(json.loads(enclosing),locator['selector']))
            else:raw=enclosing
            need(sha(raw)==artifact['byte_sha256'] and json.loads(raw)==subject['record'],'independent original Artifact byte identity '+subject['version_ref'])
            need(event['subject_identity']==row['subject_identity'] and event['subject_identity']['subject_id']==row['subject_identity']['subject_kind']+':'+sha(encode(artifact)),'native identity derives from header separately '+subject['version_ref'])
            need(event['complete_resulting_semantic_state']['typed_properties']['values']['record_sha256']==sha(raw),'native property retains actual body hash '+subject['version_ref'])
            need(governance['semantic_ref']=={'semantic_event_id':event['event_id'],'semantic_event_digest':event['event_digest'],'semantic_cursor':event['semantic_cursor']},'exact independent governance join '+subject['version_ref'])
            need(governance['complete_resulting_governance_state']['authority_effect']=='none','candidate governance supplies no authority '+subject['version_ref'])
            if row['subject_identity']['subject_kind']=='node':
                schema=row['schema_binding'];need(sha((ROOT/schema['ref']).read_bytes())==schema['sha256']==contracts[artifact['carrier_ref']]['schema_sha256'],'exact selected original schema '+subject['version_ref'])
                for witness in row['definition_witnesses']:need(sha((ROOT/witness['source_locator']).read_bytes())==witness['selected_original_sha256'],'exact original Definition witness '+witness['version_ref'])
            else:
                signature=row['signature_binding'];need(sha((ROOT/signature['ref']).read_bytes())==signature['sha256'],'exact original declared signature '+subject['version_ref'])
                need(json.loads((ROOT/signature['ref']).read_bytes())['payload']==row['closed_signature'] and row['closed_signature']['axis_id']==row['axis_ref'],'signature and orthogonal axis preserved '+subject['version_ref'])
                for endpoint in [row['source'],row['target']]:need(byver[endpoint['version_ref']]['artifact']['identity_ref']==endpoint['ref'] and byver[endpoint['version_ref']]['semantic_kind']==endpoint['kind'],'typed exact endpoint '+subject['version_ref'])
        need(original_count==23,'all23original bodies enter native mapping')
        impl=subjects[R.IMPLEMENTATION+'@'+R.VERSION]['record']
        need(impl['payload']['execution_entrypoint_ref']=='product/lab/release-candidates/v1/interface/current-source-adapter-v3/reader.py#SelectedReader.open_signed','current source Implementation names exercised qualified reader')
        need(not mapping['projection_is_host_permission'] and not mapping['native_representation_is_artifact_instance'] and mapping['active_Agents_created']==0,'no representation/authority/resource collapse')
        source_cut=mapping['source_cut'];subject_count=len(subjects)
    need(not owned_root.exists(),'actual independent cold source workspace removed')
    need(original_period.read_bytes()==old_raw and previous_period.read_bytes()==previous_raw,'original and previous fixed periods preserved')
    guard()
    output=RUN/'current-mapping-independent-observations-0005.json'
    with output.open('x') as stream:json.dump({'schema_version':'lab-current-mapping-independent-observation/v2-candidate','result':'PASS','checks':len(checks),'check_names':checks,'source_binding':bind(SOURCE),'native_replay_return_code':result.returncode,'native_replay_sha256':sha(result.stdout),'source_cut':source_cut,'captured_subject_count':subject_count,'original_body_count':original_count,'current_Agent_qualified':False,'authority_effect':'none','actual_owner_outcome':None,'goal_complete':False},stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','checks':len(checks),'captured_subjects':subject_count,'original_bodies':original_count,'observation_binding':bind(output)}),flush=True)
if __name__=='__main__':main()
