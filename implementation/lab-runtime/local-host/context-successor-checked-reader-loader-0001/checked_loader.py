"""Inert checked-buffer loader for the selected staged Reader code closure.

No Reader is instantiated and no signed or private Source is opened here.
"""
from __future__ import annotations

from contextlib import contextmanager
import datetime as dt
import hashlib
import importlib
import importlib.abc
import importlib.machinery
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import stat
import sys
import types

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
FAMILY = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
ROOT = FAMILY/'reader-stage-attempt/root'
READER_ROLE = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0002'
SOURCE_ROLE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
CORRECTION_ROLE = 'product/lab/release-candidates/v1/interface/custody-correction-v4'
READER_NAME = '_cal_checked_reader_20261020_0002'
SOURCE_NAME = '_cal_docker_reader_producer_20261020_0002'
ENGINE_LOADER_NAME = '_cal_docker_source_engine_20261020_0002'
BRIDGE_NAME = '_cal_docker_source_bridge_20261020_0002'
ENGINE_PREFIX = '_cal_R03_engine_'
READER_MANIFEST_SHA = '048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756'
READER_CODE_SHA = 'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9'
ADAPTER_DIR = LOCAL/'context-successor-local-issuer-adapter-0002'
ADAPTER_FREEZE_SHA = '6a2cf9c2fe3c90aacb13b2537668fb37c9dbd94401129b175627ceeea19d7e26'
ADAPTER_CODE_SHA = 'f4500ccdfa92b60818c58a1d50072d7985d84b4811e22c922c5eb399e0860466'
ADAPTER_REVIEW = LOCAL/'context-successor-local-issuer-independent-review-0002/review.json'
ADAPTER_REVIEW_SHA = 'fab52d2b65e742c86234a1e6770322f7111c863b83457d283f5afa56044a4c4e'
DIST_PACKAGES = Path('/usr/lib/python3/dist-packages')
EFFECT_ENABLED = False
DIR_FLAGS = os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
READ_FLAGS = os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC


class Refused(RuntimeError): pass
def need(ok, code):
    if not ok: raise Refused(code)
def sha(raw): return hashlib.sha256(raw).hexdigest()

def parse(raw):
    def pairs(rows):
        value={}
        for key,item in rows:
            need(key not in value,'DUPLICATE_MANIFEST_KEY')
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refused('NONFINITE')))

def read_pin(path, expected, maximum=2*1024*1024):
    """One held nofollow path walk; return only verified bytes, never private body."""
    path=Path(path)
    need(path.is_absolute() and (path.is_relative_to(ROOT) or
         path.is_relative_to(LOCAL)),'PIN_OUTSIDE_SELECTED_ROOT')
    fds=[]
    primary=None
    try:
        fds.append(os.open('/',DIR_FLAGS))
        for part in path.parts[1:-1]:
            fds.append(os.open(part,DIR_FLAGS,dir_fd=fds[-1]))
            st=os.fstat(fds[-1])
            need(st.st_uid in (0,os.getuid()) and
                 not(st.st_mode & 0o022),'PIN_PARENT_CUSTODY')
        fds.append(os.open(path.name,READ_FLAGS,dir_fd=fds[-1]))
        fd=fds[-1]
        before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and
             before.st_uid==os.getuid() and not(before.st_mode & 0o022) and
             0 < before.st_size <= maximum,'PIN_LEAF_CUSTODY')
        raw=bytearray()
        while len(raw) <= before.st_size:
            block=os.read(fd,min(65536,before.st_size+1-len(raw)))
            if not block:break
            raw.extend(block)
        after=os.fstat(fd)
        named=os.stat(path.name,dir_fd=fds[-2],follow_symlinks=False)
        identity=lambda st:(st.st_dev,st.st_ino,st.st_mode,st.st_uid,
                            st.st_gid,st.st_nlink,st.st_size,st.st_mtime_ns,
                            st.st_ctime_ns)
        need(len(raw)==before.st_size and
             identity(before)==identity(after)==identity(named) and
             sha(raw)==expected,'PIN_BYTES_OR_ID_DRIFT')
        return bytes(raw)
    except BaseException as exc:
        primary=exc
        raise
    finally:
        errors=[]
        for fd in reversed(fds):
            try:os.close(fd)
            except BaseException as exc:errors.append(exc)
        if errors:
            if primary is None:raise ExceptionGroup('pin close uncertain',errors)
            primary.add_note('secondary pin close uncertainty')

