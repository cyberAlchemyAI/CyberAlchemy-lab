"""Capture exact registry/source bytes into a create-only candidate snapshot.

Admission-record presence binds provenance; it does not authenticate real-world
rights. Currentness is checked at capture/publication boundaries, not forever.
POSIX descriptor-relative reads reject every symlink component.
"""
import argparse
import base64
import errno
import hashlib
import json
import os
import stat
import uuid
from pathlib import Path
from contracts import InputError,bounded_tree,finite_float,invalid_constant,pairs,validate

REGISTRY='authority/definitions/registry.json'
OUTPUT_PREFIX='docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/'


class CaptureFault(ValueError):
    def __init__(self,code,path=''):
        self.code=code;self.path=path


def digest(raw):return hashlib.sha256(raw).hexdigest()

def same_json(left,right):
    # Python equates True with 1 and 3.0 with 3; exact JSON metadata must not.
    try:return json.dumps(left,sort_keys=True,separators=(',',':'),allow_nan=False)==json.dumps(right,sort_keys=True,separators=(',',':'),allow_nan=False)
    except (ValueError,TypeError) as error:raise CaptureFault('malformed-snapshot') from error


def components(path):
    if not isinstance(path,str) or not path or '\\' in path or ':' in path or '\x00' in path:
        raise CaptureFault('unsafe-path',str(path))
    parts=path.split('/')
    if any(p in {'','.','..'} for p in parts):raise CaptureFault('unsafe-path',path)
    return parts


def open_parent(root,path,create=False):
    parts=components(path)
    if not hasattr(os,'O_NOFOLLOW'):raise CaptureFault('unsupported-platform',path)
    try:fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    except OSError as error:raise CaptureFault('invalid-root',str(root)) from error
    try:
        for part in parts[:-1]:
            if create:
                try:os.mkdir(part,mode=0o700,dir_fd=fd)
                except FileExistsError:pass
            nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=nxt
        return fd,parts[-1]
    except OSError as error:
        os.close(fd)
        raise CaptureFault('missing-source' if error.errno==errno.ENOENT else 'unsafe-path',path) from error


def read_bytes(root,path):
    parent,name=open_parent(root,path)
    try:
        fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):raise CaptureFault('unsafe-source-kind',path)
            with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(4_000_001)
            if len(raw)>4_000_000:raise CaptureFault('source-byte-limit',path)
            return raw
        finally:os.close(fd)
    except OSError as error:
        raise CaptureFault('missing-source' if error.errno==errno.ENOENT else 'unsafe-path',path) from error
    finally:os.close(parent)


def parse(raw,path):
    try:
        value=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=invalid_constant,parse_float=finite_float)
        bounded_tree(value)
        return value
    except (UnicodeError,ValueError,RecursionError,InputError) as error:
        raise CaptureFault('malformed-source-json',path) from error


def decision_catalog(read,decision_paths):
    catalog={}
    for path in sorted(decision_paths):
        try:raw=read(path);doc=parse(raw,path)
        except CaptureFault:continue  # Unrelated incomplete records are not inputs.
        if not isinstance(doc,dict):continue
        refs=[]
        if isinstance(doc.get('decision_id'),str):refs.append((doc['decision_id'],'/decision_id'))
        if isinstance(doc.get('decision_refs'),list):
            refs.extend((ref,'/decision_refs/'+str(i)) for i,ref in enumerate(doc['decision_refs']) if isinstance(ref,str))
        for ref,selector in refs:
            catalog.setdefault(ref,[]).append({'path':path,'sha256':digest(raw),'selector':selector,'record_status':doc.get('status'),'raw':raw})
    return catalog


