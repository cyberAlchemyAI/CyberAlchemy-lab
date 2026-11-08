"""Streamed atomic tools and a verified supervisor-owned qualification context."""
from pathlib import Path
import os
import selectors
import subprocess
import sys
import time
from ..p03.context import *

class ToolExhausted(ResourceExhausted):
    def __init__(self,reason,outcome):super().__init__(reason);self.outcome=outcome

class WorkerContext(QualificationContext):
    def __init__(self,job,policy):
        self.job=Path(job).resolve();self.description=C.decode((self.job/'supervision.json').read_bytes())
        self.forwarded=0;self.last_outcome=None
        super().__init__(self.job/'builds',policy)
        self.trusted += self.description['worker_sources']
        predecessor=read(BASE/'p03/task-acceptance.json')
        require(predecessor['result']=='accepted','P03 is not accepted')
        self.trusted += predecessor['artifacts']+predecessor['inputs']
        self.verify_supervision()
        self.assert_current()

    def verify_supervision(self):
        d=self.description
        require(self.job.is_relative_to(BASE) and d['job']==str(self.job),'worker job mismatch')
        require(os.getpgrp()==os.getpid() and os.getsid(0)==os.getpid(),'worker must remain the supervised session/group leader')
        require(d['policy']==self.resource_policy,'original required policy must not be rewritten')
        for ref in d['worker_sources']:check(ref)
        if self.resource_policy['memory_mode']=='required':
            require(d['enforcement']=='cgroup-v2' and d['cgroup'],'required enforcement unavailable')
            path=Path(d['cgroup']).resolve();require(path.is_relative_to('/sys/fs/cgroup'),'invalid kernel cgroup path')
            require((path/'memory.max').read_text().strip()==str(self.resource_policy['memory_bytes']),'effective memory control changed')
            require((path/'pids.max').read_text().strip()==str(d['pids_max']),'effective process control changed')
            require('0::/'+str(path.relative_to('/sys/fs/cgroup')) in Path('/proc/self/cgroup').read_text(),'worker escaped required cgroup')
        else:require(d['enforcement']=='advisory','unexpected advisory backend')

    def report(self,request):
        return {'enforcement':self.description['enforcement'],'outcome':'completed','events':[{'kind':'worker','detail':'Checked candidate prepared inside supervised group; issuance requires successful supervisor completion.'}],'policy_identity':C.identity(request['resource_policy'])}

    def run_tool(self,args,*,input=None,cwd=None,env=None,timeout=None,**ignored):
        timeout=timeout or self.resource_policy['stage_seconds'];started=time.monotonic()
        data=input.encode() if isinstance(input,str) else input
        p=subprocess.Popen(args,cwd=cwd,env=env,stdin=subprocess.PIPE if data is not None else subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        streams=selectors.DefaultSelector();output={'stdout':bytearray(),'stderr':bytearray()};offset=0
        try:
            for pipe,name in [(p.stdout,'stdout'),(p.stderr,'stderr')]:os.set_blocking(pipe.fileno(),False);streams.register(pipe,selectors.EVENT_READ,name)
            if data is not None:os.set_blocking(p.stdin.fileno(),False);streams.register(p.stdin,selectors.EVENT_WRITE,'stdin')
            while streams.get_map():
                if time.monotonic()-started>timeout:raise ToolExhausted('Atomic tool deadline exceeded.','timeout')
                for key,_ in streams.select(.02):
                    if key.data=='stdin':
                        if offset==len(data):streams.unregister(key.fileobj);p.stdin.close();continue
                        try:offset+=os.write(p.stdin.fileno(),data[offset:offset+65536])
                        except BrokenPipeError:streams.unregister(key.fileobj);p.stdin.close()
                        continue
                    chunk=os.read(key.fileobj.fileno(),65536)
                    if not chunk:streams.unregister(key.fileobj);continue
                    self.forwarded+=len(chunk)
                    if self.forwarded>self.resource_policy['output_bytes']:raise ToolExhausted('Inner tool/IPC output-byte limit.','output-limit')
                    output[key.data].extend(chunk)
                    # Forward each consumed byte once. The outer supervisor also
                    # bounds the stream while this local bound limits accumulation.
                    os.write(1 if key.data=='stdout' else 2,chunk)
            p.wait(timeout=max(.001,timeout-(time.monotonic()-started)))
            return subprocess.CompletedProcess(args,p.returncode,output['stdout'].decode(),output['stderr'].decode())
        except (ToolExhausted,subprocess.TimeoutExpired) as e:
            self.last_outcome=getattr(e,'outcome','timeout');p.kill();p.wait();raise
        finally:
            streams.close()
            if p.poll() is None:p.kill();p.wait()
            for pipe in [p.stdin,p.stdout,p.stderr]:
                if pipe is not None and not pipe.closed:pipe.close()

    def assert_current(self):
        for ref in self.trusted:check(ref)
        require(C.catalog()==self.catalog,'catalog changed during invocation')
        require(digest(self.lean)==self.lock['lean_binary_sha256'],'compiler binary changed')
        require(digest(self.lean.parent.parent/'lib/lean/libleanshared.so')==self.lock['lean_shared_library_sha256'],'kernel library changed')
        version=self.run_tool([str(self.lean),'--version'],timeout=self.resource_policy['stage_seconds'])
        require(version.returncode==0 and version.stdout.strip()==self.lock['version_output'],'compiler version changed')

    def boundary(self,proposal,result=None):
        wire={'proposal':proposal}
        if result is not None:wire['result']=result
        p=self.run_tool([sys.executable,str(BASE/'p02/legacy_boundary.py')],input=__import__('json').dumps(wire),timeout=self.resource_policy['stage_seconds'])
        answer=C.decode(p.stdout.encode())
        if not answer['ok']:
            if answer['error_type']=='Unsupported':raise UnsupportedProfile(answer['error'])
            if answer['error_type']=='Exhausted':raise ResourceExhausted(answer['error'])
            raise ValueError(answer['error'])
        require(p.returncode==0,'typed boundary failed');return answer['value']

    def compile_default(self,build,modules):
        # Same exact source guard and compiler command as accepted P03; only
        # bounded streaming replaces whole-output capture.
        records=[]
        for name,source in modules:
            self.assert_current();source=Path(source);raw=source.read_text()
            driver=V2/'s06/RuntimeVerifier.lean'
            expected=next(m['source'] for m in read(V2/'s13/build/dependencies.json')['modules'] if m['module']=='RuntimeVerifier')
            trusted_driver=name=='RuntimeVerifier' and source.resolve()==driver.resolve() and binding(source)==expected
            require(not re.search(r'^\s*axiom\s|\bsorry\b',raw,re.M),'admitted/custom-axiom source')
            require(trusted_driver or not re.search(r'\bunsafe\b|\bpartial\b',raw),'unsupported proof source')
            dest=Path(build)/(name+'.lean')
            if dest!=source:dest.write_bytes(source.read_bytes())
            started=time.monotonic();p=self.run_tool([str(self.lean),'-o',str(dest.with_suffix('.olean')),str(dest)],cwd=build,env=self.environment(build),timeout=self.resource_policy['stage_seconds'])
            output=p.stdout+p.stderr
            require(p.returncode==0 and 'warning:' not in output and 'sorryAx' not in output,'Lean compilation failed '+name+'\n'+output[:3000])
            for line in output.splitlines():
                if 'depends on axioms:' in line:
                    names=[x.strip() for x in line.split('[',1)[1].split(']',1)[0].split(',')]
                    require(set(names)<={'propext','Quot.sound','Classical.choice'},'unapproved axiom')
            records.append({'module':name,'source':binding(source),'olean':binding(dest.with_suffix('.olean')),'seconds':time.monotonic()-started,'output':output,'mode':'fresh-compilation'})
        return records

    def evaluate(self,normal):
        p=self.run_tool([sys.executable,str(BASE/'p06/evaluation_worker.py')],input=__import__('json').dumps({'normal':normal,'policy':self.resource_policy}),timeout=self.resource_policy['stage_seconds'])
        answer=C.decode(p.stdout.encode())
        if not answer['ok']:raise ResourceExhausted(answer['error'])
        require(p.returncode==0,'reference evaluation failed');return answer['value']

    def inspect(self,request,result):
        self.assert_current()
        p=self.run_tool([sys.executable,str(BASE/'p03/inspect_worker.py')],input=__import__('json').dumps({'request':request,'result':result}),timeout=self.resource_policy['stage_seconds'])
        answer=C.decode(p.stdout.encode());require(p.returncode==0 and answer['ok'],answer.get('error','saved inspection failed'))
        self.assert_current();return answer['value']
