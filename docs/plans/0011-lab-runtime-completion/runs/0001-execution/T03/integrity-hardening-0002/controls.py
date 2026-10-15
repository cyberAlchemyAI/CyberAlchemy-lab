"""Owned-file and independently held contract validation; no runtime episode."""
import argparse,hashlib,importlib.abc,importlib.util,json,os,sys,tempfile,time
from pathlib import Path

HERE=Path(__file__).absolute().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def captured(binding,name):
    path=HERE/binding['file'];raw=path.read_bytes()
    assert sha(raw)==binding['sha256']
    class Loader(importlib.abc.SourceLoader):
        selected_source_sha256=binding['sha256']
        def get_filename(self,fullname):return str(path)
        def get_data(self,filename):assert filename==str(path);return raw
        def get_code(self,fullname):return compile(raw,str(path),'exec',dont_inherit=True)
    spec=importlib.util.spec_from_file_location(name,path,loader=Loader())
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--selection-sha256',required=True);args=parser.parse_args()
    raw=(HERE/'selection.json').read_bytes();assert sha(raw)==args.selection_sha256;s=json.loads(raw)
    assert set(s)=={'schema_version','authority_effect','helper','caller','controls'} and s['authority_effect']=='none'
    assert sha(Path(__file__).read_bytes())==s['controls']['sha256']
    H=captured(s['helper'],'_cal_root_defensive_capture_selected0002');C=captured(s['caller'],'_cal_root_defensive_contract_selected0002');pin=s['helper']['sha256'];checks=[]
    before=len(os.listdir('/proc/self/fd'));start=time.monotonic()
    def passed(label):checks.append({'case':label,'result':'PASS'})
    def refused(label,callback):
        try:callback()
        except ValueError:passed(label);return
        raise AssertionError('expected validation refusal: '+label)
    contract=C.select(H,expected_path=HERE/'capture.py',expected_sha256=pin);C.check(contract,H);passed('independently-held-contract-and-fresh-kernel')
    refused('wrong-held-origin',lambda:C.select(H,expected_path=HERE/'other.py',expected_sha256=pin))
    refused('wrong-held-digest',lambda:C.select(H,expected_path=HERE/'capture.py',expected_sha256='0'*64))
    # Wrong expected metadata tests reject mismatched selected code/defaults.
    # No production function object, code, closure, clock or primitive changes.
    def inert():return None
    records=list(contract[2]);record=list(records[3]);record[1]=inert.__code__;records[3]=tuple(record)
    wrong=(*contract[:2],tuple(records),*contract[3:]);refused('held-code-reference-mismatch',lambda:C.check(wrong,H))
    records=list(contract[2]);record=list(records[3]);record[3]=();records[3]=tuple(record)
    wrong=(*contract[:2],tuple(records),*contract[3:]);refused('held-defaults-reference-mismatch',lambda:C.check(wrong,H))
    with tempfile.TemporaryDirectory(prefix='cal-root-defensive-capture-') as tmp:
        root=Path(tmp);(root/'branch').mkdir();p=root/'branch/data';data=b'bounded owned fixture\n'*4096;p.write_bytes(data)
        row={'path':'branch/data','sha256':sha(data)}
        assert H.capture_one(root,row,code_sha256=pin)==data;passed('exact-current-captured-bytes')
        assert H.verify_all(root,[row],code_sha256=pin)==1;passed('full-fresh-input-verification')
        refused('wrong-current-file-digest',lambda:H.capture_one(root,{**row,'sha256':'0'*64},code_sha256=pin))
        refused('wrong-kernel-selection',lambda:H.capture_one(root,row,code_sha256='0'*64))
        refused('duplicate-input',lambda:H.verify_all(root,[row,row],code_sha256=pin))
        for label,path in [('parent-traversal','../data'),('noncanonical-locator','branch//data'),('backslash-locator','branch\\data'),('nul-locator','branch/\0data')]:
            refused(label,lambda path=path:H.capture_one(root,{'path':path,'sha256':sha(data)},code_sha256=pin))
        absolute={'path':str(p),'sha256':sha(data)}
        refused('unselected-external-locator',lambda:H.capture_one(root,absolute,code_sha256=pin))
        assert H.capture_one(root,absolute,code_sha256=pin,selected_external=[absolute])==data;passed('exactly-selected-external-locator')
        def nested():
            with H.scope(root,pin):
                with H.scope(root,pin):pass
        refused('nested-scope',nested);assert not H._ACTIVE.value;passed('nested-refusal-clears-original-scope')
        def replaced_leaf(same_bytes):
            with H.scope(root,pin) as batch:
                assert batch.read(('tmp',root.name,'branch','data'),sha(data))==data
                q=root/'replacement';q.write_bytes(data if same_bytes else b'changed owned fixture');os.replace(q,p)
        refused('same-byte-leaf-replacement',lambda:replaced_leaf(True));p.write_bytes(data)
        refused('different-byte-leaf-replacement',lambda:replaced_leaf(False));p.write_bytes(data)
        def replaced_ancestor():
            with H.scope(root,pin) as batch:
                batch.read(('tmp',root.name,'branch','data'),sha(data))
                (root/'branch').rename(root/'old-branch');(root/'branch').mkdir();(root/'branch/data').write_bytes(data)
        refused('ancestor-replacement',replaced_ancestor)
        p=root/'branch/data'
        def exceptional_scope():
            with H.scope(root,pin) as batch:
                batch.read(('tmp',root.name,'branch','data'),sha(data));raise RuntimeError('owned fixture exception')
        try:exceptional_scope()
        except RuntimeError:passed('original-exception-unwinds-owned-FDs')
        assert H._ACTIVE.value is False;C.check(contract,H);passed('held-contract-current-after-all-cases')
    assert len(os.listdir('/proc/self/fd'))==before;passed('zero-descriptor-delta-and-owned-temporary-cleanup')
    assert sha((HERE/'capture.py').read_bytes())==pin and sha((HERE/'caller_contract.py').read_bytes())==s['caller']['sha256']
    value={'schema_version':'lab-T03-defensive-contract-controls/v1-candidate','authority_effect':'none','result':'PASS-owned-file-and-held-contract-controls','checks':checks,'count':len(checks),'elapsed_seconds':time.monotonic()-start,'python_version':sys.version.split()[0],'selection_sha256':args.selection_sha256,'helper_sha256':pin,'descriptor_delta':0,'original_callbacks_clocks_or_production_software_changed':False,'full_dependency_graph_or_adversarial_current_runtime_qualified':False,'fresh_native_family_or_current_learning_qualified':False,'task_complete':False}
    with (HERE/'controls-result.json').open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'result':value['result'],'count':value['count'],'descriptor_delta':0}))

if __name__=='__main__':main()
