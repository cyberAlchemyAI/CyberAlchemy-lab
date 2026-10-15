"""Pure exact-member resolution checks; supplied facts confer no authority.

The authenticated host must independently recognize each owner, channel and live
authority before supplying facts, then guard those sources again before storing
or exposing this calculation. This module performs no admission or owner lookup,
writes no files and does not turn test signatures into actual owner outcomes.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
URI='urn:cyberalchemy-lab:protocol:'
MAX_BYTES=8*1024*1024
CORE_FIELDS={'decision_ref','category','operation','version_ref','target_digest'}
CHANNELS={'owner-conversation','operator-signature','existing-exact-authority'}
CLAIM='Pure exact-byte resolution verification against independently supplied facts only; no owner recognition, live authority, admission or completed plan is established by this calculation.'

class ResolutionFault(ValueError):pass
def require(value,reason):
    if not value:raise ResolutionFault(reason)
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(ref,raw):return {'ref':ref,'sha256':sha(raw)}
def parse(raw):
    require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES,'bounded original bytes required')
    def pairs(rows):
        value={}
        for key,item in rows:
            require(key not in value,'duplicate JSON key');value[key]=item
        return value
    def bad(_):raise ResolutionFault('nonfinite JSON')
    try:return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=bad)
    except (UnicodeError,ValueError,RecursionError) as e:raise ResolutionFault('invalid original JSON') from e
def instant(value):
    require(type(value) is str,'explicit timestamp required')
    try:
        v=datetime.fromisoformat(value.replace('Z','+00:00'))
        require(v.tzinfo is not None and v.utcoffset() is not None,'timestamp timezone required')
        return v.astimezone(timezone.utc)
    except (ValueError,OverflowError) as e:raise ResolutionFault('invalid timestamp') from e
def source_guard():
    value=parse((HERE/'source-manifest.json').read_bytes());rows=value['files']+value['input_bindings']
    require(len({r['path'] for r in rows})==len(rows),'duplicate source binding')
    for row in rows:
        p=ROOT/row['path'];require(p.resolve()==p and p.is_file() and p.is_relative_to(ROOT),'source custody differs')
        require(sha(p.read_bytes())==row['sha256'],'selected source changed: '+row['path'])
    require(sha(encoded(rows))==value['source_sha256'],'source selection digest differs')
    return value['source_sha256']

@dataclass(frozen=True)
class Recognition:
    """Host-selected exact signing recognition, never public request claims."""
    owner_principal_ref:str
    owner_role_ref:str
    public_key:bytes
    source_cut:dict
    core_bindings:tuple
    evidence_binding:dict
    provenance_bindings:tuple
    not_before:str
    expires_at:str
    revoked:bool
    fixture_only:bool

@dataclass(frozen=True)
class Channel:
    """Independent recognized channel/provenance; authentication is external."""
    kind:str
    verification_binding:dict
    source_cut:dict
    provenance_bindings:tuple
    not_before:str
    expires_at:str
    revoked:bool
    fixture_only:bool

@dataclass(frozen=True)
class Facts:
    source_cut:dict
    package_binding:dict
    checkpoint_binding:dict
    source_proof_bindings:tuple
    channel:Channel
    recognitions:tuple

class Rules:
    def __init__(self):
        self.source_sha256=source_guard();manifest=parse((HERE/'source-manifest.json').read_bytes())
        resources=[];self.schemas={};self.schema_originals={}
        for row in manifest['input_bindings']:
            if row['path'].endswith('.schema.json') or row['path'].endswith('/schema.json'):
                self.register_original_schema((ROOT/row['path']).read_bytes(),resources)
        self.registry=Registry().with_resources(resources);self.checker=FormatChecker()
        native=HERE.parent/'custody-correction-v4/runtime/lab_runtime'
        name='_cal_checkpoint_native_custody_v4'
        if name not in sys.modules:
            spec=importlib.util.spec_from_file_location(name,native/'__init__.py',submodule_search_locations=[str(native)])
            module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
        self.common=importlib.import_module(name+'.common');self.custody=importlib.import_module(name+'.custody')
        require(Path(self.common.__file__).resolve()==native/'common.py' and Path(self.custody.__file__).resolve()==native/'custody.py','unselected native core/content implementation')
    def register_original_schema(self,raw,resources):
        value=parse(raw)
        if '$id' not in value:return
        identity=value['$id']
        if identity in self.schema_originals:
            require(self.schema_originals[identity]==raw,'conflicting original schema identity')
            return
        self.schema_originals[identity]=raw;self.schemas[identity]=value
        resources.append((identity,Resource.from_contents(value,default_specification=DRAFT202012)))
    def valid(self,uri,value):
        require(uri in self.schemas,'unselected schema')
        try:Draft202012Validator(self.schemas[uri],registry=self.registry,format_checker=self.checker).validate(value)
        except Exception as e:raise ResolutionFault('invalid original contract: '+uri) from e
    def calculate(self,original,request_binding,facts,reader,*,evaluated_at):
        """Return immutable calculation bytes, without publishing or authorizing."""
        require(source_guard()==self.source_sha256,'rule source changed')
        require(type(facts) is Facts and type(facts.channel) is Channel,'independent typed host facts required')
        require(binding(request_binding['ref'],original)==request_binding,'original resolution bytes differ')
        message=parse(original);self.valid(URI+'checkpoint-resolution:v1-candidate',message)
        clock=instant(evaluated_at);resolved=instant(message['resolved_at'])
        require(resolved<=clock,'resolution timestamp is in the future')
        source_cut=copy.deepcopy(facts.source_cut)
        read_rows={};cache={};total=0
        def read(selected):
            nonlocal total
            require(type(selected) is dict and set(selected)=={'ref','sha256'},'closed exact binding required')
            key=(selected['ref'],selected['sha256'])
            if key in cache:return cache[key]
            try:raw=reader(copy.deepcopy(selected))
            except Exception as e:raise ResolutionFault('selected original is unresolved') from e
            require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES,'bounded selected original required')
            require(sha(raw)==selected['sha256'],'selected original hash differs')
            total+=len(raw);require(total<=64*1024*1024 and len(cache)<2048,'complete resolution closure budget exceeded')
            require(selected['ref'] not in read_rows or read_rows[selected['ref']]==selected,'conflicting original material reference')
            read_rows[selected['ref']]=copy.deepcopy(selected);cache[key]=raw;return raw
        def body(selected):return parse(read(selected))
        require(message['review_package_binding']==facts.package_binding and message['checkpoint_binding']==facts.checkpoint_binding,'independent reviewed package/checkpoint selection differs')
        require(type(facts.source_proof_bindings) is tuple and facts.source_proof_bindings,'original source proof closure required')
        for selected in facts.source_proof_bindings:read(selected)
        package=body(facts.package_binding);self.valid(URI+'review-package:v1-candidate',package)
        require(package['base_cut']==source_cut,'reviewed source cut is stale')
        require(len(package['ordered_core_bindings'])<=256,'member count exceeds bound')
        require(len({encoded(b) for b in package['ordered_core_bindings']})==len(package['ordered_core_bindings']),'duplicate core')
        manifest=body(package['manifest_binding'])
        require(manifest.get('schema_version')=='lab-exact-review-materialization/v1-candidate','unselected exact review manifest version')
        require(set(manifest)==set('schema_version package_ref base_cut source_API_binding original_review_binding proposal_binding validation_report_binding original_semantic_and_operational_gaps input_posture targets ordered_core_bindings ordered_required_owner_responses workflow_decision_profile preference preference_basis preference_current_admission_claimed workflow_protocol workflow_protocol_is_WorkflowRun_artifact routing_original_binding generated_carriers example_bindings declared_consequence_bindings private_public_review_binding human_checkpoint_count all_targets_materialized atomicity_requirement actual_owner_outcome current_owner_authority_verified repository_admissions_applied runtime_activations external_effect_refs invalidation_conditions claim_ceiling authority_effect'.split()),'closed exact review manifest required')
        require(manifest['package_ref']==package['package_ref'] and manifest['base_cut']==source_cut,'manifest package/cut differs')
        for name in ('ordered_core_bindings','workflow_decision_profile','example_bindings','invalidation_conditions','all_targets_materialized','human_checkpoint_count','atomicity_requirement','authority_effect'):
            require(manifest[name]==package[name],'package/manifest field differs: '+name)
        require(manifest['actual_owner_outcome'] is None and manifest['current_owner_authority_verified'] is False,'preparation cannot supply an owner outcome')
        require(manifest['repository_admissions_applied']==manifest['runtime_activations']==0 and manifest['external_effect_refs']==[],'review preparation already claims effects')
        generated=manifest['generated_carriers']
        require(type(generated) is list and len(generated)==2,'exact generated bundle/checkpoint required')
        checkpoint_rows=[r for r in generated if r['artifact']==package['checkpoint']]
        bundle_rows=[r for r in generated if r['artifact']==package['decision_bundle']]
        require(len(checkpoint_rows)==len(bundle_rows)==1 and checkpoint_rows[0]['object_binding']==facts.checkpoint_binding,'exact carrier bindings differ')
        checkpoint=body(facts.checkpoint_binding);bundle=body(bundle_rows[0]['object_binding'])
        for value,header,kind in ((checkpoint,package['checkpoint'],'decision-checkpoint'),(bundle,package['decision_bundle'],'decision-bundle')):
            require(value['kind']==kind and value['node_id']==header['identity_ref'],'carrier identity/kind differs')
            self.valid('https://cyberalchemy.local/schemas/'+kind+'/v1',value)
            require(sha(read(checkpoint_rows[0]['object_binding'] if kind=='decision-checkpoint' else bundle_rows[0]['object_binding']))==header['byte_sha256'],'carrier/header bytes differ')
        cp=checkpoint['payload'];bp=bundle['payload']
        require(cp['checkpoint_kind']=='final-review' and cp['presentation_state']=='pending' and cp['closed_at'] is None,'checkpoint is not the pending final review')
        require(cp['decision_bundle_ref']==bundle['node_id'] and bp['checkpoint_ref']==checkpoint['node_id'],'bundle/checkpoint coupling differs')
        require(cp['workflow_profile_ref']==package['workflow_decision_profile']['version_ref'],'checkpoint workflow profile differs')
        require(bp['all_targets_materialized'] is True and bp['atomicity_requirement']=='all-or-nothing','bundle atomicity differs')
        require(bp['invalidation_conditions']==package['invalidation_conditions'],'bundle invalidation conditions differ')
        require(bp['bundle_digest']==sha(encoded(bp['ordered_decisions'])),'original bundle order digest differs')
        require(len(bp['ordered_decisions'])==len(manifest['targets'])==len(package['ordered_core_bindings']),'complete target/core/bundle membership differs')
        require(len({d['decision_ref'] for d in bp['ordered_decisions']})==len(bp['ordered_decisions']),'duplicate independent Decision identity')
        require(len({t['target']['artifact']['version_ref'] for t in manifest['targets']})==len(manifest['targets']),'duplicate independent target version')
        for i,(cb,t,decision) in enumerate(zip(package['ordered_core_bindings'],manifest['targets'],bp['ordered_decisions'])):
            core=body(cb);require(set(core)==CORE_FIELDS,'native stable core format differs')
            require(t['core_binding']==cb and decision['decision_core_sha256']==cb['sha256'] and decision['decision_ref']==core['decision_ref'],'exact core binding/order differs')
            target=t['target'];header=target['artifact']
            require(core['operation']==target['operation'] and core['version_ref']==header['version_ref'],'core operation/version differs')
            require(decision['target_refs']==[header['version_ref']] and decision['target_digests']==[{'target_ref':header['version_ref'],'sha256':header['byte_sha256']}],'bundle target bytes differ')
            require(decision['selected_outcome'] is None,'bundle preparation claims a prior outcome')
            raw=None
            if target['operation']!='withdraw':
                content=target['content'];raw=read(t['original_content_binding'])
                require(len(raw)==content['size_bytes'] and sha(raw)==content['byte_sha256']==header['byte_sha256'],'reviewed target original bytes differ')
            else:require(t['original_content_binding'] is None,'withdrawal cannot substitute new target bytes')
            metadata=body(target['candidate_binding'])
            require(set(metadata)=={'schema_version','category','decision_ref','contract'} and metadata['schema_version']=='lab-candidate-target-metadata/v1-candidate','selected native target metadata differs')
            native_target={'category':metadata['category'],'operation':target['operation'],'version_ref':header['version_ref'],
                'carrier_ref':header['carrier_ref'],'record':parse(raw) if raw is not None else None,
                'predecessor_ref':target['predecessor']['version_ref'] if target['predecessor'] is not None else None,
                'decision_ref':metadata['decision_ref'],'contract':metadata['contract'],
                'content':self.custody.content_entry(raw) if raw is not None else None}
            require(core=={'decision_ref':metadata['decision_ref'],'category':metadata['category'],'operation':target['operation'],
                'version_ref':header['version_ref'],'target_digest':self.common.digest(native_target)},'original native stable core target digest differs')
            require(read(cb)==self.common.encoded(core) and target['decision_core_binding']==cb,'native stable core originals or bindings differ')
        for name in ('validation_bindings','example_bindings','operational_instruction_bindings'):
            for selected in package[name]:read(selected)
        for name in ('original_review_binding','proposal_binding','validation_report_binding','private_public_review_binding','routing_original_binding'):
            read(manifest[name])
        read(manifest['source_API_binding'])
        for selected in manifest['declared_consequence_bindings']:read(selected)
        require(manifest['validation_report_binding'] in package['validation_bindings'],'original construction validation omitted')
        voices=manifest['ordered_required_owner_responses']
        require(type(voices) is list and 0<len(voices)<=2048,'complete required owner voices required')
        expected=[];keys=set();indices=[]
        for voice in voices:
            i=voice['core_index'];require(type(i) is int and 0<=i<len(package['ordered_core_bindings']),'owner core index differs')
            require(voice['core_binding']==package['ordered_core_bindings'][i],'owner core binding differs')
            key=(i,voice['owner_principal']['identity_ref'],voice['owner_role_ref'])
            require(key not in keys,'duplicate required owner voice');keys.add(key);indices.append(i)
            require(voice['voice_index']==sum(1 for k in expected if k[0]==i),'owner voice index/order differs')
            require(voice['selected_outcome'] is None and voice['current_owner_authority_verified'] is False,'preparation cannot authorize a member')
            read(voice['role_declaration_binding']);expected.append(key)
        require(indices==sorted(indices) and set(indices)==set(range(len(package['ordered_core_bindings']))),'every member needs its complete ordered owner set')
        outcomes=message['ordered_outcomes'];require(len(outcomes)==len(voices),'all required owner responses must be provided exactly')
        for out,voice in zip(outcomes,voices):
            require(out['core_binding']==voice['core_binding'] and out['owner_role_ref']==voice['owner_role_ref'] and out['owner_principal_ref']==voice['owner_principal']['identity_ref'],'owner outcome order, role or Principal differs')
        require(message['all_required_members_authorized']==all(o['selected_outcome']=='approve-exact-effect' for o in outcomes),'all-required authorization is not the exact computed outcome')
        channel=facts.channel
        require(channel.kind in CHANNELS and message['authorization_channel']==channel.kind and message['channel_verification_binding']==channel.verification_binding,'independently recognized channel differs')
        require(channel.source_cut==source_cut and channel.revoked is False and instant(channel.not_before)<=resolved<=clock<instant(channel.expires_at),'channel expired, revoked or outside source cut')
        require(type(channel.fixture_only) is bool and channel.provenance_bindings,'channel provenance unresolved')
        require(body(channel.verification_binding)=={'schema_version':'lab-selected-checkpoint-channel/v1-candidate',
            'channel_kind':channel.kind,'source_cut':channel.source_cut,'provenance_bindings':list(channel.provenance_bindings),
            'not_before':channel.not_before,'expires_at':channel.expires_at,'revoked':channel.revoked,
            'fixture_only':channel.fixture_only,'authority_effect':'none'},'selected channel evidence differs from host facts')
        for selected in channel.provenance_bindings:read(selected)
        recognized={}
        for fact in facts.recognitions:
            require(type(fact) is Recognition,'typed independent owner recognition required')
            key=(fact.owner_principal_ref,fact.owner_role_ref)
            require(key not in recognized,'ambiguous owner signing recognition');recognized[key]=fact
            require(fact.source_cut==source_cut and fact.revoked is False and instant(fact.not_before)<=resolved<=clock<instant(fact.expires_at),'owner recognition expired, revoked or outside source cut')
            require(type(fact.public_key) is bytes and len(fact.public_key)==32 and type(fact.fixture_only) is bool and fact.fixture_only==channel.fixture_only,'owner signing key or fixture posture differs')
            require(fact.provenance_bindings,'owner recognition provenance unresolved')
            require(body(fact.evidence_binding)=={'schema_version':'lab-selected-checkpoint-signing-recognition/v1-candidate',
                'owner_principal_ref':fact.owner_principal_ref,'owner_role_ref':fact.owner_role_ref,
                'public_key':base64.b64encode(fact.public_key).decode(),'source_cut':fact.source_cut,
                'core_bindings':list(fact.core_bindings),'provenance_bindings':list(fact.provenance_bindings),
                'not_before':fact.not_before,'expires_at':fact.expires_at,'revoked':fact.revoked,
                'fixture_only':fact.fixture_only,'authority_effect':'none'},'selected owner recognition evidence differs from host facts')
            for selected in fact.provenance_bindings:read(selected)
        require(set(recognized)=={(o['owner_principal_ref'],o['owner_role_ref']) for o in outcomes},'recognition set must cover required owners exactly')
        for out in outcomes:
            fact=recognized[(out['owner_principal_ref'],out['owner_role_ref'])]
            require(out['core_binding'] in fact.core_bindings,'owner has no independently selected permission for this exact core')
            attestation=body(out['authorization_evidence_binding'])
            require(type(attestation) is dict and set(attestation)=={'statement','signature'},'closed channel attestation required')
            statement=attestation['statement']
            require(type(statement) is dict and set(statement)=={'schema_version','review_package_binding','checkpoint_binding','source_cut','core_binding','owner_principal_ref','owner_role_ref','selected_outcome','channel_verification_binding','recognition_binding','provenance_bindings','signed_at','expires_at','nonce','authority_effect'},'closed exact owner statement required')
            require(statement['schema_version']=='lab-owner-checkpoint-statement/v1-candidate' and statement['authority_effect']=='none','unknown owner statement version/effect')
            for name in ('core_binding','owner_principal_ref','owner_role_ref','selected_outcome'):require(statement[name]==out[name],'signed owner statement differs: '+name)
            require(statement['review_package_binding']==facts.package_binding and statement['checkpoint_binding']==facts.checkpoint_binding and statement['source_cut']==source_cut,'signature belongs to another package/checkpoint/cut')
            require(statement['channel_verification_binding']==channel.verification_binding and statement['recognition_binding']==fact.evidence_binding,'signature substitutes a channel or recognition')
            require(statement['provenance_bindings']==list(fact.provenance_bindings),'signature provenance differs')
            require(type(statement['nonce']) is str and 16<=len(statement['nonce'])<=256,'bounded explicit channel nonce required')
            require(instant(fact.not_before)<=instant(statement['signed_at'])<=resolved<=clock<instant(statement['expires_at'])<=instant(fact.expires_at),'signed outcome is expired or outside recognized authority period')
            try:
                sig=base64.b64decode(attestation['signature'],validate=True)
                require(base64.b64encode(sig).decode()==attestation['signature'] and len(sig)==64,'canonical Ed25519 signature required')
                Ed25519PublicKey.from_public_bytes(fact.public_key).verify(sig,encoded(statement))
            except Exception as e:raise ResolutionFault('owner channel signature verification failed') from e
        require(source_guard()==self.source_sha256,'source changed before calculation exit')
        return encoded({'schema_version':'lab-checkpoint-resolution-calculation/v1-candidate',
            'resolution_binding':request_binding,'review_package_binding':facts.package_binding,
            'checkpoint_binding':facts.checkpoint_binding,'source_cut':source_cut,
            'ordered_outcomes':copy.deepcopy(outcomes),'all_required_members_authorized':message['all_required_members_authorized'],
            'channel_kind':channel.kind,'fixture_only':channel.fixture_only,
            'source_material_bindings':[read_rows[k] for k in sorted(read_rows)],
            'original_semantic_and_operational_gaps':copy.deepcopy(manifest['original_semantic_and_operational_gaps']),
            'recognition_and_live_authority_verified_by_this_calculation':False,
            'canonical_admission_granted':False,'authority_effect':'none','claim_ceiling':CLAIM})
