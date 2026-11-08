"""Inert Docker signed-scope projection. There is no dispatch entrypoint."""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

HERE=Path(__file__).resolve().parent
LOCAL=HERE.parent
FAMILY=Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
STAGE=FAMILY/'reader-stage-attempt/root'
READER_ROLE='product/lab/release-candidates/v1/interface/docker-reader-20261020-0002'
SOURCE_ROLE='product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
LOADER=LOCAL/'context-successor-checked-reader-loader-0001'
LOADER_FREEZE_SHA='34dc11dc1977b47ef67f7ab9b900945e86cb8afa618b8c8845af3b56f90e979c'
LOADER_CODE_SHA='740699aa42c842030dc348f65a236799a131f65a5eb37aa5ba4e926cb93832b2'
LOADER_REVIEW=LOCAL/'context-successor-checked-reader-loader-independent-review-0001/review.json'
LOADER_REVIEW_SHA='5cbf80fff93841396c83a8a0590893435611c4fe0f97d3efe481ab43fa74962a'
CONTROLLER=LOCAL/'context-successor-signed-scope-controller-0002'
CONTROLLER_FREEZE_SHA='be4fad673eb559ddf810fae4b0bfa8e288c46c8c68b1e90902310d8deb8c8bc7'
CONTROLLER_CODE_SHA='63e0b4483690cfddc40c55e82949677b09f980cbd4e979f15d563d77ce9be5c3'
CONTROLLER_REVIEW=LOCAL/'context-successor-signed-scope-controller-independent-review-0002/review.json'
CONTROLLER_REVIEW_SHA='02ad3bfbe9e2fde09b3ac7df742fcaac33a1c1fd37079cad155445e2ae66dd11'
PREDECESSOR=LOCAL/'context-successor-signed-scope-docker-plan-0001'
PREDECESSOR_FREEZE_SHA='25bab1294c5a11e886c05a582d5c4135f0f2be50dddfcb74040655068e5903d2'
PREDECESSOR_REVIEW=LOCAL/'context-successor-signed-scope-docker-plan-independent-review-0001/review.json'
PREDECESSOR_REVIEW_SHA='d4b5b25ec3fb881f81301c92208f4c6589f9f6763e2cd90e3279a7714301b236'
PORTABLE=LOCAL/'context-signed-scope-portable-bundle-0001'
PORTABLE_FREEZE_SHA='47f593a19daaa0f3c74735b1d478650c7281100a4f5c243a88a9348c3bcacad3'
BUNDLE=FAMILY/'context-signed-scope-portable-bundle-0001'
BUNDLE_MANIFEST_SHA='1419dc09dd5139ed0335e74efdc94d1b05cc961da74ca49a00ac6f8ac026be8f'
READER_MANIFEST_SHA='048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756'
SOURCE_MANIFEST_SHA='2843a67fd28a295f5c175b8d8c2b31f701040bb8d7dedeade8d76bbdf057d1d1'
PERIOD_SHA='3ff862090a38b346a384001c2d87da7cf648f18726fb056653a0fb4df40473ba'
IMAGE='sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
DOCKER='/usr/bin/docker'
DOCKER_SHA='999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00'
NAME='cal-context-signed-scope-20261020-0001'
CLAIM=FAMILY/'context-signed-scope-attempt-0002.claim'
ATTESTATION=FAMILY/'context-signed-scope-attestation-0002.json'
SCOPE='scope:cyberalchemy-lab-first-agent-episode'
EFFECT_ENABLED=False
READ_FLAGS=os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC

class Refused(RuntimeError):pass
def need(value,code):
    if not value:raise Refused(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):
    def unique(pairs):
        result={}
        for key,value in pairs:
            need(key not in result,'DUPLICATE_JSON_KEY')
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refused('NONFINITE_JSON')))
def checked(path,digest,maximum=2*1024*1024,owners=None):
    path=Path(path)
    owners=(os.getuid(),) if owners is None else owners
    need(path.is_absolute() and '..' not in path.parts,'PIN_PATH')
    fd=os.open(path,READ_FLAGS)
    try:
        before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and
             before.st_uid in owners and not(before.st_mode&0o022) and
             0<before.st_size<=maximum,'PIN_CUSTODY')
        raw=os.read(fd,before.st_size+1)
        after=os.fstat(fd)
        named=os.stat(path,follow_symlinks=False)
        key=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,
                      s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        need(len(raw)==before.st_size and key(before)==key(after)==key(named)
             and sha(raw)==digest,'PIN_DRIFT')
        return raw
    finally:os.close(fd)

