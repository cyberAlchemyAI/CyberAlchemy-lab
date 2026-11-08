"""Additive local fixture resolver over an exact signed Agent-origin capsule.

It prepares a deferred candidate revision only. Existing source-current owner
resolution implementations remain separate. No candidate is admitted here.
"""
import base64
import copy
from pathlib import Path
from . import fixture_resolution_source as R
from .protocol import source, ROOT, binding, compact

HERE=Path(__file__).resolve().parent
URI='urn:cyberalchemy-lab:protocol:'
RETAINED_SOURCE_CUT=R.frame(b'{"branch_ref":"branch:completion-legacy-local-4636eca980a5d94d","commit_sequence":2,"commit_sha256":"0f4e21b32c23bf87a3ad1a17a98f2d99ac66d7364f45d0fc0038728680bbdedd","source_profile_sha256":"3364b562c0f381ec8397ae9dbd839bbbb12ff58c9991bb97f79d8b8eec4b9c48","store_ref":"completion-legacy-local-4636eca980a5d94d","streams":[{"cursor":9,"head_sha256":"8d8a8548a71bc6fb839a9688a59270087b01d8fd12bb8e23fd74abb0a0567a37","stream_ref":"project-governance-event-history"},{"cursor":9,"head_sha256":"90e4ab4272e9e473b899b319e4ec857c4edc43843ae8cf5757472a525a341f6c","stream_ref":"project-semantic-event-history"}]}')
SUBMISSION_SHA='9b78e01d8783b1977c215fa71f566975d9ea972b40e9633c7f151298b8dbf696'

class RuleFailure(Exception):
    pass

