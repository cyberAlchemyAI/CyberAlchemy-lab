"""Effect-disabled portable buffer export/import for synthetic Docker Reader loading."""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import types

HERE=Path(__file__).resolve().parent
LOCAL=HERE.parent
FAMILY=Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
SELECTED_ROOT=FAMILY/'reader-stage-attempt/root'
DEFAULT_BUNDLE=FAMILY/'context-signed-scope-portable-bundle-0002'
BUNDLE_MANIFEST_SHA='1419dc09dd5139ed0335e74efdc94d1b05cc961da74ca49a00ac6f8ac026be8f'
PREDECESSOR=LOCAL/'context-signed-scope-portable-bundle-0001/freeze.json'
PREDECESSOR_FREEZE_SHA='47f593a19daaa0f3c74735b1d478650c7281100a4f5c243a88a9348c3bcacad3'
PREDECESSOR_REVIEW=LOCAL/'context-signed-scope-portable-bundle-independent-review-0001/review.json'
PREDECESSOR_REVIEW_SHA='e2128784a3abdc2bbfef26135e1f5a68c6809581b2c59c148d0aef7aa86ab0e7'
LOADER=LOCAL/'context-successor-checked-reader-loader-0001'
LOADER_FREEZE_SHA='34dc11dc1977b47ef67f7ab9b900945e86cb8afa618b8c8845af3b56f90e979c'
LOADER_CODE_SHA='740699aa42c842030dc348f65a236799a131f65a5eb37aa5ba4e926cb93832b2'
LOADER_REVIEW=LOCAL/'context-successor-checked-reader-loader-independent-review-0001/review.json'
LOADER_REVIEW_SHA='5cbf80fff93841396c83a8a0590893435611c4fe0f97d3efe481ab43fa74962a'
PLAN=LOCAL/'context-successor-signed-scope-docker-plan-0001/freeze.json'
PLAN_FREEZE_SHA='25bab1294c5a11e886c05a582d5c4135f0f2be50dddfcb74040655068e5903d2'
PLAN_REVIEW=LOCAL/'context-successor-signed-scope-docker-plan-independent-review-0001/review.json'
PLAN_REVIEW_SHA='d4b5b25ec3fb881f81301c92208f4c6589f9f6763e2cd90e3279a7714301b236'
IMAGE='sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
IMAGE_SITE=Path('/usr/local/lib/python3.14/site-packages')
SYNTHETIC_MARKER=b'context-portable-reader-synthetic-stage/v1; no private archive\n'
EFFECT_ENABLED=False
READ=os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC
WRITE=os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC

class Refused(RuntimeError):pass
def need(ok,code):
    if not ok:raise Refused(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def wire(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),
                                   ensure_ascii=False,allow_nan=False)+'\n').encode()
def parse(raw):
    def unique(rows):
        result={}
        for key,value in rows:
            need(key not in result,'DUPLICATE_JSON_KEY')
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refused('NONFINITE_JSON')))

def held_file(path,digest,maximum=4*1024*1024,exact_mode=None):
    path=Path(path)
    need(path.is_absolute() and '..' not in path.parts,'PIN_PATH')
    fd=os.open(path,READ)
    try:
        a=os.fstat(fd)
        need(stat.S_ISREG(a.st_mode) and a.st_nlink==1 and
             a.st_uid==os.getuid() and not(a.st_mode&0o022) and
             0<a.st_size<=maximum and
             (exact_mode is None or stat.S_IMODE(a.st_mode)==exact_mode),
             'PIN_CUSTODY')
        raw=os.read(fd,a.st_size+1)
        b=os.fstat(fd)
        named=os.stat(path,follow_symlinks=False)
        key=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,
                      s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        need(len(raw)==a.st_size and key(a)==key(b)==key(named) and
             sha(raw)==digest,'PIN_DRIFT')
        return raw
    finally:os.close(fd)

