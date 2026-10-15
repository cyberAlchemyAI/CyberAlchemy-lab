"""Owned inert controls only; no API/native/Source/Store/Service/Session imports."""
import ast,copy,importlib.util,json,os,stat,sys,tempfile,types
from pathlib import Path
from . import contracts as C
from .receipt_store import ReceiptStore,ident
from .software import SelectedSoftware

HERE=Path(__file__).absolute().parent

def main():
    checks=[]
    def good(name,fn):fn();checks.append(name)
    def denies(name,fn):
        try:fn()
        except (ValueError,KeyError,TypeError,FileExistsError):checks.append(name);return
        raise AssertionError('expected refusal: '+name)
    for name,raw in [('duplicate',b'{"x":1,"x":2}'),('nonfinite',b'{"x":NaN}'),('wrong-bytes-type','{}')]:denies('strict original JSON '+name,lambda raw=raw:C.parse(raw))
    for path in ['/absolute','../escape','a/../b','a//b','a\\b','.', 'a\0b']:denies('canonical original path '+repr(path),lambda path=path:C.relative(path))
    files={'Core.json':b'{"owned":"inert"}'};pins={p:C.sha(r)for p,r in files.items()}
    good('full original file SHA closure',lambda:C.verify_files(files,pins))
    denies('unknown original member',lambda:C.verify_files(dict(files,foreign=b'x'),pins))
    denies('changed original member',lambda:C.verify_files({'Core.json':b'changed'},pins))
    denies('absolute original member',lambda:C.verify_files({'/Core.json':b'x'},{'/Core.json':C.sha(b'x')}))
    # Full original materializer postimage has only the declared gate/time/commit
    # changes; normalize those and compare the entire original function AST.
    old=ast.parse((HERE/'preimages/original-render_bundle.py').read_bytes()).body[0]
    new=next(x for x in ast.parse((HERE/'materializer.py').read_bytes()).body if isinstance(x,ast.FunctionDef))
    normalized=copy.deepcopy(new);normalized.args=copy.deepcopy(old.args)
    start=next(i for i,x in enumerate(normalized.body)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='copy'for t in x.targets))
    end=next(i for i,x in enumerate(normalized.body)if isinstance(x,ast.Expr)and isinstance(x.value,ast.Call)and isinstance(x.value.func,ast.Attribute)and x.value.func.attr=='verify_generator')
    replacement=ast.parse("review = prepared['review']; verify_response(response, review, authority); verify_generator(review)").body
    normalized.body[start:end+1]=replacement
    class Restore(ast.NodeTransformer):
        def visit_Subscript(self,node):
            self.generic_visit(node)
            if ast.unparse(node)=="response['message']['payload']['recorded_at']":return ast.parse("response['approved_at']",mode='eval').body
            return node
        def visit_Constant(self,node):
            if node.value=='descriptor-bound-coupled-original-byte-record':return ast.Constant('atomic-no-replace-immutable-bundle-directory')
            return node
    normalized=Restore().visit(normalized)
    assert ast.dump(normalized,include_attributes=False)==ast.dump(old,include_attributes=False)
    checks.append('entire original C07 materializer AST conserved except exact declared gate/time/commit delta')
    hist=next(x for x in ast.parse((HERE/'historical_materializer.py').read_bytes()).body if isinstance(x,ast.FunctionDef))
    assert len(hist.body)==len(new.body)
    # Explicit native/target proof cannot be satisfied by event prose or flags.
    subject={'kind':'work','identity':'fixture:target','version_ref':'fixture:target@1','carrier_bytes_sha256':'a'*64}
    review={'targets':[{'version_ref':'fixture:target@1','identity':'fixture:target','kind':'work','record_sha256':'a'*64,'carrier_ref':'fixture:carrier'}]};native={'head_binding':{'path':'fixture','sha256':'1'*64},'generation':'operation-'+'0'*32,
        'event_files':{'semantic/fixture.json':{'raw':b'{}','sha256':C.sha(b'{}')}},'projection_sha256':'2'*64,
        'causal_witnesses':[{'source_view':{'schema_version':'lab-represented-subject-view/v1-candidate','authority_effect':'none','represented_subject':subject,'carrier':{'kind':'work','ref':'fixture:carrier','source_binding':{'path':'fixture:body','sha256':'a'*64}}}}]}
    control={'source_cut':{'fixture':True}};selected={'head_binding':native['head_binding'],'generation':native['generation'],
        'event_files':{'semantic/fixture.json':C.sha(b'{}')},'projection_sha256':native['projection_sha256'],'source_cut':control['source_cut'],
        'review_sha256':C.sha(C.compact(review)),'witness_correspondence':[{'target_version_ref':'fixture:target@1','witness_pointer':'/0/source_view/represented_subject','witness_sha256':C.sha(C.compact(subject))}]}
    good('actual selected original witness tuple joins native/source/review',lambda:C.validate_native_selection(selected,native,review,control))
    for field,bad in [('source_cut',{'other':True}),('review_sha256','3'*64),('generation','operation-'+'1'*32),('witness_correspondence',[])]:
        value=copy.deepcopy(selected);value[field]=bad;denies('native full correspondence refuses '+field,lambda value=value:C.validate_native_selection(value,native,review,control))
    bad=copy.deepcopy(selected);bad['witness_correspondence'][0]['witness_pointer']='/0';denies('bare witness/event container not exact subject tuple',lambda:C.validate_native_selection(bad,native,review,control))
    badreview={'targets':review['targets']+[{'version_ref':'fixture:absent@1'}]};bad=copy.deepcopy(selected);bad['review_sha256']=C.sha(C.compact(badreview));denies('no supplied subset generalized to further targets',lambda:C.validate_native_selection(bad,native,badreview,control))
    fd_before=len(os.listdir('/proc/self/fd'))
    with tempfile.TemporaryDirectory(prefix='cal-T14-inert-mechanics-')as temp:
        root=Path(temp);root.chmod(0o700)
        class FixtureBoundary:
            def guard(self):return None
        (root/'publisher.lock').touch(mode=0o600)
        store=ReceiptStore(root,ident(root.stat()),FixtureBoundary())
        try:
            lock=store.lock()
            try:
                store.write(store.fd,'stage/target.json',b'OWNED-INERT-ORIGINAL')
                base=store.directory(store.fd,'stage');assert store.snapshot(base,['target.json'])=={'target.json':b'OWNED-INERT-ORIGINAL'}
                checks.append('actual anchored staged bytes and whole original membership')
                raw=b'OWNED-INERT-COUPLED-RECEIPT';assert store._commit_record(raw,'inert.commit.json')is True
                assert store.read(store.fd,'inert.commit.json')==raw;checks.append('actual held anonymous inode descriptor commit')
                denies('no-replace preserves competing receipt',lambda:store._commit_record(b'OTHER','inert.commit.json'))
                assert(root/'inert.commit.json').read_bytes()==raw
                denies('commit rejects path separator',lambda:store._commit_record(raw,'outside/name'))
                (root/'foreign').write_bytes(b'FOREIGN-INERT');(root/'foreign').chmod(0o600)
                denies('unknown stage residue preserved',lambda:store.snapshot(store.fd,['publisher.lock','inert.commit.json','stage/target.json']))
                assert(root/'foreign').read_bytes()==b'FOREIGN-INERT';checks.append('foreign residue original bytes retained')
            finally:os.close(lock)
        finally:store.close()
        # Own executable fixture only; no imported/original callback is changed.
        code=b'def entry():\n    return 7\nclass Port:\n    def call(self):\n        return 9\n'
        path=root/'owned_code.py';path.write_bytes(code);name='_T14_OWNED_INERT_CODE'
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module
        try:
            exec(compile(code,str(path),'exec'),module.__dict__)
            binding={'path':str(path),'sha256':C.sha(code)}
            def read_public(b):assert b==binding;return path.read_bytes()
            software=SelectedSoftware(((module,binding,code),),read_public);assert software.function(module.entry)()==7;checks.append('actual selected true-origin code/context membership')
            original=module.entry;module.entry=lambda:8
            denies('foreign function cannot disappear through module filtering',software.guard)
            module.entry=original
            original_code=original.__code__;original.__code__=(lambda:8).__code__
            denies('same-object executable mutation refused',software.guard)
            original.__code__=original_code;software.guard()
        finally:sys.modules.pop(name,None)
    assert len(os.listdir('/proc/self/fd'))==fd_before;checks.append('owned inert descriptor cleanup FD delta zero')
    # Shape is checked by actual selected dependency, without API imports.
    from jsonschema import Draft202012Validator
    schema=json.loads((HERE/'adoption.schema.json').read_bytes());Draft202012Validator.check_schema(schema)
    assert not Draft202012Validator(schema).is_valid(json.loads((HERE/'UNRESOLVED-ADOPTION.json').read_bytes()));checks.append('unresolved Root selection cannot activate')
    for f in HERE.glob('*.py'):ast.parse(f.read_bytes(),filename=str(f))
    checks.append('all candidate source ASTs parse without producer imports')
    return {'result':'PASS-owned-inert-controls-only','checks':checks,'count':len(checks),'fd_delta':0,
        'actual_native_calls':0,'actual_owner_outcomes':0,'actual_C07_full_carrier_materialization_executed':False,
        'actual_outer_coupled_publication_executed':False,'Source_API_or_lease_effects':False,'authority_effect':'none','task_complete':False}
