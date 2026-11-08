"""Run the additive deferred fixture resolver through authenticated Service.call.

Preserves the exact API60 native Agent candidate; no actual owner resolution,
repository admission, Work completion or live activation is performed.
"""
from __future__ import annotations
import base64
import copy
from datetime import datetime,timedelta,timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback
import uuid

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v61-t22-fixture-resolution-0001'
SOURCE='190bec8fc0ba64e37f41262588802a4341e6eb3febe688ed1a1de3dee5cfc171'
PROFILE='2a64103d3d5a26af7d4d36aad9511a737a1f346b3fb3f55043d026feafc80d8a'
RECEIPT=HERE/'LIVE-NATIVE-FIXTURE-RESOLUTION-API61-0001.json'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def journal(vault):return {p.relative_to(vault.root).as_posix():sha(p.read_bytes()) for p in (vault.root/'journal').rglob('*') if p.is_file()}
def stamp(phase):print(json.dumps({'phase':phase,'utc':datetime.now(timezone.utc).isoformat()}),file=sys.stderr,flush=True)
def private_write(root,name,raw):
    root.mkdir(mode=0o700,parents=True,exist_ok=True)
    if root.stat().st_mode&0o077:raise ValueError('owner-only diagnostic required')
    fd=os.open(root/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())

