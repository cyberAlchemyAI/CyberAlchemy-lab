"""Bounded captured SDK loader with real selected source origins and fresh guards."""
import base64,hashlib,importlib.abc,importlib.util,json,os,re,sys
from pathlib import Path,PurePosixPath
import stat
MAX_BUNDLE=2*1024*1024
MODULES={'bootstrap','control','framing','composite'}
def need(value):
    if not value:raise ValueError('captured SDK selection differs')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def _capture_exact(root, binding):
    """Capture <=64 MiB with exact SHA and fresh complete attachment checks."""
    def require(value, reason):
        if not value:
            raise ValueError(reason)
    require(type(binding) is dict and set(binding) == {'path', 'sha256'}, 'closed exact capture binding required')
    name = binding['path']
    require(type(name) is str and bool(name) and '\\' not in name and '\x00' not in name,
            'unsafe capture path')
    path = PurePosixPath(name)
    require(path.as_posix() == name and '..' not in path.parts and name not in ('.', '/'), 'unsafe capture path')
    require(type(binding['sha256']) is str and re.fullmatch('[a-f0-9]{64}', binding['sha256']),
            'independent capture digest required')
    root = Path(root)
    require(root.is_absolute() and '..' not in root.parts, 'absolute capture root required')
    if not path.is_absolute():
        path = PurePosixPath(root.as_posix()) / path
    parts = path.parts[1:]
    directories = []
    file_handle = None
    links = []
    def identity(value):
        return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid,
                value.st_nlink, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        directories.append(parent)
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=parent)
            directories.append(child)
            info = os.fstat(child)
            require(stat.S_ISDIR(info.st_mode) and info.st_mode & 0o111, 'unsafe capture ancestor')
            attached = os.stat(part, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISDIR(attached.st_mode) and (attached.st_dev, attached.st_ino) ==
                    (info.st_dev, info.st_ino), 'capture ancestor changed during open')
            links.append((parent, part, child, info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid))
            parent = child
        file_handle = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                              dir_fd=parent)
        before = os.fstat(file_handle)
        require(stat.S_ISREG(before.st_mode) and before.st_mode & 0o444, 'regular readable capture required')
        require(before.st_size <= 64 * 1024 * 1024, 'capture metadata exceeds 64 MiB')
        size = 0
        digest = hashlib.sha256()
        chunks = []
        while True:
            chunk = os.read(file_handle, min(1024 * 1024, 64 * 1024 * 1024 - size + 1))
            if not chunk:
                break
            size += len(chunk)
            require(size <= 64 * 1024 * 1024, 'capture metadata grew beyond 64 MiB')
            digest.update(chunk)
            chunks.append(chunk)
        after = os.fstat(file_handle)
        attached = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(attached.st_mode) and size == before.st_size and
                identity(before) == identity(after) == identity(attached), 'capture file identity changed')
        require(digest.hexdigest() == binding['sha256'], 'capture digest differs')
        for ancestor, part, held, device, inode, mode, uid, gid in reversed(links):
            value = os.stat(part, dir_fd=ancestor, follow_symlinks=False)
            held_value = os.fstat(held)
            require(stat.S_ISDIR(value.st_mode) and
                    (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid) ==
                    (held_value.st_dev, held_value.st_ino, held_value.st_mode, held_value.st_uid, held_value.st_gid) ==
                    (device, inode, mode, uid, gid), 'capture ancestor attachment changed')
        require(identity(os.fstat(file_handle)) == identity(os.stat(parts[-1], dir_fd=parent,
                follow_symlinks=False)) == identity(before), 'capture file changed before return')
        return b''.join(chunks)
    except OSError as error:
        raise ValueError('capture unsafe/unreadable/missing attachment') from error
    finally:
        if file_handle is not None:
            os.close(file_handle)
        for handle in reversed(directories):
            os.close(handle)

class CapturedLoader(importlib.abc.SourceLoader):
    def __init__(self,name,path,raw,digest,root):self.name=name;self.path=path;self.raw=raw;self.digest=digest;self.root=root
    def get_filename(self,fullname):need(fullname==self.name);return self.path
    def get_data(self,path):
        need(path==self.path);need(_capture_exact(self.root,{'path':path,'sha256':self.digest})==self.raw);return self.raw
    def get_code(self,fullname):
        self.get_data(self.get_filename(fullname));return compile(self.raw,self.path,'exec',dont_inherit=True)
    def get_source(self,fullname):return self.get_data(self.get_filename(fullname)).decode('utf-8')
class CapturedFinder(importlib.abc.MetaPathFinder):
    def __init__(self,payload,root):self.payload=payload;self.root=root
    def find_spec(self,fullname,path=None,target=None):
        if fullname not in MODULES-{'bootstrap'}:return None
        value=self.payload[fullname];raw=base64.b64decode(value['source_base64'],validate=True)
        loader=CapturedLoader(fullname,value['path'],raw,value['sha256'],self.root)
        return importlib.util.spec_from_file_location(fullname,value['path'],loader=loader)
def verify(payload):
    need(type(payload) is dict and set(payload)=={'schema_version','root','modules','manifest'})
    need(payload['schema_version']=='lab-captured-SDK-bootstrap/v1-candidate' and set(payload['modules'])==MODULES)
    here=Path(__file__).parent;root=here.parents[6];need(payload['root']==str(here))
    binding=payload['manifest'];need(set(binding)=={'path','sha256','source_base64'} and binding['path']==str(here/'source-manifest.json'))
    raw=base64.b64decode(binding['source_base64'],validate=True);need(sha(raw)==binding['sha256'] and _capture_exact(root,{'path':binding['path'],'sha256':binding['sha256']})==raw)
    manifest=json.loads(raw);need(manifest['authority_effect']=='none' and manifest['schema_version']=='lab-T06-task-local-source/v3-candidate')
    rows={row['path']:row for row in manifest['files']};need(len(rows)==len(manifest['files']))
    for row in manifest['files']:_capture_exact(root,{'path':row['path'],'sha256':row['sha256']})
    for name,value in payload['modules'].items():
        need(set(value)=={'path','sha256','source_base64'} and value['path']==str(here/(name+'.py')))
        expected=rows[str(Path(value['path']).relative_to(root))];body=base64.b64decode(value['source_base64'],validate=True)
        need(len(body)<=1024*1024 and sha(body)==value['sha256']==expected['sha256'] and len(body)==expected['size_bytes'])
    return root
def run(payload,args):
    root=verify(payload)
    need(all(name not in sys.modules for name in MODULES-{'bootstrap'}))
    here=Path(__file__).parent;install=here.parents[1]/'runtime-dependencies-v2-completion-0001/installations/0004'
    sys.path.insert(0,str(install/'deps'))
    finder=CapturedFinder(payload['modules'],root);sys.meta_path.insert(0,finder)
    try:
        # Only captured SDK modules use this explicit loader. API/branch imports,
        # schemas, clocks, authentication and source guards remain original.
        from composite import main
        sys.argv=[str(here/'composite.py'),*args]
        result=main();verify(payload);return result
    finally:sys.meta_path.remove(finder)
