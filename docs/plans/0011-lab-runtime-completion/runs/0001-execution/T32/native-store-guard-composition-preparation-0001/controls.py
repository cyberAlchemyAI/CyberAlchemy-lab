"""AST preservation and owned inert read-only guard composition controls."""
import ast,copy,hashlib,json,os,stat,tempfile,types
from contextlib import contextmanager
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
OLD=HERE.parent/'native-lifecycle-recovery-adoption-0003'
def need(value,message):
    if not value:raise ValueError(message)
def shape(value):return ast.dump(value,include_attributes=False)
def functions(tree):
    rows={}
    def visit(node,prefix):
        for item in ast.iter_child_nodes(node):
            if isinstance(item,(ast.ClassDef,ast.FunctionDef)):
                name=prefix+'.'+item.name if prefix else item.name;rows[name]=item;visit(item,name)
            else:visit(item,prefix)
    visit(tree,'');return rows
def fds():
    result={}
    for name in os.listdir('/proc/self/fd'):
        try:s=os.fstat(int(name));result[name]=(s.st_dev,s.st_ino,s.st_mode)
        except OSError:continue
    return result
def main():
    baseline=fds();checks=[]
    def check(name,fn,refuses=False):
        before=fds()
        try:fn()
        except (ValueError,OSError):
            if not refuses:raise
        else:need(not refuses,'expected fixture refusal: '+name)
        need(before==fds(),'fixture FD leak');checks.append(name)
    oldtree=ast.parse((OLD/'selected_store.py').read_bytes());newtree=ast.parse((HERE/'selected_store.py').read_bytes());old=functions(oldtree);new=functions(newtree)
    check('exactly-two-private-fact-helpers-added',lambda:need(set(new)-set(old)=={'StoreFactory._guard_selection_origins','StoreFactory._guard_parent'},'unexpected declarations'))
    oldguard=old['StoreFactory.guard'];newguard=new['StoreFactory.guard']
    expanded=[]
    for node in newguard.body:
        if isinstance(node,ast.Expr)and isinstance(node.value,ast.Call)and ast.unparse(node.value.func)in('self._guard_selection_origins','self._guard_parent'):
            expanded.extend(copy.deepcopy(new['StoreFactory.'+node.value.func.attr].body))
        else:expanded.append(copy.deepcopy(node))
    check('full-external-factory-guard-expanded-AST-and-order-identical',lambda:need([shape(n)for n in expanded]==[shape(n)for n in oldguard.body],'factory guard checks/order changed'))
    selected='StoreFactory.create.SelectedCandidateStore.guard'
    check('original-selected-pending-root-original-and-committed-guard-tail-identical',lambda:need([shape(n)for n in new[selected].body[4:]]==[shape(n)for n in old[selected].body[1:]],'original guard tail changed'))
    unchanged=0
    for name,node in old.items():
        if name in('StoreFactory','StoreFactory.guard','StoreFactory.create','StoreFactory.create.SelectedCandidateStore',selected):continue
        need(shape(node)==shape(new[name]),'unrelated original function changed: '+name);unchanged+=1
    check('all-other-original-declarations-AST-identical',lambda:need(unchanged==len(old)-5,'incomplete comparison'))
    normalized=copy.deepcopy(new['StoreFactory.create'])
    nested=next(n for n in normalized.body if isinstance(n,ast.ClassDef))
    for index,node in enumerate(nested.body):
        if isinstance(node,ast.FunctionDef)and node.name=='guard':nested.body[index]=copy.deepcopy(old[selected])
    check('entire-create-method-identical-after-only-selected-guard-replacement',lambda:need(shape(normalized)==shape(old['StoreFactory.create']),'create effects changed'))
    for leaf in('__init__.py','private_io.py','capture.py','generation_store.py'):
        check('original-byte-conserved-'+leaf,lambda leaf=leaf:need((HERE/leaf).read_bytes()==(OLD/leaf).read_bytes(),'helper changed'))
    # Compile only the two actual selected guard methods into a fixture class.
    # No original API/module/GenerationStore import or native/guard execution.
    seen=[]
    class Port:
        def __init__(self,name,refuse=False):self.name=name;self.refuse=refuse
        def guard(self):
            seen.append(self.name)
            need(not self.refuse,'inert '+self.name+' refusal')
    class Generation:
        def __init__(self,executor,boundary):self.executor=executor;self.boundary=boundary
        def guard(self):self.boundary.guard();self.executor.guard();seen.append('generation-root-executable')
    factory=types.SimpleNamespace(generation=types.SimpleNamespace(GenerationStore=Generation),executor=Port('executor'),boundary=Port('boundary'))
    factory._guard_selection_origins=lambda:seen.append('selection-origins')
    factory._guard_parent=lambda:seen.append('owned-parent')
    original=types.SimpleNamespace(NativeCandidateStore=types.SimpleNamespace(guard=lambda self:seen.append('original-guard')))
    with tempfile.TemporaryDirectory(prefix='cal-T32-guard-composition-inert-')as temporary:
        root=Path(temporary);root.chmod(0o700);info=root.lstat()
        store=types.SimpleNamespace(pending_operation=None,root=root,root_identity=[info.st_dev,info.st_ino,info.st_uid,stat.S_IMODE(info.st_mode)])
        store.committed=Generation(factory.executor,factory.boundary)
        scope={'factory':factory,'original':original,'require':need,'os':os,'stat':stat,'type':type}
        def compiled(node):
            unit=ast.Module(body=[copy.deepcopy(node)],type_ignores=[]);ast.fix_missing_locations(unit);exec(compile(unit,str(HERE/'selected_store.py'),'exec'),scope);return scope['guard']
        newcall=compiled(new[selected]);oldcall=compiled(old[selected])
        factory.guard=lambda:(factory._guard_selection_origins(),factory.boundary.guard(),factory.executor.guard(),factory._guard_parent())
        oldcall(store);oldsequence=seen[:];seen.clear();newcall(store);newsequence=seen[:]
        check('old-two-versus-new-one-complete-guard-exact-inert-sequence',lambda:need(oldsequence==['selection-origins','boundary','executor','owned-parent','original-guard','boundary','executor','generation-root-executable']and newsequence==['selection-origins','boundary','owned-parent','original-guard','boundary','executor','generation-root-executable'],'guard order/count differs'))
        check('both-boundaries-and-one-full-executor-retained',lambda:need(newsequence.count('boundary')==2 and newsequence.count('executor')==1,'permission/currentness checks removed'))
        def invoke():seen.clear();newcall(store)
        factory.boundary.refuse=True
        check('early-boundary-refusal-before-private-read-retained',invoke,True)
        check('early-boundary-refusal-prevents-parent-original-read-and-executor',lambda:need(seen==['selection-origins','boundary'],'boundary skipped'))
        factory.boundary.refuse=False;factory.executor.refuse=True
        check('complete-executor-refusal-retained',invoke,True)
        factory.executor.refuse=False
        actual=store.committed
        store.committed=types.SimpleNamespace(executor=factory.executor,boundary=factory.boundary,guard=lambda:None)
        check('substitute-generation-proxy-refuses',invoke,True)
        store.committed=actual;actual.executor=Port('foreign-executor')
        check('different-executor-identity-refuses',invoke,True);actual.executor=factory.executor
        actual.boundary=Port('foreign-boundary')
        check('different-boundary-identity-refuses',invoke,True);actual.boundary=factory.boundary
        store.pending_operation={'owned':'fixture'}
        check('pending-no-Boolean-bypass-added',invoke,True)
        check('existing-pending-ok-still-runs-complete-proof',lambda:newcall(store,pending_ok=True));store.pending_operation=None
        saved=store.root_identity;store.root_identity=[-1]*4
        check('owned-root-identity-refusal-retained',invoke,True);store.root_identity=saved
        saved=factory._guard_selection_origins
        factory._guard_selection_origins=lambda:need(False,'inert mutated selection/origin')
        check('selection-origin-refusal-retained',invoke,True);factory._guard_selection_origins=saved
        saved=factory._guard_parent;factory._guard_parent=lambda:need(False,'inert parent mismatch')
        check('owned-parent-refusal-retained',invoke,True);factory._guard_parent=saved
        original.NativeCandidateStore.guard=lambda self:need(False,'inert original guard refusal')
        check('original-source-event-clock-refusal-retained',invoke,True)
        check('early-boundary-ran-before-original-read-refusal',lambda:need(seen==['selection-origins','boundary','owned-parent'],'private reads preceded boundary'))
    need(fds()==baseline,'whole inert controls FD imbalance')
    return {'result':'PASS-scoped-pure-and-owned-inert-only','checks':checks,'check_count':len(checks),'other_original_declarations_AST_unchanged':unchanged,'FD_delta':0,'actual_API_Source_native_executor_boundary_or_lease_used':False,'real_deadline_fit_or_native_qualification':False}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))
