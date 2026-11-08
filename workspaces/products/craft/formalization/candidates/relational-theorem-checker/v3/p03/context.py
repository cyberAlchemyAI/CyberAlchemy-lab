"""Invocation-owned compiler, catalogs, source bindings and private run roots."""
from dataclasses import dataclass, field
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid

BASE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in BASE.parents if (p/'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())
V2=BASE.parent/'v2'
_modules={}
_module_lock=threading.RLock()


def require(condition,message):
    if not condition:raise ValueError(message)
def read(path):return json.loads(Path(path).read_text())
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def binding(path):
    p=Path(path).resolve();return {'path':str(p.relative_to(ROOT)),'sha256':digest(p)}
def tagged(path):return {'kind':'repo',**binding(path)}
def check(ref):
    relative=Path(ref['path'])
    require(not relative.is_absolute() and '..' not in relative.parts and '\\' not in str(relative),'unsafe binding')
    p=(ROOT/relative).resolve()
    require(p.is_relative_to(ROOT) and p.is_file() and digest(p)==ref['sha256'],'missing/stale input '+str(relative))
    return p
def write(path,value):
    p=Path(path).resolve();require(p.is_relative_to(BASE),'write outside v3')
    p.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
    with p.open('xb') as out:out.write(raw)
    return binding(p)
def load(name,path):
    """Private stable module names; never replace a legacy/global function."""
    path=Path(path).resolve()
    with _module_lock:
        if name in _modules:
            require(Path(_modules[name].__file__).resolve()==path,'private import identity collision')
            return _modules[name]
        require(name not in sys.modules,'private namespace occupied')
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module
        try:spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop(name,None);raise
        _modules[name]=module
        return module

C=load('_relational_v3_contracts_context',BASE/'p01/contracts.py')
L=load('_relational_v3_layout_context',BASE/'p02/proof_layout.py')


class ResourceExhausted(ValueError):pass
class UnsupportedProfile(ValueError):pass
class UnsupportedPolicy(ValueError):pass


@dataclass
class QualificationContext:
    run_root: Path
    resource_policy: dict
    stage_compiler: object = None
    session: str = field(default_factory=lambda:uuid.uuid4().hex)
    _events: dict = field(default_factory=dict,init=False,repr=False)

    def __post_init__(self):
        self.run_root=Path(self.run_root).resolve()
        require(self.run_root.is_relative_to(BASE),'run root must stay inside v3')
        self.resource_policy=copy.deepcopy(self.resource_policy)
        C.validate('resource-policy',self.resource_policy)
        self.catalog=copy.deepcopy(C.catalog())
        # Accepted predecessor receipts fix catalog, generator and inspection code.
        self.trusted=[]
        for id in ['P00','P01','P02']:
            receipt=read(BASE/id.lower()/'task-acceptance.json')
            require(receipt['result']=='accepted','unaccepted prerequisite '+id)
            for ref in receipt['artifacts']+receipt['inputs']:check(ref)
            self.trusted += receipt['artifacts']
        self.trusted += [binding(BASE/'p03/context.py'),binding(BASE/'p03/qualification.py'),binding(BASE/'p03/inspect_worker.py')]
        formal=BASE.parent/'v1/formal'
        self.lean=formal/'.toolcache/lean-4.33.1-linux/bin/lean'
        self.lock=read(formal/'toolchain-lock.json')
        self.assert_current()
        if self.stage_compiler is None:self.stage_compiler=self.compile_default

    def assert_current(self):
        for ref in self.trusted:check(ref)
        require(C.catalog()==self.catalog,'catalog changed during invocation')
        require(digest(self.lean)==self.lock['lean_binary_sha256'],'compiler binary changed')
        require(digest(self.lean.parent.parent/'lib/lean/libleanshared.so')==self.lock['lean_shared_library_sha256'],'kernel shared library changed')
        require(subprocess.check_output([str(self.lean),'--version'],text=True).strip()==self.lock['version_output'],'compiler version changed')

    def environment(self,build):
        return {**os.environ,'LEAN_PATH':str(build),'PATH':str(self.lean.parent)+os.pathsep+os.environ.get('PATH',''),'PYTHONDONTWRITEBYTECODE':'1'}

    def allocate(self,request):
        self.run_root.mkdir(parents=True,exist_ok=True)
        return Path(tempfile.mkdtemp(prefix='qualify-'+C.identity(request)[:12]+'-',dir=self.run_root))

    def boundary(self,proposal,result=None):
        payload={'proposal':proposal}
        if result is not None:payload['result']=result
        process=subprocess.run([sys.executable,str(BASE/'p02/legacy_boundary.py')],input=json.dumps(payload),capture_output=True,text=True,timeout=self.resource_policy['stage_seconds'])
        try:answer=C.decode(process.stdout.encode())
        except Exception as e:raise ValueError('typed legacy boundary failed: '+process.stderr[:200]) from e
        if not answer['ok']:
            if answer['error_type']=='Unsupported':raise UnsupportedProfile(answer['error'])
            if answer['error_type']=='Exhausted':raise ResourceExhausted(answer['error'])
            raise ValueError(answer['error'])
        require(process.returncode==0,'typed boundary failed')
        return answer['value']

    def prepare(self,build,info,mode):
        cached=read(V2/'s13/build/dependencies.json')['modules']
        require([m['source'] for m in cached]==info['runtime_sources'],'cached source inventory differs from typed boundary')
        records=[]
        if mode=='warm':
            for m in cached:
                source=check(m['source']);compiled=check(m['olean'])
                name=m['module'];require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',name),'invalid cached module')
                (build/(name+'.lean')).write_bytes(source.read_bytes())
                dest=build/(name+'.olean');dest.write_bytes(compiled.read_bytes())
                require(digest(dest)==m['olean']['sha256'],'cache copy differs')
                records.append({'module':name,'source':m['source'],'olean':binding(dest),'mode':'byte-verified-dependency-reuse'})
        elif mode=='cold':
            for m in cached:
                source=check(m['source']);records+=self.stage_compiler(build,[(m['module'],source)])
        else:raise ValueError('unknown dependency mode')
        write(build/'dependencies.json',{'modules':records,'policy':'Dependency reuse is currentness only; each instance and general replay is fresh.'})
        return records

    def compile_default(self,build,modules):
        records=[]
        for name,source in modules:
            self.assert_current();source=Path(source)
            raw=source.read_text()
            driver=V2/'s06/RuntimeVerifier.lean'
            expected_driver=next(m['source'] for m in read(V2/'s13/build/dependencies.json')['modules'] if m['module']=='RuntimeVerifier')
            trusted_driver=name=='RuntimeVerifier' and source.resolve()==driver.resolve() and binding(source)==expected_driver
            require(not re.search(r'^\s*axiom\s|\bsorry\b',raw,re.M),'admitted/custom-axiom source')
            require(trusted_driver or not re.search(r'\bunsafe\b|\bpartial\b',raw),'unsupported proof source')
            dest=Path(build)/(name+'.lean')
            if dest!=source:dest.write_bytes(source.read_bytes())
            start=time.monotonic()
            process=subprocess.run([str(self.lean),'-o',str(dest.with_suffix('.olean')),str(dest)],cwd=build,env=self.environment(build),capture_output=True,text=True,timeout=self.resource_policy['stage_seconds'])
            output=process.stdout+process.stderr
            if len(output.encode())>self.resource_policy['output_bytes']:raise ResourceExhausted('compiler output ceiling')
            require(process.returncode==0 and 'warning:' not in output and 'sorryAx' not in output,'Lean compilation failed '+name+'\n'+output[:3000])
            axioms=set(re.findall(r'\b(?:propext|Quot\.sound|Classical\.choice)\b',output))
            for line in output.splitlines():
                if 'depends on axioms:' in line:
                    names=[x.strip() for x in line.split('[',1)[1].split(']',1)[0].split(',')]
                    require(set(names)<= {'propext','Quot.sound','Classical.choice'},'unapproved emitted axiom')
            records.append({'module':name,'source':binding(source),'olean':binding(dest.with_suffix('.olean')),'seconds':time.monotonic()-start,'output':output,'mode':'fresh-compilation'})
        return records

    def inspect(self,request,result):
        self.assert_current()
        process=subprocess.run([sys.executable,str(BASE/'p03/inspect_worker.py')],input=json.dumps({'request':request,'result':result}),text=True,capture_output=True,timeout=self.resource_policy['stage_seconds'])
        answer=C.decode(process.stdout.encode())
        require(process.returncode==0 and answer['ok'],answer.get('error','saved inspection failed'))
        self.assert_current()
        return answer['value']

    def record_fresh(self,result):
        self._events[result['run_id']]={'request_identity':result['request_identity'],'manifest_identity':C.identity(result['manifest']),'session':self.session}

    def live_event(self,result):
        return self._events.get(result['run_id'])=={'request_identity':result['request_identity'],'manifest_identity':C.identity(result['manifest']),'session':self.session}
