"""Authored owned inert final input-custody checks; no private/API/runtime input.

Mode tests use an observer on the candidate reader over a newly owned fixture.
UID tests compile only its two pure held-metadata methods in a distinct inert
namespace with synthetic UID observations; real filesystem ownership is intact.
"""
import ast,copy,hashlib,importlib.util,json,os,stat,sys,tempfile,types
from pathlib import Path
HERE=Path(__file__).absolute().parent;POST=HERE/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
def main():
    pkg='_T31_v5_OWNED_INERT_custody';parent=types.ModuleType(pkg);parent.__path__=[str(HERE/'pure')];sys.modules[pkg]=parent
    def load(leaf,path):
        spec=importlib.util.spec_from_file_location(pkg+'.'+leaf,path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
    load('protocol',HERE/'pure/protocol.py');load('workflow_output_contracts',POST/'workflow_output_contracts.py');load('workflow_output_validation',POST/'workflow_output_validation.py');M=load('workflow_output_material',POST/'workflow_output_material.py');checks=[];before=len(os.listdir('/proc/self/fd'))
    def refuses(label,fn):
        try:fn()
        except ValueError:checks.append(label)
        else:raise AssertionError(label)
    with tempfile.TemporaryDirectory(prefix='cal-T31-v5-own-custody-')as folder:
        root=Path(folder);root.chmod(0o700);sub=root/'materials';sub.mkdir(mode=0o700);leaf=sub/'input.json';raw=b'{"OWNED-INERT":true}\n';leaf.write_bytes(raw);leaf.chmod(0o600);r=root.stat();s=leaf.stat()
        material=object.__new__(M.PrivateOutputMaterial);material.host_guard=lambda:None;material.before={};material.descriptor={'output_custody':{'root':str(root),'identity':[r.st_dev,r.st_ino,os.getuid(),0o700],'output_roots':['materials']}}
        row={'path':'materials/input.json','original_binding':{'ref':'OWNED-INERT:input','sha256':hashlib.sha256(raw).hexdigest()}};identity=[s.st_dev,s.st_ino,os.getuid(),0o600]
        assert material.capture(row,input_identity=identity)==raw;checks.append('exact input root intermediate700 leaf600 identity and bytes pass')
        # Deterministic observation at the final input checker; no module,
        # function, callback, clock, OS operation or actual input is replaced.
        def final_mode_change(target):
            assert sys.gettrace()is None
            changed=[]
            def observer(frame,event,arg):
                if event=='call'and frame.f_code.co_name=='input_attached'and frame.f_code.co_filename==str(POST/'workflow_output_material.py')and not changed:
                    target.chmod(0o755);changed.append(True)
                return observer
            try:
                sys.settrace(observer);return material.capture(row,input_identity=identity)
            finally:sys.settrace(None);target.chmod(0o700)
        refuses('final required intermediate700-to755 change refuses actual input capture',lambda:final_mode_change(sub))
        refuses('final required root700-to755 change refuses actual input capture',lambda:final_mode_change(root))
        # Ordinary output modes retain their original separate contract.
        sub.chmod(0o755);assert material.capture(row)==raw;checks.append('ordinary original output directory755 remains permitted');sub.chmod(0o700)
        rootfd,handles,links,_=material.root_fd();fd=os.open('materials',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=rootfd);handles.append(fd);i=os.fstat(fd);links.append((rootfd,'materials',fd,(i.st_dev,i.st_ino)))
        try:
            source=ast.parse((POST/'workflow_output_material.py').read_bytes());klass=next(n for n in source.body if isinstance(n,ast.ClassDef)and n.name=='PrivateOutputMaterial');methods=[copy.deepcopy(n)for n in klass.body if isinstance(n,ast.FunctionDef)and n.name in('attached','input_attached')]
            unit=ast.Module(body=[ast.ClassDef(name='OwnInertHeldMetadata',bases=[],keywords=[],body=methods,decorator_list=[])],type_ignores=[]);ast.fix_missing_locations(unit)
            for target,label in [(rootfd,'root'),(fd,'intermediate')]:
                def observation(s):return types.SimpleNamespace(st_dev=s.st_dev,st_ino=s.st_ino,st_uid=os.getuid()+1,st_mode=s.st_mode)
                class OwnMetadata:
                    getuid=staticmethod(os.getuid)
                    @staticmethod
                    def fstat(held):
                        s=os.fstat(held);return observation(s)if held==target else s
                    @staticmethod
                    def stat(name,*,dir_fd,follow_symlinks):
                        s=os.stat(name,dir_fd=dir_fd,follow_symlinks=follow_symlinks)
                        return observation(s)if(s.st_dev,s.st_ino)==(os.fstat(target).st_dev,os.fstat(target).st_ino)else s
                def need(v,message):
                    if not v:raise ValueError(message)
                namespace={'os':OwnMetadata,'stat':stat,'need':need};exec(compile(unit,str(HERE/'input_custody_controls.py'),'exec'),namespace)
                fixture=namespace['OwnInertHeldMetadata']();fixture.descriptor=material.descriptor
                refuses('synthetic final '+label+' UID mismatch refuses exact held metadata methods',lambda:fixture.input_attached(links,rootfd))
        finally:
            for held in reversed(handles):os.close(held)
        assert material.capture(row,input_identity=identity)==raw;checks.append('sibling positive exact input capture still succeeds after refused observations')
    assert len(os.listdir('/proc/self/fd'))==before;checks.append('all owned custody controls balance descriptors')
    return checks