def reviewed_loader():
    predecessor=parse(held_file(PREDECESSOR,PREDECESSOR_FREEZE_SHA,65536))
    predecessor_review=parse(held_file(PREDECESSOR_REVIEW,PREDECESSOR_REVIEW_SHA,65536))
    freeze=parse(held_file(LOADER/'freeze.json',LOADER_FREEZE_SHA,65536))
    review=parse(held_file(LOADER_REVIEW,LOADER_REVIEW_SHA,65536))
    plan=parse(held_file(PLAN,PLAN_FREEZE_SHA,65536))
    plan_review=parse(held_file(PLAN_REVIEW,PLAN_REVIEW_SHA,65536))
    need(predecessor['effect_enabled'] is False and
         predecessor_review['candidate_freeze_sha256']==PREDECESSOR_FREEZE_SHA and
         predecessor_review['verdict']=='HOLD_BUNDLE_ADMISSION_AND_DURABILITY' and
         predecessor['members']['portable.py']==
         '86863b6d4a82678a93ede709edab9285834839c69a7cebba25c50495da66cfff' and
         freeze['effect_enabled'] is False and
         freeze['members']['checked_loader.py']==LOADER_CODE_SHA and
         review['verdict']=='PASS_BOUNDED_INERT_BUFFER_LOADER_ONLY' and
         review['candidate_freeze_sha256']==LOADER_FREEZE_SHA and
         review['effect_release_ready'] is False and
         plan['effect_enabled'] is False and plan['real_effect']=='NOT_RUN' and
         plan['loader_review_sha256']==LOADER_REVIEW_SHA and
         plan_review['verdict']=='HOLD_STRICT_SCALAR_OBSERVER_CORRECTION' and
         plan_review['candidate_freeze_sha256']==PLAN_FREEZE_SHA,
         'INERT_REVIEWED_PREDECESSORS')
    raw=held_file(LOADER/'checked_loader.py',LOADER_CODE_SHA)
    module=types.ModuleType('portable_reviewed_checked_reader_loader')
    module.__file__=str(LOADER/'checked_loader.py')
    exec(compile(raw,module.__file__,'exec'),module.__dict__)
    need(module.EFFECT_ENABLED is False and module.ROOT==SELECTED_ROOT,
         'LOADER_IDENTITY')
    return module

def export_manifest(capture):
    def relative_map(buffers):
        result={}
        for path,raw in buffers.items():
            path=Path(path)
            need(path.is_relative_to(SELECTED_ROOT),'SELECTED_BUFFER_PATH')
            relative=path.relative_to(SELECTED_ROOT).as_posix()
            need(relative not in result and '..' not in Path(relative).parts and
                 not relative.endswith('/branch.snapshot'),
                 'BUFFER_PATH_DUPLICATE_OR_PRIVATE')
            result[relative]={'sha256':sha(raw),'size':len(raw)}
        return result
    code=relative_map(capture.code)
    metadata={}
    for relative,raw in capture.metadata_buffers.items():
        need(relative not in metadata and not relative.startswith('/') and
             '..' not in Path(relative).parts and
             not relative.endswith('/branch.snapshot'),
             'METADATA_PATH_DUPLICATE_OR_PRIVATE')
        metadata[relative]={'sha256':sha(raw),'size':len(raw)}
    need(len(code)==40 and len(metadata)==85 and
         len(capture.reader_rows)==948 and len(capture.source_manifest['files'])==940 and
         len(capture.engine_rows)==45,'CAPTURE_CLOSURE_COUNT')
    selected={key:capture.selected[key] for key in
              ('scope_expected','reader','source_period_start','source_period_end')}
    return {'schema':'context-portable-reader-buffers/v1-inert',
            'effect':'NOT_RUN','private_archive':'NOT_COPIED',
            'selected_root':str(SELECTED_ROOT),'image':IMAGE,
            'loader_freeze_sha256':LOADER_FREEZE_SHA,
            'loader_review_sha256':LOADER_REVIEW_SHA,
            'plan_freeze_sha256':PLAN_FREEZE_SHA,
            'plan_hold_review_sha256':PLAN_REVIEW_SHA,
            'loader_source':{'sha256':LOADER_CODE_SHA,
                             'size':len(held_file(LOADER/'checked_loader.py',LOADER_CODE_SHA))},
            'selected':selected,'code':code,'metadata':metadata,
            'source_manifest':capture.source_manifest,
            'package':capture.package,'reader_rows':capture.reader_rows,
            'engine_rows':capture.engine_rows}