def _checked_adapter(now):
    freeze_raw=read_pin(ADAPTER_DIR/'freeze.json',ADAPTER_FREEZE_SHA)
    freeze=parse(freeze_raw)
    need(freeze['effect_enabled'] is False and
         freeze['members']['adapter.py']==ADAPTER_CODE_SHA,
         'ADAPTER_FREEZE_SCOPE')
    review=parse(read_pin(ADAPTER_REVIEW,ADAPTER_REVIEW_SHA))
    need(review['verdict']=='PASS_BOUNDED_INERT_MODEL_ONLY' and
         review['candidate_freeze_sha256']==ADAPTER_FREEZE_SHA,
         'ADAPTER_REVIEW_SCOPE')
    raw=read_pin(ADAPTER_DIR/'adapter.py',ADAPTER_CODE_SHA)
    module=types.ModuleType('checked_local_issuer_selection_0002')
    module.__file__=str(ADAPTER_DIR/'adapter.py')
    exec(compile(raw,module.__file__,'exec'),module.__dict__)
    need(module.EFFECT_ENABLED is False,'ADAPTER_EFFECT_DRIFT')
    return module.select(now)

def _rows(manifest):
    need(manifest['authority_effect']=='none' and
         manifest['actual_owner_outcome'] is None and
         type(manifest['files']) is list,'READER_MANIFEST_SCOPE')
    rows={}
    for row in manifest['files']:
        need(type(row) is dict and set(row)=={'path','sha256'} and
             type(row['path']) is str and type(row['sha256']) is str and
             re.fullmatch('[0-9a-f]{64}',row['sha256']) and
             not row['path'].startswith('/') and '..' not in Path(row['path']).parts and
             row['path'] not in rows,'READER_MANIFEST_ROWS')
        rows[row['path']]=row['sha256']
    return rows

def _bound_rows(items,prefix):
    need(type(items) is list,'BOUND_ROW_LIST')
    result={}
    for row in items:
        need(type(row) is dict and set(row)=={'path','sha256'} and
             type(row['path']) is str and row['path'].startswith(prefix) and
             row['path'] not in result and
             all(part not in ('','.','..') for part in row['path'].split('/')) and
             type(row['sha256']) is str and
             re.fullmatch('[0-9a-f]{64}',row['sha256']),
             'BOUND_ROW_PATH_OR_DIGEST')
        result[row['path']]=row['sha256']
    return result