class FixtureResolution:
    def __init__(self,host,routing_binding,host_source_binding):
        from .service import Service
        from .auth import ReaderChannel
        source.require(type(host) is Service and type(host.channel) is ReaderChannel,'actual local fixture Service/Reader required')
        self.host=host;self.vault=host.vault;self.schemas=host.schemas
        self.routing_binding=copy.deepcopy(routing_binding)
        self.host_source_binding=copy.deepcopy(host_source_binding)
        source.require(host_source_binding=={'path':str((HERE/'source-manifest.json').relative_to(ROOT)),
            'sha256':source.sha((HERE/'source-manifest.json').read_bytes())},'exact local fixture resolver selection required')
        self.raw=self.vault.object_read(routing_binding)
        selected=R.frame(self.raw)
        source.require(type(selected) is dict,'closed fixture source object required')
        self.retained=None
        if selected.get('schema_version')=='lab-local-retained-Agent-resolution/v1-fixture':
            source.require(set(selected)=={'schema_version','original_signed_source','original_source_records',
                'coordinating_source_cut','original_source_posture','authority_effect'}
                and selected['authority_effect']=='none'
                and selected['original_source_posture']=='historical-verified-native-origin',
                'closed retained native origin fixture profile required')
            self.retained=selected
            self.capsule=selected['original_signed_source']
        else:self.capsule=selected
    def retained_original(self,kind):
        source.require(self.retained is not None and kind in ('work','challenge-contract'),
            'exact retained source record kind required')
        originals=self.retained['original_source_records']
        source.require(type(originals) is dict and set(originals)=={'work','challenge-contract'},
            'closed retained original Work/Contract bytes required')
        raw=base64.b64decode(originals[kind],validate=True)
        body=R.frame(raw);R.validate(kind,body)
        header=self.capsule['response']['subject' if kind=='work' else 'challenge_contract']
        source.require(body['kind']==kind and body['node_id']==header['identity_ref']
            and body['scope_ref']==header['scope_ref']==self.capsule['envelope']['payload']['scope_ref']
            and source.sha(raw)==header['byte_sha256'],'retained original source header/body differs')
        return raw
    def verify_origin(self,public,outer,time):
        R.verify(self.capsule,selected_public_hex=public,selected_submission_sha256=SUBMISSION_SHA,
                 selected_source_cut=(RETAINED_SOURCE_CUT if self.retained is not None else outer),now=time)
        if self.retained is not None:
            source.require(R.canon(self.retained)==R.canon(R.frame(self.raw))
                and self.capsule is self.retained['original_signed_source'],
                'captured retained fixture routing changed')
            source.require(self.retained['coordinating_source_cut']==outer,
                'retained fixture coordinating cut differs from current request')
        if self.retained is not None:
            self.retained_original('work');self.retained_original('challenge-contract')
    def header(self,kind,raw=None,version=None):
        body=self.capsule['members'][kind] if raw is None else R.frame(raw)
        raw=R.canon(body) if raw is None else raw
        return {'scope_ref':body['scope_ref'],'identity_ref':body['node_id'],
            'version_ref':body['node_id']+'@'+(version or 'local-fixture.1'),
            'carrier_ref':'cal.artifact-type.'+kind+'/v1','byte_sha256':R.sha(raw)}
    def preflight(self,message,outer,key):
        from .guard import verify
        from .auth import now
        from .handlers import cut
        verify(self.host_source_binding['sha256']);self.schemas.guard()
        context=self.host.channel.guard();policy=self.host.channel.policy_guard()
        source.require(policy['source_name']==source.CURRENT_LEGACY_NAME
            and policy['schema_version']=='lab-local-challenge-resolution-policy/v1-candidate'
            and policy['session_control'] is None and 'challenge.resolve' in policy['allowed_operations'],
            'independent fixture resolution-only Reader grant required')
        method=binding(str(Path(__file__).relative_to(ROOT)),Path(__file__).read_bytes())
        source.require(policy['resolution_control']=={'routing_binding':self.routing_binding,'method_binding':method}
            and self.vault.object_read(self.routing_binding)==self.raw,'fixture resolution policy/source changed')
        public=base64.b64decode(policy['reader_public_key'],validate=True).hex()
        self.verify_origin(public,outer,now())
        p=self.capsule['envelope']['payload']
        source.require(context['principal_ref']==p['fixture_principal_ref']
            and context['agent_instance_ref'] is None and context['session_ref'] is None
            and p['scope_ref'] in context['scope_refs']
            and outer==cut(self.host.handlers.view)==message['source_cut']
            and source.current_legacy_view(self.host.handlers.view),
            'fixture signer/Actor/current signed family differs')
        # Select exact original Work/Contract bytes from the same-cut current
        # Source or the independently pinned historical native origin.
        from . import artifact_model as M
        for header,kind in [(self.capsule['response']['subject'],'work'),
                            (self.capsule['response']['challenge_contract'],'challenge-contract')]:
            if self.retained is None:
                row=self.host.handlers.resolve_exact(header)
                raw=M.record_bytes(self.host.handlers.view,row)[0]
            else:
                # The API71 origin/request/candidate and signature were checked
                # above against independent immutable pins. These are its exact
                # historical inputs, never relabeled as current Source records.
                raw=self.retained_original(kind)
            body=R.frame(raw)
            source.require(body['kind']==kind and source.sha(raw)==header['byte_sha256'],
                'fixture response original source header/body differs')
        rules=body['payload']  # Last exact source above is the Challenge Contract.
        original_event=R.frame(base64.b64decode(self.capsule['original_challenge_base64']))
        source.require('agent-instance' in rules['eligible_challenger_kinds']
            and 'work' in rules['challengeable_subject_kinds']
            and original_event['payload']['ground'] in rules['grounds']
            and self.capsule['response']['response_mode'] in rules['response_modes']
            and set(rules['required_evidence_kinds'])<=set(['source','validation-receipt']),
            'selected original Challenge Contract does not permit fixture Agent response')
        evidence=self.capsule['original_request']['evidence_bindings']
        source.require(len(evidence)==2 and evidence[0]['ref']==self.capsule['response']['subject']['version_ref'],
            'original native source evidence shape differs')
        if self.retained is None:
            work_row=self.host.handlers.resolve_exact(self.capsule['response']['subject'])
            work_raw=M.record_bytes(self.host.handlers.view,work_row)[0]
        else:work_raw=self.retained_original('work')
        source.require(source.sha(work_raw)==evidence[0]['sha256'],'original native Work evidence changed')
        expected_validation='product/lab/release-candidates/v1/interface/api-integration-v71-t15-integrated-closure-0001/t22-validation-receipt.json'
        source.require(evidence[1]['ref']==expected_validation,'original validation receipt source differs')
        source.original({'path':expected_validation,'sha256':evidence[1]['sha256']})
        expected={'schema_version':'lab-local-fixture-challenge-resolution/v1-candidate',
            'challenge':self.header('challenge-event',base64.b64decode(self.capsule['original_challenge_base64']), 'challenge.candidate.1'),
            'resolution_decision':self.header('decision'), 'evidence_bindings':[self.routing_binding],
            'semantic_change_proposal_binding':None,'governance_change_proposal_binding':None,
            'unresolved_gaps':[],'source_cut':outer,'authority_effect':'none'}
        source.require(message==expected and self.schemas.protocol_valid(URI+'challenge-resolution:v1-candidate',message),
            'exact fixture source/Decision/consequence inputs differ')
        source.require(now()<min(R.instant(p['expires_at']),R.instant(policy['expires_at'])),
            'fixture resolution currentness ceiling expired')
        return True
    def prepare(self,message,request,outer,key):
        from .auth import now
        self.preflight(message,outer,key)
        successor=self.capsule['members']['challenge-event'];raw=R.canon(successor)
        # This is a fixture Decision declaration, explicitly not a native
        # admission core. It is retained as candidate evidence in the Vault.
        check={'schema_version':'lab-local-fixture-deferred-consequence/v1-candidate',
            'fixture_outcome':'defer','source_binding':self.routing_binding,
            'original_candidate_sha256':self.capsule['envelope']['payload']['original_challenge_sha256'],
            'response_sha256':self.capsule['envelope']['payload']['response_sha256'],
            'actual_owner_outcome':None,'canonical_admissions':0,'authority_effect':'none'}
        if self.retained is not None:
            check.update(original_source_posture='historical-verified-native-origin',
                original_source_cut=copy.deepcopy(self.capsule['envelope']['payload']['source_cut']),
                coordinating_source_cut=copy.deepcopy(outer),original_Work_or_Contract_Source_current=False)
        self.preflight(message,outer,key)
        original=self.vault.object(base64.b64decode(self.capsule['original_challenge_base64']))
        content=self.vault.object(raw);core=self.vault.object(compact(check))
        metadata=self.vault.object(compact({'schema_version':'lab-local-fixture-candidate-metadata/v1',
            'category':'artifact-instance','decision_ref':self.capsule['members']['decision']['node_id'],
            'contract':None,'authority_effect':'none'}))
        context=self.host.channel.context
        actor={name:context[name] for name in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
        actor['role_assignment_refs']=context['role_assignment_bindings']
        evidence=[self.routing_binding,original,core]
        result={'schema_version':'lab-change-proposal/v1-candidate',
            'proposal_ref':'proposal:local-fixture-deferred-contest:'+R.sha(compact({'key':key,'source':self.routing_binding})),
            'actor':actor,'scope_ref':successor['scope_ref'],'base_cut':copy.deepcopy(outer),
            'source_profile_binding':{'ref':self.host.handlers.view.handle.manifest['profile_binding']['path'],
                'sha256':self.host.handlers.view.handle.manifest['profile_binding']['sha256']},
            'workspace_binding':self.vault.control_binding,
            'targets':[{'operation':'revise','artifact':self.header('challenge-event',raw,'local-fixture.deferred.1'),
                'predecessor':message['challenge'], 'content':{'content_ref':content['ref'],'byte_sha256':content['sha256'],
                    'size_bytes':len(raw),'media_type':'application/json'},
                'candidate_binding':metadata,'requested_effect':('Prepare deferred retained-origin fixture candidate only; historical Work/Contract remain historical and unresolved owner residue remains.' if self.retained is not None else 'Prepare deferred local fixture candidate only; retain unresolved residue.'),
                'decision_core_binding':core}],
            'schema_bindings':[],'connection_proposals':[],'evidence_bindings':evidence,
            'idempotency_key':key,'challenge_route':self.host.handlers.view.data['config']['challenge_route'],
            'authority_effect':'none'}
        source.require(self.schemas.protocol_valid(URI+'change-proposal:v1-candidate',result),
            'fixture consequence result violates original candidate output schema')
        self.preflight(message,outer,key)
        return result,evidence