def write_exclusive(path,raw):
    fd=os.open(path,WRITE,0o600)
    try:
        os.fchmod(fd,0o600)
        view=memoryview(raw)
        while view:
            n=os.write(fd,view)
            need(n>0,'BUNDLE_SHORT_WRITE')
            view=view[n:]
        os.fsync(fd)
        os.lseek(fd,0,os.SEEK_SET)
    finally:os.close(fd)

def publish(bundle=DEFAULT_BUNDLE,now=None):
    """Public selected buffers only. No Source archive body is opened."""
    bundle=Path(bundle)
    need(bundle.is_absolute() and bundle.name.startswith(('context-signed-scope-portable-bundle-',
                                                         'bundle')) and
         bundle.parent in (FAMILY,) or
         (bundle.is_absolute() and bundle.parent.parent in (Path('/tmp'),FAMILY) and
          bundle.parent.name.startswith('fixture-portable-bundle-')),
         'OWNER_ONLY_BUNDLE_DESTINATION')
    parent=os.stat(bundle.parent,follow_symlinks=False)
    need(stat.S_ISDIR(parent.st_mode) and parent.st_uid==os.getuid() and
         stat.S_IMODE(parent.st_mode)==0o700 and
         not os.path.lexists(bundle),'BUNDLE_PARENT_OR_EXISTING')
    loader=reviewed_loader()
    capture=loader.capture(now)
    manifest=export_manifest(capture)
    os.mkdir(bundle,0o700)
    os.mkdir(bundle/'blobs',0o700)
    write_exclusive(bundle/'blobs'/LOADER_CODE_SHA,
                    held_file(LOADER/'checked_loader.py',LOADER_CODE_SHA))
    for buffers in (capture.code,capture.metadata_buffers):
        for raw in buffers.values():
            digest=sha(raw)
            target=bundle/'blobs'/digest
            if target.exists():
                need(held_file(target,digest,len(raw)+1)==raw,'BLOB_DEDUP_DRIFT')
                continue
            write_exclusive(target,raw)
    raw=wire(manifest)
    need(sha(raw)==BUNDLE_MANIFEST_SHA,'BUNDLE_MANIFEST_SELECTION_DRIFT')
    write_exclusive(bundle/'manifest.json',raw)
    for path in (bundle/'blobs',bundle):
        fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:os.fsync(fd)
        finally:os.close(fd)
    audit_bundle(bundle)
    # The bundle name is not durable until its containing directory is synced.
    try:
        fd=os.open(bundle.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:os.fsync(fd)
        finally:os.close(fd)
    except OSError as exc:
        raise Refused('PARENT_FSYNC_UNKNOWN_CONSUMED_NO_RETRY') from exc
    return {'bundle':str(bundle),'manifest_sha256':sha(raw),
            'code_buffers':len(manifest['code']),
            'metadata_buffers':len(manifest['metadata']),
            'private_archive':'NOT_COPIED','effect':'NOT_RUN'}

def audit_bundle(bundle=DEFAULT_BUNDLE):
    bundle=Path(bundle)
    need(bundle.is_absolute(),'BUNDLE_ABSOLUTE')
    for directory in (bundle,bundle/'blobs'):
        st=os.stat(directory,follow_symlinks=False)
        need(stat.S_ISDIR(st.st_mode) and st.st_uid==os.getuid() and
             stat.S_IMODE(st.st_mode)==0o700,'BUNDLE_DIRECTORY_CUSTODY')
    with os.scandir(bundle) as rows:
        entries={row.name:row.stat(follow_symlinks=False) for row in rows}
    need(set(entries)=={'manifest.json','blobs'} and
         stat.S_ISREG(entries['manifest.json'].st_mode) and
         stat.S_IMODE(entries['manifest.json'].st_mode)==0o600 and
         stat.S_ISDIR(entries['blobs'].st_mode) and
         stat.S_IMODE(entries['blobs'].st_mode)==0o700,
         'BUNDLE_EXACT_ROOT_TREE')
    raw=held_file(bundle/'manifest.json',BUNDLE_MANIFEST_SHA,exact_mode=0o600)
    manifest=parse(raw)
    need(manifest['schema']=='context-portable-reader-buffers/v1-inert' and
         manifest['private_archive']=='NOT_COPIED' and
         len(manifest['code'])==40 and len(manifest['metadata'])==85,
         'BUNDLE_MANIFEST_SCOPE')
    expected=({LOADER_CODE_SHA}|
              {r['sha256'] for r in manifest['code'].values()}|
              {r['sha256'] for r in manifest['metadata'].values()})
    with os.scandir(bundle/'blobs') as rows:
        blob_entries={row.name:row.stat(follow_symlinks=False) for row in rows}
    actual=set(blob_entries)
    need(actual==expected and len(actual)==105 and
         all(stat.S_ISREG(row.st_mode) and stat.S_IMODE(row.st_mode)==0o600
             for row in blob_entries.values()),'BUNDLE_EXACT_BLOB_SET_AND_MODE')
    for digest in sorted(expected):
        held_file(bundle/'blobs'/digest,digest,exact_mode=0o600)
    return {'schema':'context-portable-reader-bundle-audit/v1-inert',
            'manifest_sha256':BUNDLE_MANIFEST_SHA,'blobs':len(actual),
            'code_buffers':40,'metadata_buffers':85,
            'private_archive':'NOT_COPIED','effect':'NOT_RUN'}

def reconstruct(bundle,manifest_sha,stage_root,site_packages):
    """Use checked original buffers with a selected synthetic stage layout."""
    bundle=Path(bundle);stage_root=Path(stage_root);site_packages=Path(site_packages)
    need(manifest_sha==BUNDLE_MANIFEST_SHA,'BUNDLE_MANIFEST_NOT_SELECTED')
    need(bundle.is_absolute() and stage_root.is_absolute() and
         held_file(stage_root/'.portable-synthetic-only',
                   sha(SYNTHETIC_MARKER),1024)==SYNTHETIC_MARKER,
         'SYNTHETIC_STAGE_ONLY')
    audit_bundle(bundle)
    raw=held_file(bundle/'manifest.json',manifest_sha)
    manifest=parse(raw)
    need(manifest['schema']=='context-portable-reader-buffers/v1-inert' and
         manifest['effect']=='NOT_RUN' and manifest['private_archive']=='NOT_COPIED' and
         manifest['selected_root']==str(SELECTED_ROOT) and
         manifest['image']==IMAGE and
         manifest['loader_freeze_sha256']==LOADER_FREEZE_SHA and
         manifest['loader_review_sha256']==LOADER_REVIEW_SHA and
         manifest['plan_freeze_sha256']==PLAN_FREEZE_SHA and
         manifest['plan_hold_review_sha256']==PLAN_REVIEW_SHA and
         manifest['loader_source']['sha256']==LOADER_CODE_SHA and
         len(manifest['code'])==40 and len(manifest['metadata'])==85,
         'PORTABLE_MANIFEST_SCOPE')
    def buffers(rows):
        result={}
        for relative,record in rows.items():
            need(type(relative) is str and not relative.startswith('/') and
                 '..' not in Path(relative).parts and
                 not relative.endswith('/branch.snapshot') and
                 type(record) is dict and set(record)=={'sha256','size'} and
                 re.fullmatch('[0-9a-f]{64}',record['sha256']) and
                 type(record['size']) is int and 0<record['size']<=4*1024*1024,
                 'BUNDLE_ROW_SHAPE')
            blob=held_file(bundle/'blobs'/record['sha256'],record['sha256'])
            need(len(blob)==record['size'],'BUNDLE_BLOB_SIZE')
            result[str(stage_root/relative)]=blob
        return result
    code=buffers(manifest['code'])
    metadata={str(Path(path).relative_to(stage_root)):raw
              for path,raw in buffers(manifest['metadata']).items()}
    loader_raw=held_file(bundle/'blobs'/LOADER_CODE_SHA,LOADER_CODE_SHA)
    need(len(loader_raw)==manifest['loader_source']['size'],
         'LOADER_SOURCE_BUNDLE_SIZE')
    loader=types.ModuleType('portable_reviewed_checked_reader_loader')
    loader.__file__=str(bundle/'blobs'/LOADER_CODE_SHA)
    exec(compile(loader_raw,loader.__file__,'exec'),loader.__dict__)
    need(loader.EFFECT_ENABLED is False and loader.ROOT==SELECTED_ROOT,
         'BUNDLED_LOADER_IDENTITY')
    loader.ROOT=stage_root
    loader.DIST_PACKAGES=site_packages
    capture=loader.Capture(manifest['selected'],code,metadata,
                           manifest['engine_rows'],manifest['source_manifest'],
                           manifest['package'],manifest['reader_rows'])
    return loader,capture,manifest

def materialize_synthetic_stage(bundle,manifest_sha,output):
    """Public buffer fixture only, never the selected actual stage root."""
    bundle=Path(bundle);output=Path(output)
    need(output.is_absolute() and output.parent.parent in (Path('/tmp'),FAMILY) and
         output.parent.name.startswith('fixture-portable-stage-') and
         not os.path.lexists(output),'DISPOSABLE_STAGE_DESTINATION')
    parent=os.stat(output.parent,follow_symlinks=False)
    need(stat.S_ISDIR(parent.st_mode) and parent.st_uid==os.getuid() and
         stat.S_IMODE(parent.st_mode)==0o700,'DISPOSABLE_STAGE_PARENT')
    manifest=parse(held_file(bundle/'manifest.json',manifest_sha))
    need(manifest['private_archive']=='NOT_COPIED' and
         len(manifest['code'])==40 and len(manifest['metadata'])==85,
         'SYNTHETIC_MANIFEST')
    os.mkdir(output,0o700)
    for rows in (manifest['code'],manifest['metadata']):
        for relative,record in rows.items():
            path=Path(relative)
            need(not path.is_absolute() and '..' not in path.parts and
                 not relative.endswith('/branch.snapshot'),
                 'SYNTHETIC_STAGE_PATH')
            target=output/path
            target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            raw=held_file(bundle/'blobs'/record['sha256'],record['sha256'])
            if target.exists():
                need(held_file(target,record['sha256'])==raw,
                     'SYNTHETIC_STAGE_DUPLICATE')
            else:write_exclusive(target,raw)
    write_exclusive(output/'.portable-synthetic-only',SYNTHETIC_MARKER)
    return {'stage':str(output),'private_archive':'ABSENT',
            'code_files':40,'metadata_files':85,'effect':'NOT_RUN'}

def open_real_signed(*_args,**_kwargs):raise Refused('EFFECT_DISABLED_NO_PRIVATE_SIGNED_REOPEN')
def issue_auth(*_args,**_kwargs):raise Refused('EFFECT_DISABLED_NO_AUTH')

if __name__=='__main__':
    raise SystemExit('effect-disabled library; no CLI publication or signed execution')