def capture(now=None):
    """Capture code and public configuration only; branch.snapshot is excluded."""
    now=dt.datetime.now(dt.timezone.utc) if now is None else now
    selected=_checked_adapter(now)
    need(selected['reader']['sha256']==READER_CODE_SHA and
         selected['reader']['manifest_sha256']==READER_MANIFEST_SHA and
         selected['scope_actual']=='NOT_OPENED' and
         selected['auth']['issued_sha256']=='UNMINTED_UNSELECTED',
         'CURRENT_READER_SELECTION')
    manifest=parse(read_pin(ROOT/READER_ROLE/'source-manifest.json',READER_MANIFEST_SHA))
    rows=_rows(manifest)
    source_manifest_path=SOURCE_ROLE+'/source-manifest.json'
    need(rows[source_manifest_path]==selected['reader']['source_manifest_sha256'] and
         manifest['producer_source_binding']==
         {'path':source_manifest_path,'sha256':rows[source_manifest_path]} and
         manifest['producer_package_binding']==
         {'path':SOURCE_ROLE+'/packages/0001/manifest.json',
          'sha256':selected['reader']['source_package_manifest_sha256']},
         'PRODUCER_BINDING')
    source_manifest=parse(read_pin(ROOT/source_manifest_path,rows[source_manifest_path]))
    need(source_manifest['authority_effect']=='none' and
         source_manifest['actual_owner_outcome'] is None,
         'SOURCE_MANIFEST_AUTHORITY')
    source_rows=_bound_rows(source_manifest['files'],'')
    need(len(source_rows)==940 and
         all(rows.get(path)==digest for path,digest in source_rows.items()),
         'SOURCE_READER_EXACT_ROW_JOIN')
    need(set(rows)==set(source_rows)|{source_manifest_path}|
         {path for path in rows if path.startswith(READER_ROLE+'/')},
         'READER_EXTRANEOUS_ROW')
    package_prefix=SOURCE_ROLE+'/packages/0001/'
    package_path=package_prefix+'manifest.json'
    package=parse(read_pin(ROOT/package_path,
                           selected['reader']['source_package_manifest_sha256']))
    need(package['authority_effect']=='none' and
         package['actual_owner_outcome'] is None and
         package['source_manifest_binding']==
         {'path':source_manifest_path,'sha256':rows[source_manifest_path]},
         'PACKAGE_BINDING')
    package_rows=_bound_rows(package['files'],package_prefix)
    need(len(package_rows)==len(package['files']) and
         package_prefix+'branch.snapshot' in package_rows,
         'PACKAGE_ROWS')
    engine_manifest_path=CORRECTION_ROLE+'/engine-manifest.json'
    engine_manifest=parse(read_pin(ROOT/engine_manifest_path,
                                   rows[engine_manifest_path]))
    need(engine_manifest['authority_effect']=='none' and
         engine_manifest['actual_owner_outcome'] is None,
         'ENGINE_MANIFEST_AUTHORITY')
    engine_rows=_bound_rows(engine_manifest['files'],CORRECTION_ROLE+'/')
    need(len(engine_rows)==45 and len(engine_rows)==len(engine_manifest['files']) and
         all(rows.get(path)==digest for path,digest in engine_rows.items()),
         'ENGINE_READER_JOIN')
    parent_binding=engine_manifest['parent_binding']
    need(rows[parent_binding['path']]==parent_binding['sha256'],
         'ENGINE_PARENT_BINDING')
    parent_manifest=parse(read_pin(ROOT/parent_binding['path'],parent_binding['sha256']))
    parent_rows=_bound_rows(parent_manifest['files'],
                            str(Path(parent_binding['path']).parent)+'/')
    need(len(parent_rows)==len(parent_manifest['files']) and
         all(rows.get(path)==digest for path,digest in parent_rows.items()),
         'ENGINE_PARENT_READER_JOIN')
    code_paths=(
        [path for path in rows if path.startswith(READER_ROLE+'/') and path.endswith('.py')]+
        [path for path in rows if path.startswith(SOURCE_ROLE+'/') and path.endswith('.py')]+
        [CORRECTION_ROLE+'/loader.py',CORRECTION_ROLE+'/reader_adapter.py']+
        [path for path in engine_rows if path.endswith('.py')])
    need(len(code_paths)==len(set(code_paths)) and
         len([p for p in code_paths if p.startswith(READER_ROLE+'/')])==7 and
         len([p for p in code_paths if p.startswith(SOURCE_ROLE+'/')])==5 and
         all(rows.get(path)==engine_rows.get(path) for path in engine_rows if path.endswith('.py')),
         'CODE_CLOSURE')
    code={str(ROOT/path):read_pin(ROOT/path,rows[path],1024*1024)
          for path in code_paths}
    need(sha(code[str(ROOT/READER_ROLE/'reader.py')])==READER_CODE_SHA,
         'SELECTED_READER_CODE')
    metadata_paths=(
        [path for path in engine_rows if not path.endswith('.py')]+ 
        [CORRECTION_ROLE+'/pins.json',SOURCE_ROLE+'/episode-contract.json',
         parent_binding['path']]+
        list(parent_rows)+
        [path for path in rows if path in (
            'docs/plans/0011-lab-runtime-completion/runs/0001-execution/source-only-dev-20261020-successor/authorization.json',
            'product/lab/release-candidates/v1/interface/current-participation-v5/packages/0001/period.json',
            'product/lab/release-candidates/v1/interface/current-participation-v5/episode-contract.json')])
    metadata_buffers={}
    for path in metadata_paths:
        expected=rows[path]
        need(path not in metadata_buffers or sha(metadata_buffers[path])==expected,
             'DUPLICATE_METADATA_BINDING')
        metadata_buffers[path]=read_pin(ROOT/path,expected,1024*1024)
    for path,digest in package_rows.items():
        if path.endswith('/branch.snapshot'):continue
        metadata_buffers[path]=read_pin(ROOT/path,digest,1024*1024)
    need(all(not path.endswith('branch.snapshot') for path in metadata_buffers),
         'PRIVATE_ARCHIVE_METADATA_CAPTURE')
    return Capture(selected,code,metadata_buffers,engine_rows,
                   source_manifest,package,rows)


