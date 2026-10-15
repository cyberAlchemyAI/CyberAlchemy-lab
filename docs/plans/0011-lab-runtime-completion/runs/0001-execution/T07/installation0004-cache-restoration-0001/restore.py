"""Inactive exact148 cache quarantine candidate. Root alone may execute.

Host Python only. Cooperative exclusive maintenance is mandatory. Pathname
rename cannot bind a source inode atomically against uncooperative same-UID
replacement; before/after checks detect uncertainty, never authorize rollback.
"""
import argparse
import ctypes
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from datetime import datetime,timezone

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
DEPENDENCY={'path':str((RUN/'T07/revision-0002/dependency-selection-0002.json').relative_to(ROOT)), 'sha256':'2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'}
INVENTORY={'path':str((RUN/'T05/machine-read-development-terminal-0003.json').relative_to(ROOT)), 'sha256':'f38b6c0296b2902535bdc154c093817aae7ca40ad8074e0dc5c2c74868fd03ad'}
SOURCE={'path':'product/lab/release-candidates/v1/interface/api-integration-v17/source-manifest.json','sha256':'ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1'}
FIELDS={'schema_version','status','purpose','authority_effect','installation_identity','dependency_selection_binding','Root_inventory_binding','current_Source_binding','quarantine_parent','quarantine_parent_identity','quarantine_leaf','Root_exclusive_cooperative_maintenance','non_atomic_source_rename_ceiling_accepted'}


def need(value,message):
    if not value:raise ValueError(message)


def parse(raw):
    def pairs(items):
        value={}
        for key,item in items:
            need(key not in value,'duplicate selection field');value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'nonfinite JSON'))


def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def identity(s):return [s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]
def attrs(s):return {'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'size_bytes':s.st_size,'nlink':s.st_nlink,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'atime_ns':s.st_atime_ns}
def canonical(value):
    need(type(value) is str and value==os.path.normpath(value) and Path(value).is_absolute(),'canonical absolute root required')
    return Path(value)
def relative(value):
    need(type(value) is str and value and Path(value).as_posix()==value and not Path(value).is_absolute() and '..' not in Path(value).parts and '\\' not in value,'canonical relative leaf required')
    return Path(value)


class Tree:
    """Held no-follow ancestors and parents, attachment rechecked on each read."""
    def __init__(self,path,expected=None):
        self.path=canonical(str(path));self.fds=[];self.links=[];self.parents={}
        try:
            self.fds=[os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)]
            for name in self.path.parts[1:]:
                parent=self.fds[-1];child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
                self.fds.append(child);self.links.append((parent,name,child,identity(os.fstat(child))))
            self.fd=self.fds[-1];self.parents['']=self.fd
            if expected is not None:need(identity(os.fstat(self.fd))==expected,'selected directory identity differs')
            self.check()
        except BaseException:self.close();raise
    def check(self):
        for parent,name,child,expected in self.links:
            need(identity(os.stat(name,dir_fd=parent,follow_symlinks=False))==identity(os.fstat(child))==expected,'selected ancestor detached')
    def parent(self,rel):
        parts=relative(rel).parts;prefix='';fd=self.fd
        for name in parts[:-1]:
            prefix=prefix+'/'+name if prefix else name
            if prefix not in self.parents:
                child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);self.fds.append(child)
                self.links.append((fd,name,child,identity(os.fstat(child))));self.parents[prefix]=child
            fd=self.parents[prefix]
        self.check();return fd,parts[-1]
    def read(self,rel,pin=None,size=None,mode=None,keep=False):
        parent,name=self.parent(rel);fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_NOATIME,dir_fd=parent)
        transferred=False
        try:
            before=os.fstat(fd);need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_size<=128*1024*1024,'bounded owned regular input required')
            if size is not None:need(before.st_size==size,'selected size differs')
            if mode is not None:need(stat.S_IMODE(before.st_mode)==mode,'selected mode differs')
            chunks=[]
            while block:=os.read(fd,1024*1024):chunks.append(block)
            raw=b''.join(chunks);digest=hashlib.sha256(raw).hexdigest()
            need(attrs(before)==attrs(os.fstat(fd))==attrs(os.stat(name,dir_fd=parent,follow_symlinks=False)),'selected input changed during capture')
            if pin is not None:need(digest==pin,'selected byte digest differs')
            self.check()
            if keep:
                transferred=True;return fd,raw,attrs(before),parent,name
            return raw,attrs(before)
        finally:
            if not transferred:os.close(fd)
    def files(self):
        output=set()
        def walk(fd,prefix):
            for name in sorted(os.listdir(fd)):
                s=os.stat(name,dir_fd=fd,follow_symlinks=False);path=prefix+name
                if stat.S_ISDIR(s.st_mode):
                    child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                    try:
                        need(identity(s)==identity(os.fstat(child)),'inventory directory changed');walk(child,path+'/')
                        need(identity(os.stat(name,dir_fd=fd,follow_symlinks=False))==identity(os.fstat(child)),'inventory directory detached')
                    finally:os.close(child)
                else:need(stat.S_ISREG(s.st_mode),'unselected special file');output.add(path)
        self.check();walk(self.fd,'');self.check();return output
    def close(self):
        for fd in reversed(self.fds):os.close(fd)
        self.fds=[]


