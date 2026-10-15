"""Scoped public install bridge and honest candidate release review.

Private operator custody selects exact plan bytes independently of public calls.
Installation is immutable R02 package publication plus an owned active descriptor;
no runtime or service is started. Retained generations support explicit rollback.
"""
import copy
import fcntl
import os
from pathlib import Path
import stat
import uuid
from .protocol import source, compact, ROOT, HERE
from .auth import now, instant
from .handlers import ApplicationError, cut, gap
from .workspace import read_private, atomic, privacy
from . import r02_installer as R02
from . import r02_common as C


class InstallationRelease:
    def __init__(self, host, operation, deadline):
        self.host=host;self.vault=host.vault;self.operation=operation;self.deadline=deadline
        selected=host.channel.policy_guard().get('installation_release_control')
        if selected is None:raise ApplicationError('unauthorized','Independent installation/release custody plan is unavailable.')
        self.plan_binding=selected['plan_binding'];self.plan=source.parse(self.read(self.plan_binding))
        source.require(set(self.plan)=={'schema_version','principal_ref','source_cut','install','release','authority_effect','actual_owner_outcome'},'closed custody plan required')
        source.require(self.plan['schema_version']=='lab-installation-release-plan/v1-candidate' and self.plan['authority_effect']=='none' and self.plan['actual_owner_outcome'] is None,'candidate custody plan required')
        source.require(self.plan['principal_ref']==host.channel.context['principal_ref'],'private custody principal differs')

    def read(self, selected):
        if selected['ref'].startswith('workspace-object:'):
            raw=self.vault.object_read(selected);privacy(source.parse(raw));return raw
        if selected['ref'].startswith('candidate:'):
            return self.vault.material(selected)
        p=ROOT/selected['ref']
        source.require(p.is_relative_to(ROOT) and not any(x in ('..','.env','.local') for x in p.parts),'unselected release evidence path')
        raw=C.read(p);source.require(source.sha(raw)==selected['sha256'],'exact original evidence binding differs');privacy(raw)
        return raw

    def guard(self, *, deadline=True):
        self.host.channel.guard();self.host.schemas.guard();self.vault.guard()
        source.require(self.host.handlers.current(),'original signed source changed')
        source.require(source.parse(self.read(self.plan_binding))==self.plan,'private custody plan changed')
        if deadline and now()>=self.deadline:raise ApplicationError('deadline-exceeded','Strictest real clock window expired before installation effect.')

    def owned(self):
        p=self.plan['install'];root=Path(p['root']);info=root.lstat()
        source.require(root.is_absolute() and root.resolve()==root and root.is_relative_to(Path('/tmp')) and not root.is_relative_to(ROOT),'isolated private install root required')
        source.require(stat.S_ISDIR(info.st_mode) and info.st_uid==os.geteuid() and stat.S_IMODE(info.st_mode)==0o700,'private operator owned install root required')
        source.require([info.st_dev,info.st_ino]==p['root_identity'],'owned install root identity changed')
        raw=read_private(root/'.scope.json');source.require(source.sha(raw)==p['scope_binding']['sha256'],'independent scope bytes changed')
        scope=source.parse(raw)
        source.require(scope=={'schema_version':'lab-owned-install-root/v1-candidate','root':str(root),'root_identity':p['root_identity'],'principal_ref':self.plan['principal_ref'],'private_custody_scope_ref':p['private_custody_scope_ref'],'authority_effect':'none'},'custody scope differs')
        R02.OwnedScope(str(root)).destination(root/p['generation'])
        return root

    def active(self, root):
        if not os.path.lexists(root/'active.json'):return None
        row=source.parse(read_private(root/'active.json'))
        source.require(set(row)=={'schema_version','generation','package_binding','authority_effect'} and row['schema_version']=='lab-installed-active/v1-candidate' and row['authority_effect']=='none','closed active descriptor required')
        source.require(Path(row['generation']).name==row['generation'] and not row['generation'].startswith('.'),'unsafe retained generation')
        return row

    def preflight(self, message, outer, key):
        self.guard();source.require(outer==self.plan['source_cut']==cut(self.host.handlers.view),'exact custody source cut differs')
        if self.operation=='release.prepare':
            self.release_review(message, outer, write=False);return
        p=self.plan['install']
        source.require(set(p)=={'root','root_identity','scope_binding','private_custody_scope_ref','generation','package_path','package_binding','request_controls','approval_binding'},'closed installation grant required')
        source.require(set(p['request_controls'])=={'operation','release_manifest_binding','source_profile_binding','target_environment_binding','preimage_binding','recovery_contract_binding','private_custody_scope_ref'},'closed exact request controls required')
        source.require(Path(p['generation']).name==p['generation'] and not p['generation'].startswith('.'),'canonical installation generation required')
        source.require(p['package_binding']['ref']==p['package_path']+'/selection.json','independent package location differs')
        root=self.owned();controls={k:message[k] for k in p['request_controls']}
        if controls!=p['request_controls']:raise ApplicationError('unauthorized','Public request differs from independently selected exact installation controls.')
        authority=message['authority_basis']
        self.deadline=min(self.deadline,instant(authority['expires_at']))
        source.require(authority['authority_scope']=='operator-local' and authority['owner_principal_ref']==self.plan['principal_ref'] and authority['scope_refs']==[p['private_custody_scope_ref']],'independent local operator authority differs')
        if instant(authority['expires_at'])<=now():raise ApplicationError('expired-authority','Exact local installation authority expired.')
        source.require(authority['policy_bindings']==[self.plan_binding] and authority['evidence_bindings']==[p['approval_binding']],'installation authority must select exact custody policy and isolated approval')
        approval=source.parse(self.read(p['approval_binding']))
        source.require(approval=={'schema_version':'lab-isolated-install-approval/v1-candidate','principal_ref':self.plan['principal_ref'],'package_binding':p['package_binding'],'scope_binding':p['scope_binding'],'request_controls':p['request_controls'],'authorized_effect':'owned-candidate-installation-only','whole_lab_release_approved':False,'authority_effect':'none'},'independent exact package approval differs')
        release=source.parse(self.read(message['release_manifest_binding']))
        source.require(self.host.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:release-manifest:v1-candidate',release),'original release manifest contract differs')
        source.require(release['posture']=='candidate' and release['release_decision_binding'] is None and p['package_binding'] in release['package_bindings'],'isolated package install cannot claim whole release approval')
        package=ROOT/p['package_path'];C.need(package.is_relative_to(ROOT),'selected package outside candidate repository');selection,files=R02.package_bytes(package,p['package_binding']['sha256'])
        source.require(source.parse(self.read(message['target_environment_binding']))==selection['environment'],'actual installation environment differs')
        source.require(message['source_profile_binding']=={'ref':self.host.handlers.view.handle.manifest['profile_binding']['path'],'sha256':self.host.handlers.view.handle.manifest['profile_binding']['sha256']},'selected original source profile differs')
        recovery=source.parse(self.read(message['recovery_contract_binding']))
        source.require(recovery=={'schema_version':'lab-install-recovery-contract/v1-candidate','preserve_generations':True,'restore_sessions':False,'activate_services':False,'uncertain_retry':'inspect-only','authority_effect':'none'},'exact nonactivating retained-history recovery contract differs')
        preimage=source.parse(self.read(message['preimage_binding']))
        source.require(preimage=={'schema_version':'lab-install-preimage/v1-candidate','active':self.active(root),'authority_effect':'none'},'exact active preimage changed')
        active=preimage['active'];operation=message['operation']
        if (operation=='install') != (active is None):raise ApplicationError('conflict','Install requires empty active state; upgrade and rollback require an exact retained predecessor.')
        if active is not None:
            old_package=ROOT/active['package_binding']['ref'];R02.verify_install(root/active['generation'],old_package.parent,active['package_binding']['sha256'])
        if operation=='rollback':
            source.require((root/p['generation']).is_dir(),'rollback requires retained installed generation');R02.verify_install(root/p['generation'],package,p['package_binding']['sha256'])
        elif os.path.lexists(root/p['generation']):
            raise ApplicationError('path-collision','New installation generation already exists; refuse before durable claim.')

    def prepare(self, message, request, outer, key):
        if self.operation=='release.prepare':return self.release_review(message,outer,write=True)
        p=self.plan['install'];root=self.owned()
        lock=os.open(root/'.api-install.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.preflight(message,outer,key)
            package=ROOT/p['package_path']
            self.guard()
            if message['operation']!='rollback':
                R02.install(package,p['package_binding']['sha256'],root/p['generation'],R02.OwnedScope(str(root)))
            verified=R02.verify_install(root/p['generation'],package,p['package_binding']['sha256'])
            # After publication every failure remains an uncertain durable claim.
            self.guard();self.owned()
            active={'schema_version':'lab-installed-active/v1-candidate','generation':p['generation'],'package_binding':p['package_binding'],'authority_effect':'none'}
            pending=root/('.active-'+uuid.uuid4().hex+'.json');atomic(pending,compact(active))
            source.require(source.parse(self.read(message['preimage_binding']))['active']==self.active(root),'installation preimage changed before active descriptor commit')
            self.guard();os.replace(pending,root/'active.json')
            fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            try:os.fsync(fd)
            finally:os.close(fd)
            source.require(self.active(root)==active,'installed active descriptor differs')
            self.guard();self.owned()
            evidence=self.vault.object(compact({'schema_version':'lab-isolated-install-verification/v1-candidate','verification':verified,'active':active,'runtime_activations':0,'external_effects':0,'service_running_proven':False,'retained_history_preserved':True,'authority_effect':'none'}))
            postimage=self.vault.object(compact(active))
            domain={'schema_version':'lab-installation-receipt/v1-candidate','request_binding':request,'release_manifest_binding':message['release_manifest_binding'],'preimage_binding':message['preimage_binding'],'postimage_binding':postimage,'posture':'rolled-back' if message['operation']=='rollback' else 'installed','verification_bindings':[evidence],'private_credentials_in_repository':False,'recovery_required':False,'gaps':[],'claim_ceiling':'Exact owned scratch package and active descriptor only. No service, whole Lab release approval, canonical admission or operational acceptance.','authority_effect':'none'}
            return domain,[self.plan_binding,p['approval_binding'],postimage,evidence]
        finally:os.close(lock)

    def release_review(self, message, outer, write):
        selected=self.plan['release']
        source.require(set(selected)=={'manifest_binding','required_evidence'} and source.parse(self.read(selected['manifest_binding']))==message,'release candidate must equal independent exact manifest selection')
        if message['posture']!='candidate' or message['release_decision_binding'] is not None:raise ApplicationError('gate-required','Release preparation requires candidate posture and no inferred release Decision.')
        gaps=[];checked=[]
        for artifact in [message['product'],message['thesis'],*message['capability_refs']]:
            try:
                subject=self.host.handlers.resolve_exact(artifact)
                source.require(subject['effective_state'] in ('admitted-current','local-admitted-current'),'Product source is not current')
            except (ApplicationError,ValueError):gaps.append(gap(artifact['version_ref'],'The exact current Product/thesis/capability source is unresolved; candidate references do not establish Product acceptance.','release-readiness'))
        for field in ('implementation_bindings','package_bindings','acceptance_contract_bindings','pilot_evidence_bindings','supported_environment_bindings','validation_bindings'):
            for item in message[field]:
                try:
                    self.read(item)
                    if field=='package_bindings':
                        package=ROOT/item['ref'];source.require(package.name=='selection.json','Only selected R02 installation package evidence is supported by this candidate.')
                        R02.package_bytes(package.parent,item['sha256'])
                    checked.append(item)
                except (ValueError,OSError):gaps.append(gap(item['ref'],'Required exact '+field+' evidence is absent or changed.','release-readiness'))
        for field in ('privacy_review_binding','install_contract_binding'):
            try:self.read(message[field]);checked.append(message[field])
            except (ValueError,OSError):gaps.append(gap(message[field]['ref'],'Required exact '+field+' evidence is absent or changed.','release-readiness'))
        for role in selected['required_evidence']:
            # Selected unresolved obligations are honest input evidence, never proof.
            source.require(set(role)=={'subject_ref','reason','binding'},'closed release obligation required')
            value=source.parse(self.read(role['binding']))
            source.require(value.get('authority_effect')=='none' and value.get('result') in ('missing','blocked','not-qualified'),'release obligation must retain the actual unresolved disposition')
            gaps.append(gap(role['subject_ref'],role['reason'],'release-readiness'))
        source.require(selected['required_evidence'],'Whole Lab release requires independent actual human pilot, complete API qualification and owner checkpoint evidence; none is authorized by this development plan.')
        report={'schema_version':'lab-release-preparation-report/v1-candidate','manifest_binding':selected['manifest_binding'],'verified_bindings':checked,'gaps':gaps,'result':'blocked','whole_lab_release_approved':False,'publication_performed':False,'installation_performed':False,'runtime_activations':0,'authority_effect':'none'}
        if not write:return report
        self.guard();report_binding=self.vault.object(compact(report))
        core=self.vault.object(compact({'schema_version':'lab-candidate-release-content-core/v1-candidate','release_manifest_binding':selected['manifest_binding'],'release_ref':message['release_ref'],'package_bindings':message['package_bindings'],'release_decision_created':False,'actual_owner_outcome':None,'authority_effect':'none'}))
        effects=self.vault.object(compact({'schema_version':'lab-release-consequence-review/v1-candidate','release_manifest_binding':selected['manifest_binding'],'review_posture':'blocked','installation_performed':False,'publication_performed':False,'runtime_activations':0,'external_effects':0,'canonical_admissions':0,'authority_effect':'none'}))
        privacy_binding=self.vault.object(compact({'schema_version':'lab-release-private-public-review/v1-candidate','release_manifest_binding':selected['manifest_binding'],'selected_verified_materials':checked,'unresolved_privacy_review_binding':message['privacy_review_binding'],'private_credentials_exported':False,'human_privacy_outcome':None,'publication_permitted':False,'authority_effect':'none'}))
        domain={'schema_version':'lab-proposal-review/v1-candidate','proposal_binding':selected['manifest_binding'],'source_cut':outer,'validation_report_binding':report_binding,'stable_core_bindings':[core],'example_bindings':[effects],'declared_consequence_bindings':[effects],'private_public_review_binding':privacy_binding,'gaps':gaps,'posture':'blocked','authority_effect':'none'}
        return domain,[selected['manifest_binding'],report_binding,core,effects,privacy_binding,*checked,*[r['binding'] for r in selected['required_evidence']]]
