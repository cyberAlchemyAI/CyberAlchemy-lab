"""Materialize exact public ABI bytes with a fresh actual directory attestation."""
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import uuid


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()


def identity(path):
    info = Path(path).lstat()
    need(stat.S_ISDIR(info.st_mode),'native root is not a regular directory')
    return [info.st_dev,info.st_ino,info.st_uid,stat.S_IMODE(info.st_mode)]


def safe_root(path):
    path = Path(path)
    need(path.is_absolute() and path.as_posix()==str(path) and '..' not in path.parts,
         'closed absolute native root required')
    for ancestor in (path,*path.parents):
        need(stat.S_ISDIR(ancestor.lstat().st_mode),'native root ancestry linked or missing')
    need(identity(path)[2:]==[os.getuid(),0o700],'owned private native parent required')
    return path


def relative(value):
    need(type(value) is str and value and '\\' not in value and '\0' not in value,
         'closed native member locator required')
    path = Path(value)
    need(not path.is_absolute() and path.as_posix()==value and '..' not in path.parts
         and value not in ('.','installation.json'),'canonical native payload locator required')
    return path


def validate_members(members):
    need(type(members) is dict and len(members)==1010,'exact original1010 native members required')
    for name,row in members.items():
        relative(name)
        need(type(row) is dict and set(row)=={'sha256','size_bytes','mode'}
             and type(row['sha256']) is str and len(row['sha256'])==64
             and all(ch in '0123456789abcdef' for ch in row['sha256'])
             and type(row['size_bytes']) is int and row['size_bytes']>=0
             and type(row['mode']) is int and 0<=row['mode']<=0o777,
             'closed exact native member metadata required')


def exact_file(path, row):
    # This helper reads only explicitly selected payload paths, never a global
    # repository or home-directory walk.
    path = Path(path)
    for parent in path.parents:
        need(stat.S_ISDIR(parent.lstat().st_mode),'native payload linked ancestor')
    fd = os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size==row['size_bytes']
             and stat.S_IMODE(before.st_mode)==row['mode'],'native payload file metadata differs')
        chunks = []
        while block := os.read(fd,1024*1024):
            chunks.append(block)
        raw = b''.join(chunks)
        stamp = lambda info:(info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns,info.st_mode)
        need(stamp(before)==stamp(os.fstat(fd))==stamp(path.lstat())
             and len(raw)==row['size_bytes'] and sha(raw)==row['sha256'],
             'native payload bytes or attachment changed')
        return raw
    finally:
        os.close(fd)


def write_new(path, raw, mode):
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    fd = os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
    try:
        os.fchmod(fd,mode)
        view = memoryview(raw)
        while view:
            count = os.write(fd,view)
            need(count>0,'native payload short write')
            view = view[count:]
        os.fsync(fd)
    finally:
        os.close(fd)


def publish(stage, destination):
    libc = ctypes.CDLL(None,use_errno=True)
    rename = getattr(libc,'renameat2',None)
    need(rename is not None,'atomic no-replace directory publication unavailable')
    rename.argtypes = [ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-100,os.fsencode(stage),-100,os.fsencode(destination),1):
        code = ctypes.get_errno()
        raise OSError(code,os.strerror(code),str(destination))


def verify(destination, members, selection_sha256):
    validate_members(members)
    destination = safe_root(destination)
    for name,row in members.items():
        exact_file(destination/relative(name),row)
    actual = set()
    for directory,subdirs,names in os.walk(destination,followlinks=False):
        for name in subdirs+names:
            need(not (Path(directory)/name).is_symlink(),'unexpected native payload link')
        for name in names:
            actual.add((Path(directory)/name).relative_to(destination).as_posix())
    need(actual==set(members)|{'installation.json'},'native installed file set differs')
    receipt_path = destination/'installation.json'
    info = receipt_path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid()
         and stat.S_IMODE(info.st_mode)==0o600,'native receipt ownership differs')
    raw = receipt_path.read_bytes()
    receipt = json.loads(raw)
    need(set(receipt)=={'schema','identity','selection_sha256','file_count','payload_manifest_sha256'}
         and receipt['schema']=='cal-clean-installed-native-runtime/v1'
         and receipt['identity']==identity(destination)
         and receipt['selection_sha256']==selection_sha256 and receipt['file_count']==1010
         and receipt['payload_manifest_sha256']==sha(encoded(members)),
         'native actual installation attestation differs')
    return {'path':str(receipt_path),'sha256':sha(raw),'identity':identity(destination),'files':1010}


def install(private_root, payload_root, members, selection_sha256):
    validate_members(members)
    private_root = safe_root(private_root)
    payload_root = safe_root(payload_root)
    destination = private_root/'native'
    need(not destination.exists() and not destination.is_symlink(),'native destination already exists')
    before = identity(private_root)
    stage = private_root/('.native-stage-'+uuid.uuid4().hex)
    stage.mkdir(mode=0o700)
    published = False
    try:
        for name,row in sorted(members.items()):
            raw = exact_file(payload_root/relative(name),row)
            write_new(stage/name,raw,row['mode'])
        receipt = {'schema':'cal-clean-installed-native-runtime/v1','identity':identity(stage),
                   'selection_sha256':selection_sha256,'file_count':1010,
                   'payload_manifest_sha256':sha(encoded(members))}
        write_new(stage/'installation.json',encoded(receipt),0o600)
        verify(stage,members,selection_sha256)
        need(identity(private_root)==before,'native destination parent changed')
        publish(stage,destination)
        published = True
        fd = os.open(private_root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        return verify(destination,members,selection_sha256)
    finally:
        if not published and stage.exists():
            shutil.rmtree(stage)


def cold_abi(destination):
    destination = safe_root(destination)
    code = """import importlib.metadata,json,platform,sys
sys.path.insert(0,sys.argv[1])
value={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
if value!={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}:raise ValueError('fresh installed ABI differs')
print(json.dumps({'result':'PASS','environment':value,'bytecode_disabled':sys.dont_write_bytecode},sort_keys=True))
"""
    command = [str(destination/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache',
               '--library-path',str(destination/'lib/abi'),str(destination/'bin/python'),
               '-I','-B','-S','-c',code,str(destination/'deps')]
    child = subprocess.run(command,stdin=subprocess.DEVNULL,capture_output=True,timeout=30,
                           env={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1','HOME':str(destination.parent)},check=False)
    need(child.returncode==0,'fresh native ABI cold process failed')
    value = json.loads(child.stdout)
    need(value['result']=='PASS' and value['bytecode_disabled'] is True,'fresh ABI cold result differs')
    return value
