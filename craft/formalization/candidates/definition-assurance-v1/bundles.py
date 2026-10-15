"""Create-only captured evidence directories; collisions preserve all bytes."""
import ctypes
import errno
import json
import os
import sys
import uuid
from pathlib import Path
import resolver as r

ROOT=Path(__file__).resolve().parents[4]
BASE='docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
CONTRACT_UNIT=ROOT/BASE/'units/E01'
sys.path.insert(0,str(CONTRACT_UNIT))
import evidence_contract as e

MAX_TOTAL_BYTES=32_000_000
MAX_ENVELOPE_BYTES=4_000_000
RENAME_NOREPLACE=1


class BundleFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()+b'\n'


def checked_contract():
    receipt=r.parse((CONTRACT_UNIT/'receipt.json').read_bytes(),str(CONTRACT_UNIT/'receipt.json'))
    selected={row['path']:row['sha256'] for row in receipt['outputs']}
    for path in [e.SCHEMA_PATH,CONTRACT_UNIT/'evidence_contract.py']:
        if selected.get(path.relative_to(ROOT).as_posix())!=r.digest(path.read_bytes()):raise BundleFault('stale-selected-evidence-contract')
    return {'schema_sha256':r.digest(e.SCHEMA_PATH.read_bytes()),'checker_sha256':r.digest((CONTRACT_UNIT/'evidence_contract.py').read_bytes()),'receipt_sha256':r.digest((CONTRACT_UNIT/'receipt.json').read_bytes()),'publisher_sha256':r.digest(Path(__file__).read_bytes())}


def validate_snapshot(bundle,captured,root):
    snapshot=r.parse(captured[bundle['snapshot_ref']['path']],bundle['snapshot_ref']['path']);r.verify(snapshot,root)
    current={row['version_ref']:row for row in snapshot['current_entries']}
    for source in bundle['sources']:
        row=current.get(source['version_ref'])
        if row is None or any(source[key]!=row[key] for key in ['definition_id','path','sha256']):raise BundleFault('bundle-source-outside-selected-current-snapshot',source['version_ref'])
    return snapshot


def capture(root,bundle,expected_required):
    report=e.check(bundle,expected_required)
    if report['status']!='candidate-accounted':raise BundleFault('invalid-evidence-contract')
    captured={};total=0
    for ref in e.artifact_refs(bundle):
        raw=r.read_bytes(root,ref['path'])
        if r.digest(raw)!=ref['sha256']:raise BundleFault('stale-artifact-at-capture',ref['path'])
        total+=len(raw)
        if total>MAX_TOTAL_BYTES:raise BundleFault('bundle-total-byte-limit')
        captured[ref['path']]=raw
    report=e.check(bundle,expected_required,captured=captured)
    if report['status']!='candidate-accounted':raise BundleFault('captured-contract-or-native-data-invalid')
    validate_snapshot(bundle,captured,root)
    return captured,report


def parent_fd(root,path):
    parts=r.components(path)
    if not path.startswith(BASE+'/'):raise BundleFault('output-outside-candidate-evidence-area',path)
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for part in parts:
            try:os.mkdir(part,0o700,dir_fd=fd)
            except FileExistsError:pass
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=child
        return fd
    except BaseException:os.close(fd);raise


def write_file(directory,name,raw):
    fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
    try:
        with os.fdopen(fd,'wb',closefd=False) as stream:stream.write(raw);stream.flush();os.fsync(fd)
    finally:os.close(fd)


def install_no_replace(parent,attempt,target):
    # rename() can replace an existing empty directory. There is no fallback.
    library=ctypes.CDLL(None,use_errno=True)
    try:function=library.renameat2
    except AttributeError:raise BundleFault('atomic-no-replace-unavailable')
    function.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];function.restype=ctypes.c_int
    if function(parent,os.fsencode(attempt),parent,os.fsencode(target),RENAME_NOREPLACE):
        code=ctypes.get_errno()
        if code in {errno.EEXIST,errno.ENOTEMPTY}:raise BundleFault('publication-target-collision',target)
        if code in {errno.ENOSYS,errno.EINVAL,errno.EOPNOTSUPP}:raise BundleFault('atomic-no-replace-unavailable')
        raise BundleFault('atomic-publication-failed',str(code))


