"""Exact historical API originals from terminal common-caller observations.

This reader reconstructs no old channel, Session, signer, or Source currentness.
A fresh separately authenticated coordinator must authorize later effects.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import stat

FIELDS={'scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256'}
def need(value,message):
    if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def relative(value):
    need(type(value)is str and value and '\\'not in value and '\0'not in value,'closed archive member required')
    path=Path(value);need(not path.is_absolute() and path.as_posix()==value and '..'not in path.parts and value!='.','closed archive member required');return path
def read(path):
    path=Path(path);need(path.is_absolute() and '..'not in path.parts,'absolute selected original path required')
    handles=[]
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);handles.append(parent)
        for part in path.parts[1:-1]:
            parent=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);handles.append(parent)
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent);handles.append(fd);before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_nlink==1
             and stat.S_IMODE(before.st_mode)==0o600 and before.st_size<=16*1024*1024,'bounded private original required')
        chunks=[];size=0
        while raw:=os.read(fd,65536):chunks.append(raw);size+=len(raw);need(size<=before.st_size,'original grew during capture')
        stamp=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)) and size==before.st_size,
             'selected original changed during capture')
        return b''.join(chunks)
    finally:
        for handle in reversed(handles):os.close(handle)

def consume(*,archive,observation_sha256,terminal_result,terminal_sha256,source_sha256,profile_sha256,operation):
    archive=Path(archive).absolute();terminal_result=Path(terminal_result).absolute()
    need(archive.is_dir() and not archive.is_symlink() and archive.stat().st_uid==os.getuid()
         and stat.S_IMODE(archive.stat().st_mode)==0o700,'private retained original archive required')
    traw=read(terminal_result);need(sha(traw)==terminal_sha256,'independently selected terminal result differs');terminal=json.loads(traw)
    need(terminal['result']=='PASS' and terminal['source_sha256']==source_sha256 and terminal['profile_sha256']==profile_sha256,
         'terminal original operation unit is not a passing exact selection')
    oraw=read(archive/'OBSERVATION.json');need(sha(oraw)==observation_sha256,'independently selected observation differs');observed=json.loads(oraw)
    need(observed['schema_version']=='lab-retained-actual-caller-vault/v1' and observed['Reader_credentials_retained']is False
         and observed['current_permission_or_Session_reconstructed']is False and observed['requires_unit_terminal_PASS']is True
         and observed['authority_effect']=='none','bounded original retention contract differs')
    witness=observed['observation'];case=witness['case']
    need(witness['source_sha256']==source_sha256 and witness['profile_sha256']==profile_sha256 and witness['unit']==terminal['unit'],
         'actual retained producer selection differs')
    selected=[c for c in terminal['cases'] if c.get('retained_originals',{}).get('path')==str(archive)
              and c['retained_originals']['observation_sha256']==observation_sha256]
    need(len(selected)==1 and all(selected[0].get(k)==v for k,v in case.items()),'retained case is not exact terminal original')
    need(case['result']=='PASS' and case['operation']==operation and case['expected_kind']=='result','actual producer did not complete successful operation')
    request_raw=base64.b64decode(case['original_request_base64'],validate=True);request=json.loads(request_raw);reply=case['actual_reply']
    need(sha(request_raw)==case['request_sha256']==reply['request_binding']['sha256'] and request==witness['original_request']
         and request['operation']==reply['operation']==operation and reply['kind']=='result'
         and reply['contract_profile_binding']['sha256']==profile_sha256,'actual original request/reply/profile binding differs')
    files={}
    for row in observed['files']:
        need(type(row)is dict and set(row)=={'path','sha256','size_bytes'},'closed original archive row required')
        rel=relative(row['path']);need(str(rel)not in files,'duplicate retained archive member')
        raw=read(archive/rel);need(sha(raw)==row['sha256'] and len(raw)==row['size_bytes'],'actual retained original member differs')
        need(b'PRIVATE KEY-----'not in raw,'credential is not eligible retained workflow evidence');files[str(rel)]=raw
    actual={p.relative_to(archive).as_posix() for p in archive.rglob('*') if p.is_file()}
    need(not any(p.is_symlink() for p in archive.rglob('*')) and actual==set(files)|{'OBSERVATION.json'},'retained original archive closure differs')
    outputs=[];candidate_targets={}
    projection=None
    if operation=='proposal.review':
        candidates=[reply['message']['decision_bundle'],reply['message']['checkpoint']]
    elif operation=='ontology.project':
        receipt=reply['message']
        need(receipt['schema_version']=='lab-ontology-projection-receipt/v1-candidate' and receipt['posture']=='applied'
             and receipt['lab_source_cut']==request['expected_source_cut'] and receipt['authority_effect']=='none'
             and receipt['recovery_required']is False,'actual projection producer did not complete its bounded representation')
        originals=[]
        for name,raw in files.items():
            if name.startswith('vault/objects/') and name.endswith('.json'):
                try:value=json.loads(raw)
                except (ValueError,UnicodeError):continue
                if value==receipt:originals.append((name,raw))
        need(len(originals)==1,'one exact retained projection result original required')
        name,raw=originals[0]
        need(Path(name).stem==sha(raw),'actual projection receipt object address differs')
        projection={'producer_kind':'actual-ontology-projection','receipt':receipt,'receipt_original':raw,
                    'receipt_original_binding':{'ref':str(archive/name),'sha256':sha(raw)},
                    'typed_generation_headers_inferred':False}
        # This view is actually returned by ontology.project. The generation's
        # other rich carriers still need an explicit original capture contract.
        candidates=[receipt['ontology_view']]
    else:
        targets=reply['message'].get('targets',[])
        candidates=[target.get('artifact') for target in targets]
        candidate_targets={target['artifact']['version_ref']:target for target in targets}
        need(len(candidate_targets)==len(targets),'duplicate actual returned candidate revision')
    for header in candidates:
        need(type(header)is dict and set(header)in(FIELDS,FIELDS|{'candidate_contract_binding'}),'exact original candidate artifact header required')
        header={k:header[k] for k in FIELDS};digest=header['byte_sha256'];name='vault/objects/'+digest+'.json'
        target=candidate_targets.get(header['version_ref'])
        if target is None:
            need(name in files and sha(files[name])==digest,'actual typed candidate original missing');raw=files[name]
        else:
            # These operations return an exact prospective ChangeProposal.
            # A returned original may be an independently selected input
            # material or an API-created object.  The latter is eligible only
            # at its exact workspace namespace, content digest and object
            # address, all present in the retained archive closure.
            content=target['content'];need(target['operation']!='withdraw'and content is not None
                 and content['media_type']=='application/json'and content['byte_sha256']==digest,'actual returned candidate content binding differs')
            need('vault/workspace.json'in files,'actual candidate workspace manifest original missing');workspace=json.loads(files['vault/workspace.json'])
            matches=[row for row in workspace['materials']if row['ref']==content['content_ref']]
            if content['content_ref'].startswith('workspace-object:'):
                need(content['content_ref']=='workspace-object:'+workspace['workspace_ref']+':'+digest,
                     'actual returned candidate object namespace differs')
                need(name in files and sha(files[name])==digest and len(files[name])==content['size_bytes'],
                     'actual returned candidate object address or bytes differ')
                raw=files[name]
                need(len(matches)<=1,'ambiguous selected material aliases API-created object')
                if matches:
                    need(matches[0]['sha256']==digest,
                         'selected material alias digest differs from API-created object')
                    path='vault/'+str(relative(matches[0]['path']))
                    need(path in files and files[path]==raw,
                         'selected material alias differs from API-created object')
            else:
                need(len(matches)==1 and matches[0]['sha256']==digest,
                     'actual returned candidate has no exact selected original material')
                path='vault/'+str(relative(matches[0]['path']))
                need(path in files and sha(files[path])==digest and len(files[path])==content['size_bytes'],
                     'actual returned candidate original material differs')
                raw=files[path]
                if name in files:need(files[name]==raw,'copied candidate object differs from original material')
        outputs.append((header,raw))
    need(outputs,'actual successful proposal has no retained typed outputs')
    return {'original_request':request,'actual_reply':reply,'outputs':outputs,'files':files,'projection_producer':projection,
      'observation_binding':{'ref':str(archive/'OBSERVATION.json'),'sha256':observation_sha256},
      'terminal_binding':{'ref':str(terminal_result),'sha256':terminal_sha256},'original_source_cut':request['expected_source_cut'],
      'retained_originals_are_Source_current':False,'old_permission_or_Session_reconstructed':False,'authority_effect':'none'}