class Capture:
    def __init__(self,selected,code,metadata_buffers,engine_rows,
                 source_manifest,package,reader_rows):
        self.selected=selected
        self.code=code
        self.code_digests={path:reader_rows[str(Path(path).relative_to(ROOT))]
                           for path in code}
        self.metadata_buffers=metadata_buffers
        self.metadata_digests={path:sha(raw) for path,raw in metadata_buffers.items()}
        self.engine_rows=engine_rows
        self.source_manifest=source_manifest
        self.package=package
        self.reader_rows=reader_rows
    def summary(self):
        host_environment={'python':platform.python_version(),
                          'jsonschema':importlib.metadata.version('jsonschema'),
                          'cryptography':importlib.metadata.version('cryptography')}
        return {'schema':'checked-original-reader-loader-capture/v1-inert',
                'effect':'NOT_RUN','signed_scope':'NOT_OPENED',
                'reader_method':'SelectedReader.open_signed',
                'reader_code_sha256':READER_CODE_SHA,
                'reader_manifest_sha256':READER_MANIFEST_SHA,
                'code_buffers':len(self.code),
                'metadata_buffers':len(self.metadata_digests),
                'engine_manifest_files':len(self.engine_rows),
                'source_required_environment':self.source_manifest['environment'],
                'host_environment':host_environment,
                'host_environment_matches':host_environment==self.source_manifest['environment'],
                'protected_archive_body':'UNOPENED',
                'source_period_end':self.selected['source_period_end']}
    def guard_metadata(self):
        """Recheck selected public configuration against captured bytes."""
        for path,raw in self.metadata_buffers.items():
            need(sha(raw)==self.metadata_digests[path],
                 'CAPTURED_METADATA_BUFFER_DRIFT')
            read_pin(ROOT/path,self.metadata_digests[path],1024*1024)


class BufferLoader(importlib.abc.Loader):
    def __init__(self,owner,name,origin,raw,is_package):
        self.owner=owner;self.name=name;self.origin=str(origin)
        self.raw=raw;self.is_package=is_package
    def create_module(self,spec):return None
    def exec_module(self,module):
        need(sha(self.raw)==self.owner.expected_code_sha(self.origin),
             'EXECUTED_BUFFER_DRIFT')
        self.owner.executed.append((self.name,self.origin,sha(self.raw)))
        module.__file__=self.origin
        if self.is_package:module.__path__=[str(Path(self.origin).parent)]
        exec(compile(self.raw,self.origin,'exec'),module.__dict__)