def manifest_for(bundle,captured,contract):
    envelope=canonical(bundle)
    if len(envelope)>MAX_ENVELOPE_BYTES:raise BundleFault('envelope-byte-limit')
    rows=[{'path':path,'sha256':r.digest(raw),'size_bytes':len(raw),'object_path':'objects/'+r.digest(raw)+'.bin'} for path,raw in sorted(captured.items())]
    identity={'schema_version':'definition-assurance-published-manifest/v1-candidate','authority_effect':'none','envelope_sha256':r.digest(envelope),'files':rows,'contract_bindings':contract,'required_set_sha256':bundle['required_set']['required_set_sha256'],'capture_scope':'E01 explicit artifact references; external runtime requirements are byte-bound records, not an included runtime distribution.'}
    identity_sha=e.digest(identity)
    return {**identity,'bundle_id':'bundle:'+identity_sha},'bundle-'+identity_sha,envelope


def publish(root,bundle,expected_required,output_parent,before_publish=None):
    parent=None;stage=None;objects=None;attempt=None;target=None;installed=False
    try:
        root=r.resolve_root(root);contract=checked_contract();captured,report=capture(root,bundle,expected_required)
        manifest,target,envelope=manifest_for(bundle,captured,contract);parent=parent_fd(root,output_parent)
        attempt='.attempt-'+uuid.uuid4().hex;os.mkdir(attempt,0o700,dir_fd=parent);os.fsync(parent);stage=os.open(attempt,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
        os.mkdir('objects',0o700,dir_fd=stage);objects=os.open('objects',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=stage)
        written=set()
        for row in manifest['files']:
            name=row['sha256']+'.bin'
            if name not in written:write_file(objects,name,captured[row['path']]);written.add(name)
        os.fsync(objects);write_file(stage,'envelope.json',envelope);write_file(stage,'manifest.json',canonical(manifest));os.fsync(stage)
        if before_publish:before_publish({'root':root,'output_parent':output_parent,'attempt':attempt,'target':target,'manifest':manifest})
        # Rehash all inputs and the complete source capture at final boundary.
        for path,raw in captured.items():
            if r.read_bytes(root,path)!=raw:raise BundleFault('artifact-changed-before-publication',path)
        validate_snapshot(bundle,captured,root)
        if not r.same_json(contract,checked_contract()):raise BundleFault('contract-or-producer-changed-before-publication')
        # Ensure the held parent still denotes the selected repository path.
        checked,name=r.open_parent(root,output_parent+'/unused-marker')
        try:
            if (os.fstat(checked).st_dev,os.fstat(checked).st_ino)!=(os.fstat(parent).st_dev,os.fstat(parent).st_ino):raise BundleFault('publication-parent-moved')
        finally:os.close(checked)
        install_no_replace(parent,attempt,target);installed=True;os.fsync(parent)
        for path,raw in captured.items():
            if r.read_bytes(root,path)!=raw:raise BundleFault('artifact-changed-at-publication-boundary',path)
        validate_snapshot(bundle,captured,root)
        if not r.same_json(contract,checked_contract()):raise BundleFault('contract-or-producer-changed-at-publication-boundary')
        return {'status':'published-candidate','authority_effect':'none','semantic_ready':False,'bundle_id':manifest['bundle_id'],'bundle_ref':output_parent+'/'+target,'artifact_files':len(captured),'unique_objects':len(written),'contract_accounting':report,'source_currentness':'verified-at-final-publication-boundary','claim_ceiling':'Exact captured candidate bytes and atomic create-only installation. No accepted source fidelity, independent proof/readiness or authority effect.'}
    except (BundleFault,r.CaptureFault,OSError,ValueError,TypeError,KeyError,IndexError) as error:
        code=getattr(error,'code',type(error).__name__)
        status=('published-durability-unconfirmed' if isinstance(error,OSError) else 'published-currentness-unconfirmed') if installed else 'publication-collision' if code=='publication-target-collision' else 'publication-unresolved'
        return {'status':status,'authority_effect':'none','semantic_ready':False,'diagnostics':[{'code':code,'path':getattr(error,'path','')}],'preserved_attempt_ref':output_parent+'/'+attempt if attempt and not installed else None,'published_ref':output_parent+'/'+target if installed else None,'claim_ceiling':'Failed or indeterminate publication is not readiness. Existing outputs, captured attempts and source files are preserved.'}
    finally:
        for fd in [objects,stage,parent]:
            if fd is not None:os.close(fd)


def inspect(root,bundle_ref,expected_required,live_source_root=None,expected_contract=None):
    """Verify exact captured package bytes; no provider truth/readiness claim."""
    root=r.resolve_root(root);r.components(bundle_ref)
    if not bundle_ref.startswith(BASE+'/'):raise BundleFault('bundle-outside-candidate-area')
    manifest=r.parse(r.read_bytes(root,bundle_ref+'/manifest.json'),'manifest');envelope_raw=r.read_bytes(root,bundle_ref+'/envelope.json');bundle=r.parse(envelope_raw,'envelope')
    required_keys={'schema_version','authority_effect','envelope_sha256','files','contract_bindings','required_set_sha256','capture_scope','bundle_id'}
    if not isinstance(manifest,dict) or set(manifest)!=required_keys or manifest['schema_version']!='definition-assurance-published-manifest/v1-candidate' or manifest['authority_effect']!='none':raise BundleFault('malformed-published-manifest')
    contract=manifest['contract_bindings']
    if not isinstance(contract,dict) or set(contract)!={'schema_sha256','checker_sha256','receipt_sha256','publisher_sha256'} or any(not isinstance(value,str) or len(value)!=64 or any(char not in '0123456789abcdef' for char in value) for value in contract.values()):raise BundleFault('malformed-published-contract-bindings')
    if expected_contract is not None and not r.same_json(contract,expected_contract):raise BundleFault('published-contract-build-substitution')
    identity={key:value for key,value in manifest.items() if key!='bundle_id'};identity_sha=e.digest(identity)
    if manifest['bundle_id']!='bundle:'+identity_sha or bundle_ref.rsplit('/',1)[-1]!='bundle-'+identity_sha:raise BundleFault('bundle-identity-or-directory-mismatch')
    if r.digest(envelope_raw)!=manifest['envelope_sha256'] or manifest['required_set_sha256']!=bundle['required_set']['required_set_sha256']:raise BundleFault('envelope-or-required-set-binding-mismatch')
    selected=e.artifact_refs(bundle)
    if len(manifest['files'])!=len(selected):raise BundleFault('published-artifact-denominator-mismatch')
    captured={};objects=set()
    for row,ref in zip(manifest['files'],selected):
        if not isinstance(row,dict) or set(row)!={'path','sha256','size_bytes','object_path'} or row['path']!=ref['path'] or row['sha256']!=ref['sha256'] or row['object_path']!='objects/'+ref['sha256']+'.bin' or type(row['size_bytes']) is not int or row['size_bytes']<0:raise BundleFault('published-file-binding-mismatch')
        raw=r.read_bytes(root,bundle_ref+'/'+row['object_path'])
        if r.digest(raw)!=row['sha256'] or len(raw)!=row['size_bytes']:raise BundleFault('corrupt-published-object',row['path'])
        captured[row['path']]=raw;objects.add(row['sha256']+'.bin')
    parent,name=r.open_parent(root,bundle_ref+'/unused-marker')
    try:
        if set(os.listdir(parent))!={'objects','manifest.json','envelope.json'}:raise BundleFault('unexpected-published-file')
        fd=os.open('objects',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
        try:
            if set(os.listdir(fd))!=objects:raise BundleFault('unexpected-or-missing-published-object')
        finally:os.close(fd)
    finally:os.close(parent)
    report=e.check(bundle,expected_required,captured=captured)
    if report['status']!='candidate-accounted':raise BundleFault('published-contract-accounting-invalid')
    snapshot=validate_snapshot(bundle,captured,live_source_root)
    return {'result':'PASS','authority_effect':'none','semantic_ready':False,'bundle_id':manifest['bundle_id'],'files':len(captured),'source_currentness':'verified-live' if live_source_root is not None else 'historical-capture-only','producer_build':'compared-with-independently-selected-build' if expected_contract is not None else 'historical-claim-not-independently-selected','contract_accounting':report,'claim_ceiling':'Exact closed captured package/source bindings only; no model/solver/theorem truth, owner fidelity or readiness.'}
