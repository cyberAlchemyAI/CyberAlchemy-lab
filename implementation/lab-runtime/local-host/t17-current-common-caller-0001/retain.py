"""Retain exact fixture Vault originals without retaining Reader credentials.

Trusted caller-only evidence custody. It neither grants permission nor revives
an original channel, Session, operation or historical Source capability.
"""
import hashlib
import json
import os
from pathlib import Path
import stat


def need(value,message):
    if not value:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def capture(path):
    need(not any(p.is_symlink() for p in path.parents),'linked retained input ancestor')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_size<=64*1024*1024,
             'bounded owned original required')
        chunks=[];size=0
        while block:=os.read(fd,1024*1024):
            chunks.append(block);size+=len(block);need(size<=before.st_size,'retained original grew')
        after=os.fstat(fd)
        stamp=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_uid,s.st_nlink)
        need(stamp(before)==stamp(after)==stamp(path.stat(follow_symlinks=False)) and size==before.st_size,
             'retained original changed during capture')
        raw=b''.join(chunks)
        need(b'PRIVATE KEY-----' not in raw,'credential material cannot enter retained Vault evidence')
        return raw
    finally:os.close(fd)


def write(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())


def archive(destination,vault,observation,*,native_inputs=None):
    destination=Path(destination).absolute();vault=Path(vault).absolute()
    need(not destination.exists() and not destination.is_symlink(),'fresh retained observation required')
    parent=destination.parent
    need(not parent.is_symlink() and parent.is_dir() and parent.stat().st_uid==os.getuid()
         and stat.S_IMODE(parent.stat().st_mode)==0o700,'private retained parent required')
    need(vault.is_relative_to(Path('/tmp')) and not vault.is_symlink() and vault.is_dir()
         and vault.stat().st_uid==os.getuid() and stat.S_IMODE(vault.stat().st_mode)==0o700,
         'actual owned private fixture Vault required')
    destination.mkdir(mode=0o700);target=destination/'vault';target.mkdir(mode=0o700)
    rows=[]
    for path in sorted(vault.rglob('*')):
        relative=path.relative_to(vault)
        need(not path.is_symlink(),'linked original cannot be archived')
        if path.is_dir():(target/relative).mkdir(mode=0o700)
        else:
            raw=capture(path);write(target/relative,raw)
            rows.append({'path':'vault/'+relative.as_posix(),'sha256':sha(raw),'size_bytes':len(raw)})
    # The fixture reader.pem belongs outside the Vault. Never copy its parent
    # policy directory or infer a new live channel from this archive.
    if native_inputs:
        folder=destination/'native-inputs';folder.mkdir(mode=0o700)
        for name,path in native_inputs.items():
            need(Path(name).name==name and name not in ('.','..'),'closed native input name required')
            raw=capture(Path(path));write(folder/name,raw)
            rows.append({'path':'native-inputs/'+name,'sha256':sha(raw),'size_bytes':len(raw)})
    # A timer or another writer invalidates a mixed snapshot; a retained partial
    # folder is diagnostic evidence, never a completed observation receipt.
    for row in rows:
        source=vault/Path(row['path']).relative_to('vault') if row['path'].startswith('vault/') else Path(native_inputs[Path(row['path']).name])
        need(sha(capture(source))==row['sha256'],'original changed before archive seal')
    actual={p.relative_to(vault).as_posix() for p in vault.rglob('*') if p.is_file()}
    need(actual=={r['path'][len('vault/'):] for r in rows if r['path'].startswith('vault/')},
         'Vault inventory changed before archive seal')
    value={'schema_version':'lab-retained-actual-caller-vault/v1','observation':observation,
        'original_vault_path':str(vault),'files':rows,'Reader_credentials_retained':False,
        'current_permission_or_Session_reconstructed':False,'requires_unit_terminal_PASS':True,'authority_effect':'none'}
    raw=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    write(destination/'OBSERVATION.json',raw)
    directory=os.open(destination,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(directory)
    finally:os.close(directory)
    return {'path':str(destination),'observation_sha256':sha(raw),'original_file_count':len(rows)}
