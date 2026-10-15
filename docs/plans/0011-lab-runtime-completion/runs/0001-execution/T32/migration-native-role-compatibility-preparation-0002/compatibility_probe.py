"""Unexecuted native compatibility probe; Root-only explicit technical fixture.

Replays all176 historical metadata events through selected574, reseals all typed
drafts, appends in a fresh owned store, compares literal event bytes and both
full cold projections. It never executes external source or old480 native.
All child streams and stores remain in the selected private root on refusal.
"""
import base64,copy,datetime,inspect,os,stat,sys
from pathlib import Path
from .execution_contract import (ROOT,HERE,INPUTS,EXECUTION,HISTORICAL,NATIVE,OLD_NATIVE,
    EXECUTOR_ORIGIN,need,parse,bytes_for,bind,evidence,input_guard,sha,canonical)
from .private_io import directory,write

def root_guard(root,identity):
    root=Path(root)
    need(root.is_absolute()and '..'not in root.parts and not root.is_relative_to(ROOT),'owned compatibility root outside repository required')
    with directory(root)as fd:
        s=os.fstat(fd)
        need([s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]==identity and s.st_uid==os.getuid()and stat.S_IMODE(s.st_mode)==0o700,
             'independently selected compatibility root differs')

def probe(executor,*,technical_boundary,owned_root,root_identity):
    need(type(executor).__name__=='SelectedOntologyExecutor'and Path(inspect.getsourcefile(type(executor)))==ROOT/EXECUTOR_ORIGIN
         and sys.modules[type(executor).__module__].SelectedOntologyExecutor is type(executor)
         and executor.raw==bytes_for(EXECUTION)and executor.pin==EXECUTION['sha256']and executor.executable_sha256==NATIVE,
         'actual independently selected574 executor required')
    root=Path(owned_root)
    def guard():
        root_guard(root,root_identity);technical_boundary.guard();executor.guard();input_guard()
    guard()
    with directory(root)as fd:need(os.listdir(fd)==[],'new empty owned compatibility root required')
    selected=parse(bytes_for(INPUTS));archive_binding=next({k:r[k]for k in('path','sha256')}for r in selected['inputs']
        if r['path']=='implementation/lab-ontology/candidates/v1/migration/candidate/0001/native.snapshot')
    archive=parse(bytes_for(archive_binding))
    need(archive['native_executable_sha256']==OLD_NATIVE and archive['semantic_cursor']==archive['governance_cursor']==88,
         'full original historical480 metadata archive required')
    families={'semantic':[],'governance':[]};raws={}
    for family in families:
        for i in range(1,89):
            name=f'{family}/{i:08d}-ontology-{family}:O05:{i}.json';row=archive['files'][name]
            raw=base64.b64decode(row['base64_original_bytes'],validate=True)
            need(sha(raw)==row['sha256'],'original event bytes changed');raws[name]=raw;families[family].append(parse(raw))
    need(set(raws)==set(archive['files']),'unselected historical archive entries')
    # Each ancestor is created beneath a held and rechecked selected root.
    with directory(root)as fd:
        for name in('original','appended','streams'):os.mkdir(name,0o700,dir_fd=fd)
        os.fsync(fd)
    for name in('original','appended'):
        with directory(root/name)as fd:
            for family in families:os.mkdir(family,0o700,dir_fd=fd)
            os.fsync(fd)
    for name,raw in raws.items():write(root/'original'/name,raw)
    def files(name):
        result={}
        with directory(root/name)as fd:
            need(set(os.listdir(fd))==set(families),'unexpected compatibility store residue')
            for family in families:
                with directory(root/name/family)as sub:
                    for leaf in os.listdir(sub):
                        path=root/name/family/leaf
                        # No unknown files, links, or normalized event aliases are accepted.
                        relative=family+'/'+leaf;need(relative in raws,'unexpected event store filename')
                        from .capture import capture_path
                        result[relative]=sha(capture_path(path,maximum=32*1024*1024,required_uid=os.getuid()))
        return result
    observations=[]
    def call(mode,args,request=None,store=None):
        guard();before=files(store)if store else {};n=len(observations)
        request_binding=None
        if request is not None:
            p=root/'streams'/f'{n:02d}-request.json';raw=canonical(request);write(p,raw)
            request_binding={'path':str(p),'sha256':sha(raw)};args=[*args,str(p)]
        child=executor.run_native(mode,args)
        out=root/'streams'/f'{n:02d}-stdout.json';err=root/'streams'/f'{n:02d}-stderr.txt'
        write(out,child.stdout);write(err,child.stderr)
        row={'mode':mode,'returncode':child.returncode,'request_binding':request_binding,
             'stdout_binding':{'path':str(out),'sha256':sha(child.stdout)},'stderr_binding':{'path':str(err),'sha256':sha(child.stderr)},
             'files_before':before,'files_after':files(store)if store else {}}
        observations.append(row)
        # Retain progress before interpreting or refusing any actual native response.
        write(root/f'observation-{n:02d}.json',canonical(row));guard()
        need(child.returncode==0,'native compatibility child refused; retain owned evidence')
        return parse(child.stdout)
    call('read',[str(root/'original/semantic'),str(root/'original/governance'),'88'],store='original')
    drafts=copy.deepcopy(families)
    for events in drafts.values():
        for event in events:event['event_digest']='0'*64
    call('seal',[],request=drafts)
    call('append',[str(root/'appended/semantic'),str(root/'appended/governance')],request=families,store='appended')
    call('read',[str(root/'appended/semantic'),str(root/'appended/governance'),'88'],store='appended')
    result={'schema_version':'lab-O05-native-byte-compatibility/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
        'execution_selection_binding':EXECUTION,'historical_scope_binding':HISTORICAL,'input_selection_binding':INPUTS,
        'probe_module_binding':bind(Path(__file__)),'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'historical_archive_binding':archive_binding,'event_bytes':{k:sha(v)for k,v in raws.items()},'observations':observations}
    evidence(result,runtime_bindings=[bind(Path(__file__))]);guard()
    write(root/'compatibility-evidence.json',canonical(result))
    return {'path':str(root/'compatibility-evidence.json'),'sha256':sha(canonical(result))}

if __name__=='__main__':raise SystemExit('Trusted Root bootstrap must provide exact executor, technical boundary and empty owned root; no implicit CLI authority.')