class CheckedFinder(importlib.abc.MetaPathFinder):
    def __init__(self,capture):
        self.capture=capture
        self.executed=[]
        self.engine_roots={}
        self.original_spec=importlib.util.spec_from_file_location
    def expected_code_sha(self,origin):
        path=Path(origin)
        if str(path) in self.capture.code_digests:
            return self.capture.code_digests[str(path)]
        for name,root in self.engine_roots.items():
            if path.is_relative_to(root):
                relative=path.relative_to(root)
                original=ROOT/CORRECTION_ROLE/'runtime/lab_runtime'/relative
                if str(original) in self.capture.code_digests:
                    return self.capture.code_digests[str(original)]
        raise Refused('UNSELECTED_CODE_ORIGIN')
    def _spec(self,name,origin,raw,is_package):
        loader=BufferLoader(self,name,origin,raw,is_package)
        spec=importlib.machinery.ModuleSpec(name,loader,origin=str(origin),
                                             is_package=is_package)
        if is_package:spec.submodule_search_locations=[str(Path(origin).parent)]
        return spec
    def _known(self,name):
        if name==READER_NAME or name.startswith(READER_NAME+'.'):
            prefix=READER_NAME;root=ROOT/READER_ROLE
        elif name==SOURCE_NAME or name.startswith(SOURCE_NAME+'.'):
            prefix=SOURCE_NAME;root=ROOT/SOURCE_ROLE
        else:return None
        suffix=name[len(prefix):].lstrip('.')
        base=root.joinpath(*suffix.split('.')) if suffix else root
        package=base/'__init__.py';module=base.with_suffix('.py')
        if str(package) in self.capture.code:return package,True
        if str(module) in self.capture.code:return module,False
        raise Refused('UNSELECTED_READER_OR_SOURCE_IMPORT_'+name)
    def find_spec(self,fullname,path=None,target=None):
        known=self._known(fullname)
        if known is not None:
            origin,is_package=known
            return self._spec(fullname,origin,self.capture.code[str(origin)],is_package)
        for engine_name,root in self.engine_roots.items():
            if fullname==engine_name or fullname.startswith(engine_name+'.'):
                suffix=fullname[len(engine_name):].lstrip('.')
                base=root.joinpath(*suffix.split('.')) if suffix else root
                package=base/'__init__.py';module=base.with_suffix('.py')
                for candidate,is_package in ((package,True),(module,False)):
                    original=ROOT/CORRECTION_ROLE/'runtime/lab_runtime'/candidate.relative_to(root)
                    if str(original) in self.capture.code:
                        return self._spec(fullname,candidate,self.capture.code[str(original)],
                                          is_package)
                raise Refused('UNSELECTED_ENGINE_IMPORT_'+fullname)
        if fullname.startswith(ENGINE_PREFIX):
            raise Refused('ENGINE_PACKAGE_NOT_CAPTURED')
        return None
    def checked_spec_from_file_location(self,name,location,*args,**kwargs):
        origin=Path(location)
        fixed={SOURCE_NAME:ROOT/SOURCE_ROLE/'__init__.py',
               ENGINE_LOADER_NAME:ROOT/CORRECTION_ROLE/'loader.py',
               BRIDGE_NAME:ROOT/CORRECTION_ROLE/'reader_adapter.py'}
        if name in fixed:
            need(origin==fixed[name] and str(origin) in self.capture.code,
                 'DYNAMIC_SELECTED_PATH_DRIFT')
            is_package=name==SOURCE_NAME
            if is_package:
                need(kwargs.get('submodule_search_locations')==[str(origin.parent)],
                     'SOURCE_PACKAGE_SEARCH_PATH_DRIFT')
            else:
                need(not kwargs.get('submodule_search_locations'),
                     'DYNAMIC_MODULE_PACKAGE_DRIFT')
            return self._spec(name,origin,self.capture.code[str(origin)],is_package)
        if re.fullmatch(r'_cal_R03_engine_[0-9a-f]{32}',name):
            need(origin.name=='__init__.py' and origin.parent.name=='lab_runtime' and
                 origin.parent.parent.name=='v2' and
                 origin.parents[4].name=='captured' and
                 origin.parents[5].name.startswith('cal-R03-pinned-engine-') and
                 kwargs.get('submodule_search_locations')==[str(origin.parent)],
                 'ENGINE_CAPTURED_PATH_DRIFT')
            need(name not in self.engine_roots,'ENGINE_CAPTURE_NAME_REUSE')
            root=origin.parent
            self.engine_roots[name]=root
            original=ROOT/CORRECTION_ROLE/'runtime/lab_runtime/__init__.py'
            return self._spec(name,origin,self.capture.code[str(original)],True)
        if (name.startswith((ENGINE_PREFIX,'_cal_docker_')) or
                origin.is_relative_to(ROOT) or
                any(origin.is_relative_to(root) for root in self.engine_roots.values())):
            raise Refused('UNSELECTED_DYNAMIC_MODULE_'+name)
        return self.original_spec(name,location,*args,**kwargs)


