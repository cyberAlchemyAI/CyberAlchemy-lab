"""Owned generation wrapper; HEAD replacement commits a complete native batch.

The original native implementation is unchanged. Interrupted stages are never
cleaned or adopted. Recovery repeats the exact uncommitted request in a new
generation; original native validation and cold replay remain mandatory.
"""
from contextlib import contextmanager
import ctypes
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid
from .private_io import canonical, require, sha, read, sync, write, atomic, directory

def original_event_bytes(executable,request_path,request,executor):
    child=executor.run_native('seal',[str(request_path)])
    require(child.returncode==0,'original native typed serialization refused')
    require(json.loads(child.stdout)==request,'request events were not already exactly sealed')
    # Preserve the exact native serialized event substring, including native
    # struct/map field order and number/string encoding. No Python re-encoding.
    text=child.stdout.decode('utf-8');decoder=json.JSONDecoder();position=0;out={}
    for family,prefix in [('semantic','{"semantic":['),('governance','],"governance":[')]:
        require(text.startswith(prefix,position),'native sealing envelope differs');position+=len(prefix);rows=[]
        for index,event in enumerate(request[family]):
            if index:require(text[position]==',','native event separator differs');position+=1
            value,end=decoder.raw_decode(text,position);require(value==event,'native event postimage differs');rows.append(text[position:end].encode()+b'\n');position=end
        out[family]=rows
    require(text[position:]==']}\n','native sealing suffix differs')
    return out

@dataclass(frozen=True)
class PendingPins:
    pending_sha256:str
    expected_head_sha256:str
    request_sha256:str
    executable_sha256:str

