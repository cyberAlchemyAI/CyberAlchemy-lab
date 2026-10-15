"""Pinned authoritative bindings and explicitly authorized documentary captures."""
from pathlib import Path
import hashlib
import json
import re

BASE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in BASE.parents if (p/'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())
FORMAL=BASE.parent/'v1/formal'
COMPILER_ROOT=FORMAL/'.toolcache/lean-4.33.1-linux'


def require(condition,message):
    if not condition:raise ValueError(message)
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def repo(path):
    p=Path(path).resolve();require(p.is_relative_to(ROOT),'outside repository')
    return {'kind':'repo','path':str(p.relative_to(ROOT)),'sha256':digest(p)}
def legacy(ref):return {'kind':'repo','path':ref['path'],'sha256':ref['sha256']}
def plain(ref):return {k:ref[k] for k in ['path','sha256']}


class Resolver:
    def __init__(self,compiler_root=COMPILER_ROOT):
        self.compiler_root=Path(compiler_root).resolve()
        require(self.compiler_root==COMPILER_ROOT.resolve(),'alternate toolchain root rejected')
        self.lock_path=FORMAL/'toolchain-lock.json'
        lock=json.loads(self.lock_path.read_text());self.toolchain_identity=digest(self.lock_path)
        require(digest(self.compiler_root/'bin/lean')==lock['lean_binary_sha256'],'compiler pin drift')
        require(digest(self.compiler_root/'lib/lean/libleanshared.so')==lock['lean_shared_library_sha256'],'kernel pin drift')
        self.memo={};self.hashes=0;self.hits=0

    def locate(self,ref):
        kind=ref.get('kind')
        expected={'kind','path','sha256'} if kind=='repo' else {'kind','path','sha256','toolchain_identity'}
        require(kind in ['repo','toolchain'] and set(ref)==expected,'invalid authoritative binding fields')
        relative=Path(ref['path'])
        require(isinstance(ref['path'],str) and not relative.is_absolute() and '..' not in relative.parts and '\\' not in ref['path'],'unsafe binding path')
        require(re.fullmatch('[0-9a-f]{64}',ref['sha256']) is not None,'invalid binding digest')
        if kind=='toolchain':
            require(ref['toolchain_identity']==self.toolchain_identity and ref['path'].startswith('lib/lean/'),'toolchain identity/path mismatch')
            path=(self.compiler_root/relative).resolve()
            require(path.is_relative_to(self.compiler_root),'toolchain path escape')
        else:
            path=(ROOT/relative).resolve();require(path.is_relative_to(ROOT),'repository symlink escape')
        return path

    def check(self,ref):
        path=self.locate(ref)
        require(path.is_file(),'missing authoritative artifact '+str(path))
        stat=path.stat();stamp=(stat.st_ino,stat.st_size,stat.st_mtime_ns)
        key=(str(path),ref['sha256'])
        if self.memo.get(key)==stamp:self.hits+=1;return path
        self.hashes+=1
        require(digest(path)==ref['sha256'],'stale authoritative artifact '+str(path))
        self.memo[key]=stamp;return path

    def toolchain(self,relative,sha):
        ref={'kind':'toolchain','toolchain_identity':self.toolchain_identity,'path':relative,'sha256':sha}
        self.check(ref);return ref

    def documentary(self,entry,allowed):
        require(set(entry)=={'kind','id','description','capture'},'invalid documentary shape')
        require(entry['kind']=='documentary' and entry in allowed,'unauthorized documentary relabeling')
        self.check(entry['capture'])
        return {'id':entry['id'],'description':entry['description'],'capture':entry['capture'],'qualification_dependency':False}
