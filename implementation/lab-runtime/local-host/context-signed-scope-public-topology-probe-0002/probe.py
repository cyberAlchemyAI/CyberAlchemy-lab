"""Inert public three-bind Docker projection; no dispatch entrypoint."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import types

HERE=Path(__file__).resolve().parent
LOCAL=HERE.parent
FAMILY=Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
STAGE_TARGET=FAMILY/'reader-stage-attempt/root'
BUNDLE=FAMILY/'context-signed-scope-portable-bundle-0001'
PLAN=LOCAL/'context-successor-signed-scope-docker-plan-0002/freeze.json'
PLAN_SHA='957671b00d3055ef23046571a59e1016b2e945290d77c214639092df11cde5fc'
PLAN_REVIEW=LOCAL/'context-successor-signed-scope-docker-plan-independent-review-0002/review.json'
PLAN_REVIEW_SHA='83086cd3c7323fdb4244af0b884e9beb62b26f39c323a4101f69dd59afb6235f'
PREDECESSOR=LOCAL/'context-signed-scope-public-topology-probe-0001/freeze.json'
PREDECESSOR_SHA='26b2911798621e9acb1cefd1a2428f310e1e79ee6aedb9bf201c235991460378'
PREDECESSOR_REVIEW=LOCAL/'context-signed-scope-public-topology-probe-independent-review-0001/review.json'
PREDECESSOR_REVIEW_SHA='472d8669e727d6b5647f136e055859a2f169600c74b24264c94fb150fb2c8301'
PORTABLE=LOCAL/'context-signed-scope-portable-bundle-0002'
PORTABLE_SHA='b6a57791f21464e5b3bb8b568cd9cbbf42c96288528fc68e622cb7d70afd2d7f'
PORTABLE_REVIEW=LOCAL/'context-signed-scope-portable-bundle-independent-review-0002/review.json'
PORTABLE_REVIEW_SHA='c2023455d719c874bd7113e2fb4ddc95cb44b1bba4cf3df671450e166c150457'
CHILD=HERE/'child.py'
CHILD_SHA='504d09e31f028407622d13adc2bdd565a2befdf0ec22135260f034c9b60dd37f'
DOCKER='/usr/bin/docker'
DOCKER_SHA='999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00'
IMAGE='sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
NAME='cal-context-signed-scope-public-topology-20261020-0002'
STAGE_MARKER=b'public-only signed-scope topology stage; no private archive\n'
CLAIM_MARKER=b'public-only signed-scope topology claim; no authority\n'
EFFECT_ENABLED=False
READ=os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC

class Refused(RuntimeError):pass
def need(ok,code):
    if not ok:raise Refused(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):
    def unique(rows):
        out={}
        for key,value in rows:
            need(key not in out,'DUPLICATE_JSON_KEY')
            out[key]=value
        return out
    return json.loads(raw,object_pairs_hook=unique)
def held(path,digest,maximum=1024*1024,mode=None,owners=None):
    path=Path(path)
    need(path.is_absolute() and '..' not in path.parts,'PIN_PATH')
    fd=os.open(path,READ)
    try:
        first=os.fstat(fd)
        allowed=(os.getuid(),) if owners is None else owners
        need(stat.S_ISREG(first.st_mode) and first.st_nlink==1 and
             first.st_uid in allowed and not(first.st_mode&0o022) and
             (mode is None or stat.S_IMODE(first.st_mode)==mode) and
             0<first.st_size<=maximum,'PIN_CUSTODY')
        raw=os.read(fd,first.st_size+1)
        second=os.fstat(fd)
        named=os.stat(path,follow_symlinks=False)
        key=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,
                      s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        need(len(raw)==first.st_size and key(first)==key(second)==key(named) and
             sha(raw)==digest,'PIN_DRIFT')
        return raw,first
    finally:os.close(fd)

def basis():
    plan=parse(held(PLAN,PLAN_SHA,65536)[0])
    review=parse(held(PLAN_REVIEW,PLAN_REVIEW_SHA,65536)[0])
    predecessor=parse(held(PREDECESSOR,PREDECESSOR_SHA,65536)[0])
    predecessor_review=parse(held(PREDECESSOR_REVIEW,PREDECESSOR_REVIEW_SHA,65536)[0])
    portable=parse(held(PORTABLE/'freeze.json',PORTABLE_SHA,65536)[0])
    portable_review=parse(held(PORTABLE_REVIEW,PORTABLE_REVIEW_SHA,65536)[0])
    need(predecessor['effect_enabled'] is False and
         predecessor_review['verdict']=='HOLD_INCOMPLETE_MOUNTINFO_CAPTURE' and
         predecessor_review['candidate_freeze_sha256']==PREDECESSOR_SHA and
         predecessor['members']['child.py']==
         '000a19c5dd2b48a6024a74222e47d4978464e60fb981ca7b903cf3a5b21423b2' and
         predecessor['docker_create_or_start']=='NOT_RUN' and
         plan['effect_enabled'] is False and plan['real_effect']=='NOT_RUN' and
         review['verdict']=='PASS_BOUNDED_INERT_PLAN_ONLY' and
         review['candidate_freeze_sha256']==PLAN_SHA and
         review['effect_ready'] is False and
         portable['effect_enabled'] is False and
         portable['durable_bundle_0002']=='ABSENT' and
         portable_review['verdict']=='PASS_BOUNDED_INERT_BUNDLE_CORRECTION' and
         portable_review['candidate_freeze_sha256']==PORTABLE_SHA and
         portable['predecessor_hold_review_sha256']==
         'e2128784a3abdc2bbfef26135e1f5a68c6809581b2c59c148d0aef7aa86ab0e7',
         'PREDECESSOR_SCOPE')
    raw,_=held(PORTABLE/'portable.py',portable['members']['portable.py'])
    module=types.ModuleType('checked_inert_portable_bundle_0002')
    module.__file__=str(PORTABLE/'portable.py')
    exec(compile(raw,module.__file__,'exec'),module.__dict__)
    need(module.EFFECT_ENABLED is False and
         module.BUNDLE_MANIFEST_SHA==portable['selected_manifest_sha256'] and
         module.IMAGE==IMAGE and module.DEFAULT_BUNDLE!=BUNDLE,
         'PORTABLE_BUNDLE_SCOPE')
    audit=module.audit_bundle(BUNDLE)
    need(audit['blobs']==105 and audit['private_archive']=='NOT_COPIED' and
         audit['manifest_sha256']==portable['selected_manifest_sha256'],
         'PUBLIC_RETAINED_BUNDLE_AUDIT')
    return {'schema':'context-signed-scope-public-topology-basis/v1-inert',
            'plan_freeze_sha256':PLAN_SHA,'plan_review_sha256':PLAN_REVIEW_SHA,
            'predecessor_freeze_sha256':PREDECESSOR_SHA,
            'predecessor_hold_review_sha256':PREDECESSOR_REVIEW_SHA,
            'portable_freeze_sha256':PORTABLE_SHA,
            'portable_review_sha256':PORTABLE_REVIEW_SHA,
            'portable_review':'PASS_BOUNDED_INERT_BUNDLE_CORRECTION',
            'retained_bundle_manifest_sha256':module.BUNDLE_MANIFEST_SHA,
            'private_archive':'UNOPENED','effect':'NOT_RUN'}

def fixture(stage,claim):
    stage=Path(stage);claim=Path(claim)
    need(stage.is_absolute() and claim.is_absolute() and
         stage.parent==claim.parent and stage.name=='stage' and
         claim.name=='attempt.claim' and
         stage.parent.parent==FAMILY and
         stage.parent.name.startswith('fixture-signed-scope-topology-'),
         'PUBLIC_FIXTURE_PATHS')
    for path in (stage.parent,stage):
        st=os.stat(path,follow_symlinks=False)
        need(stat.S_ISDIR(st.st_mode) and st.st_uid==os.getuid() and
             stat.S_IMODE(st.st_mode)==0o700,'PUBLIC_FIXTURE_DIRECTORY')
    need(set(os.listdir(stage))=={'.public-topology-only'},
         'SYNTHETIC_STAGE_EXACT_ONLY')
    held(stage/'.public-topology-only',sha(STAGE_MARKER),1024,0o600)
    raw,st=held(claim,sha(CLAIM_MARKER),1024,0o600)
    need(raw==CLAIM_MARKER,'PUBLIC_CLAIM_MARKER')
    return {'stage':str(stage),'claim':str(claim),
            'claim_dev':st.st_dev,'claim_ino':st.st_ino,
            'stage_marker_sha256':sha(STAGE_MARKER),
            'claim_marker_sha256':sha(CLAIM_MARKER)}

def projection(stage,claim,token):
    selected=basis()
    public=fixture(stage,claim)
    need(type(token) is str and re.fullmatch('[0-9a-f]{32}',token),
         'PUBLIC_NONCE_SHAPE')
    child,_=held(CHILD,CHILD_SHA,65536)
    config={k:public[k] for k in ('claim_dev','claim_ino',
                                   'stage_marker_sha256','claim_marker_sha256')}
    argv=[DOCKER,'create','--name',NAME,
          '--label','cal.context.public-topology='+token,
          '--network','none','--read-only','--cap-drop','ALL',
          '--security-opt','no-new-privileges','--pids-limit','128',
          '--memory','1g','--cpus','1','--user','1000:1000',
          '--mount',f'type=bind,src={stage},dst={STAGE_TARGET},readonly',
          '--mount',f'type=bind,src={BUNDLE},dst=/bundle,readonly',
          '--mount',f'type=bind,src={claim},dst=/control/attempt.claim,readonly',
          '--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777',
          '--tmpfs','/scratch:rw,nosuid,nodev,size=512m,mode=0700,uid=1000,gid=1000',
          IMAGE,'python','-I','-B','-c',child.decode('utf-8'),
          json.dumps(config,sort_keys=True,separators=(',',':'))]
    mounts=[argv[i+1] for i,value in enumerate(argv) if value=='--mount']
    need(len(mounts)==3 and
         not any(f'src={STAGE_TARGET},' in mount for mount in mounts),
         'NO_ACTUAL_PRIVATE_STAGE_MOUNT')
    return {'schema':'context-signed-scope-public-three-bind-projection/v1-inert',
            'effect_enabled':False,'docker_invoked':False,
            'name':NAME,'image':IMAGE,'basis':selected,'fixture':public,
            'create_argv':argv,'private_archive':'ABSENT',
            'signed_scope':'NOT_OPENED'}

def readonly_docker_preflight(runner=subprocess.run):
    held(DOCKER,DOCKER_SHA,100*1024*1024,owners=(0,))
    image=runner([DOCKER,'image','inspect',IMAGE,'--format',
                  '{{.Id}} {{.Architecture}} {{.Config.User}} {{.Config.WorkingDir}}'],
                 stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,timeout=10,check=False)
    need(type(image.returncode) is int and image.returncode==0 and
         type(image.stdout) is bytes and type(image.stderr) is bytes and
         image.stdout==f'{IMAGE} amd64 20001:20001 /attempt/root\n'.encode() and
         image.stderr==b'','DOCKER_IMAGE_PREFLIGHT')
    absent=runner([DOCKER,'container','inspect',NAME,'--format','{{.Id}}'],
                  stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                  stderr=subprocess.PIPE,timeout=10,check=False)
    need(type(absent.returncode) is int and absent.returncode==1 and
         type(absent.stdout) is bytes and type(absent.stderr) is bytes and
         absent.stdout==b'\n' and
         absent.stderr==('Error response from daemon: No such container: '+NAME+'\n').encode(),
         'DOCKER_NAME_PREFLIGHT')
    return {'image':IMAGE,'name_absent':True,'image_stdout_sha256':sha(image.stdout),
            'absence_stderr_sha256':sha(absent.stderr),'docker_effect':'NOT_RUN'}

def dispatch(*_args,**_kwargs):raise Refused('EFFECT_DISABLED_NO_PUBLIC_DOCKER_CREATE')
