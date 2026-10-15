"""Independently decode all23 new body originals from the signed source cut."""
import argparse
import base64
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
PACKAGE=ROOT/'product/lab/release-candidates/v1/interface/current-participation-v3'
SOURCE=RUN/'current-participation-audit-source-0003.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);args=parser.parse_args()
    assert sha(SOURCE.read_bytes())==args.source_sha256
    frozen=json.loads(SOURCE.read_bytes())
    def guard():
        for row in frozen['files']:assert bind(ROOT/row['path'])==row,row['path']
    guard();name='_cal_independent_current_participation_0003'
    spec=importlib.util.spec_from_file_location(name,PACKAGE/'__init__.py',submodule_search_locations=[str(PACKAGE)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    B=__import__(name+'.base',fromlist=['*']);C=__import__(name+'.cold',fromlist=['*']);R=__import__(name+'.records',fromlist=['*'])
    checks=[];bodies=[]
    def need(condition,label):
        assert condition,label
        checks.append(label)
    prior=PACKAGE.parent/'custody-participation-v1/packages/0001/period.json';prior_original=prior.read_bytes()
    previous_candidate=PACKAGE.parent/'current-participation-v2/packages/0001/period.json';previous_raw=previous_candidate.read_bytes()
    archive=json.loads((PACKAGE/'packages/0001/branch.snapshot').read_bytes())
    originals={path:base64.b64decode(row['base64_original_bytes'],validate=True) for path,row in archive['files'].items()}
    for path,raw in originals.items():need(sha(raw)==archive['files'][path]['sha256'],'independent exact archived bytes '+path)
    with C.open_source(frozen['produced_source_binding']['sha256'],frozen['produced_package_binding']['sha256']) as view:
        owned_root=view.root
        need(view.data['head']['sequence']==2,'actual signed cold replay includes both new local transactions')
        selected=[s for s in view.data['projection']['subjects'].values() if s['source'].get('encoding')==view.handle.custody.ENCODING]
        need(len(selected)==23,'all23new original bodies including both setup revisions')
        for subject in selected:
            locator=subject['source'];enclosing=json.loads(originals[locator['path']])
            selector=locator['record_selector'].removesuffix('/record')
            for token in selector.split('/')[1:]:
                token=token.replace('~1','/').replace('~0','~')
                enclosing=enclosing[int(token)] if isinstance(enclosing,list) else enclosing[token]
            raw=base64.b64decode(enclosing['content']['data'],validate=True)
            need(sha(raw)==locator['sha256'] and json.loads(raw)==subject['record'],'independent original transaction extraction '+subject['version_ref'])
            need(raw!=view.handle.common.encoded(subject['record']),'original encoding is distinct from parsed value serialization '+subject['version_ref'])
            need(view.handle.custody.original_bytes(view.handle.store_module.Store(view.store,ROOT),subject['version_ref'],view.data['head']['transaction_digest'])==raw,'actual selected Store original retrieval '+subject['version_ref'])
            bodies.append({'version_ref':subject['version_ref'],'carrier_ref':subject['carrier_ref'],'byte_sha256':sha(raw),'enclosing_transaction_sha256':sha(originals[locator['path']]),'locator':locator})
        principal=view.data['projection']['subjects'][R.PRINCIPAL+'@'+R.VERSION]['record'];assignment=view.data['projection']['subjects'][R.ASSIGNMENT+'@'+R.VERSION]['record']
        need(principal['payload']['stable_subject_ref']=='ed25519-public-key-sha256:'+sha(bytes.fromhex(view.data['config']['public_key'])),'new exact Principal source signer reference')
        old=json.loads(prior_original)
        need(view.period['principal_ref']!=old['principal_ref'] and view.period['assignment_version_ref']!=old['assignment_version_ref'],'new Principal and Assignment identities rather than renewed old episode')
        need(assignment['payload']['eligible_agent_ref']==R.PROFILE+'@'+R.VERSION and assignment['payload']['period']==view.period['period_ref'],'new Assignment eligibility and independently bounded period')
        need(datetime.fromisoformat(view.period['not_before'])<=datetime.now(timezone.utc)<datetime.fromisoformat(view.period['expires_at']),'new independent source period currently valid; not host permission')
        need(view.data['config']['authorized_domain_scope_refs']==['scope:cyberalchemy-lab-first-agent-episode'],'existing declared codec domain unchanged')
        result=json.loads((PACKAGE/'packages/0001/build-result.json').read_bytes())
        need(result['owned_store_and_key_removed'] and not Path(result['owned_root']).exists(),'actual producer owned store and signer disposed')
        need(result['active_Agents_created']==0 and result['Session_memory_rehydrated'] is False and result['private_keys_exported'] is False,'source construction creates no live Agent or restored memory')
        previous=json.loads(previous_raw)
        need(view.period['principal_ref']!=previous['principal_ref'] and view.period['assignment_version_ref']!=previous['assignment_version_ref'],'previous candidate identities are not recycled')
        implementation=view.data['projection']['subjects'][R.IMPLEMENTATION+'@'+R.VERSION]['record']
        adapter_root=PACKAGE.parent/'current-source-adapter-v2'
        expected=adapter_root.relative_to(ROOT).as_posix()+'/reader.py#SelectedReader.open_signed'
        need(implementation['payload']['execution_entrypoint_ref']==expected,'source Implementation names actual successor adapter method')
        adapter_name='_cal_independent_current_participation_adapter_0003'
        spec=importlib.util.spec_from_file_location(adapter_name,adapter_root/'__init__.py',submodule_search_locations=[str(adapter_root)])
        adapter_package=importlib.util.module_from_spec(spec);sys.modules[adapter_name]=adapter_package;spec.loader.exec_module(adapter_package)
        reader_class=__import__(adapter_name+'.reader',fromlist=['*']).SelectedReader
        need(reader_class.open_signed.__qualname__=='SelectedReader.open_signed','actual method selector exists in loaded code')
        reader=reader_class(frozen['adapter_source_binding']['sha256'],frozen['produced_source_binding']['sha256'],frozen['produced_package_binding']['sha256'])
        with reader.open_signed(frozen['produced_source_binding']['sha256'],frozen['produced_package_binding']['sha256']) as selected:
            need(selected.source_cut['commit_sha256']==view.data['head']['transaction_digest'] and selected.source_cut['commit_sequence']==view.data['head']['sequence'],'actual selected successor reader shares cold signed source cut')
            actual,_=selected.sources.resolve(R.IMPLEMENTATION+'@'+R.VERSION)
            need(json.loads(actual.original)==implementation,'actual successor reader resolves original Implementation body')
            need(B.verify_source(frozen['produced_source_binding']['sha256'])['implementation_code_binding']==bind(adapter_root/'reader.py'),'actual reader code bytes equal producer selected realization')
        need(selected.closed,'actual successor reader closed after read')
        observed={'period':view.period,'source_head':view.data['head'],'new_principal_ref':R.PRINCIPAL,'new_assignment_version_ref':R.ASSIGNMENT+'@'+R.VERSION,'body_bindings':bodies}
    need(not owned_root.exists(),'actual independent cold read workspace removed')
    need(prior.read_bytes()==prior_original,'original expired Assignment preserved byte for byte')
    need(previous_candidate.read_bytes()==previous_raw,'previous candidate fixed period preserved byte for byte')
    guard()
    out=RUN/'current-participation-independent-observations-0003.json'
    with out.open('x') as stream:
        json.dump({'schema_version':'lab-current-participation-independent-observation/v1-candidate','result':'PASS','checks':len(checks),'check_names':checks,'source_binding':bind(SOURCE),'observations':observed,'current_Agent_qualified':False,'public_API_qualification':False,'original_Assignment_renewed':False,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False},stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','checks':len(checks),'original_bodies':len(bodies),'observation_binding':bind(out)}),flush=True)
if __name__=='__main__':main()
