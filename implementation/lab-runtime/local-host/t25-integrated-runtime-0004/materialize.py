"""Materialize an exact public repository closure into a fresh owned root.

Input paths are installer inputs, never API wire configuration. Host snapshots
remain data in a separate directory until a private namespace installs them.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda value:(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def need(value,reason):
    if not value:raise ValueError(reason)
def relative(value):
    p=Path(value)
    need(type(value)is str and value and p.as_posix()==value and not p.is_absolute() and '..'not in p.parts and '\\'not in value,'closed materialization path required')
    return p
def exact(path,row):
    path=Path(path);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size==row['size_bytes'],'selected materialization source size/type differs: '+str(path))
        need(stat.S_IMODE(before.st_mode)==row['mode'],'selected materialization source mode differs: '+str(path))
        chunks=[]
        while block:=os.read(fd,1024*1024):chunks.append(block)
        raw=b''.join(chunks);after=os.fstat(fd)
        stamp=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mode,s.st_mtime_ns,s.st_ctime_ns)
        need(stamp(before)==stamp(after)==stamp(path.lstat()),'materialization source changed during capture')
        need(sha(raw)==row['sha256'],'selected materialization source bytes differ: '+str(path))
        return raw
    finally:os.close(fd)
def owned_directory(path):
    path=Path(path)
    need(path.is_absolute() and '..'not in path.parts,'absolute materialization destination required')
    cur=Path('/')
    for part in path.parts[1:]:
        cur/=part
        if not cur.exists():cur.mkdir(mode=0o700)
        info=cur.lstat();need(stat.S_ISDIR(info.st_mode),'linked/non-directory materialization ancestor')
    info=path.lstat();need(info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o700,'owned private materialization directory required')
    return path
def write_new(path,raw,mode):
    path=Path(path);owned_directory(path.parent)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,'wb',closefd=False) as out:out.write(raw);out.flush();os.fsync(fd)
        os.fchmod(fd,mode)
    finally:os.close(fd)
def materialize(view,repository):
    view=Path(view);repository=owned_directory(repository)
    need(not any(repository.iterdir()),'refuse nonempty repository destination')
    manifest_raw=(view/'PACKAGE-MANIFEST.json').read_bytes();manifest=json.loads(manifest_raw)
    inputs=json.loads((view/'BUILD-INPUTS.json').read_bytes())
    need(inputs['package_manifest_sha256']==sha(manifest_raw),'package assembly selection differs')
    rows={row['path']:row for row in manifest['members']}
    need(len(rows)==len(manifest['members']) and set(rows)==set(inputs['repository_inputs']),'package assembly member set differs')
    completed=0
    for name,row in sorted(rows.items()):
        rel=relative(name);source=inputs['repository_inputs'][name]
        need(all(source[key]==row[key] for key in ('sha256','size_bytes','mode')),'assembly input descriptor differs')
        raw=exact(source['input_path'],row)
        write_new(repository/rel,raw,row['mode']);completed+=1
        if completed%5000==0:print(json.dumps({'copied_repository_members':completed}),flush=True)
    write_new(repository/'.cal-package-manifest.json',manifest_raw,0o644)
    return {'result':'PASS-public-repository-materialization','package_manifest_sha256':sha(manifest_raw),'repository_members':completed,'repository':str(repository),'host_namespace_materialized':False,'API_qualified':False,'authority_effect':'none'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('view',type=Path);p.add_argument('repository',type=Path);a=p.parse_args();print(json.dumps(materialize(a.view,a.repository),sort_keys=True),flush=True)
