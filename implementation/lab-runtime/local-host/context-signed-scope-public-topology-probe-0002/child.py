"""Public synthetic mount probe only; injected as checked Python -c bytes."""
from __future__ import annotations
import errno
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import stat
import sys
import time

STAGE=Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-stage-attempt/root')
BUNDLE=Path('/bundle')
CLAIM=Path('/control/attempt.claim')
MARKER='.public-topology-only'
TARGETS=(str(STAGE),str(BUNDLE),str(CLAIM))

def need(ok,code):
    if not ok:raise RuntimeError(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read_bounded(path,maximum,read_fn=os.read,open_fn=os.open,
                 close_fn=os.close,clock_fn=time.monotonic,
                 max_calls=4096,max_seconds=2.0):
    need(type(maximum) is int and 0<maximum<=128*1024 and
         type(max_calls) is int and 0<max_calls<=4096 and
         type(max_seconds) in (int,float) and 0<max_seconds<=2.0,
         'PUBLIC_READ_LIMITS')
    fd=open_fn(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
    try:
        start=clock_fn();parts=[];total=0;calls=0
        while True:
            need(calls<max_calls and clock_fn()-start<=max_seconds,
                 'PUBLIC_READ_INCOMPLETE')
            block=read_fn(fd,min(65536,maximum-total+1))
            calls+=1
            need(clock_fn()-start<=max_seconds,'PUBLIC_READ_INCOMPLETE')
            need(type(block) is bytes,'PUBLIC_READ_TYPE')
            if not block:break
            total+=len(block)
            need(total<=maximum,'PUBLIC_READ_BOUND')
            parts.append(block)
        need(total>0,'PUBLIC_READ_BOUND')
        return b''.join(parts)
    finally:close_fn(fd)

def mountinfo_ro(raw):
    need(type(raw) is bytes and 0<len(raw)<=128*1024,'MOUNTINFO_BOUND')
    rows=[]
    try:
        for line in raw.decode('ascii').splitlines():
            head,_=line.split(' - ',1)
            fields=head.split(' ')
            need(len(fields)>=6,'MOUNTINFO_SHAPE')
            rows.append((fields[4],set(fields[5].split(','))))
    except (UnicodeError,ValueError) as exc:
        raise RuntimeError('MOUNTINFO_SHAPE') from exc
    for target in TARGETS:
        matches=[options for path,options in rows if path==target]
        need(len(matches)==1 and 'ro' in matches[0] and 'rw' not in matches[0],
             'THREE_VFS_READ_ONLY_BINDS')
        need(not any(path.startswith(target+'/') for path,_ in rows),
             'NESTED_MOUNT_UNDER_PROBE_TARGET')
    return sha(raw)

def erofs_create(path,open_fn=os.open,exists_fn=os.path.lexists):
    need(not exists_fn(path),'SENTINEL_PREEXISTS')
    try:
        fd=open_fn(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    except OSError as exc:
        need(exc.errno==errno.EROFS and not exists_fn(path),'EROFS_CREATE')
        return errno.EROFS
    os.close(fd)
    raise RuntimeError('WRITABLE_PROBE_BIND')

def erofs_claim_write(open_fn=os.open):
    try:
        fd=open_fn(CLAIM,os.O_WRONLY|os.O_NOFOLLOW)
    except OSError as exc:
        need(exc.errno==errno.EROFS,'EROFS_CLAIM')
        return errno.EROFS
    os.close(fd)
    raise RuntimeError('WRITABLE_CLAIM_BIND')

def verify_claim(claim_stat,claim_marker,config):
    need(stat.S_ISREG(claim_stat.st_mode) and
         type(config['claim_dev']) is int and type(config['claim_ino']) is int and
         (claim_stat.st_dev,claim_stat.st_ino)==
         (config['claim_dev'],config['claim_ino']),
         'HELD_PUBLIC_CLAIM_IDENTITY')
    need(sha(claim_marker)==config['claim_marker_sha256'] and
         claim_marker==b'public-only signed-scope topology claim; no authority\n',
         'HELD_PUBLIC_CLAIM_MARKER')

def run(config):
    need(type(config) is dict and set(config)==
         {'stage_marker_sha256','claim_marker_sha256','claim_dev','claim_ino'} and
         type(config['stage_marker_sha256']) is str and
         type(config['claim_marker_sha256']) is str and
         len(config['stage_marker_sha256'])==64 and
         len(config['claim_marker_sha256'])==64 and
         type(config['claim_dev']) is int and config['claim_dev']>0 and
         type(config['claim_ino']) is int and config['claim_ino']>0,
         'PUBLIC_PROBE_CONFIG')
    need((os.getuid(),os.getgid())==(1000,1000),'CHILD_UID_GID')
    need(sys.version_info[:3]==(3,14,4) and
         importlib.metadata.version('jsonschema')=='4.23.0' and
         importlib.metadata.version('cryptography')=='46.0.5',
         'CHILD_DEPENDENCY_VERSIONS')
    need(set(os.listdir(STAGE))=={MARKER},'SYNTHETIC_STAGE_ONLY')
    stage_marker=read_bounded(STAGE/MARKER,1024)
    need(sha(stage_marker)==config['stage_marker_sha256'] and
         stage_marker==b'public-only signed-scope topology stage; no private archive\n',
         'SYNTHETIC_STAGE_MARKER')
    need(set(os.listdir(BUNDLE))=={'manifest.json','blobs'},
         'PUBLIC_BUNDLE_ROOT')
    claim_stat=os.stat(CLAIM,follow_symlinks=False)
    claim_marker=read_bounded(CLAIM,1024)
    verify_claim(claim_stat,claim_marker,config)
    mount_sha=mountinfo_ro(read_bounded('/proc/self/mountinfo',128*1024))
    need(erofs_create(STAGE/'.public-probe-write')==errno.EROFS and
         erofs_create(BUNDLE/'.public-probe-write')==errno.EROFS and
         erofs_claim_write()==errno.EROFS,'PROBE_READ_ONLY')
    return {'schema':'context-signed-scope-public-three-bind-child/v1',
            'status':'PUBLIC_SYNTHETIC_TOPOLOGY_ONLY',
            'stage_marker_sha256':sha(stage_marker),
            'claim_marker_sha256':sha(claim_marker),
            'claim_dev':claim_stat.st_dev,'claim_ino':claim_stat.st_ino,
            'mountinfo_sha256':mount_sha,'erofs_errno':errno.EROFS,
            'python':'3.14.4','jsonschema':'4.23.0',
            'cryptography':'46.0.5','private_archive':'ABSENT',
            'signed_scope':'NOT_OPENED'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==2,'CHILD_ARGV')
        result=run(json.loads(sys.argv[1]))
        sys.stdout.write(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
    except BaseException:
        sys.stderr.write('PUBLIC_TOPOLOGY_UNKNOWN\n')
        raise SystemExit(1) from None
