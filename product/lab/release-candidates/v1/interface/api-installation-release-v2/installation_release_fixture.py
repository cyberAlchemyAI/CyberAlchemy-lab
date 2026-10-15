"""Fresh explicit candidate grants, cryptographic transport, real R02 installation."""
import copy
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
import tempfile
import uuid
from .protocol import *
from .handlers import cut
from . import metadata_fixture as MF
from .auth import ReaderChannel, now
from .fixtures import proof, call
from .service import Service
from .workspace import atomic
from . import r02_installer as R02, r02_common as C

@contextmanager
def example(view,schemas,operation='install',release=False,readiness_contract_overrides=None):
    with tempfile.TemporaryDirectory(prefix='cal-installation-release-0148-') as directory:
        base=Path(directory);key,path,_=MF.provision(base,{}, {},scoped=False)
        policy=source.parse(path.read_bytes());workspace=Path(policy['workspace']['root']);wm=source.parse((workspace/'workspace.json').read_bytes())
        def store(value):
            raw=compact(value);digest=source.sha(raw);atomic(workspace/'objects'/(digest+'.json'),raw)
            return {'ref':'workspace-object:'+wm['workspace_ref']+':'+digest,'sha256':digest}
        actor={'principal_ref':policy['principal_ref'],'role_assignment_refs':[],'agent_instance_ref':None,'assignment_ref':None,'session_ref':None}
        root=base/'installation';root.mkdir(mode=0o700);identity=[root.stat().st_dev,root.stat().st_ino];scope='install-scope:'+uuid.uuid4().hex
        scope_raw=compact({'schema_version':'lab-owned-install-root/v1-candidate','root':str(root),'root_identity':identity,'principal_ref':policy['principal_ref'],'private_custody_scope_ref':scope,'authority_effect':'none'});atomic(root/'.scope.json',scope_raw);scope_binding=binding('owned-scope:'+scope,scope_raw)
        package=ROOT/('product/lab/release-candidates/v1/packaging/R02/packages/'+('0002' if operation=='rollback' else '0003'));package_binding=binding(str((package/'selection.json').relative_to(ROOT)),(package/'selection.json').read_bytes())
        source_profile={'ref':view.handle.manifest['profile_binding']['path'],'sha256':view.handle.manifest['profile_binding']['sha256']}
        environment=store(C.load(package/'selection.json')['environment'])
        recovery=store({'schema_version':'lab-install-recovery-contract/v1-candidate','preserve_generations':True,'restore_sessions':False,'activate_services':False,'uncertain_retry':'inspect-only','authority_effect':'none'})
        generation='retained-release' if operation=='rollback' else 'new-release';active=None
        if operation in ('upgrade','rollback'):
            previous=ROOT/('product/lab/release-candidates/v1/packaging/R02/packages/'+('0003' if operation=='rollback' else '0002'));previous_binding=binding(str((previous/'selection.json').relative_to(ROOT)),(previous/'selection.json').read_bytes())
            R02.install(previous,previous_binding['sha256'],root/'previous-release',R02.OwnedScope(str(root)))
            active={'schema_version':'lab-installed-active/v1-candidate','generation':'previous-release','package_binding':previous_binding,'authority_effect':'none'}
            if operation=='rollback':
                R02.install(package,package_binding['sha256'],root/'retained-release',R02.OwnedScope(str(root)))
            atomic(root/'active.json',compact(active))
        preimage=store({'schema_version':'lab-install-preimage/v1-candidate','active':active,'authority_effect':'none'})
        # Current whole-Lab obligations are captured as missing; these are not pilot outcomes.
        missing=store({'schema_version':'lab-release-unresolved-obligation/v1-candidate','result':'missing','human_pilot_observed':False,'complete_API_qualification_observed':False,'actual_owner_outcome':None,'authority_effect':'none'})
        schema=source.parse((ROOT/'docs/proposals/0008-lab-api-contracts/examples/release.prepare/request.json').read_bytes())['message']
        manifest=copy.deepcopy(schema)
        # The manifest retains explicit candidate references. Their actual admission
        # and whole-product satisfaction remain named unresolved obligations.
        for item in [manifest['product'],manifest['thesis'],*manifest['capability_refs']]:item['scope_ref']=view.data['config']['scope_ref'];item['identity_ref']='candidate:'+item['carrier_ref'];item['version_ref']=item['identity_ref']+'@0148'
        manifest.update(release_ref='candidate-release:installation-0148',posture='candidate',release_decision_binding=None,implementation_bindings=[binding(str((HERE/'installation_release.py').relative_to(ROOT)),(HERE/'installation_release.py').read_bytes())],package_bindings=[package_binding],acceptance_contract_bindings=[missing],pilot_evidence_bindings=[missing],privacy_review_binding=missing,validation_bindings=[missing],install_contract_binding=recovery,supported_environment_bindings=[environment],claim_ceiling='Isolated packaging fixture only; human Product pilot and complete Lab release evidence are absent.')
        manifest_binding=store(manifest)
        controls={'operation':operation,'release_manifest_binding':manifest_binding,'source_profile_binding':source_profile,'target_environment_binding':environment,'preimage_binding':preimage,'recovery_contract_binding':recovery,'private_custody_scope_ref':scope}
        approval=store({'schema_version':'lab-isolated-install-approval/v1-candidate','principal_ref':policy['principal_ref'],'package_binding':package_binding,'scope_binding':scope_binding,'request_controls':controls,'authorized_effect':'owned-candidate-installation-only','whole_lab_release_approved':False,'authority_effect':'none'})
        acceptance_path=ROOT/'product/lab/release-candidates/v1/release-scope.json'
        readiness_contract_data={'schema_version':'lab-release-readiness-contract/v1-candidate','manifest_binding':manifest_binding,'source_cut':cut(view),'acceptance_scope_binding':binding(str(acceptance_path.relative_to(ROOT)),acceptance_path.read_bytes()),'evidence_requirements':[],'signers':[],'owner_prerequisites':[],'authority_effect':'none','actual_owner_outcome':None}
        readiness_contract_data.update(readiness_contract_overrides or {})
        readiness_contract=store(readiness_contract_data)
        plan={'schema_version':'lab-installation-release-plan/v1-candidate','principal_ref':policy['principal_ref'],'source_cut':cut(view),'install':{'root':str(root),'root_identity':identity,'scope_binding':scope_binding,'private_custody_scope_ref':scope,'generation':generation,'package_path':str(package.relative_to(ROOT)),'package_binding':package_binding,'request_controls':controls,'approval_binding':approval},'release':{'manifest_binding':manifest_binding,'readiness_contract_binding':readiness_contract},'authority_effect':'none','actual_owner_outcome':None}
        plan_binding=store(plan)
        policy['expires_at']=(now()+timedelta(hours=2)).isoformat()
        policy.update(schema_version='lab-local-installation-release-policy/v1-candidate',allowed_operations=list(INSTALLATION_RELEASE_SUPPORTED),purpose='durable-metadata-and-exact-installation-release',installation_release_control={'plan_binding':plan_binding})
        raw=compact(policy);path.write_bytes(raw);channel=ReaderChannel(path,source.sha(raw),schemas);channel.authenticate(proof(key,channel.challenge));host=Service(view,channel,schemas)
        try:
            wire=call(channel.context,'lab.status',cut(view));wire.update(operation='release.prepare' if release else 'installation.execute',idempotency_key='installation-release:'+uuid.uuid4().hex,deadline=(now()+timedelta(minutes=60)).isoformat())
            wire['message']=manifest if release else dict(schema_version='lab-install-request/v1-candidate',request_ref='request:installation-0148',actor=actor,authority_basis={'authority_scope':'operator-local','owner_principal_ref':policy['principal_ref'],'policy_bindings':[plan_binding],'evidence_bindings':[approval],'scope_refs':[scope],'expires_at':policy['expires_at']},runtime_activations=0,external_effect_refs=[],authority_effect='none',**controls)
            yield host,wire,plan
        finally:host.close()