class GenerationStore:
    def __init__(self,root,identity,executable,executable_sha256,*,executor,boundary):
        self.executor=executor;self.boundary=boundary
        self.root=Path(root);self.identity=tuple(identity);self.executable=Path(executable);self.executable_sha256=executable_sha256;self.guard()
    def guard(self):
        self.boundary.guard();self.executor.guard()
        require(Path(self.executor.executable_path)==self.executable and self.executor.executable_sha256==self.executable_sha256,
                'selected ontology executor origin differs')
        require(self.root.is_absolute() and not any(p.is_symlink() for p in [self.root,*self.root.parents]),'exact absolute store root required')
        s=self.root.stat();require((s.st_dev,s.st_ino)==self.identity and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode)==0o700,'owned store identity/mode changed')
        require(sha(read(self.executable))==self.executable_sha256 and stat.S_IMODE(self.executable.stat().st_mode)==0o755,'native executable pin/mode changed')
    @contextmanager
    def lock(self):
        self.guard()
        with directory(self.root) as parent:
            fd=os.open('writer.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600,dir_fd=parent)
            try:
                selected=os.fstat(fd)
                def check():
                    current=os.stat('writer.lock',dir_fd=parent,follow_symlinks=False)
                    opened=os.fstat(fd)
                    key=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_mode,s.st_size)
                    require(key(current)==key(opened)==key(selected) and stat.S_ISREG(current.st_mode)
                            and current.st_uid==os.geteuid() and stat.S_IMODE(current.st_mode)==0o600
                            and current.st_size==0,'unknown/replaced writer lock; preserve state')
                    self.guard()
                check();fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);check()
                try:yield
                finally:check()
            finally:os.close(fd)
    def bootstrap(self):
        self.guard();require(not list(self.root.iterdir()),'bootstrap refuses existing state')
        generations=self.root/'generations';generations.mkdir(mode=0o700);genesis=generations/'genesis';genesis.mkdir(mode=0o700)
        for name in ['semantic','governance']:(genesis/name).mkdir(mode=0o700);sync(genesis/name)
        sync(genesis);sync(generations)
        write(self.root/'HEAD.json',canonical({'generation':'genesis','files':{},'request_sha256':None,'authority_effect':'none'}));sync(self.root)
    def tree(self,directory,allow_residue=False,expected=None):
        directory=Path(directory);require(not directory.is_symlink(),'generation symlink')
        require(isinstance(expected,dict),'independent expected event membership required')
        require({p.name for p in directory.iterdir()}=={'semantic','governance'},'unknown generation entries')
        out={}
        for family in ['semantic','governance']:
            folder=directory/family;require(folder.is_dir() and not folder.is_symlink(),'generation family changed')
            for p in folder.iterdir():
                name=family+'/'+p.name
                if allow_residue and p.name=='.append.lock':require(read(p)==b'','unknown append lock bytes');continue
                if allow_residue and p.name.startswith('.') and p.name.endswith('.tmp'):
                    name=family+'/'+p.name[1:-4]
                    require(name in expected,'unknown temporary residue');require(sha(read(p))==expected[name],'changed temporary residue');continue
                require(p.name.endswith('.json') and not p.name.startswith('.'),'unknown generation file')
                require(name in expected,'unselected generation event');raw=read(p);require(sha(raw)==expected[name],'unknown or changed event bytes')
                out[name]=sha(raw)
        return out
    def head(self):
        raw=read(self.root/'HEAD.json');head=json.loads(raw)
        require(set(head)=={'generation','files','request_sha256','authority_effect'} and head['authority_effect']=='none','closed generation head required')
        require(head['generation'] and '/' not in head['generation'] and '..' not in head['generation'],'invalid generation name')
        directory=self.root/'generations'/head['generation'];require(self.tree(directory,expected=head['files'])==head['files'],'committed generation bytes changed')
        return head,raw,directory
    def read_committed(self):
        self.guard();head,raw,directory=self.head()
        if not head['files']:return {'result':'EMPTY-GENESIS','files':{},'native_cut':None}
        cursor=sum(n.startswith('semantic/') for n in head['files'])
        child=self.executor.run_native('read',[str(directory/'semantic'),str(directory/'governance'),str(cursor)])
        require(child.returncode==0,'cold native replay failed: '+child.stderr.decode())
        require(read(self.root/'HEAD.json')==raw,'head changed during read')
        require(self.tree(directory,expected=head['files'])==head['files'],'generation changed during replay')
        return {'result':'PASS','files':head['files'],'native_cut':json.loads(child.stdout),'native_stdout_bytes':child.stdout,'native_stdout_sha256':sha(child.stdout)}
    def prepare(self,request_path,request_sha256):
        with self.lock():
            head,head_raw,base=self.head();request_raw=read(request_path);require(sha(request_raw)==request_sha256,'independent request digest differs')
            request=json.loads(request_raw);require(set(request)=={'semantic','governance'},'closed native request required')
            operation=uuid.uuid4().hex;request_copy=self.root/('request-'+operation+'.json');write(request_copy,request_raw)
            native_bytes=original_event_bytes(self.executable,request_copy,request,self.executor)
            expected=dict(head['files'])
            for family,cursor_field in [('semantic','semantic_cursor'),('governance','governance_cursor')]:
                for event,event_bytes in zip(request[family],native_bytes[family]):
                    event_id=event['event_id'];require(event_id and '/' not in event_id and '..' not in event_id,'unsafe event file identifier')
                    name=family+'/'+f"{event[cursor_field]:08d}-{event_id}.json";require(name not in expected,'event target already exists');expected[name]=sha(event_bytes)
            stage=self.root/('stage-'+operation);stage.mkdir(mode=0o700)
            for family in ['semantic','governance']:(stage/family).mkdir(mode=0o700)
            for name,digest in head['files'].items():
                raw=read(base/name);require(sha(raw)==digest,'base changed before copy');write(stage/name,raw)
            for family in ['semantic','governance']:sync(stage/family)
            sync(stage);s=stage.stat()
            pending={'schema_version':'native-generation-pending/v1-candidate','operation':operation,'stage':stage.name,'stage_identity':[s.st_dev,s.st_ino],'expected_head_sha256':sha(head_raw),'base_head':head,'expected_post_files':expected,'request_path':request_copy.name,'request_sha256':request_sha256,'executable_sha256':self.executable_sha256,'authority_effect':'none'}
            path=self.root/('pending-'+operation+'.json');raw=canonical(pending);write(path,raw);sync(self.root)
            return path,PendingPins(sha(raw),sha(head_raw),request_sha256,self.executable_sha256)
    def pending(self,path,pins):
        require(type(pins) is PendingPins,'independent pending pins required')
        require(Path(path).parent==self.root,'pending outside selected root')
        raw=read(path);require(sha(raw)==pins.pending_sha256,'independent pending digest differs')
        value=json.loads(raw);require(set(value)=={'schema_version','operation','stage','stage_identity','expected_head_sha256','base_head','expected_post_files','request_path','request_sha256','executable_sha256','authority_effect'},'closed pending controls required')
        require(value['schema_version']=='native-generation-pending/v1-candidate' and value['authority_effect']=='none' and value['expected_head_sha256']==pins.expected_head_sha256 and value['request_sha256']==pins.request_sha256 and value['executable_sha256']==pins.executable_sha256==self.executable_sha256,'pending operation controls differ')
        require(value['stage']=='stage-'+value['operation'] and value['request_path']=='request-'+value['operation']+'.json' and len(value['operation'])==32 and all(n in '0123456789abcdef' for n in value['operation']),'bounded operation paths required')
        require(sha(read(self.root/value['request_path']))==pins.request_sha256,'request changed')
        return value
    def finish_publication(self,value,pins,checkpoint=None):
        publication=self.root/('publication-'+value['operation']+'.json')
        record=json.loads(read(publication))
        require(set(record)=={'pending_sha256','stage','stage_identity','post_files','request_sha256','expected_head_sha256'},'unknown publication controls')
        require(record['pending_sha256']==pins.pending_sha256 and record['request_sha256']==pins.request_sha256 and record['expected_head_sha256']==pins.expected_head_sha256 and record['post_files']==value['expected_post_files'],'publication selection differs')
        name=record['stage'];require(name==value['stage'] or name.startswith('recovery-'+value['operation']+'-') and len(name.rsplit('-',1)[-1])==32 and all(n in '0123456789abcdef' for n in name.rsplit('-',1)[-1]),'unknown publication stage')
        final=self.root/'generations'/('operation-'+value['operation']);stage=self.root/name
        require(not (stage.exists() and final.exists()),'ambiguous existing generation')
        selected=stage if stage.exists() else final;s=selected.stat()
        require((s.st_dev,s.st_ino)==tuple(record['stage_identity']) and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode)==0o700,'publication generation identity differs')
        require(self.tree(selected,expected=value['expected_post_files'])==value['expected_post_files'],'publication postimage changed')
        cursor=sum(name.startswith('semantic/') for name in value['expected_post_files'])
        cold=self.executor.run_native('read',[str(selected/'semantic'),str(selected/'governance'),str(cursor)])
        require(cold.returncode==0,'cold publication replay failed: '+cold.stderr.decode())
        if stage.exists():
            if checkpoint:checkpoint('before-generation-publish')
            libc=ctypes.CDLL(None,use_errno=True);rename=libc.renameat2
            rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];rename.restype=ctypes.c_int
            with directory(self.root) as source_fd, directory(final.parent) as destination_fd:
                require(rename(source_fd,os.fsencode(stage.name),destination_fd,os.fsencode(final.name),1)==0,'generation publish conflict; retain state')
            sync(final.parent)
        if checkpoint:checkpoint('before-head-commit')
        require(sha(read(self.root/'HEAD.json'))==pins.expected_head_sha256,'head changed before commit')
        require(self.tree(final,expected=value['expected_post_files'])==value['expected_post_files'],'published generation changed')
        self.guard()
        atomic(self.root/'HEAD.json',canonical({'generation':final.name,'files':value['expected_post_files'],'request_sha256':pins.request_sha256,'authority_effect':'none'}))
        if checkpoint:checkpoint('after-head-commit')
        self.guard();return {'result':'PASS','committed':True,'idempotent':False,'native_replay':json.loads(cold.stdout),'commit_point':'fsynced-HEAD-replacement'}
    def run(self,path,pins,*,recover=False,native_observer_env=None,checkpoint=None):
        with self.lock():
            value=self.pending(path,pins);head,head_raw,base=self.head()
            if head['request_sha256']==pins.request_sha256 and head['files']==value['expected_post_files']:
                return {'result':'PASS','committed':True,'idempotent':True,'native_replay':self.read_committed()}
            require(sha(head_raw)==pins.expected_head_sha256 and head==value['base_head'],'base head changed; reconciliation required')
            publication=self.root/('publication-'+value['operation']+'.json')
            if publication.exists():
                require(recover,'publication residue requires explicit recovery')
                return self.finish_publication(value,pins,checkpoint)
            stage=self.root/value['stage'];s=stage.stat();require((s.st_dev,s.st_ino)==tuple(value['stage_identity']) and stat.S_IMODE(s.st_mode)==0o700,'selected stage identity changed')
            existing=self.tree(stage,allow_residue=recover,expected=value['expected_post_files'])
            if recover:
                # Never remove a stale lock, target, temporary, or old stage.
                require(all(name in value['expected_post_files'] for name in existing),'unrecognized residue')
                fresh=self.root/('recovery-'+value['operation']+'-'+uuid.uuid4().hex);fresh.mkdir(mode=0o700)
                for family in ['semantic','governance']:(fresh/family).mkdir(mode=0o700)
                for name,digest in value['base_head']['files'].items():
                    raw=read(base/name);require(sha(raw)==digest,'original base changed');write(fresh/name,raw)
                stage=fresh
            else:require(existing==value['base_head']['files'],'stage has residue; inspect/recover explicitly')
            if native_observer_env is not None:
                require(type(native_observer_env) is dict,'explicit dedicated checkpoint selection required')
                with self.executor.start_checkpoint([str(stage/'semantic'),str(stage/'governance'),str(self.root/value['request_path'])],native_observer_env) as owned:
                    child=owned.wait()
            else:
                child=self.executor.run_native('append',[str(stage/'semantic'),str(stage/'governance'),str(self.root/value['request_path'])])
            require(child.returncode==0,'native append failed; retain uncommitted stage: '+child.stderr.decode())
            require(self.tree(stage,expected=value['expected_post_files'])==value['expected_post_files'],'native postimage differs')
            cursor=sum(name.startswith('semantic/') for name in value['expected_post_files'])
            cold=self.executor.run_native('read',[str(stage/'semantic'),str(stage/'governance'),str(cursor)])
            require(cold.returncode==0,'fresh full native replay rejected postimage: '+cold.stderr.decode())
            for family in ['semantic','governance']:sync(stage/family)
            sync(stage)
            s=stage.stat();write(publication,canonical({'pending_sha256':pins.pending_sha256,'stage':stage.name,'stage_identity':[s.st_dev,s.st_ino],'post_files':value['expected_post_files'],'request_sha256':pins.request_sha256,'expected_head_sha256':pins.expected_head_sha256}));sync(self.root)
            result=self.finish_publication(value,pins,checkpoint);result['retained_original_stage_on_recovery']=recover;return result
