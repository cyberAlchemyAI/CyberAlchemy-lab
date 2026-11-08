"""Closed private installation inputs selected before any runtime import.

This module is trusted bootstrap code. API messages cannot activate a selection
or supply its paths, pins, native identity or Source/Context bindings.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
from types import MappingProxyType

ROOT = Path(__file__).resolve().parents[4]
PRIVATE = ROOT.parent / '.cal-runtime'
_ACTIVE = None
_MINT = object()
BINDINGS = frozenset(('api.source','api.profile','family.source','family.source_package',
    'family.reader_source','family.reader_package','family.mapper_source','family.mapper_package',
    'family.mapping','family.context_source','family.context_package','family.delivery',
    'family.period','family.record_index','family.archive_handle','family.context_native_role','family.cold',
    'engine.profile','engine.manifest','engine.loader','engine.pins'))
VALUES = frozenset(('identity.family','identity.store','identity.source_name','identity.scope',
    'native.root','native.identity','native.receipt','native.dependency_selection',
    'archive.path','archive.sha256','period.not_before','period.expires_at'))
CONSTRUCTION_REQUIRED = frozenset(('family.source','family.source_package',
    'family.period','family.record_index','family.archive_handle','family.context_native_role',
    'engine.profile','engine.manifest','engine.loader','engine.pins'))


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',', ':'),allow_nan=False).encode()


def freeze_package(value):
    """Own immutable JSON containers; mutable backing dictionaries never escape."""
    if type(value) is dict:
        return MappingProxyType({key:freeze_package(item) for key,item in value.items()})
    if type(value) is list:
        return tuple(freeze_package(item) for item in value)
    need(value is None or type(value) in (str,int,float,bool),'public package must contain JSON scalars only')
    return value


def parse(raw):
    def pairs(rows):
        value = {}
        for key,item in rows:
            need(key not in value, 'duplicate installed selection key')
            value[key] = item
        return value
    return json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda _:need(False,'nonfinite installed selection'))


def closed(value, names, reason):
    need(type(value) is dict and set(value)==set(names),reason)


def relative(value):
    need(type(value) is str and value and '\\' not in value and '\0' not in value,
         'closed installed relative locator required')
    path = Path(value)
    need(not path.is_absolute() and path.as_posix()==value and '..' not in path.parts
         and value!='.', 'canonical installed relative locator required')
    return path


def identity(path):
    value = Path(path).lstat()
    need(stat.S_ISDIR(value.st_mode),'installed directory is missing or linked')
    return [value.st_dev,value.st_ino,value.st_uid,stat.S_IMODE(value.st_mode)]


def verify_native_receipt(raw, expected_identity, selection_sha256):
    value = parse(raw)
    closed(value,('schema','identity','selection_sha256','file_count','payload_manifest_sha256'),
           'closed fresh native receipt required')
    need(value['schema']=='cal-clean-installed-native-runtime/v1'
         and value['identity']==expected_identity and value['selection_sha256']==selection_sha256
         and value['file_count']==1010,'native receipt body identity or selection differs')
    return value


def capture(path, digest, *, private=False, limit=64*1024*1024):
    """Read a bounded exact file through no-follow ancestor descriptors."""
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts,'absolute installed capture required')
    handles = []
    links = []
    fd = None
    stamp = lambda value:(value.st_dev,value.st_ino,value.st_mode,value.st_uid,
                         value.st_size,value.st_mtime_ns,value.st_ctime_ns)
    try:
        parent = os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        handles.append(parent)
        for part in path.parts[1:-1]:
            child = os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            value = os.fstat(child)
            links.append((parent,part,child,value.st_dev,value.st_ino))
            handles.append(child)
            parent = child
        fd = os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size<=limit,'bounded installed regular file required')
        if private:
            need(before.st_uid==os.getuid() and stat.S_IMODE(before.st_mode)==0o600,
                 'installed control file owner/mode differs')
        chunks = []
        size = 0
        while block := os.read(fd,1024*1024):
            size += len(block)
            need(size<=limit,'installed control file grew beyond limit')
            chunks.append(block)
        raw = b''.join(chunks)
        need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False))
             and size==before.st_size and sha(raw)==digest,'installed selected bytes changed')
        for parent,name,child,device,inode in reversed(links):
            current = os.stat(name,dir_fd=parent,follow_symlinks=False)
            held = os.fstat(child)
            need(stat.S_ISDIR(current.st_mode) and (current.st_dev,current.st_ino)==(held.st_dev,held.st_ino)==(device,inode),
                 'installed ancestor attachment changed')
        return raw
    finally:
        if fd is not None:
            os.close(fd)
        for handle in reversed(handles):
            os.close(handle)


class PackageFileSeal:
    """Exact full capture once; fresh descriptor/name metadata at every use.

    Byte writes (including restored mtime), chmod, inode replacement and
    ancestor detachment invalidate the seal. Source/policy/native data retain
    their own fresh physical byte verification at original boundaries.
    """
    __slots__=('handles','links','leaf','parent','name','stamp')
    @staticmethod
    def stamp_of(value):
        return (value.st_dev,value.st_ino,value.st_mode,value.st_uid,value.st_gid,
                value.st_nlink,value.st_size,value.st_mtime_ns,value.st_ctime_ns)
    @staticmethod
    def directory_of(value):
        return (value.st_dev,value.st_ino,value.st_mode,value.st_uid,value.st_gid)
    def __init__(self,path,digest):
        handles=[];links=[]
        try:
            path=Path(path);parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            handles.append(parent)
            for part in path.parts[1:-1]:
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
                handles.append(child);info=os.fstat(child)
                need(stat.S_ISDIR(info.st_mode),'package seal ancestor differs')
                links.append((parent,part,child,self.directory_of(info)));parent=child
            leaf=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
            handles.append(leaf);before=os.fstat(leaf)
            need(stat.S_ISREG(before.st_mode) and before.st_size<=64*1024*1024,'bounded package seal file required')
            calculated=hashlib.sha256();size=0
            while block:=os.read(leaf,1024*1024):
                calculated.update(block);size+=len(block);need(size<=before.st_size,'package seal capture grew')
            need(size==before.st_size and calculated.hexdigest()==digest,'package seal initial bytes differ')
            for name,value in (('handles',tuple(handles)),('links',tuple(links)),('leaf',leaf),
                               ('parent',parent),('name',path.name),('stamp',self.stamp_of(before))):
                object.__setattr__(self,name,value)
            self.guard()
        except BaseException:
            for handle in reversed(handles):os.close(handle)
            raise
    def __setattr__(self,name,value):raise AttributeError('package descriptor seal is immutable')
    def guard(self):
        try:
            need(self.stamp_of(os.fstat(self.leaf))==self.stamp
                 and self.stamp_of(os.stat(self.name,dir_fd=self.parent,follow_symlinks=False))==self.stamp,
                 'stable package manifest descriptor/name stamp changed')
            for ancestor,name,held,expected in self.links:
                need(self.directory_of(os.fstat(held))==expected
                     and self.directory_of(os.stat(name,dir_fd=ancestor,follow_symlinks=False))==expected,
                     'stable package manifest ancestor attachment changed')
            need(self.stamp_of(os.fstat(self.leaf))==self.stamp,'stable package manifest changed before guard exit')
        except OSError as error:raise ValueError('stable package manifest attachment missing') from error
        return True


class Selected:
    __slots__ = ('receipt_pin','receipt_raw','selection_pin','selection_raw',
                 'package_pin','package_raw','value','package','private_identity','native_identity',
                 'value_stamp','package_stamp','package_identity','package_file_seal','phase','purpose')
    def __init__(self, key, receipt_pin, purpose):
        need(key is _MINT,'installation selection is bootstrap-minted only')
        need(purpose in ('runtime','construct-context'),'closed bootstrap purpose required')
        receipt_path = PRIVATE/'installation.json'
        receipt_raw = capture(receipt_path,receipt_pin,private=True,limit=1024*1024)
        receipt = parse(receipt_raw)
        closed(receipt,('schema_version','package_manifest_sha256','host_selection_sha256',
                        'private_root_identity','authority_effect','fixture_only','phase'),
               'closed installed receipt required')
        need(receipt['schema_version']=='lab-private-installation-receipt/v1'
             and receipt['authority_effect']=='none' and receipt['fixture_only'] is True,
             'installed receipt cannot confer domain authority')
        need(receipt['phase'] in ('construct-context','ready')
             and (purpose=='construct-context' or receipt['phase']=='ready'),
             'provisional construction cannot activate the runtime')
        private_identity = receipt['private_root_identity']
        need(identity(PRIVATE)==private_identity and private_identity[2:]==[os.getuid(),0o700],
             'private installed root identity differs')
        package_raw = capture(ROOT/'.cal-package-manifest.json',receipt['package_manifest_sha256'])
        package = parse(package_raw)
        selection_raw = capture(PRIVATE/'bindings/host-selection.json',receipt['host_selection_sha256'],private=True)
        value = parse(selection_raw)
        closed(value,('schema_version','package_manifest_sha256','repository_root','bindings','values',
                      'authority_effect','fixture_only'), 'closed installed host selection required')
        need(value['schema_version']=='lab-private-host-selection/v1'
             and value['package_manifest_sha256']==receipt['package_manifest_sha256']
             and value['repository_root']==str(ROOT) and value['authority_effect']=='none'
             and value['fixture_only'] is True, 'installed host selection scope differs')
        closed(value['bindings'],BINDINGS,'closed complete installed binding slots required')
        closed(value['values'],VALUES,'closed complete installed value slots required')
        need(package['schema_version']=='lab-stable-runtime-package/v1' and package['authority_effect']=='none',
             'stable package identity differs')
        need(value['values']['identity.family']==package['dataset']['family']
             and value['values']['identity.store']==package['dataset']['store']
             and value['values']['identity.scope']==package['dataset']['scope'],
             'installed Source cannot retarget packaged artifact meaning')
        need(value['values']['identity.source_name']=='completion-legacy:'+package['dataset']['family'],
             'installed Source name differs from packaged dataset')
        generated = set(package['generated_metadata_paths'])
        stable = {row['path']:row for row in package['members']}
        closed(package['binding_paths'],BINDINGS,'stable package binding slots differ')
        for slot,row in value['bindings'].items():
            if row is None:
                need(purpose=='construct-context' and receipt['phase']=='construct-context'
                     and slot not in CONSTRUCTION_REQUIRED,
                     'required or finalized installed binding is unresolved: '+slot)
                continue
            closed(row,('path','sha256'),'closed installed binding required')
            relative(row['path'])
            need(row['path']==package['binding_paths'][slot], 'installed binding path differs from public slot: '+slot)
            need(row['path'] in generated or
                 (row['path'] in stable and row['sha256']==stable[row['path']]['sha256']),
                 'binding outside declared stable/generated metadata slots: '+slot)
            capture(ROOT/row['path'],row['sha256'])
        native = Path(value['values']['native.root'])
        need(native==PRIVATE/'native','native installation outside selected private root')
        native_identity = value['values']['native.identity']
        need(identity(native)==native_identity and native_identity[2:]==[os.getuid(),0o700],
             'fresh native installation identity differs')
        native_receipt = value['values']['native.receipt']
        closed(native_receipt,('path','sha256'),'closed native receipt selection required')
        need(native_receipt['path']==str(native/'installation.json'),'native receipt path differs')
        native_raw = capture(native/'installation.json',native_receipt['sha256'],private=True,limit=4*1024*1024)
        # A matching hash over old receipt bytes is not an attestation of this
        # new directory. Full1010 verification also runs in trusted bootstrap.
        verify_native_receipt(native_raw,native_identity,
            value['values']['native.dependency_selection']['sha256'])
        need(Path(value['values']['archive.path'])==PRIVATE/'fixture-archives/branch.snapshot',
             'fixture archive outside declared private location')
        frozen_package=freeze_package(package)
        package_file_seal=PackageFileSeal(ROOT/'.cal-package-manifest.json',receipt['package_manifest_sha256'])
        for key,item in {'receipt_pin':receipt_pin,'receipt_raw':receipt_raw,
                         'selection_pin':receipt['host_selection_sha256'],'selection_raw':selection_raw,
                         'package_pin':receipt['package_manifest_sha256'],'package_raw':package_raw,
                         'value':value,'package':frozen_package,'package_identity':id(frozen_package),
                         'package_file_seal':package_file_seal,'private_identity':private_identity,
                         'native_identity':native_identity,'value_stamp':sha(canonical(value)),
                         'package_stamp':sha(canonical(package)),'phase':receipt['phase'],
                         'purpose':purpose}.items():
            object.__setattr__(self,key,item)
        self.guard()

    def __setattr__(self,name,value):
        raise AttributeError('installed selection is frozen')

    def __delattr__(self,name):
        raise AttributeError('installed selection is frozen')

    def guard(self):
        need(sha(canonical(self.value))==self.value_stamp
             and type(self.package) is MappingProxyType and id(self.package)==self.package_identity,
             'captured installed selection changed')
        need(identity(PRIVATE)==self.private_identity and self.private_identity[2:]==[os.getuid(),0o700],
             'selected private root changed')
        need(capture(PRIVATE/'installation.json',self.receipt_pin,private=True,limit=1024*1024)==self.receipt_raw,
             'installed receipt changed')
        need(capture(PRIVATE/'bindings/host-selection.json',self.selection_pin,private=True)==self.selection_raw,
             'installed host selection changed')
        self.package_file_seal.guard()
        need(identity(PRIVATE/'native')==self.native_identity,'native root identity changed')
        row = self.value['values']['native.receipt']
        raw = capture(Path(row['path']),row['sha256'],private=True,limit=4*1024*1024)
        verify_native_receipt(raw,self.native_identity,self.value['values']['native.dependency_selection']['sha256'])
        return True


def activate(receipt_sha256, *, purpose='runtime'):
    global _ACTIVE
    need(_ACTIVE is None,'installed selection already activated')
    selected = Selected(_MINT,receipt_sha256,purpose)
    _ACTIVE = selected
    return selected


def current():
    need(type(_ACTIVE) is Selected,'trusted installed bootstrap has not selected runtime inputs')
    _ACTIVE.guard()
    return _ACTIVE


def root():
    current()
    return ROOT


def binding(slot):
    selected = current()
    need(slot in BINDINGS,'unknown installed binding slot')
    need(selected.value['bindings'][slot] is not None,
         'construction binding is unresolved: '+slot)
    return copy.deepcopy(selected.value['bindings'][slot])


def value(slot):
    selected = current()
    need(slot in VALUES,'unknown installed value slot')
    return copy.deepcopy(selected.value['values'][slot])


def guard():
    current()
    return True


def require_runtime_ready():
    selected = current()
    need(selected.phase=='ready' and selected.purpose=='runtime',
         'API import requires finalized runtime selection')
    return True