def pinned_basis(now=None):
    now=dt.datetime.now(dt.timezone.utc) if now is None else now
    need(type(now) is dt.datetime and now.tzinfo is not None and
         now.utcoffset()==dt.timedelta(),'CURRENT_UTC')
    loader_freeze=parse(checked(LOADER/'freeze.json',LOADER_FREEZE_SHA,65536))
    review=parse(checked(LOADER_REVIEW,LOADER_REVIEW_SHA,65536))
    controller_freeze=parse(checked(CONTROLLER/'freeze.json',CONTROLLER_FREEZE_SHA,65536))
    controller_review=parse(checked(CONTROLLER_REVIEW,CONTROLLER_REVIEW_SHA,65536))
    predecessor=parse(checked(PREDECESSOR/'freeze.json',PREDECESSOR_FREEZE_SHA,65536))
    predecessor_review=parse(checked(PREDECESSOR_REVIEW,PREDECESSOR_REVIEW_SHA,65536))
    portable=parse(checked(PORTABLE/'freeze.json',PORTABLE_FREEZE_SHA,65536))
    bundle_manifest=parse(checked(BUNDLE/'manifest.json',BUNDLE_MANIFEST_SHA,512*1024))
    need(loader_freeze['effect_enabled'] is False and
         loader_freeze['members']['checked_loader.py']==LOADER_CODE_SHA and
         review['verdict']=='PASS_BOUNDED_INERT_BUFFER_LOADER_ONLY' and
         review['candidate_freeze_sha256']==LOADER_FREEZE_SHA and
         review['effect_release_ready'] is False and
         review['private_archive_opened'] is False and
         review['reader_rows']==948 and review['source_rows']==940 and
         controller_freeze['effect_enabled'] is False and
         controller_freeze['members']['controller.py']==CONTROLLER_CODE_SHA and
         controller_review['verdict']=='PASS_BOUNDED_INERT_HELD_FILE_FIXTURE_ONLY' and
         controller_review['candidate_freeze_sha256']==CONTROLLER_FREEZE_SHA and
         controller_review['real_effect']=='NOT_RUN' and
         controller_review['real_attempt_absent'] is True and
         controller_review['private_archive_body']=='UNOPENED' and
         controller_freeze['predecessor_hold_review_sha256']==
         '3c3ecf98743f598959d5c8a79b237fe42d72954732282f377b0d5450aaa8cb92' and
         predecessor['effect_enabled'] is False and
         predecessor_review['candidate_freeze_sha256']==PREDECESSOR_FREEZE_SHA and
         predecessor_review['verdict']=='HOLD_STRICT_SCALAR_OBSERVER_CORRECTION' and
         portable['effect_enabled'] is False and
         portable['selected_bundle_manifest_sha256']==BUNDLE_MANIFEST_SHA and
         portable['status']=='HOLD_BUNDLE_ONLY_SIGNED_OPEN_AND_PRIVATE_STAGE_MOUNT' and
         portable['selected_image']==IMAGE,
         'PREDECESSOR_SCOPE')
    need(type(bundle_manifest) is dict and
         bundle_manifest.get('schema')=='context-portable-reader-buffers/v1-inert' and
         bundle_manifest.get('image')==IMAGE and
         bundle_manifest.get('loader_freeze_sha256')==LOADER_FREEZE_SHA and
         bundle_manifest.get('loader_review_sha256')==LOADER_REVIEW_SHA and
         bundle_manifest.get('private_archive')=='NOT_COPIED',
         'PORTABLE_BUNDLE_MANIFEST')
    bundle_stat=os.stat(BUNDLE,follow_symlinks=False)
    need(stat.S_ISDIR(bundle_stat.st_mode) and bundle_stat.st_uid==os.getuid() and
         stat.S_IMODE(bundle_stat.st_mode)==0o700,'PORTABLE_BUNDLE_CUSTODY')
    checked(LOADER/'checked_loader.py',LOADER_CODE_SHA)
    checked(CONTROLLER/'controller.py',CONTROLLER_CODE_SHA)
    reader=parse(checked(STAGE/READER_ROLE/'source-manifest.json',READER_MANIFEST_SHA))
    source=parse(checked(STAGE/SOURCE_ROLE/'source-manifest.json',SOURCE_MANIFEST_SHA))
    period=parse(checked(STAGE/SOURCE_ROLE/'packages/0001/period.json',PERIOD_SHA,65536))
    need(reader['producer_source_binding']==
         {'path':SOURCE_ROLE+'/source-manifest.json','sha256':SOURCE_MANIFEST_SHA} and
         source['environment']=={'python':'3.14.4','jsonschema':'4.23.0',
                                 'cryptography':'46.0.5'} and
         period['authority_effect']=='none' and period['actual_owner_outcome'] is None and
         dt.datetime.fromisoformat(period['not_before'])<=now<
         dt.datetime.fromisoformat(period['expires_at']),
         'SELECTED_SOURCE_PERIOD_OR_ENVIRONMENT')
    stage_stat=os.stat(STAGE,follow_symlinks=False)
    parent_stat=os.stat(STAGE.parent,follow_symlinks=False)
    need(stat.S_ISDIR(stage_stat.st_mode) and stage_stat.st_uid==1000 and
         stage_stat.st_gid==1000 and stat.S_IMODE(stage_stat.st_mode)==0o755 and
         stat.S_ISDIR(parent_stat.st_mode) and parent_stat.st_uid==1000 and
         parent_stat.st_gid==1000 and stat.S_IMODE(parent_stat.st_mode)==0o700,
         'STAGE_ROOT_CUSTODY')
    need(not os.path.lexists(CLAIM) and not os.path.lexists(ATTESTATION),
         'ATTEMPT_ALREADY_CONSUMED')
    return {'schema':'context-docker-signed-scope-basis/v1-inert',
            'source_period_start':period['not_before'],
            'source_period_end':period['expires_at'],
            'source_period_sha256':PERIOD_SHA,
            'reader_manifest_sha256':READER_MANIFEST_SHA,
            'reader_code_sha256':loader_freeze['selected_reader_code_sha256'],
            'source_manifest_sha256':SOURCE_MANIFEST_SHA,
            'loader_freeze_sha256':LOADER_FREEZE_SHA,
            'loader_review_sha256':LOADER_REVIEW_SHA,
            'controller_freeze_sha256':CONTROLLER_FREEZE_SHA,
            'controller_review_sha256':CONTROLLER_REVIEW_SHA,
            'predecessor_hold_review_sha256':PREDECESSOR_REVIEW_SHA,
            'portable_freeze_sha256':PORTABLE_FREEZE_SHA,
            'portable_bundle_manifest_sha256':BUNDLE_MANIFEST_SHA,
            'scope_expected':SCOPE,'effect':'NOT_RUN'}

