"""Synthetic pure-rule fixtures. No actual owner, live store or Agent exists."""
import base64
import copy
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from . import rules as E

class Fixture:
    def __init__(self,kind='operator-signature',outcomes=None):
        self.engine=E.Rules();self.materials={};self.keys={}
        self.now=datetime.now(timezone.utc);self.start=(self.now-timedelta(minutes=1)).isoformat();self.end=(self.now+timedelta(minutes=10)).isoformat()
        self.signed=(self.now-timedelta(seconds=1)).isoformat();self.at=self.now.isoformat()
        self.cut={'store_ref':'fixture:checkpoint-store','branch_ref':'fixture:checkpoint-branch','commit_sequence':1,
            'commit_sha256':'a'*64,'source_profile_sha256':'b'*64,'streams':[]}
        def store(ref,value,raw=None):
            raw=E.encoded(value) if raw is None else raw;selected=E.binding(ref,raw)
            self.materials[(ref,selected['sha256'])]=raw;return selected
        self.store=store
        proof=store('fixture:source-proof',{'fixture_only':True,'source_cut':self.cut,'authority_effect':'none'})
        self.cores=[];targets=[];decisions=[]
        for i in range(2):
            record=E.parse((E.ROOT/'authority/artifact-types/work/v1/fixtures/valid/record.json').read_bytes())
            record.update(node_id='work:checkpoint-fixture:'+str(i),scope_ref='scope:checkpoint-fixture')
            raw=(__import__('json').dumps(record,indent=3,ensure_ascii=False)+'\n').encode()
            content=store('fixture:target:'+str(i),record,raw)
            header={'scope_ref':'scope:checkpoint-fixture','identity_ref':record['node_id'],
                'version_ref':record['node_id']+'@candidate.1','carrier_ref':'cal.artifact-type.work/v1','byte_sha256':E.sha(raw)}
            metadata={'schema_version':'lab-candidate-target-metadata/v1-candidate','category':'artifact-instance',
                'decision_ref':'decision:fixture:'+str(i),'contract':None}
            mb=store('fixture:metadata:'+str(i),metadata)
            native={'category':metadata['category'],'operation':'admit','version_ref':header['version_ref'],
                'carrier_ref':header['carrier_ref'],'record':record,'predecessor_ref':None,
                'decision_ref':metadata['decision_ref'],'contract':None,'content':self.engine.custody.content_entry(raw)}
            core={'decision_ref':metadata['decision_ref'],'category':metadata['category'],'operation':'admit',
                'version_ref':header['version_ref'],'target_digest':self.engine.common.digest(native)}
            cb=store('fixture:core:'+str(i),core,self.engine.common.encoded(core));self.cores.append(cb)
            target={'operation':'admit','artifact':header,'predecessor':None,'content':{'content_ref':content['ref'],
                'byte_sha256':content['sha256'],'size_bytes':len(raw),'media_type':'application/json'},
                'candidate_binding':mb,'requested_effect':'Synthetic exact target for rule checks only.', 'decision_core_binding':cb}
            targets.append({'target':target,'original_content_binding':content,'core_binding':cb,
                'requested_effect':target['requested_effect'],'admission_posture':'unadmitted-proposed-effect'})
            decisions.append({'decision_ref':core['decision_ref'],'decision_core_sha256':cb['sha256'],
                'scope_ref':'scope:checkpoint-fixture','owner_ref':'principal:fixture:a','effect_kind':'artifact-instance:admit',
                'target_refs':[header['version_ref']],'target_digests':[{'target_ref':header['version_ref'],'sha256':header['byte_sha256']}],
                'selected_outcome':None})
        def carrier(kind,payload):
            value=E.parse((E.ROOT/f'authority/artifact-types/{kind}/v1/fixtures/valid/record.json').read_bytes())
            value.update(node_id=kind+':checkpoint-fixture',scope_ref='scope:checkpoint-fixture',payload=payload)
            selected=store('fixture:'+kind,value)
            header={'scope_ref':value['scope_ref'],'identity_ref':value['node_id'],'version_ref':value['node_id']+'@candidate.1',
                'carrier_ref':'cal.artifact-type.'+kind+'/v1','byte_sha256':selected['sha256']}
            return value,header,selected
        invalidation=['any-target-original-byte-change','owner-routing-or-current-authority-change']
        bundle,bh,bb=carrier('decision-bundle',{'ordered_decisions':decisions,'bundle_digest':E.sha(E.encoded(decisions)),
            'all_targets_materialized':True,'atomicity_requirement':'all-or-nothing','checkpoint_ref':'decision-checkpoint:checkpoint-fixture',
            'invalidation_conditions':invalidation})
        profile={'scope_ref':'scope:checkpoint-fixture','identity_ref':'workflow-decision-profile:fixture',
            'version_ref':'workflow-decision-profile:fixture@1','carrier_ref':'cal.artifact-type.workflow-decision-profile/v1','byte_sha256':'c'*64}
        checkpoint,ch,cpb=carrier('decision-checkpoint',{'workflow_instance_ref':'protocol:fixture:review',
            'workflow_profile_ref':profile['version_ref'],'resolved_preference_ref':'preference:fixture@1',
            'decision_bundle_ref':bundle['node_id'],'checkpoint_kind':'final-review','presentation_state':'pending',
            'opened_at':self.start,'closed_at':None})
        self.checkpoint_binding=cpb
        shared=store('fixture:construction-material',{'fixture_only':True,'authority_effect':'none'})
        voices=[]
        for i,principal,role in ((0,'principal:fixture:a','role:fixture:a'),(0,'principal:fixture:b','role:fixture:b'),(1,'principal:fixture:a','role:fixture:a')):
            principal_body={'scope_ref':'scope:checkpoint-fixture','identity_ref':principal,'version_ref':principal+'@1',
                'carrier_ref':'cal.artifact-type.principal/v1','byte_sha256':E.sha(E.encoded({'fixture_principal':principal}))}
            voices.append({'core_index':i,'voice_index':sum(v['core_index']==i for v in voices),'core_binding':self.cores[i],
                'owner_role_ref':role,'owner_principal':principal_body,'role_declaration_binding':shared,
                'selected_outcome':None,'current_owner_authority_verified':False})
        self.manifest={'schema_version':'lab-exact-review-materialization/v1-candidate','package_ref':'review-package:checkpoint-fixture',
            'base_cut':self.cut,'source_API_binding':shared,'original_review_binding':shared,'proposal_binding':shared,
            'validation_report_binding':shared,'original_semantic_and_operational_gaps':[{'reason':'Synthetic unadmitted target; live authority/semantic closure is not asserted.'}],
            'input_posture':'blocked','targets':targets,'ordered_core_bindings':self.cores,'ordered_required_owner_responses':voices,
            'workflow_decision_profile':profile,'preference':{'fixture_only':True},'preference_basis':'candidate-proposal',
            'preference_current_admission_claimed':False,'workflow_protocol':{'reference':'protocol:fixture:review'},
            'workflow_protocol_is_WorkflowRun_artifact':False,'routing_original_binding':shared,
            'generated_carriers':[{'artifact':bh,'object_binding':bb},{'artifact':ch,'object_binding':cpb}],
            'example_bindings':[shared],'declared_consequence_bindings':[shared],'private_public_review_binding':shared,
            'human_checkpoint_count':1,'all_targets_materialized':True,'atomicity_requirement':'all-or-nothing',
            'actual_owner_outcome':None,'current_owner_authority_verified':False,'repository_admissions_applied':0,
            'runtime_activations':0,'external_effect_refs':[],'invalidation_conditions':invalidation,
            'claim_ceiling':'Synthetic pure-rule fixture only.','authority_effect':'none'}
        self.package={'schema_version':'lab-review-package/v1-candidate','package_ref':self.manifest['package_ref'],'base_cut':self.cut,
            'manifest_binding':store('fixture:manifest',self.manifest),'decision_bundle':bh,'checkpoint':ch,'workflow_decision_profile':profile,
            'ordered_core_bindings':self.cores,'validation_bindings':[shared],'example_bindings':[shared],
            'operational_instruction_bindings':[],'all_targets_materialized':True,'human_checkpoint_count':1,
            'atomicity_requirement':'all-or-nothing','invalidation_conditions':invalidation,'authority_effect':'none'}
        self.package_binding=store('fixture:review-package',self.package)
        channel_raw={'schema_version':'lab-selected-checkpoint-channel/v1-candidate','channel_kind':kind,'source_cut':self.cut,
            'provenance_bindings':[proof],'not_before':self.start,'expires_at':self.end,'revoked':False,'fixture_only':True,'authority_effect':'none'}
        channel=E.Channel(kind,store('fixture:channel',channel_raw),self.cut,(proof,),self.start,self.end,False,True)
        recognitions=[]
        for principal,role in sorted({(v['owner_principal']['identity_ref'],v['owner_role_ref']) for v in voices}):
            key=Ed25519PrivateKey.generate();self.keys[(principal,role)]=key
            public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
            cores=tuple(v['core_binding'] for v in voices if (v['owner_principal']['identity_ref'],v['owner_role_ref'])==(principal,role))
            recognition_raw={'schema_version':'lab-selected-checkpoint-signing-recognition/v1-candidate','owner_principal_ref':principal,
                'owner_role_ref':role,'public_key':base64.b64encode(public).decode(),'source_cut':self.cut,'core_bindings':list(cores),
                'provenance_bindings':[proof],'not_before':self.start,'expires_at':self.end,'revoked':False,'fixture_only':True,'authority_effect':'none'}
            recognitions.append(E.Recognition(principal,role,public,self.cut,cores,store('fixture:recognition:'+role,recognition_raw),
                (proof,),self.start,self.end,False,True))
        self.facts=E.Facts(self.cut,self.package_binding,cpb,(proof,),channel,tuple(recognitions))
        self.message={'schema_version':'lab-checkpoint-resolution/v1-candidate','review_package_binding':self.package_binding,
            'checkpoint_binding':cpb,'resolved_at':self.at,'ordered_outcomes':[], 'authorization_channel':kind,
            'channel_verification_binding':channel.verification_binding,'all_required_members_authorized':True,'authority_effect':'none'}
        for i,v in enumerate(voices):
            outcome=(outcomes or ['approve-exact-effect']*len(voices))[i]
            self.message['ordered_outcomes'].append({'core_binding':v['core_binding'],'owner_principal_ref':v['owner_principal']['identity_ref'],
                'owner_role_ref':v['owner_role_ref'],'selected_outcome':outcome,'authorization_evidence_binding':shared})
        self.message['all_required_members_authorized']=all(o['selected_outcome']=='approve-exact-effect' for o in self.message['ordered_outcomes'])
        self.message=copy.deepcopy(self.message)
        self.resign()
    def resign(self):
        for i,out in enumerate(self.message['ordered_outcomes']):
            fact=next(r for r in self.facts.recognitions if r.owner_principal_ref==out['owner_principal_ref'] and r.owner_role_ref==out['owner_role_ref'])
            statement={'schema_version':'lab-owner-checkpoint-statement/v1-candidate','review_package_binding':self.message['review_package_binding'],
                'checkpoint_binding':self.message['checkpoint_binding'],'source_cut':self.cut,'core_binding':out['core_binding'],
                'owner_principal_ref':out['owner_principal_ref'],'owner_role_ref':out['owner_role_ref'],'selected_outcome':out['selected_outcome'],
                'channel_verification_binding':self.message['channel_verification_binding'],'recognition_binding':fact.evidence_binding,
                'provenance_bindings':list(fact.provenance_bindings),'signed_at':self.signed,'expires_at':self.end,
                'nonce':'fixture-exact-voice-'+str(i),'authority_effect':'none'}
            attestation={'statement':statement,'signature':base64.b64encode(self.keys[(fact.owner_principal_ref,fact.owner_role_ref)].sign(E.encoded(statement))).decode()}
            out['authorization_evidence_binding']=self.store('fixture:attestation:'+str(i),attestation)
    def read(self,b):return self.materials[(b['ref'],b['sha256'])]
    def calculate(self):
        raw=E.encoded(self.message)
        return E.parse(self.engine.calculate(raw,E.binding('fixture:resolution',raw),self.facts,self.read,evaluated_at=self.at))
    def rebind_manifest(self):
        self.package['manifest_binding']=self.store('fixture:manifest',self.manifest)
        self.package_binding=self.store('fixture:review-package',self.package)
        self.facts=replace(self.facts,package_binding=self.package_binding)
        self.message['review_package_binding']=self.package_binding;self.resign()
    def change_attestation(self,index,fn,*,sign=False):
        out=self.message['ordered_outcomes'][index];attestation=copy.deepcopy(E.parse(self.read(out['authorization_evidence_binding'])))
        fn(attestation)
        if sign:
            s=attestation['statement'];attestation['signature']=base64.b64encode(self.keys[(s['owner_principal_ref'],s['owner_role_ref'])].sign(E.encoded(s))).decode()
        out['authorization_evidence_binding']=self.store('fixture:attestation:'+str(index),attestation)
    def close(self):self.keys.clear();self.materials.clear()