def binding_read(tree,binding):
    need(type(binding) is dict and set(binding)=={'path','sha256'},'closed public binding required')
    return tree.read(binding['path'],binding['sha256'])[0]


def shape(value):
    need(type(value) is dict and set(value)==FIELDS,'closed independent Root selection required')
    need(value['schema_version']=='lab-installation0004-cache-restoration-selection/v1-candidate' and value['status']=='Root-selected-for-maintenance'
         and value['purpose']=='restore-exact-selected-installation0004-inventory' and value['authority_effect']=='none','inactive or wrong Root maintenance selection')
    need(value['Root_exclusive_cooperative_maintenance'] is True and value['non_atomic_source_rename_ceiling_accepted'] is True,'explicit cooperative Root maintenance boundary required')
    need(value['dependency_selection_binding']==DEPENDENCY and value['Root_inventory_binding']==INVENTORY and value['current_Source_binding']==SOURCE,'exact original independently selected evidence required')
    for key in ['installation_identity','quarantine_parent_identity']:
        need(type(value[key]) is list and len(value[key])==4 and all(type(v) is int for v in value[key]) and value[key][2]==os.getuid(),'independent current owned directory identity required')
    parent=canonical(value['quarantine_parent']);leaf=value['quarantine_leaf']
    need(type(leaf) is str and leaf.startswith('cal-lab-cache-quarantine-') and Path(leaf).name==leaf and leaf not in ['.','..'],'fresh flat explicit quarantine leaf required')
    need(not (parent/leaf).is_relative_to(ROOT),'quarantined byte bodies must remain outside Git repository')
    return value


