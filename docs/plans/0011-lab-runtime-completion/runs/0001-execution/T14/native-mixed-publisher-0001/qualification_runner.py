"""Bounded owned controls; this runner never activates the gateway."""
import argparse,hashlib,json,os,sys,types
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--selection-sha256',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    here=Path(__file__).absolute().parent;selection_raw=(here/'pure-input-selection-0002.json').read_bytes()
    assert hashlib.sha256(selection_raw).hexdigest()==a.selection_sha256;selection=json.loads(selection_raw)
    inputs={row['path']:Path(row['path']).read_bytes()for row in selection['files']}
    for row in selection['files']:assert hashlib.sha256(inputs[row['path']]).hexdigest()==row['sha256']
    sys.path.append('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps')
    name='_T14_OWNED_FINAL_PURE';package=types.ModuleType(name);package.__file__=str(here/'__init__.py');package.__path__=[str(here)];sys.modules[name]=package
    for part in ('contracts','receipt_store','software','pure_controls','pure_controls_v2','owner_history','owner_fixture_controls'):
        path=here/(part+'.py');module=types.ModuleType(name+'.'+part);module.__file__=str(path);module.__package__=name;sys.modules[module.__name__]=module;setattr(package,part,module)
        exec(compile(inputs[str(path)],str(path),'exec'),module.__dict__)
    fd_before=len(os.listdir('/proc/self/fd'));one=sys.modules[name+'.pure_controls_v2'].main()
    original=Path('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/owner-response-ingress-v1-completion-0001/owner_ingress.py')
    two=module.main(original,'7f2623791fdf985c32be0e0a91cc04e65d14601c81244e2c084329fc92076fe4',lambda path:inputs[str(path)])
    assert len(os.listdir('/proc/self/fd'))==fd_before
    for row in selection['files']:assert Path(row['path']).read_bytes()==inputs[row['path']]
    result={'schema_version':'lab-T14-native-mixed-owned-controls/v1-candidate','result':'PASS-owned-components-only','checks':one['checks']+two['checks'],
        'count':one['count']+two['count'],'fd_delta':0,'pid':os.getpid(),'bounded_inputs_entry_exit':len(inputs),'selection_sha256':a.selection_sha256,
        'full_Source_API_installed_guard':False,'actual_Lab_native_calls':0,'actual_owner_outcome':None,'actual_full_C07_materializer_execution':False,
        'actual_coupled_native_publication':False,'actual_lease_effects':False,'authority_effect':'none','task_complete':False}
    output=Path(a.output);assert output.parent==here
    fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb')as stream:stream.write((json.dumps(result,sort_keys=True,indent=2)+'\n').encode());stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'result':result['result'],'count':result['count'],'fd_delta':0,'pid':os.getpid()}))
if __name__=='__main__':main()