@contextmanager
def checked_modules(capture_value):
    """Execute exact code buffers, including named dynamic imports, then unload."""
    need(type(capture_value) is Capture and EFFECT_ENABLED is False,
         'INERT_CAPTURE_REQUIRED')
    capture_value.guard_metadata()
    package_stat=os.stat(DIST_PACKAGES,follow_symlinks=False)
    need(stat.S_ISDIR(package_stat.st_mode) and package_stat.st_uid==0 and
         not(package_stat.st_mode & 0o022),'DISTRIBUTION_DEPENDENCY_CUSTODY')
    names=(READER_NAME,SOURCE_NAME,ENGINE_LOADER_NAME,BRIDGE_NAME)
    need(not any(name in names or
                 any(name.startswith(prefix+'.') for prefix in names) or
                 name.startswith(ENGINE_PREFIX) for name in sys.modules),
         'SELECTED_MODULE_ALREADY_LOADED')
    finder=CheckedFinder(capture_value)
    old_spec=importlib.util.spec_from_file_location
    added_path=False
    try:
        if str(DIST_PACKAGES) not in sys.path:
            sys.path.insert(0,str(DIST_PACKAGES));added_path=True
        sys.meta_path.insert(0,finder)
        importlib.util.spec_from_file_location=finder.checked_spec_from_file_location
        package=importlib.import_module(READER_NAME)
        reader=importlib.import_module(READER_NAME+'.reader')
        need(reader.SelectedReader.__module__==READER_NAME+'.reader' and
             reader.SelectedReader.open_signed.__wrapped__.__code__.co_filename==
             str(ROOT/READER_ROLE/'reader.py'),
             'ORIGINAL_READER_ENTRYPOINT')
        try:yield reader,finder
        finally:capture_value.guard_metadata()
    finally:
        importlib.util.spec_from_file_location=old_spec
        if finder in sys.meta_path:sys.meta_path.remove(finder)
        if added_path:sys.path.remove(str(DIST_PACKAGES))
        for name in list(sys.modules):
            if (name in names or any(name.startswith(prefix+'.') for prefix in names) or
                    name.startswith(ENGINE_PREFIX)):
                sys.modules.pop(name,None)


def observe_synthetic_scope(capture_value, signed):
    """Synthetic shape check only; never converts caller data into authority."""
    expected=capture_value.selected['scope_expected']
    basis={'manifest_sha256':capture_value.selected['reader']['source_package_manifest_sha256'],
           'source_manifest_sha256':capture_value.selected['reader']['source_manifest_sha256'],
           'adapter_source_sha256':READER_MANIFEST_SHA}
    need(signed.guard() is True and
         signed.view.data['config']['scope_ref']==expected and
         signed.sources.scope_ref==expected and
         signed.selected['candidate_selection_basis']==basis,
         'SYNTHETIC_SIGNED_SCOPE_OR_BASIS')
    return {'status':'SYNTHETIC_SCOPE_ONLY_NOT_ATTESTED',
            'scope_ref':expected,'actual_reader_open':'NOT_RUN'}


def open_actual_signed(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_PRIVATE_SIGNED_REOPEN')

if __name__=='__main__':
    if sys.argv[1:]!=['--capture']:
        raise SystemExit('expected --capture')
    print(json.dumps(capture().summary(),sort_keys=True,separators=(',',':')))
