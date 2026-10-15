"""Owned actual authenticated export fixture; no synthetic publication callback."""
from contextlib import contextmanager
import copy
import json
from pathlib import Path
import tempfile

from . import metadata_fixture as MF, protocol as P, auth as A
from .package_fixture import target_materials
from .package_import import PUB,T,schema_original
from .package_export import public
from .workspace import atomic
from .handlers import cut
from .service import Service
from . import artifact_model as model

KEY='fixture:R03-public-package-export'

@contextmanager
def example(view,schemas,*,admitted=False,grant=True):
    R=P.source.custody_delivery().records
    with tempfile.TemporaryDirectory(prefix='cal-R03-public-package-export-') as temporary:
        root=Path(temporary);root.chmod(0o700)
        rows={};metadata={};target=None
        if not admitted:
            record=copy.deepcopy(view.subjects[R.WORK+'@'+R.VERSION]['record'])
            record.update(node_id='work:R03-public-package-export',name='Candidate package export Work',relation_refs=[])
            record['payload'].update(project_ref=view.data['config']['scope_ref'],goal_refs=[R.GOAL+'@'+R.VERSION],
                input_refs=[R.INTENT+'@'+R.VERSION],output_refs=[R.INTENT+'@'+R.VERSION],completion_state='candidate-prepared',
                work_statement='Prepare exact candidate package export for review; no completed Work or target admission.')
            rows,metadata,target=target_materials(view,record,'public-export')
            target['requested_effect']='Prepare exact candidate package export for final review; no source or target admission.'
        key,policy_path,_=MF.provision(root,rows,metadata,scoped=False)
        policy=P.frame_parse(policy_path.read_bytes());workspace=Path(policy['workspace']['root'])
        manifest=P.frame_parse((workspace/'workspace.json').read_bytes())
        actor={'principal_ref':policy['principal_ref'],'role_assignment_refs':[],
            'agent_instance_ref':None,'assignment_ref':None,'session_ref':None}
        selected_cut=cut(view)
        def store(value):
            raw=P.compact(value);digest=P.source.sha(raw);atomic(workspace/'objects'/(digest+'.json'),raw)
            return {'ref':'workspace-object:'+manifest['workspace_ref']+':'+digest,'sha256':digest}
        proposal_binding=None
        if target is not None:
            proposal_binding=store({'schema_version':'lab-change-proposal/v1-candidate',
                'proposal_ref':'proposal:R03-public-package-export','actor':actor,'scope_ref':view.data['config']['scope_ref'],
                'base_cut':selected_cut,'source_profile_binding':{'ref':view.handle.manifest['profile_binding']['path'],
                    'sha256':view.handle.manifest['profile_binding']['sha256']},
                'workspace_binding':{'ref':'workspace:'+manifest['workspace_ref'],'sha256':policy['workspace']['manifest_sha256']},
                'targets':[target],'schema_bindings':[],'connection_proposals':[],'evidence_bindings':[],
                'idempotency_key':KEY,'challenge_route':view.data['config']['challenge_route'],'authority_effect':'none'})
        material_rows={};originals={}
        def material(selected,raw,dependencies,origin,header=None):
            ref=selected['ref'];assert ref not in material_rows or originals[ref]==raw
            material_rows[ref]={'binding':selected,'artifact':header,'dependencies':dependencies,'origin':origin,'encoding':'json-utf8'}
            originals[ref]=raw;return selected
        proof_bindings=[]
        for row in (view.selected['archive_binding'],view.handle.manifest['profile_binding']):
            selected={'ref':row['path'],'sha256':row['sha256']}
            proof_bindings.append(material(selected,P.source.original(row),[],'source-proof'))
        def schema(carrier):
            selected,raw=schema_original(view,carrier)
            return material(selected,raw,[],'schema')
        def current(requested):
            matches=[s for s in view.subjects.values() if requested in (s['identity'],s['version_ref'])
                and s['effective_state'] in ('admitted-current','local-admitted-current')]
            assert len(matches)==1,requested
            subject=matches[0];header=model.artifact_ref(view,subject);raw,_,_,_=model.record_bytes(view,subject)
            selected=T.pin('package:retained:'+header['version_ref'],raw)
            return material(selected,raw,[*proof_bindings,schema(header['carrier_ref'])],'artifact',header),header
        with model.model_read_batch(view):
            if target is not None:
                deps=[]
                for requested in (view.data['config']['scope_ref'],R.GOAL+'@'+R.VERSION,R.INTENT+'@'+R.VERSION):
                    selected,_=current(requested)
                    if selected not in deps:deps.append(selected)
                for selected in (target['candidate_binding'],target['decision_core_binding']):
                    deps.append(material(selected,rows[selected['ref']],[],'proposal-input'))
                deps.append(schema(target['artifact']['carrier_ref']))
                selected={'ref':target['content']['content_ref'],'sha256':target['content']['byte_sha256']}
                root_header=public(target['artifact']);material(selected,rows[selected['ref']],deps,'artifact',root_header)
            else:
                _,root_header=current(R.WORK+'@'+R.VERSION)
        transfer=T.Transfer(PUB.TRANSFER_SOURCE)
        materials=tuple(T.Material(T.encoded(row['binding']),originals[row['binding']['ref']],T.encoded(row['dependencies']),
            None if row['artifact'] is None else T.encoded(row['artifact'])) for row in material_rows.values())
        graph=transfer.graph(materials);roots=[root_header];admission=proof_bindings if admitted else []
        closure=transfer.closure(graph,roots,admission)
        contract={'schema_version':'lab-package-export-contract/v2-candidate','source_cut':selected_cut,
            'artifact_refs':roots,'dependency_bindings':closure,'source_admission_basis':admission,
            'source_posture':'admitted-source' if admitted else 'controlled-candidate',
            'maximum_package_bytes':T.MAX_PACKAGE_BYTES,'authority_effect':'none','actual_owner_outcome':None}
        contract_binding=store(contract)
        review={'schema_version':'lab-package-privacy-review/v2-candidate','source_cut':selected_cut,
            'export_contract_binding':contract_binding,'materials':[graph[k]['binding'] for k in sorted(graph)],
            'material_encodings':[{'binding':graph[k]['binding'],'encoding':graph[k]['encoding']} for k in sorted(graph)],
            'include_session_memory':False,'include_private_credentials':False,'authority_effect':'none','actual_owner_outcome':None}
        review_binding=store(review)
        output=workspace/'packages';output.mkdir(mode=0o700)
        scope='package-output:R03-public-export';identity=PUB.identity(output.stat())
        scope_raw=PUB.encoded({'schema_version':'lab-owned-package-root/v1-candidate','output_root':str(output),
            'output_root_scope_ref':scope,'principal_ref':policy['principal_ref'],'output_root_identity':identity,
            'authority_effect':'none','actual_owner_outcome':None})
        atomic(output/'.scope.json',scope_raw)
        plan={'schema_version':'lab-package-export-plan/v1-candidate','source_cut':selected_cut,
            'export_contract_binding':contract_binding,'privacy_review_binding':review_binding,
            'source_proposal_binding':proposal_binding,'materials':[material_rows[k] for k in sorted(material_rows)],
            'output_root':str(output),'output_root_scope_ref':scope,'output_root_identity':identity,
            'scope_binding':T.pin('package-scope:R03-public-export',scope_raw),
            'max_package_bytes':T.MAX_PACKAGE_BYTES,'max_generations':2,'authority_effect':'none','actual_owner_outcome':None}
        plan_binding=store(plan)
        if grant:
            policy.update(schema_version='lab-local-package-export-policy/v1-candidate',
                allowed_operations=list(P.PACKAGE_EXPORT_SUPPORTED),purpose='durable-metadata-and-exact-package-export',
                package_export_control={'plan_binding':plan_binding})
        else:
            (output/'.scope.json').unlink();output.rmdir()
        policy_path.write_bytes(P.compact(policy))
        channel=A.ReaderChannel(policy_path,P.source.sha(policy_path.read_bytes()),schemas)
        authenticated=channel.authenticate(MF.proof(key,channel.challenge))
        host=Service(view,channel,schemas)
        try:
            request=MF.call(channel.context,'lab.status',selected_cut)
            request.update(operation='package.export',idempotency_key=KEY,
                message={'schema_version':'lab-package-export-request/v1-candidate','request_ref':'request:R03-public-export',
                    'actor':actor,'source_cut':selected_cut,'artifact_refs':roots,'dependency_bindings':closure,
                    'privacy_review_binding':review_binding,'export_contract_binding':contract_binding,
                    'include_session_memory':False,'include_private_credentials':False,'authority_effect':'none'})
            yield host,request,{'root':root,'output':output,'policy_path':policy_path,'plan':plan,
                'plan_binding':plan_binding,'proposal_binding':proposal_binding,'authentication':authenticated,
                'original_materials':originals,'source_posture':contract['source_posture']}
        finally:host.close();key=None
    P.source.require(not root.exists(),'owned export policy, signer or generation remained')
