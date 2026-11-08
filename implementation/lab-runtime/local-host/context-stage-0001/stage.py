"""Effect-disabled Context stage closure and fake-only held copy mechanism."""
from __future__ import annotations
import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath

REPO=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).resolve().parent
LOCAL=REPO/'implementation/lab-runtime/local-host'
ROOT=Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/root')
INTERFACE='product/lab/release-candidates/v1/interface'
MAPPER=INTERFACE+'/docker-mapped-20261020-0001'
ARCHIVE=INTERFACE+'/docker-source-20261020-0001/packages/0001/branch.snapshot'
STAGE_PLAN=LOCAL/'reader-only-unified-0006/stage-plan.json'
STAGE_PLAN_SHA='82ddcf898953881d49cfb1b99ba0b91f4f9c7393cfde5ae3bb9549b5a769e524'
FAMILY_FREEZE=LOCAL/'context-family-0001/freeze.json'
FAMILY_FREEZE_SHA='8ca69aca91aa114b0cd08660b2fffda605fed02ec408352eb8a16195ebc05797'
FAMILY_REVIEW=LOCAL/'CONTEXT-FAMILY-INDEPENDENT-STATIC-REVIEW-0001.md'
FAMILY_REVIEW_SHA='bd56faad04e691e37d93d6808decaf335c75876a08343ed0a22b3d9cc30731e0'
MAPPER_MANIFEST_SHA='0b3635dc9896034203e9e318ad99d58f2c37ca5acd419841d338f6ec9e4a1aea'
MAPPER_SOURCE_FILES={'__init__.py':'a88e78979e6f4ddfaf89055996e294a92987e42ca63526252a56defb8bc05362',
    'base.py':'9cdade5a637b09c95ab0111a0465aa71a0a7e2b3ef33d6118181e064dd72ad8a',
    'build.py':'855016aff7902452eb36308bd7a27fb262c59a0ef0cf533bbf0ad039fb735083',
    'policy.json':'1c2ddd360e56666fec0f4ff2095f32369705cff7b96edecbc5ba0720136457ab',
    'source-manifest.json':'0bd6696a1e33750bca01cdeae65d3a5ae977b433c0e0b608009422161b3c1358'}
MAX_FILE=4*1024*1024