def expected_rows(value):
    need(len(value['inputs'])==720 and len(value['original_bindings'])==5,'complete original dependency provenance required')
    expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in value['inputs']}
    expected.update(value['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755
    need(len(expected)==1010 and all(not p.endswith('.pyc') and '__pycache__' not in Path(p).parts for p in expected),'exact selected non-cache1010 closure required')
    for p in expected:relative(p)
    return expected


def audit(tree,expected):
    for path,row in expected.items():tree.read(path,row['sha256'],row['size_bytes'],row['mode'])
    return {'selected_body_rows':len(expected),'SHA_size_mode_verified':True}


def write_all(fd,raw):
    offset=0
    while offset<len(raw):
        count=os.write(fd,raw[offset:]);need(count>0,'durable manifest write stalled');offset+=count
    os.fsync(fd)


def execute(args):
    need(sys.flags.isolated and sys.flags.dont_write_bytecode and sys.flags.no_site,'host Python must use -I -B -S')
    need(not Path(sys.executable).resolve().is_relative_to(INSTALL) and not Path(sys.prefix).resolve().is_relative_to(INSTALL),'use host Python, never selected0004 for pre-relocation imports')
    need(all(not (Path(p).is_absolute() and Path(p).is_relative_to(INSTALL)) for p in sys.path),'host must not import selected installation caches')
    need(hasattr(os,'O_NOATIME') and args.execute,'inactive candidate: explicit execute switch required')
    public=Tree(ROOT);install=None;quarantine_parent=None;qfd=None;mfd=None;held=[];moved=[]
    libc=ctypes.CDLL(None,use_errno=True);rename=libc.renameat2;rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];rename.restype=ctypes.c_int
    try:
        value=shape(parse(binding_read(public,{'path':str(canonical(args.selection).relative_to(ROOT)),'sha256':args.selection_sha256})))
        # Reassert the inherited coordinator descriptor's same open-file lock;
        # never open a second lock or release the coordinator's lock here.
        need(args.runtime_lock_fd>2,'explicit inherited coordinator lock descriptor required')
        lock_parent,lock_leaf=public.parent(str((RUN/'lease-sensitive-runtime.lock').relative_to(ROOT)))
        need(identity(os.fstat(args.runtime_lock_fd))==identity(os.stat(lock_leaf,dir_fd=lock_parent,follow_symlinks=False))
             and stat.S_ISREG(os.fstat(args.runtime_lock_fd).st_mode) and identity(os.fstat(args.runtime_lock_fd))[2:]==[os.getuid(),0o600],'exact inherited shared runtime lock required')
        fcntl.flock(args.runtime_lock_fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        dependency=parse(binding_read(public,DEPENDENCY));expected=expected_rows(dependency)
        receipt=parse(binding_read(public,INVENTORY));source=parse(binding_read(public,SOURCE))
        rows=sorted(receipt['extra_files'],key=lambda r:r['relative_path']);names={r['relative_path'] for r in rows}
        need(len(rows)==len(names)==148 and receipt['missing_expected']==[],'exact148 independently recorded extras required')
        current_paths={r['path'] for r in source['files']}
        need(all(r['path']==str((INSTALL/relative(r['relative_path'])).relative_to(ROOT)) and r['path'] not in current_paths and r['relative_path'].endswith('.pyc') and '__pycache__' in Path(r['relative_path']).parts for r in rows),'selected/current-source or non-cache leaf cannot move')
        install=Tree(INSTALL,value['installation_identity']);entry=audit(install,expected)
        installation_raw,installation_attrs=install.read('installation.json');installation_sha=hashlib.sha256(installation_raw).hexdigest()
        need(install.files()==set(expected)|{'installation.json'}|names,'unexpected/missing input inventory; no effects performed')
        for index,row in enumerate(rows):
            fd,raw,pre,parent,name=install.read(row['relative_path'],row['sha256'],row['size_bytes'],row['mode'],True)
            held.append((fd,row,pre,parent,name,f'{index:04d}-'+row['sha256'][:16]+'.pyc'))
            need(all(pre[k]==row[k] for k in ['device','inode','uid','mode','size_bytes','mtime_ns','ctime_ns']) and pre['nlink']==1,'Root exact extra identity changed')
        quarantine_parent=Tree(value['quarantine_parent'],value['quarantine_parent_identity'])
        ps=os.fstat(quarantine_parent.fd)
        need(ps.st_uid==os.getuid() and not stat.S_IMODE(ps.st_mode)&0o022 and ps.st_dev==os.fstat(install.fd).st_dev,'owned non-writable same-filesystem quarantine parent required')
        leaf=value['quarantine_leaf'];quarantine_parent.check();os.mkdir(leaf,0o700,dir_fd=quarantine_parent.fd)
        qfd=os.open(leaf,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=quarantine_parent.fd);qidentity=identity(os.fstat(qfd))
        need(qidentity[2:]==[os.getuid(),0o700],'fresh quarantine custody differs')
        def qcheck():
            quarantine_parent.check();install.check()
            need(identity(os.stat(leaf,dir_fd=quarantine_parent.fd,follow_symlinks=False))==identity(os.fstat(qfd))==qidentity,'quarantine detached')
        qcheck();mfd=os.open('maintenance-manifest.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=qfd);manifest_identity=identity(os.fstat(mfd))
        def event(event):
            qcheck();need(identity(os.stat('maintenance-manifest.jsonl',dir_fd=qfd,follow_symlinks=False))==identity(os.fstat(mfd))==manifest_identity,'manifest detached')
            write_all(mfd,encoded({'at':datetime.now(timezone.utc).isoformat(),**event})+b'\n');qcheck()
        event({'event':'preflight-complete','selection_sha256':args.selection_sha256,'entry_original_selected':entry,'installation_receipt_sha256':installation_sha,
            'exact148':[{'original':r,'prestat':pre,'quarantine_leaf':dest} for fd,r,pre,parent,name,dest in held],
            'scope':'Root exclusive cooperative maintenance; no atomic inode-binding guarantee against uncooperative same-UID replacement.','quarantine_identity':qidentity})
        os.fsync(qfd);os.fsync(quarantine_parent.fd)
        try:
            for fd,row,pre,parent,name,dest in held:
                qcheck();need(attrs(os.fstat(fd))==attrs(os.stat(name,dir_fd=parent,follow_symlinks=False))==pre,'held exact source changed before rename')
                event({'event':'rename-intent','original_relative_path':row['relative_path'],'quarantine_leaf':dest,'original_sha256':row['sha256'],'prestat':pre})
                need(rename(parent,os.fsencode(name),qfd,os.fsencode(dest),1)==0,'renameat2 no-replace refused; preserve partial state')
                os.fsync(parent);os.fsync(qfd)
                post=attrs(os.fstat(fd));qcheck()
                need(attrs(os.stat(dest,dir_fd=qfd,follow_symlinks=False))==post,'renamed destination is not held source; uncertainty')
                need({k:v for k,v in pre.items() if k!='ctime_ns'}=={k:v for k,v in post.items() if k!='ctime_ns'},'rename changed protected source attributes beyond documented ctime')
                try:os.stat(name,dir_fd=parent,follow_symlinks=False)
                except FileNotFoundError:pass
                else:raise ValueError('source name unexpectedly remains or was replaced; uncertainty')
                os.lseek(fd,0,os.SEEK_SET);digest=hashlib.sha256()
                while block:=os.read(fd,1024*1024):digest.update(block)
                need(digest.hexdigest()==row['sha256'] and attrs(os.fstat(fd))==post,'quarantined held bytes changed')
                moved.append(dest);event({'event':'rename-observed','original_relative_path':row['relative_path'],'quarantine_leaf':dest,'sha256':row['sha256'],'prestat':pre,'poststat':post,'ctime_change_documented':True})
            need(install.files()==set(expected)|{'installation.json'},'strict original inventory not restored')
            exit=audit(install,expected);raw,post_receipt=install.read('installation.json',installation_sha)
            need(post_receipt==installation_attrs,'original installation receipt changed')
            binding_read(public,DEPENDENCY);binding_read(public,INVENTORY);binding_read(public,SOURCE)
            need(set(os.listdir(qfd))==set(moved)|{'maintenance-manifest.jsonl'},'quarantine inventory changed')
            event({'event':'restoration-complete','moved_count':len(moved),'exit_original_selected':exit,'original_receipt_preserved':True,
                'post_inventory_regular_files':1011,'all148_bytes_inodes_owner_group_mode_mtime_atime_preserved':True,'only_leaf_ctime_may_change_from_rename':True,
                'fresh_selected0004_original_strict_control_installed_check':'REQUIRED separately by Root; not executed by host maintenance script','authority_effect':'none'})
            print(json.dumps({'result':'RESTORED-PENDING-FRESH-ORIGINAL-STRICT-CHECK','quarantine':str(Path(value['quarantine_parent'])/leaf),'moved_count':148,'selected1010_entry_exit':True,'authority_effect':'none','task_complete':False},sort_keys=True));return 0
        except BaseException as error:
            try:event({'event':'REFUSED-OR-UNCERTAIN-PARTIAL-STATE','exception_class':type(error).__name__,'last_errno':ctypes.get_errno(),'observed_completed_moves':moved,'automatic_rollback':False,'all_remaining_originals_and_quarantine_must_be_preserved':True})
            except BaseException:pass
            raise
    finally:
        for fd,row,pre,parent,name,dest in reversed(held):os.close(fd)
        if mfd is not None:os.close(mfd)
        if qfd is not None:os.close(qfd)
        if quarantine_parent is not None:quarantine_parent.close()
        if install is not None:install.close()
        public.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--selection',required=True);parser.add_argument('--selection-sha256',required=True)
    parser.add_argument('--runtime-lock-fd',required=True,type=int);parser.add_argument('--execute',action='store_true')
    return execute(parser.parse_args())

if __name__=='__main__':raise SystemExit(main())