def run():
    if not sys.flags.isolated or not sys.dont_write_bytecode or RECEIPT.exists():
        raise ValueError('isolated bytecode-disabled no-replace run required')
    sys.path.insert(0,str(API.parent));sys.path.insert(0,str(HERE))
    package=API.name
    G=importlib.import_module(package+'.guard');G.verify(SOURCE)
    P=importlib.import_module(package+'.protocol');S=importlib.import_module(package+'.service')
    A=importlib.import_module(package+'.auth');F=importlib.import_module(package+'.fixtures')
    W=importlib.import_module(package+'.workspace');H=importlib.import_module(package+'.handlers')
    R=importlib.import_module(package+'.fixture_resolution_source')
    FH=importlib.import_module(package+'.fixture_resolution_handler')
    inputs=importlib.import_module('build_fixture_resolution_source')
    sub,obs,original,old_request=inputs.selected_inputs()
    schemas=P.Schemas(PROFILE)
    observations=[];diagnostic=Path.home()/'.local/share/cyberalchemy-lab/t22-fixture-resolution-diagnostics'/uuid.uuid4().hex
    stamp('source-replay-start')
    with P.source.replay_source(P.source.CURRENT_LEGACY_NAME) as view:
        stamp('source-replay-pass')
        cut=H.cut(view)
        if cut!=sub['source_cut']:raise ValueError('actual submitted candidate selected another source cut')
        with tempfile.TemporaryDirectory(prefix='cal-T22-native-fixture-resolution-') as temporary:
            root=Path(temporary);root.chmod(0o700)
            principal='principal:local-fixture-resolution-owner:'+uuid.uuid4().hex
            key,policy_path,_=F.provision(root,source_name=P.source.CURRENT_LEGACY_NAME,principal=principal,materials={})
            policy=P.frame_parse(policy_path.read_bytes())
            capsule=R.build(submission=sub,observation=obs,candidate_raw=original,request=old_request,
                now=A.now(),period_end='2026-10-24T17:54:44.262511+00:00',signing_key=key,fixture_principal_ref=principal)
            capsule_raw=R.canon(capsule);capsule_sha=sha(capsule_raw)
            workspace=root/'workspace';manifest=P.frame_parse((workspace/'workspace.json').read_bytes())
            W.atomic(workspace/'objects'/(capsule_sha+'.json'),capsule_raw)
            routing={'ref':'workspace-object:'+manifest['workspace_ref']+':'+capsule_sha,'sha256':capsule_sha}
            method=P.binding(str((API/'fixture_resolution_handler.py').relative_to(ROOT)),(API/'fixture_resolution_handler.py').read_bytes())
            authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
            policy.update(schema_version='lab-local-challenge-resolution-policy/v1-candidate',
                allowed_operations=list(P.RESOLUTION_SUPPORTED),session_control=None,
                purpose='durable-metadata-and-exact-challenge-resolution',scope_control=None,
                development_authorization_binding=P.binding(str(authority.relative_to(ROOT)),authority.read_bytes()),
                resolution_control={'routing_binding':routing,'method_binding':method})
            policy_path.write_bytes(P.compact(policy));policy_path.chmod(0o600)
            private_write(diagnostic,'source-capsule.json',capsule_raw)
            private_write(diagnostic,'reader-policy-public.json',P.compact(policy))
            stamp('fixture-source-created')
            channel=A.ReaderChannel(policy_path,sha(policy_path.read_bytes()),schemas)
            context=channel.authenticate(F.proof(key,channel.challenge));del key
            stamp('reader-authenticated')
            host=S.Service(view,channel,schemas)
            stamp('native-service-created')
            builder=FH.FixtureResolution(host,routing,{'path':str((API/'source-manifest.json').relative_to(ROOT)),'sha256':SOURCE})
            message={'schema_version':'lab-local-fixture-challenge-resolution/v1-candidate',
                'challenge':builder.header('challenge-event',original,'challenge.candidate.1'),
                'resolution_decision':builder.header('decision'),'evidence_bindings':[routing],
                'semantic_change_proposal_binding':None,'governance_change_proposal_binding':None,
                'unresolved_gaps':[],'source_cut':cut,'authority_effect':'none'}
            if not schemas.protocol_valid('urn:cyberalchemy-lab:protocol:challenge-resolution:v1-candidate',message):
                raise ValueError('additive fixture request schema invalid')
            def native(call):
                reply=host.call(P.compact(call));W.privacy(reply)
                observations.append({'operation':call['operation'],'kind':reply.get('kind'),'code':reply.get('message',{}).get('code',reply.get('code')),
                                     'reply_sha256':sha(P.compact(reply))})
                if not schemas.valid('api-reply',reply):raise ValueError('native response is not original API envelope')
                return reply
            def call(suffix):
                value=F.call(context,'lab.status',cut)
                value.update(operation='challenge.resolve',message=copy.deepcopy(message),
                    idempotency_key='fixture:Agent-contest-resolution:'+suffix)
                return value
            # Wrong Actor is refused by the actual service before a journal claim.
            bad=call('bad-actor');bad['message']['actor']={name:context[name] for name in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
            bad['message']['actor']['role_assignment_refs']=context['role_assignment_bindings']
            bad['message']['actor']['principal_ref']='principal:foreign-fixture-owner'
            before=journal(host.vault);reply=native(bad)
            if reply['kind']!='error' or reply['message']['code']!='unauthorized' or journal(host.vault)!=before:
                raise ValueError('wrong native Actor not refused before claim')
            stamp('native-wrong-Actor-refused')
            # Signed capsule verifier currentness/signature negatives use actual
            # current time and never grant authority from a request body.
            wrong_signature=copy.deepcopy(capsule);wrong_signature['envelope']['signature']=base64.b64encode(bytes(64)).decode()
            for changed in [wrong_signature]:
                try:R.verify(changed,selected_public_hex=capsule['issuer_public_hex'],selected_submission_sha256=FH.SUBMISSION_SHA,
                             selected_source_cut=cut,now=A.now())
                except Exception:pass
                else:raise ValueError('bad fixture signature accepted')
            try:R.verify(capsule,selected_public_hex='00'*32,selected_submission_sha256=FH.SUBMISSION_SHA,
                         selected_source_cut=cut,now=A.now())
            except Exception:pass
            else:raise ValueError('unselected signer accepted')
            # Use a real past time declaration signed by the fixture signer only
            # in the independent pure test suite; this live capsule must be current.
            stamp('native-positive-start')
            positive=call('defer-0001');before=journal(host.vault);reply=native(positive)
            stamp('native-positive-return')
            if reply['kind']!='result':
                try:builder.preflight(message,cut,positive['idempotency_key'])
                except Exception as error:private_write(diagnostic,'preflight-trace.txt',''.join(traceback.format_exception(error)).encode())
                raise ValueError('native fixture resolution refused: '+str(reply.get('message',{}).get('code')))
            proposal=reply['message']
            after=journal(host.vault);delta=set(after)-set(before)
            names=[Path(name).name.removesuffix('.result.json') for name in delta if name.endswith('.result.json')]
            if len(names)!=1:raise ValueError('one native resolution result journal required')
            cold=W.Vault(channel);claim,result=cold.state(names[0])
            if claim['operation']!='challenge.resolve' or result['posture']!='completed' or P.frame_parse(cold.object_read(result['domain_binding']))!=proposal:
                raise ValueError('fresh native Vault did not reopen exact result')
            target=proposal['targets'][0]
            successor=P.frame_parse(cold.object_read({'ref':target['content']['content_ref'],'sha256':target['content']['byte_sha256']}))
            if successor!=capsule['members']['challenge-event'] or target['predecessor']['byte_sha256']!=sha(original):
                raise ValueError('actual native consequence lost original Agent lineage')
            retry=copy.deepcopy(positive);retry['call_id']+=':retry'
            retry_before=journal(host.vault);retried=native(retry)
            if retried['kind']!='result' or retried['message']!=proposal or journal(host.vault)!=retry_before:
                raise ValueError('native exact resolution retry changed result or journal')
            private_write(diagnostic,'proposal.json',P.compact(proposal))
            private_write(diagnostic,'resolution-request.json',P.compact(positive))
            receipt={'schema_version':'lab-T22-native-local-fixture-resolution/v1','result':'PASS',
                'api_source_sha256':SOURCE,'api_profile_sha256':PROFILE,'source_cut':cut,
                'fixture_source_sha256':capsule_sha,'native_submitted_original_sha256':sha(original),
                'native_submission_receipt_sha256':R.sha(R.canon(sub)),
                'native_proposal_sha256':sha(P.compact(proposal)),
                'fresh_Vault_journal_replay':True,'native_exact_retry_read_only':True,
                'wrong_Actor_refused_before_claim':True,'signature_and_signer_refusals':True,
                'selected_fixture_outcome':'defer','candidate_response_state':successor['payload']['response_state'],
                'recorded_fixture_resolution':True,'actual_owner_outcome':None,
                'repository_admissions':0,'authority_effect':'none','native_operations':observations,
                'private_diagnostic_locator_sha256':sha(str(diagnostic).encode())}
    G.verify(SOURCE)
    fd=os.open(RECEIPT,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(json.dumps(receipt,sort_keys=True,indent=2).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
    return {'result':'PASS','receipt_sha256':sha(RECEIPT.read_bytes())}

if __name__=='__main__':print(json.dumps(run(),sort_keys=True))