class Refused(ValueError):pass
def require(ok,why):
    if not ok:raise Refused(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def safe_rel(name):
    require(type(name) is str and name and not name.startswith('/') and '\\' not in name and
            '//' not in name and PurePosixPath(name).as_posix()==name and
            all(x not in ('','.','..') for x in name.split('/')),'unsafe relative member')
    return name

def held_dir(path):
    """Open every absolute ancestor without following links; caller owns all FDs."""
    path=Path(path)
    require(path.is_absolute() and str(path)==path.as_posix(),'absolute directory required')
    fds=[]
    try:
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        fds.append(fd)
        for component in path.parts[1:]:
            fd=os.open(component,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
            fds.append(fd)
        return fds
    except BaseException:
        for fd in reversed(fds):os.close(fd)
        raise

def held_read(root,name,pin,limit=MAX_FILE,capture=False):
    safe_rel(name)
    require(name!=ARCHIVE,'protected archive body excluded from static stage')
    fds=held_dir(root)
    try:
        parent=fds[-1]
        for component in name.split('/')[:-1]:
            parent=os.open(component,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
            fds.append(parent)
        fd=os.open(name.split('/')[-1],os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        fds.append(fd)
        before=os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and
                0<=before.st_size<=limit,'bounded one-link regular member required')
        h=hashlib.sha256();total=0;parts=[]
        while True:
            chunk=os.read(fd,min(65536,before.st_size+1-total))
            if not chunk:break
            total+=len(chunk)
            require(total<=before.st_size,'member grew during read')
            h.update(chunk)
            if capture:parts.append(chunk)
        after=os.fstat(fd)
        require((before.st_dev,before.st_ino,before.st_mode,before.st_uid,before.st_gid,
                 before.st_nlink,before.st_size)==
                (after.st_dev,after.st_ino,after.st_mode,after.st_uid,after.st_gid,
                 after.st_nlink,after.st_size) and total==before.st_size and
                h.hexdigest()==pin,'member changed or digest differs')
        answer={'sha256':h.hexdigest(),'size':total,'mode':format(before.st_mode&0o777,'04o'),
                'uid':before.st_uid,'gid':before.st_gid,'dev':before.st_dev,'ino':before.st_ino}
        if capture:answer['bytes']=b''.join(parts)
        return answer
    finally:
        failures=[]
        for fd in reversed(fds):
            try:os.close(fd)
            except OSError as exc:failures.append(exc)
        if failures:raise Refused('member FD cleanup uncertain')

def held_stat(root,name):
    safe_rel(name)
    fds=held_dir(root)
    try:
        parent=fds[-1]
        for component in name.split('/')[:-1]:
            parent=os.open(component,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
            fds.append(parent)
        return os.stat(name.split('/')[-1],dir_fd=parent,follow_symlinks=False)
    finally:
        for fd in reversed(fds):os.close(fd)

def verify_inventory():
    # Metadata selectors are public and bounded; the archive row remains data only.
    plan_bytes=held_read(REPO,STAGE_PLAN.relative_to(REPO).as_posix(),STAGE_PLAN_SHA,capture=True)['bytes']
    held_read(REPO,FAMILY_FREEZE.relative_to(REPO).as_posix(),FAMILY_FREEZE_SHA)
    held_read(REPO,FAMILY_REVIEW.relative_to(REPO).as_posix(),FAMILY_REVIEW_SHA)
    plan=json.loads(plan_bytes)
    require(plan['archive_path']==ARCHIVE and len(plan['files'])==986 and
            len({x['path'] for x in plan['files']})==986 and
            plan['archive_body_opened'] is False,'Reader stage inventory differs')
    private=[x for x in plan['files'] if x['path']==ARCHIVE]
    require(len(private)==1 and private[0]['sha256']==
            '6d3cfc3f721b9be4fb8a1df14d4f43214709887213eaeae543927f214fdb9323',
            'protected archive reviewed binding differs')
    archive_stat=held_stat(ROOT,ARCHIVE)
    require(stat.S_ISREG(archive_stat.st_mode) and archive_stat.st_nlink==1 and
            archive_stat.st_size==23550300 and archive_stat.st_mode&0o777==0o600 and
            archive_stat.st_uid==os.geteuid() and archive_stat.st_gid==os.getegid(),
            'protected archive custody metadata differs')
    public=[]
    for row in plan['files']:
        if row['path']==ARCHIVE:continue
        observed=held_read(ROOT,row['path'],row['sha256'])
        require(observed['mode']==row['target_mode'] and observed['uid']==os.geteuid() and
                observed['gid']==os.getegid(),'Reader stage member mode/owner differs')
        public.append({'path':row['path'],'sha256':row['sha256'],'size':observed['size'],
                       'mode':observed['mode']})
    require(len(public)==985,'public Reader stage inventory incomplete')
    mapper_source=[]
    for name,pin in MAPPER_SOURCE_FILES.items():
        path=MAPPER+'/'+name
        observed=held_read(ROOT,path,pin)
        require(observed['mode']=='0444' and observed['uid']==os.geteuid() and
                observed['gid']==os.getegid(),'Mapper source mode/owner differs')
        mapper_source.append({'path':path,'sha256':pin,'size':observed['size'],'mode':observed['mode']})
    manifest_path=MAPPER+'/packages/0001/manifest.json'
    manifest_bytes=held_read(ROOT,manifest_path,MAPPER_MANIFEST_SHA,capture=True)['bytes']
    manifest=json.loads(manifest_bytes)
    require(len(manifest['files'])==54 and len({x['path'] for x in manifest['files']})==54,
            'Mapper package inventory differs')
    mapped=[]
    for row in manifest['files']:
        name=safe_rel(row['path'])
        require(name.startswith(MAPPER+'/packages/0001/') and name!=ARCHIVE,
                'Mapper package member escaped selected root')
        observed=held_read(ROOT,name,row['sha256'])
        require(observed['mode']=='0600' and observed['uid']==os.geteuid() and
                observed['gid']==os.getegid(),'Mapper package member mode/owner differs')
        mapped.append({'path':name,'sha256':row['sha256'],'size':observed['size'],'mode':observed['mode']})
    expected={x['path'] for x in plan['files']}|{x['path'] for x in mapper_source}|\
             {x['path'] for x in mapped}|{manifest_path}
    observed=set()
    for base,dirs,files in os.walk(ROOT,followlinks=False):
        for name in dirs+files:
            path=Path(base)/name
            info=path.lstat()
            require(stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode),
                    'selected family contains nonregular member')
            if stat.S_ISREG(info.st_mode):observed.add(path.relative_to(ROOT).as_posix())
    require(observed==expected and len(observed)==1046,'selected family file closure differs')
    return {'reader_stage_public':public,'reader_stage_protected_binding':
                {'path':ARCHIVE,'sha256':private[0]['sha256'],
                 'mode':private[0]['target_mode'],'size':archive_stat.st_size,
                 'body':'UNOPENED_UNCOPIED'},
            'mapper_source_files':mapper_source,
            'mapper_package_members':mapped,
            'mapper_package_manifest':{'path':manifest_path,'sha256':MAPPER_MANIFEST_SHA},
            'selected_family_total_files':len(observed),
            'copy_source_root':str(ROOT),'future_copy':'NOT_RUN'}

def copy_fake_public(source_root,target_root,row):
    """Causal disposable-fixture proof of the selected exclusive copy primitive."""
    name=safe_rel(row['path'])
    require(name!=ARCHIVE,'protected archive copy requires separate reviewed effect')
    for root in (Path(source_root),Path(target_root)):
        require(root.is_absolute() and root.parent.name.startswith('cal-context-stage-fake-') and
                root.parent.is_relative_to(Path('/tmp')) and root not in (ROOT,REPO),
                'fake-only copy root required')
    source_fds=held_dir(source_root);target_fds=held_dir(target_root)
    created=False;out_fd=None
    try:
        source_parent=source_fds[-1];target_parent=target_fds[-1]
        for part in name.split('/')[:-1]:
            source_parent=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=source_parent)
            source_fds.append(source_parent)
            target_parent=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=target_parent)
            target_fds.append(target_parent)
        leaf=name.split('/')[-1]
        source_fd=os.open(leaf,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=source_parent)
        source_fds.append(source_fd)
        a=os.fstat(source_fd)
        require(stat.S_ISREG(a.st_mode) and a.st_nlink==1 and a.st_size<=MAX_FILE,
                'copy input not bounded regular file')
        out_fd=os.open(leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,
                       int(row['mode'],8),dir_fd=target_parent)
        created=True;h=hashlib.sha256();count=0
        os.fchmod(out_fd,int(row['mode'],8))
        while True:
            chunk=os.read(source_fd,min(65536,a.st_size+1-count))
            if not chunk:break
            count+=len(chunk);require(count<=a.st_size,'copy input grew')
            h.update(chunk)
            view=memoryview(chunk)
            while view:
                n=os.write(out_fd,view)
                require(n>0,'copy output stalled')
                view=view[n:]
        os.fsync(out_fd)
        b=os.fstat(source_fd)
        require((a.st_dev,a.st_ino,a.st_mode,a.st_nlink,a.st_size)==
                (b.st_dev,b.st_ino,b.st_mode,b.st_nlink,b.st_size) and
                count==a.st_size and h.hexdigest()==row['sha256'],'copy source changed')
        os.close(out_fd);out_fd=None
        copied=held_read(target_root,name,row['sha256'])
        require(copied['mode']==row['mode'],'copy target mode differs')
        return count
    except BaseException:
        if out_fd is not None:os.close(out_fd)
        if created:
            try:os.unlink(name.split('/')[-1],dir_fd=target_fds[-1])
            except OSError:pass
        raise
    finally:
        for fd in reversed(target_fds+source_fds):os.close(fd)

def final_context_manifest(*_args,**_kwargs):raise Refused('protected stage, JIT pins and runtime import unresolved')
def launch_context(*_args,**_kwargs):raise Refused('effect-disabled Context stage candidate')

if __name__=='__main__':
    value=verify_inventory()
    print(json.dumps({'public_reader_files':len(value['reader_stage_public']),
                      'mapper_package_files':len(value['mapper_package_members'])+1,
                      'protected_body':value['reader_stage_protected_binding']['body'],
                      'context_launch':'REFUSED'},sort_keys=True))
