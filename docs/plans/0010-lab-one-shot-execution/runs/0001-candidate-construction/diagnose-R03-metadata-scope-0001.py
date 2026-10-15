"""Retain actual construction refusal evidence before owned host cleanup."""
import argparse,hashlib,importlib.util,json,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-v22'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);a=parser.parse_args();f=HERE/'metadata-scope-diagnostic-source-0001.json';assert bind(f)['sha256']==a.source_sha256;source=json.loads(f.read_bytes())
    for row in source['files']:assert bind(ROOT/row['path'])==row,row['path']
    s=importlib.util.spec_from_file_location('_cal_meta_scope_diagnostic_api',API/'__init__.py',submodule_search_locations=[str(API)]);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
    def module(n):return __import__(s.name+'.'+n,fromlist=['*'])
    P=module('protocol');F=module('metadata_fixture');S=module('service');A=module('auth');G=module('guard');G.verify('d41eec82412e5912350510e643ada32572c9a102794c24991c8a41dd2cf28910');schemas=P.Schemas('70e55cbdaccfdf8964e6abd0369ee886498ee2ba49ebd7115b1180ab3f403f56');details=[]
    with P.source.replay_source('custody-participation') as view:
        rows,metadata,targets=F.materials(view)
        with tempfile.TemporaryDirectory(prefix='cal-R03-metadata-scope-diagnostic-') as t:
            root=Path(t);root.chmod(0o700);key,path,pin=F.provision(root,rows,metadata);channel=A.ReaderChannel(path,pin,schemas);proof=F.proof(key,channel.challenge);auth=channel.authenticate(proof);service=S.Service(view,channel,schemas)
            try:
                call=F.candidate(service,targets,'change.validate','fixture:diagnostic-owner-validation');reply=service.call(P.compact(call));report=reply['message']
                for check in report.get('checks',[]):
                    for b in check['evidence_bindings']:
                        value=P.source.parse(service.vault.object_read(b));details.append(value)
                result={'schema_version':'lab-metadata-scope-diagnostic/v1-candidate','source_binding':bind(f),'actual_reply':reply,'actual_check_objects':details,'public_policy':P.source.parse(path.read_bytes()),'signed_nonce_proof':P.source.parse(proof),'authentication_reply':auth,'owned_root':str(root),'diagnostic_only':True,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
            finally:service.close();key=None
        assert not root.exists();result['owned_host_removed']=True
    G.verify('d41eec82412e5912350510e643ada32572c9a102794c24991c8a41dd2cf28910')
    for row in source['files']:assert bind(ROOT/row['path'])==row,row['path']
    p=HERE/'metadata-scope-diagnostic-result-0001.json';p.open('x').write(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'diagnostic_result_binding':bind(p),'domain_result':report.get('result'),'actual_refusals':[x.get('details') for x in details if x.get('check')=='candidate-construction-refusal']}),flush=True)
if __name__=='__main__':main()
