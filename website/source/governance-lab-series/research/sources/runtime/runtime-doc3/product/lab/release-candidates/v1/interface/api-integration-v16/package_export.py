"""Authenticated publication of exact native candidates or signed source roots.

The independently provisioned plan selects destination, original materials,
dependency graph and controls. Caller fields never grant export permission.
"""
import copy
from pathlib import Path
import importlib

from .protocol import source, compact, binding, HERE, ROOT
from .handlers import ApplicationError, cut
from .workspace import read_private, safe, privacy
from .package_import import PUB, T, schema_original
from .guarded_candidate import selection, calculation, B
from .auth import now
from . import artifact_model as model

PLAN_URI='urn:cyberalchemy-lab:internal:package-export-plan:v1-candidate'
PUBLIC_FIELDS=('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')

def public(header):return {key:copy.deepcopy(header[key]) for key in PUBLIC_FIELDS}

def validate_control(policy,schemas):
    source.require(policy['schema_version']=='lab-local-package-export-policy/v1-candidate','independent export policy required')
    root=Path(policy['workspace']['root'])
    manifest=source.parse(read_private(root/'workspace.json'))
    selected=policy['package_export_control']['plan_binding']
    source.require(selected['ref']=='workspace-object:'+manifest['workspace_ref']+':'+selected['sha256'],'export plan namespace differs')
    raw=read_private(root/'objects'/(selected['sha256']+'.json'))
    source.require(source.sha(raw)==selected['sha256'],'independent export plan bytes changed')
    plan=source.parse(raw)
    source.require(schemas.protocol_valid(PLAN_URI,plan),'closed export plan required')
    output=Path(plan['output_root'])
    source.require(output==root/'packages','export destination is outside selected owned workspace')
    safe(output,0o700)
    source.require(PUB.identity(output.stat())==plan['output_root_identity'],'export destination identity changed')
    scope_raw=read_private(output/'.scope.json')
    expected={'schema_version':'lab-owned-package-root/v1-candidate','output_root':str(output),
        'output_root_scope_ref':plan['output_root_scope_ref'],'principal_ref':policy['principal_ref'],
        'output_root_identity':plan['output_root_identity'],'authority_effect':'none','actual_owner_outcome':None}
    source.require(source.sha(scope_raw)==plan['scope_binding']['sha256'] and source.parse(scope_raw)==expected,'export destination scope changed')
    return plan