def assemble(read,decision_paths,registry_path=REGISTRY):
    captured={}
    def take(path,expected=None):
        components(path)
        raw=read(path)
        sha=digest(raw)
        if expected is not None and sha!=expected:raise CaptureFault('stale-source-hash',path)
        if path in captured and captured[path]!=raw:raise CaptureFault('capture-race',path)
        captured[path]=raw
        return parse(raw,path)
    registry=take(registry_path)
    if not isinstance(registry,dict) or not isinstance(registry.get('entries'),list) or not isinstance(registry.get('current_lookup'),dict):
        raise CaptureFault('malformed-registry',registry_path)
    if registry.get('status')!='owner-admitted':raise CaptureFault('non-admitted-registry',registry_path)
    entries={}
    for entry in registry['entries']:
        if not isinstance(entry,dict) or not {'definition_id','version','path','sha256','term','lifecycle_state','admission_decision_ref'}<=set(entry):
            raise CaptureFault('malformed-registry-entry',registry_path)
        if any(not isinstance(entry[k],str) or not entry[k] for k in ('definition_id','version','path','sha256','term','admission_decision_ref')):
            raise CaptureFault('malformed-registry-entry',registry_path)
        ref=entry['definition_id']+'@'+entry['version']
        if ref in entries:raise CaptureFault('duplicate-version',ref)
        if not isinstance(entry['lifecycle_state'],str) or entry['lifecycle_state'] not in {'admitted','admitted-current','admitted-historical'}:raise CaptureFault('non-admitted-entry',ref)
        entries[ref]=entry
    for identity,ref in registry['current_lookup'].items():
        if not isinstance(identity,str) or not isinstance(ref,str) or ref not in entries or entries[ref]['definition_id']!=identity:raise CaptureFault('unbound-current-selection',str(identity))
        if entries[ref]['lifecycle_state']=='admitted-historical':raise CaptureFault('historical-current-selection',str(identity))
    identities={e['definition_id'] for e in entries.values()}
    if identities!=set(registry['current_lookup']):raise CaptureFault('incomplete-current-lookup',registry_path)
    decision_refs={e['admission_decision_ref'] for e in entries.values()}
    if isinstance(registry.get('admission_decision_ref'),str):decision_refs.add(registry['admission_decision_ref'])
    catalog=decision_catalog(read,decision_paths)
    decisions=[]
    for ref in sorted(decision_refs):
        matches=catalog.get(ref,[])
        if len(matches)!=1:raise CaptureFault('missing-or-ambiguous-admission-record',ref)
        record=matches[0]
        if record['record_status']!='owner-admitted':raise CaptureFault('non-admitted-decision-record',ref)
        captured[record['path']]=record['raw']
        decisions.append({'decision_ref':ref,**{k:record[k] for k in ('path','sha256','selector','record_status')}})
    current=[];historical=[]
    for ref,entry in sorted(entries.items()):
        document=take(entry['path'],entry['sha256'])
        if not isinstance(document,dict) or document.get('definition_id')!=entry['definition_id'] or document.get('version')!=entry['version']:
            raise CaptureFault('source-identity-version-mismatch',entry['path'])
        if document.get('term')!=entry['term']:raise CaptureFault('source-term-mismatch',entry['path'])
        row={**entry,'version_ref':ref,'effective_state':'admitted-current' if registry['current_lookup'][entry['definition_id']]==ref else 'admitted-historical'}
        (current if row['effective_state']=='admitted-current' else historical).append(row)
    def references(rows):return [{k:r[k] for k in ('definition_id','version_ref','path','sha256')} for r in rows]
    envelope={'schema_version':'definition-assurance-input/v1-candidate','kind':'source','authority_effect':'none','payload':{
        'snapshot_id':'snapshot:'+digest(captured[registry_path]),'registry_path':registry_path,'registry_sha256':digest(captured[registry_path]),
        'sources':references(current),'historical_sources':references(historical),'capture_status':'captured',
        'current_lookup_sha256':digest(json.dumps(registry['current_lookup'],sort_keys=True,separators=(',',':')).encode())}}
    if validate(envelope,'source')['status']!='structurally-valid':raise CaptureFault('invalid-captured-envelope',registry_path)
    return {'schema_version':'definition-assurance-source-snapshot/v1-candidate','authority_effect':'none','source_envelope':envelope,
            'current_entries':current,'historical_entries':historical,'admission_decision_bindings':decisions,
            'captured_files':[{'path':path,'sha256':digest(raw),'size_bytes':len(raw),'content_base64':base64.b64encode(raw).decode('ascii')} for path,raw in sorted(captured.items())],
            'counts':{'current_identities':len(current),'admitted_versions':len(entries),'historical_versions':len(historical),'decision_refs':len(decisions)},
            'claim_ceiling':'Exact source bytes and selected effective registry references. No source-fidelity theorem, real authorization authentication or semantic admission.',
            'currentness':'Verified at capture and publication boundaries; recheck exact bindings before later use.'}


