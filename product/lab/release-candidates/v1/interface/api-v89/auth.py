"""One-use cryptographic stdio challenge from a provisioned local reader policy."""
import base64
import copy
from datetime import datetime,timezone
import os
from pathlib import Path
import secrets
import uuid
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .protocol import *

import importlib.util,sys
_fact_name='_cal_lab_fact_read_scope_v1'
_fact_path=HERE.parent/'fact-read-scope-v1'
if _fact_name not in sys.modules:
    _spec=importlib.util.spec_from_file_location(_fact_name,_fact_path/'__init__.py',submodule_search_locations=[str(_fact_path)])
    _module=importlib.util.module_from_spec(_spec);sys.modules[_fact_name]=_module;_spec.loader.exec_module(_module)
FACT_SCOPE=__import__(_fact_name+'.scope',fromlist=['policy_scope'])
source.require(Path(FACT_SCOPE.__file__).resolve()==_fact_path/'scope.py','unselected API fact scope kernel')


def instant(text):
    value=datetime.fromisoformat(text.replace('Z','+00:00'))
    if value.tzinfo is None:raise ValueError('timezone required')
    return value.astimezone(timezone.utc)


def now():return datetime.now(timezone.utc)


class ReaderChannel:
    def __init__(self,path,expected_sha,schemas):
        self.path=Path(path);self.expected_sha=expected_sha;self.schemas=schemas;self.context=None
        self.termination_basis=None
        self.used=False;self.host='host:R03-api:'+uuid.uuid4().hex;self.connection='connection:R03-api:'+uuid.uuid4().hex
        self.nonce=secrets.token_hex(32);self.policy=self.policy_guard()
        self.challenge={'schema_version':'lab-local-reader-challenge/v1-candidate','host_instance_ref':self.host,
            'connection_ref':self.connection,'nonce':self.nonce,'policy_sha256':expected_sha,
            'expires_at':self.policy['expires_at'],'authority_effect':'none'}
        source.require(self.schemas.valid('reader-authentication',self.challenge),'constructed challenge shape differs')
    def policy_guard(self,*,check_source=True):
        p=self.path
        source.require(p.is_file() and p.is_absolute() and '..' not in p.parts and p.resolve()==p and not p.is_symlink() and not any(a.is_symlink() for a in p.parents), 'unsafe reader policy')
        source.require(not p.is_relative_to(ROOT) and p.is_relative_to(Path('/tmp')),'independently provisioned external policy required')
        stat=p.stat();source.require(stat.st_uid==os.getuid() and stat.st_mode&0o777==0o600,'reader policy owner/mode differ')
        raw=p.read_bytes();source.require(len(raw)<=16384 and source.sha(raw)==self.expected_sha,'reader policy revoked or changed')
        value=frame_parse(raw)
        source.require(self.schemas.valid('reader-authentication',value),'reader policy schema differs')
        fields='schema_version principal_ref reader_public_key host_uid source_name scope_refs expires_at max_request_bytes max_response_bytes max_calls allowed_operations revoked scope_posture authority_effect actual_owner_outcome workspace session_control projection_control'.split()
        export=value['schema_version']=='lab-local-export-candidate-policy/v1-candidate'
        review=value['schema_version']=='lab-local-review-candidate-policy/v1-candidate'
        references=value['schema_version']=='lab-local-reference-closed-review-policy/v1-candidate'
        workflow=references or value['schema_version']=='lab-local-challenge-review-policy/v1-candidate'
        challenge=workflow or value['schema_version']=='lab-local-challenge-candidate-policy/v1-candidate'
        classification=value['schema_version']=='lab-local-classification-candidate-policy/v1-candidate'
        assessment=value['schema_version']=='lab-local-lesson-assessment-policy/v1-candidate'
        application_session=value['schema_version']=='lab-local-lesson-application-policy/v2-candidate'
        application=application_session or value['schema_version']=='lab-local-lesson-application-policy/v1-candidate'
        reference_resolution=value['schema_version']=='lab-local-integrated-challenge-resolution-policy/v3-candidate'
        integrated=reference_resolution or value['schema_version']=='lab-local-integrated-challenge-resolution-policy/v2-candidate'
        resolution=integrated or value['schema_version']=='lab-local-challenge-resolution-policy/v1-candidate'
        failure=value['schema_version']=='lab-local-failure-candidate-policy/v1-candidate'
        typed=value['schema_version']=='lab-local-typed-extension-candidate-policy/v1-candidate'
        lesson=value['schema_version']=='lab-local-lesson-read-policy/v1-candidate'
        package=value['schema_version']=='lab-local-package-import-policy/v1-candidate'
        package_export=value['schema_version']=='lab-local-package-export-policy/v1-candidate'
        metadata=resolution or (application and not application_session) or assessment or export or review or challenge or classification or failure or typed or package or package_export or value['schema_version']=='lab-local-metadata-candidate-policy/v1-candidate'
        if lesson:fields+=['lesson_control','development_authorization_binding']
        if metadata:fields+=['purpose','development_authorization_binding','scope_control']
        if challenge:fields+=['challenge_control']
        if workflow:fields+=['composition_control']
        if references:fields+=['reference_control']
        if classification:fields+=['classification_control']
        if resolution:fields+=['resolution_control']
        if integrated:fields+=['integrated_source_control']
        if reference_resolution:fields+=['resolution_reference_control']
        if failure:fields+=['failure_control']
        if application:fields+=['application_control']
        if application_session:fields+=['purpose','development_authorization_binding']
        if assessment:fields+=['assessment_control']
        if typed:fields+=['typed_control']
        if export:fields+=['export_control']
        if package:fields+=['package_control']
        if package_export:fields+=['package_export_control']
        source.require(set(value)==set(fields) and value['schema_version'] in ('lab-local-candidate-policy/v4-candidate','lab-local-metadata-candidate-policy/v1-candidate','lab-local-export-candidate-policy/v1-candidate','lab-local-review-candidate-policy/v1-candidate','lab-local-classification-candidate-policy/v1-candidate','lab-local-failure-candidate-policy/v1-candidate','lab-local-typed-extension-candidate-policy/v1-candidate','lab-local-lesson-read-policy/v1-candidate','lab-local-package-import-policy/v1-candidate','lab-local-package-export-policy/v1-candidate','lab-local-challenge-candidate-policy/v1-candidate','lab-local-challenge-review-policy/v1-candidate','lab-local-reference-closed-review-policy/v1-candidate','lab-local-lesson-assessment-policy/v1-candidate','lab-local-lesson-application-policy/v1-candidate','lab-local-lesson-application-policy/v2-candidate','lab-local-challenge-resolution-policy/v1-candidate','lab-local-integrated-challenge-resolution-policy/v2-candidate','lab-local-integrated-challenge-resolution-policy/v3-candidate')
            and value['scope_posture']=='isolated-candidate-preparation' and value['authority_effect']=='none'
            and value['actual_owner_outcome'] is None and value['revoked'] is False,'closed local candidate reader policy required')
        source.require(type(value['principal_ref']) is str and value['principal_ref']
            and value['host_uid']==os.getuid() and type(value['host_uid']) is int
            and isinstance(value['scope_refs'],list) and len(value['scope_refs'])==1
            and value['allowed_operations']==list(RESOLUTION_SUPPORTED if resolution else APPLICATION_SESSION_SUPPORTED if application_session else APPLICATION_SUPPORTED if application else ASSESSMENT_SUPPORTED if assessment else WORKFLOW_SUPPORTED if workflow else PACKAGE_EXPORT_SUPPORTED if package_export else PACKAGE_SUPPORTED if package else LESSON_SUPPORTED if lesson else EXPORT_SUPPORTED if export else CHALLENGE_SUPPORTED if challenge else REVIEW_SUPPORTED if review else CLASSIFICATION_SUPPORTED if classification else FAILURE_SUPPORTED if failure else TYPED_SUPPORTED if typed else METADATA_SUPPORTED if metadata else LEGACY_SUPPORTED),'reader authority scope differs')
        source.require(instant(value['expires_at'])>now(),'reader policy expired')
        source.require(type(value['max_request_bytes']) is int and 4096<=value['max_request_bytes']<=1024*1024
            and type(value['max_response_bytes']) is int and 4096<=value['max_response_bytes']<=4*1024*1024
            and type(value['max_calls']) is int and 1<=value['max_calls']<=256,'reader policy budget differs')
        from .workspace import validate_scope
        selected_root,selected_manifest=validate_scope(value)
        if lesson:
            from .workspace import read_private
            authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
            selected=value['lesson_control']['plan_binding']
            matches=[row for row in selected_manifest['materials'] if row['ref']==selected['ref'] and row['sha256']==selected['sha256']]
            source.require(value['source_name']=='custody-participation' and value['development_authorization_binding']==binding(str(authority.relative_to(ROOT)),authority.read_bytes()) and len(matches)==1,'lesson policy lacks exact independent development/plan selection')
            plan_raw=read_private(selected_root/matches[0]['path'])
            source.require(source.sha(plan_raw)==selected['sha256'] and frame_parse(plan_raw).get('schema_version')=='lab-lesson-host-plan/v1-candidate','independent lesson plan bytes differ')
        if classification:
            from .workspace import read_private
            selected=value['classification_control']['routing_binding']
            source.require(selected['ref']=='workspace-object:'+selected_manifest['workspace_ref']+':'+selected['sha256'],'classification routing object namespace differs')
            selected_raw=read_private(selected_root/'objects'/(selected['sha256']+'.json'))
            source.require(source.sha(selected_raw)==selected['sha256'],'independent classification routing bytes changed')
        if assessment:
            from .workspace import read_private
            selected=value['assessment_control']['routing_binding']
            source.require(selected['ref']=='workspace-object:'+selected_manifest['workspace_ref']+':'+selected['sha256'],'assessment routing namespace differs')
            selected_raw=read_private(selected_root/'objects'/(selected['sha256']+'.json'))
            source.require(source.sha(selected_raw)==selected['sha256'],'assessment routing bytes changed')
            method=HERE.parent/'lesson-assessment-v1/preparation.py'
            source.require(value['assessment_control']['method_binding']==binding(str(method.relative_to(ROOT)),method.read_bytes()),'assessment method selection differs')
        if application:
            from .workspace import read_private
            selected=value['application_control']['routing_binding']
            source.require(selected['ref']=='workspace-object:'+selected_manifest['workspace_ref']+':'+selected['sha256'],'application routing namespace differs')
            selected_raw=read_private(selected_root/'objects'/(selected['sha256']+'.json'))
            source.require(source.sha(selected_raw)==selected['sha256'],'application routing bytes changed')
            method=HERE.parent/('lesson-application-v2' if application_session else 'lesson-application-v1')/'preparation.py'
            source.require(value['application_control']['method_binding']==binding(str(method.relative_to(ROOT)),method.read_bytes()),'application method selection differs')
        if application_session:
            authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
            source.require(value['source_name']=='custody-participation' and value['session_control'] is not None
                and value['purpose']=='current-participation-and-exact-lesson-application'
                and value['development_authorization_binding']==binding(str(authority.relative_to(ROOT)),authority.read_bytes()),
                'application requires original participation plus exact development authorization')
        if resolution:
            from .workspace import read_private
            selected=value['resolution_control']['routing_binding']
            source.require(selected['ref']=='workspace-object:'+selected_manifest['workspace_ref']+':'+selected['sha256'],'resolution routing namespace differs')
            selected_raw=read_private(selected_root/'objects'/(selected['sha256']+'.json'))
            source.require(source.sha(selected_raw)==selected['sha256'],'resolution routing original changed')
            method=HERE.parent/('challenge-resolution-v4' if reference_resolution else 'challenge-resolution-v3' if integrated else 'challenge-resolution-v1')/'preparation.py'
            source.require(value['resolution_control']['method_binding']==binding(str(method.relative_to(ROOT)),method.read_bytes()),'resolution method selection differs')
        if reference_resolution:
            from .challenge_resolution import implementation
            method,_=implementation(value)
            method.validate_reference_control(value)
        if failure:
            from .workspace import read_private
            selected=value['failure_control']['routing_binding']
            source.require(selected['ref']=='workspace-object:'+selected_manifest['workspace_ref']+':'+selected['sha256'],'failure routing object namespace differs')
            selected_raw=read_private(selected_root/'objects'/(selected['sha256']+'.json'))
            source.require(source.sha(selected_raw)==selected['sha256'],'independent failure routing bytes changed')
        if typed:
            from .workspace import read_private
            selected=value['typed_control']['routing_binding']
            source.require(selected['ref']=='workspace-object:'+selected_manifest['workspace_ref']+':'+selected['sha256'],'typed routing object namespace differs')
            selected_raw=read_private(selected_root/'objects'/(selected['sha256']+'.json'))
            source.require(source.sha(selected_raw)==selected['sha256'],'independent typed routing bytes changed')
        if challenge:
            from .challenge_submission import validate_control
            validate_control(value,self.schemas)
        if references:
            from .carrier_references import validate_control as validate_references
            validate_references(value)
        if workflow:
            from .workflow_composition import validate_control as validate_composition
            source.require(value['scope_control'] is None,'workflow composition cannot add an undeclared domain-scope policy')
            validate_composition(value,self.schemas)
        if package_export:
            from .package_export import validate_control
            validate_control(value,self.schemas)
        if integrated:
            source.require(value['source_name']=='integrated-participation' and value['session_control'] is None,'integrated resolution is metadata only')
            source.require(value['integrated_source_control']==source.integrated_bindings(),'independent integrated source pins differ')
        borrowed=FACT_SCOPE.policy_scope(self)
        # Invocation-local producer selection only: no source bytes, digest,
        # policy, permission or clock are cached between calls. The original
        # preflight and reader selection still execute in this invocation.
        selected_delivery=None
        if borrowed is not None:
            source.require(value['source_name']=='custody-participation' and borrowed.host is self,'borrowed source selection differs')
            borrowed.check()
        elif check_source:
            if value['source_name']=='custody-participation':
                selected_delivery=source.custody_delivery()
                selected_delivery.reader.selection(selected_delivery.SOURCE_PIN,selected_delivery.SOURCE_PACKAGE,value['source_name'])
            else:source.source_selection(value['source_name'])
        control=value['session_control']
        if metadata:
            authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
            d=source.integrated_reader() if integrated else borrowed.producer if borrowed is not None else selected_delivery if selected_delivery is not None else source.custody_delivery()
            source.require(value['source_name']==('integrated-participation' if integrated else 'custody-participation') and control is None
                and value['purpose']==('durable-metadata-and-exact-integrated-challenge-resolution' if integrated else 'durable-metadata-and-exact-challenge-resolution' if resolution else 'durable-metadata-and-exact-reference-closed-review' if references else 'durable-metadata-and-exact-challenge-review-composition' if workflow else 'durable-metadata-and-exact-package-export' if package_export else 'durable-metadata-and-exact-package-import' if package else 'durable-metadata-and-managed-file-export' if export else 'durable-metadata-and-exact-challenge-preparation' if challenge else 'durable-metadata-and-exact-review-preparation' if review else 'durable-metadata-and-exact-classification-preparation' if classification else 'durable-metadata-and-exact-lesson-assessment' if assessment else 'durable-metadata-and-exact-lesson-application' if application else 'durable-metadata-and-exact-failure-preparation' if failure else 'durable-metadata-and-exact-typed-extension-preparation' if typed else 'durable-metadata-and-exact-candidate-preparation')
                and value['principal_ref'] not in (d.records.PRINCIPAL,'principal:R03-fresh-reader')
                and value['development_authorization_binding']==binding(str(authority.relative_to(ROOT)),authority.read_bytes()),'metadata grant cannot claim original Agent participation or owner authority')
        elif value['source_name']=='custody-participation':
            if check_source:
                d=borrowed.producer if borrowed is not None else selected_delivery;period=d.reader.HERE/'packages/0001/period.json';p=d.load(period)
                source.require(value['principal_ref']==d.records.PRINCIPAL and control is not None and control['period_binding']==binding(str(period.relative_to(ROOT)),period.read_bytes()),'original participation permission or exact period differs')
                source.require(instant(p['not_before'])<=now()<instant(value['expires_at'])<=instant(p['expires_at']),'original source host window exceeds retained absolute Assignment interval')
                # Capture source identity only. Every terminating use rereads the
                # actual policy and exact period bytes and checks the real clock.
                self.termination_basis={'period_binding':copy.deepcopy(control['period_binding']),'principal_ref':d.records.PRINCIPAL}
            else:
                basis=self.termination_basis
                source.require(type(basis) is dict and set(basis)=={'period_binding','principal_ref'} and control is not None,'verified termination source basis is unavailable')
                selected=basis['period_binding'];period=ROOT/selected['ref']
                source.require(period==ROOT/'product/lab/release-candidates/v1/interface/current-participation-v5/packages/0001/period.json' and not period.is_symlink() and not any(p.is_symlink() for p in period.parents),'unselected termination period')
                raw=period.read_bytes();p=source.parse(raw)
                source.require(binding(str(period.relative_to(ROOT)),raw)==selected==control['period_binding'] and p['principal_ref']==value['principal_ref']==basis['principal_ref'],'exact current termination period or Principal differs')
                source.require(instant(p['not_before'])<=now()<instant(value['expires_at'])<=instant(p['expires_at']),'original source host window exceeds retained absolute Assignment interval')
        elif value['source_name']=='fresh-participation':
            period=HERE.parent/'session-participation-v2/packages/0001/period.json'
            source.require(value['principal_ref']=='principal:R03-fresh-reader' and control is not None and control['period_binding']==binding(str(period.relative_to(ROOT)),period.read_bytes()),'fresh participation permission or absolute period differs')
            p=source.parse(period.read_bytes())
            source.require(instant(p['not_before'])<=now()<instant(value['expires_at'])<=instant(p['expires_at']),'historical fresh source host window exceeds retained absolute Assignment interval')
        else:source.require(control is None,'Session control requires the fresh source')
        if export:
            from .file_exports import validate_control
            validate_control(value)
        if package:
            from .package_import import validate_control
            validate_control(value,self.schemas)
        Ed25519PublicKey.from_public_bytes(base64.b64decode(value['reader_public_key'],validate=True))
        return value
    def authenticate(self,raw):
        source.require(not self.used and self.context is None,'challenge already consumed')
        self.used=True;self.policy_guard();proof=frame_parse(raw)
        source.require(self.schemas.valid('reader-authentication',proof),'reader proof schema differs')
        source.require(set(proof)=={'schema_version','challenge','signature'} and proof['schema_version']=='lab-local-reader-proof/v1-candidate'
            and proof['challenge']==self.challenge,'proof is not for this host/connection/challenge')
        Ed25519PublicKey.from_public_bytes(base64.b64decode(self.policy['reader_public_key'],validate=True)).verify(
            base64.b64decode(proof['signature'],validate=True),compact(self.challenge))
        profile=source.source_selection(self.policy['source_name'])['engine_pins']['profile_sha256']
        authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        self.context={'schema_version':'lab-trusted-call-context/v1-candidate','context_ref':'context:R03-api:'+uuid.uuid4().hex,
            'host_instance_ref':self.host,'connection_ref':self.connection,'principal_ref':self.policy['principal_ref'],
            'role_assignment_bindings':[],'authority_scope':'operator-local','scope_refs':self.policy['scope_refs'],
            'source_profile_binding':{'ref':str(source.custody_delivery().reader.HERE.parent.joinpath('custody-correction-v4/runtime/profile.json').relative_to(ROOT)) if self.policy['source_name']=='custody-participation' else 'implementation/lab-runtime/v2/profile.json','sha256':profile},
            'authentication_evidence_binding':binding('authentication:'+self.connection,raw),
            'policy_bindings':[{'ref':'policy:'+self.connection,'sha256':self.expected_sha},binding(str(authority.relative_to(ROOT)),authority.read_bytes())],
            'agent_instance_ref':None,'session_ref':None,'assignment_ref':None,'expires_at':self.policy['expires_at'],
            'limits':{'max_request_bytes':self.policy['max_request_bytes'],'max_response_bytes':self.policy['max_response_bytes'],
                'max_actions':self.policy['workspace']['max_actions'],'deadline':self.policy['expires_at']},'origin':'verified-local-adapter',
            'accept_client_supplied_authority_context':False,'private_credentials_in_context':False}
        source.require(self.schemas.valid('trusted-call-context',self.context),'constructed context shape differs')
        result={'schema_version':'lab-local-reader-authenticated/v1-candidate','context':self.context,
            'trusted_context_binding':binding(self.context['context_ref'],compact(self.context)),'authority_effect':'none'}
        source.require(self.schemas.valid('reader-authentication',result),'authenticated response shape differs')
        return copy.deepcopy(result)
    def guard(self):
        if getattr(self,'bound_termination_call',False):return self.termination_guard()
        source.require(self.context is not None,'channel unauthenticated');self.policy_guard()
        source.require(instant(self.context['expires_at'])>now(),'channel expired')
        return copy.deepcopy(self.context)
    def termination_guard(self):
        source.require(self.context is not None,'channel unauthenticated');self.policy_guard(check_source=False)
        source.require(instant(self.context['expires_at'])>now(),'channel expired')
        return copy.deepcopy(self.context)
    def close(self):
        self.context=None;self.nonce=None;self.challenge=None;self.used=True