def docker_readonly_observation(runner=subprocess.run):
    checked(DOCKER,DOCKER_SHA,100*1024*1024,(0,))
    argv=[DOCKER,'image','inspect',IMAGE,'--format',
          '{{.Id}} {{.Architecture}} {{.Config.User}} {{.Config.WorkingDir}}']
    result=runner(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                  stderr=subprocess.PIPE,timeout=10,check=False)
    need(type(result.returncode) is int and result.returncode==0 and
         type(result.stdout) is bytes and type(result.stderr) is bytes and
         len(result.stdout)<=4096 and
         result.stderr==b'' and result.stdout==
         f'{IMAGE} amd64 20001:20001 /attempt/root\n'.encode(),
         'DOCKER_IMAGE_ID_OR_CONFIG')
    absent=runner([DOCKER,'container','inspect',NAME,'--format','{{.Id}}'],
                  stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                  stderr=subprocess.PIPE,timeout=10,check=False)
    expected_error=('Error response from daemon: No such container: '+NAME+'\n').encode()
    need(type(absent.returncode) is int and absent.returncode==1 and
         type(absent.stdout) is bytes and type(absent.stderr) is bytes and
         absent.stdout==b'\n' and
         absent.stderr==expected_error and
         len(absent.stdout)<=4096 and len(absent.stderr)<=4096,
         'DOCKER_NAME_ABSENCE')
    return {'image_id':IMAGE,'architecture':'amd64',
            'image_default_user':'20001:20001',
            'selected_user':'1000:1000',
            'image_observation_sha256':sha(result.stdout),
            'container_absent':True,
            'absence_observation_sha256':sha(absent.stderr)}

def projected_create_argv(token):
    """Only a command projection; claim and reviewed child are absent."""
    need(type(token) is str and re.fullmatch('[0-9a-f]{32}',token),
         'ONE_SHOT_LABEL_SHAPE')
    stage=str(STAGE)
    return [DOCKER,'create','--name',NAME,'--label','cal.context.signed-scope='+token,
            '--network','none','--read-only','--cap-drop','ALL',
            '--security-opt','no-new-privileges','--pids-limit','128',
            '--memory','1g','--cpus','1','--user','1000:1000',
            '--mount',f'type=bind,src={stage},dst={stage},readonly',
            '--mount',f'type=bind,src={BUNDLE},dst=/bundle,readonly',
            '--mount',f'type=bind,src={CLAIM},dst=/control/attempt.claim,readonly',
            '--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777',
            '--tmpfs','/scratch:rw,nosuid,nodev,size=512m,mode=0700,uid=1000,gid=1000',
            IMAGE,'python','-I','-B','-c',
            'raise SystemExit("EFFECT_DISABLED_NO_REVIEWED_SIGNED_OPEN_CHILD")']

def plan(now=None,token='0'*32):
    basis=pinned_basis(now)
    return {'schema':'context-signed-scope-docker-plan/v1-inert',
            'status':'HOLD_PORTABLE_REVIEW_AND_PRIVATE_MOUNT_PROBE',
            'effect_enabled':False,'docker_invoked':False,
            'image':IMAGE,'name':NAME,'claim':str(CLAIM),
            'basis':basis,'create_argv':projected_create_argv(token),
            'mount_roots':[str(STAGE),str(BUNDLE),str(CLAIM)],
            'unresolved':['portable_bundle_independent_review',
                          'reviewed_signed_open_child_and_real_source_manifest',
                          'exact_private_path_mount_and_same_uid_custody_probe',
                          'one_shot_external_observer_release']}

def execute(*_args,**_kwargs):raise Refused('EFFECT_DISABLED_NO_DOCKER_OR_PRIVATE_REOPEN')
def create_claim(*_args,**_kwargs):raise Refused('EFFECT_DISABLED_NO_CLAIM')

if __name__=='__main__':
    import sys
    if sys.argv[1:]!=['--plan']:raise SystemExit('expected --plan')
    print(json.dumps(plan(),sort_keys=True,separators=(',',':')))