class PackageExport:
    def __init__(self,host):
        service=importlib.import_module(__package__+'.service')
        auth=importlib.import_module(__package__+'.auth')
        source.require(type(host) is service.Service and type(host.channel) is auth.ReaderChannel,
            'actual selected Service and authenticated operator channel required')
        self.host=host;self.vault=host.vault;self.schemas=host.schemas
        self.transfer=T.Transfer(PUB.TRANSFER_SOURCE)

    def read(self,selected):
        return self.vault.object_read(selected) if selected['ref'].startswith('workspace-object:') else self.vault.material(selected)

    def proofs(self,view):
        # These are the original public signed-source archive and replay profile,
        # never a private signer, a caller-selected path or an Agent RAM buffer.
        rows=[view.selected['archive_binding'],view.handle.manifest['profile_binding']]
        return [{'ref':row['path'],'sha256':row['sha256']} for row in rows]

    def publisher(self,plan,deadline):
        def source_guard():source.require(self.host.handlers.current(),'original export source changed')
        def permission():
            self.host.channel.guard()
            source.require(validate_control(self.host.channel.policy,self.schemas)==plan,'independent export permission changed')
            return now()<deadline
        return PUB.Publisher(plan['output_root'],plan['output_root_scope_ref'],plan['output_root_identity'],
            plan['scope_binding'],self.host.channel.context['principal_ref'],self.transfer,source_guard,
            permission,plan['max_package_bytes'],plan['max_generations'])

    def evaluate(self,message,outer,key,deadline,writer):
        context=self.host.channel.guard();plan=validate_control(self.host.channel.policy,self.schemas)
        observed=self.host.handlers.selected_cut({'source_cut':message['source_cut']},outer)
        source.require(observed==cut(self.host.handlers.view)==plan['source_cut'],'export does not select the exact current source cut')
        for name in ('export_contract_binding','privacy_review_binding'):
            if message[name]!=plan[name]:raise ApplicationError('unauthorized','Export controls differ from independent host selection.')
        source.require(now()<deadline and type(key) is str and key,'current bounded export command required')
        actor={name:context[name] for name in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
        actor['role_assignment_refs']=context['role_assignment_bindings']
        source.require(message['actor']==actor,'export Actor differs from verified channel')
        contract_raw=self.read(plan['export_contract_binding']);review_raw=self.read(plan['privacy_review_binding'])
        contract=self.transfer.closed('export-contract',contract_raw)
        self.transfer.closed('privacy-review',review_raw)
        source.require(contract['maximum_package_bytes']<=plan['max_package_bytes'],'contract exceeds independently provisioned package budget')
        view=self.host.handlers.selected_view;proofs=self.proofs(view)
        candidate={};evidence=[];references=[];allowed_inputs=[]
        proposal_binding=plan['source_proposal_binding']
        if contract['source_posture']=='controlled-candidate':
            source.require(proposal_binding is not None,'controlled roots require their independently selected native proposal')
            raw=self.read(proposal_binding);proposal=source.parse(raw)
            source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate',proposal),
                'original native ChangeProposal contract required')
            source.require(proposal['actor']==actor and proposal['idempotency_key']==key and proposal['base_cut']==observed,
                'native export proposal Actor, key or cut differs')
            report,details=self.host.candidates.validate(proposal,proposal_binding,observed,raw,evidence_writer=writer)
            if report['result']!='pass' or report['gaps']:
                raise ApplicationError('closure-missing','Original native proposal validation did not close all export obligations.')
            source.require(all(t['operation']!='withdraw' for t in proposal['targets']),'withdrawals are not candidate export bodies')
            candidate={t['artifact']['version_ref']:t for t in proposal['targets']}
            source.require(message['artifact_refs']==[public(t['artifact']) for t in proposal['targets']],
                'export roots must preserve every exact native proposal target in declared order')
            evidence.extend(details['evidence']);references=report['reference_checks']
            allowed_inputs=proposal['schema_bindings']+proposal['evidence_bindings']
            for target in candidate.values():allowed_inputs.extend([target['candidate_binding'],target['decision_core_binding']])
        else:
            source.require(contract['source_posture']=='admitted-source' and proposal_binding is None,
                'admitted roots cannot substitute a candidate proposal or unknown source posture')
            source.require(contract['source_admission_basis']==proofs,'signed roots require complete independently selected original archive/profile basis')
            for header in message['artifact_refs']:
                subject=self.host.handlers.resolve_exact(header)
                source.require(subject['effective_state'] in ('admitted-current','local-admitted-current'),'export root is not current in its selected signed source')
        materials=[]
        with model.model_read_batch(view):
            for row in plan['materials']:
                selected=row['binding'];header=row['artifact'];origin=row['origin']
                if origin=='artifact':
                    source.require(header is not None and row['encoding']=='json-utf8','original artifact carrier required')
                    target=candidate.get(header['version_ref'])
                    if target is not None:
                        source.require(header==public(target['artifact']),'candidate header differs from native proposal')
                        raw=self.vault.material({'ref':target['content']['content_ref'],'sha256':target['content']['byte_sha256']})
                        required=[target['candidate_binding'],target['decision_core_binding']]
                    else:
                        subject=self.host.handlers.resolve_exact(header)
                        source.require(subject['effective_state'] in ('admitted-current','local-admitted-current'),'dependency is not exact current signed source')
                        raw,_,_,_=model.record_bytes(view,subject);required=proofs
                    schema,schema_raw=schema_original(view,header['carrier_ref'])
                    required=[*required,schema]
                    for dependency in required:source.require(dependency in row['dependencies'],'artifact omits required schema/core/signed-source proof')
                elif origin=='schema':
                    source.require(header is None and row['encoding']=='json-utf8','schema material cannot masquerade as artifact')
                    matches=[(carrier,entry) for carrier,entry in view.data['projection']['contracts'].items()
                        if {'ref':entry['schema_path'],'sha256':entry['schema_sha256']}==selected]
                    source.require(matches,'unselected carrier schema')
                    actual,raw=schema_original(view,matches[0][0])
                    source.require(actual==selected,'carrier schema selection differs')
                elif origin=='source-proof':
                    source.require(header is None and row['encoding']=='json-utf8' and selected in proofs,'unselected original source proof')
                    raw=source.original({'path':selected['ref'],'sha256':selected['sha256']})
                else:
                    source.require(origin=='proposal-input' and header is None and selected in allowed_inputs
                        and row['encoding']=='json-utf8','unselected native proposal metadata/core/evidence input')
                    raw=self.vault.material(selected)
                source.require(source.sha(raw)==selected['sha256'],'selected material original bytes differ')
                materials.append(T.Material(T.encoded(selected),raw,T.encoded(row['dependencies']),
                    None if header is None else T.encoded(header),row['encoding']))
        materials=tuple(materials);graph=self.transfer.graph(materials)
        def covers(header):return [entry for entry in graph.values() if entry['artifact']==header]
        for check in references:
            source.require(check['posture']=='resolved' and check['resolved_ref'] is not None,'native export reference remains unresolved')
            target=check['resolved_ref'];source.require(len(covers(target))==1,'package omits native verified domain reference')
            source_version=check['source_version_ref']
            source_rows=[entry for entry in graph.values() if entry['artifact'] is not None and entry['artifact']['version_ref']==source_version]
            source.require(len(source_rows)==1 and covers(target)[0]['binding'] in source_rows[0]['dependencies'],
                'package graph omits explicit native domain dependency')
        facts=T.ExportFacts(T.encoded(actor),T.encoded(observed),T.encoded(plan['export_contract_binding']),
            T.encoded(plan['privacy_review_binding']),materials)
        # Original transfer verification includes complete reachability, all
        # declared encodings, privacy controls, exact roots and byte budgets.
        archive=self.transfer.export(compact(message),facts,contract_raw,review_raw)
        package_binding=T.pin('source-package:'+source.sha(archive),archive)
        verification={'schema_version':'lab-private-package-export-verification/v1-candidate',
            'source_cut':observed,'plan_binding':self.host.channel.policy['package_export_control']['plan_binding'],
            'package_binding':package_binding,'source_posture':contract['source_posture'],
            'source_proof_bindings':proofs,'native_proposal_binding':proposal_binding,
            'material_bindings':[entry['binding'] for entry in graph.values()],
            'dependency_bindings':message['dependency_bindings'],'target_admission_granted':False,
            'contains_private_credentials':False,'contains_session_memory':False,
            'authority_effect':'none','actual_owner_outcome':None}
        evidence.append(writer.object(compact(verification)))
        return plan,archive,package_binding,evidence

    def preflight(self,message,outer,key,deadline):
        buffer=B.EvidenceBuffer(self.vault.manifest['workspace_ref'],lambda raw:privacy(source.parse(raw)))
        try:
            with selection(self.host):self.evaluate(message,outer,key,deadline,buffer)
        finally:buffer.discard()

    def prepare(self,message,request,outer,key,deadline,original_message):
        source.require(binding(request['ref'],original_message)==request,'original export request bytes differ')
        with calculation(self.host) as writer:
            plan,archive,package_binding,evidence=self.evaluate(message,outer,key,deadline,writer)
        publisher=self.publisher(plan,deadline)
        try:
            receipt=publisher.publish(archive,package_binding,request,message['source_cut'])
        except PUB.RecoveryRequired:
            receipt={'schema_version':'lab-file-materialization-receipt/v1-candidate','request_binding':request,
                'manifest_binding':None,'source_cut':message['source_cut'],'generation_ref':None,
                'posture':'indeterminate','output_bindings':[],'canonical_replay_source':False,
                'unmanaged_files_overwritten':False,
                'gaps':[{'gap_ref':'gap:package-export-reconciliation','subject_ref':message['request_ref'],
                    'reason':'Managed publication may have reserved a generation. Inspect exact owned state; never overwrite or redispatch.',
                    'owner_route':'R03/S02/R08','blocking_use':'package-use'}],
                'claim_ceiling':'Uncertain candidate package publication only; no completed generation, target admission or automatic replay.',
                'authority_effect':'none','recovery_required':True}
        source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:file-materialization-receipt:v1-candidate',receipt),
            'actual publication receipt violates original public contract')
        return receipt,evidence

    def readback(self,message,outer,key,deadline,recorded):
        if recorded['recovery_required']:raise ApplicationError('recovery-required','Recorded package publication is uncertain; no write retry is permitted.')
        buffer=B.EvidenceBuffer(self.vault.manifest['workspace_ref'],lambda raw:privacy(source.parse(raw)))
        try:
            with selection(self.host):plan,archive,package_binding,_=self.evaluate(message,outer,key,deadline,buffer)
        finally:buffer.discard()
        try:
            actual,receipt=self.publisher(plan,deadline).read_package(package_binding,recorded['request_binding'],
                recorded['source_cut'],recorded['generation_ref'])
        except PUB.RecoveryRequired as error:raise ApplicationError('recovery-required','Recorded package generation requires read-only reconciliation.') from error
        source.require(actual==archive and receipt==recorded,'recorded package generation differs from exact verified originals')
        return copy.deepcopy(recorded)