def resolve_root(root):
    try:
        candidate=Path(root)
        if candidate.is_symlink():raise CaptureFault('invalid-root',str(root))
        resolved=candidate.resolve(strict=True)
        if not resolved.is_dir():raise CaptureFault('invalid-root',str(root))
        return resolved
    except (OSError,ValueError) as error:
        if isinstance(error,CaptureFault):raise
        raise CaptureFault('invalid-root',str(root)) from error


def catalog_paths(root):
    return [file.relative_to(root).as_posix() for file in (root/'docs/decisions').glob('*/decision.json')]


def capture(root,registry_path=REGISTRY,after_capture=None):
    root=resolve_root(root)
    snapshot=assemble(lambda path:read_bytes(root,path),catalog_paths(root),registry_path)
    if after_capture:after_capture()
    for row in snapshot['captured_files']:
        if read_bytes(root,row['path'])!=base64.b64decode(row['content_base64']):raise CaptureFault('capture-race',row['path'])
    # A newly introduced conflicting admission record also invalidates capture.
    if not same_json(snapshot,assemble(lambda path:read_bytes(root,path),catalog_paths(root),registry_path)):
        raise CaptureFault('capture-race',registry_path)
    return snapshot


def verify(snapshot,root=None):
    if not isinstance(snapshot,dict):raise CaptureFault('malformed-snapshot')
    captured={}
    try:
        for row in snapshot['captured_files']:
            path=row['path'];components(path)
            if path in captured:raise CaptureFault('duplicate-captured-path',path)
            try:raw=base64.b64decode(row['content_base64'],validate=True)
            except (ValueError,TypeError) as error:raise CaptureFault('malformed-captured-bytes',path) from error
            if len(raw)!=row['size_bytes'] or digest(raw)!=row['sha256']:raise CaptureFault('corrupt-captured-bytes',path)
            captured[path]=raw
        def read(path):
            if path not in captured:raise CaptureFault('missing-captured-source',path)
            return captured[path]
        registry_path=snapshot['source_envelope']['payload']['registry_path']
        paths=[path for path in captured if path.startswith('docs/decisions/') and path.endswith('/decision.json')]
        reconstructed=assemble(read,paths,registry_path)
        if not same_json(snapshot,reconstructed):raise CaptureFault('inconsistent-snapshot-bindings',registry_path)
        if root is not None:
            root=resolve_root(root)
            for path,raw in captured.items():
                if read_bytes(root,path)!=raw:raise CaptureFault('stale-captured-source',path)
            if not same_json(capture(root,registry_path),snapshot):raise CaptureFault('stale-captured-selection',registry_path)
    except (KeyError,TypeError,IndexError,AttributeError) as error:
        raise CaptureFault('malformed-snapshot') from error
    return {'result':'PASS','files':len(captured),'meaning':'Exact snapshot bytes and reconstructed registry/source/provenance bindings'+(' with currentness checked against repository' if root is not None else '')+'. No semantic proof.'}


def publish(snapshot,root,output):
    if not isinstance(output,str) or not output.startswith(OUTPUT_PREFIX):raise CaptureFault('protected-output',output)
    root=resolve_root(root)
    parent,name=open_parent(root,output,create=True)
    temporary='.capture-'+uuid.uuid4().hex+'.tmp'
    try:
        fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parent)
        with os.fdopen(fd,'wb') as stream:
            stream.write((json.dumps(snapshot,indent=2,sort_keys=True)+'\n').encode());stream.flush();os.fsync(stream.fileno())
        verify(snapshot,root)
        try:os.link(temporary,name,src_dir_fd=parent,dst_dir_fd=parent,follow_symlinks=False)
        except FileExistsError as error:raise CaptureFault('output-already-exists',output) from error
        os.fsync(parent)
    except OSError as error:
        raise CaptureFault('publication-io-failure',output) from error
    finally:
        try:os.unlink(temporary,dir_fd=parent)
        except FileNotFoundError:pass
        os.close(parent)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repo',required=True);parser.add_argument('--output')
    args=parser.parse_args()
    try:
        snapshot=capture(args.repo)
        if args.output:publish(snapshot,args.repo,args.output)
        print(json.dumps({'result':'PASS','authority_effect':'none','counts':snapshot['counts'],'published':args.output,
                          'claim_ceiling':snapshot['claim_ceiling']},indent=2));return 0
    except CaptureFault as error:
        print(json.dumps({'result':'unresolved','code':error.code,'path':error.path,'authority_effect':'none'},indent=2));return 2


if __name__=='__main__':raise SystemExit(main())
