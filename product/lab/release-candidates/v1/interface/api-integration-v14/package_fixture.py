"""Owned candidate package fixture; publication permission is explicitly synthetic.

Import itself uses the real one-use cryptographic channel and original signed
target source. No public export, source admission or participant outcome is made.
"""
import base64
import copy
import json
from pathlib import Path

from .protocol import source, compact, binding, PACKAGE_SUPPORTED
from .handlers import cut
from . import artifact_model as model
from . import metadata_fixture as MF
from .workspace import atomic
from .package_import import PUB, T, schema_original

KEY = 'fixture:R03-package-import'


def target_materials(view, record, label):
    identity = record['node_id']
    version = identity + '@candidate.1'
    carrier = 'cal.artifact-type.work/v1'
    decision = 'decision:R03-package-' + label
    raw = (json.dumps(record, indent=3, ensure_ascii=False) + '\n').encode()
    native = {'category': 'artifact-instance', 'operation': 'admit', 'version_ref': version,
        'carrier_ref': carrier, 'record': record, 'predecessor_ref': None, 'decision_ref': decision,
        'contract': None, 'content': view.handle.custody.content_entry(raw)}
    core = {'decision_ref': decision, 'category': 'artifact-instance', 'operation': 'admit',
        'version_ref': version, 'target_digest': view.handle.common.digest(native)}
    metadata = {'schema_version': 'lab-candidate-target-metadata/v1-candidate',
        'category': 'artifact-instance', 'decision_ref': decision, 'contract': None}
    refs = {name: 'candidate:package-' + label + '-' + name for name in ('body', 'metadata', 'core')}
    rows = {refs['body']: raw, refs['metadata']: source.encoded(metadata),
            refs['core']: view.handle.common.encoded(core)}
    meta_binding = binding(refs['metadata'], rows[refs['metadata']])
    contract = view.data['projection']['contracts'][carrier]
    header = {'scope_ref': view.data['config']['scope_ref'], 'identity_ref': identity,
        'version_ref': version, 'carrier_ref': carrier, 'byte_sha256': source.sha(raw),
        'candidate_contract_binding': {'ref': contract['schema_path'], 'sha256': contract['schema_sha256']}}
    target = {'operation': 'admit', 'artifact': header, 'predecessor': None,
        'content': {'content_ref': refs['body'], 'byte_sha256': source.sha(raw),
                    'size_bytes': len(raw), 'media_type': 'application/json'},
        'candidate_binding': meta_binding, 'decision_core_binding': binding(refs['core'], rows[refs['core']]),
        'requested_effect': 'Prepare exact candidate import for final review; no admission or completed Work.'}
    return rows, {version: meta_binding}, target


def provision(root, view):
    R = source.custody_delivery().records
    record = copy.deepcopy(view.subjects[R.WORK + '@' + R.VERSION]['record'])
    record['node_id'] = 'work:R03-package-import-source'
    record['payload'].update(project_ref=view.data['config']['scope_ref'],
        goal_refs=[R.GOAL + '@' + R.VERSION], input_refs=[R.INTENT + '@' + R.VERSION],
        output_refs=[R.INTENT + '@' + R.VERSION], completion_state='candidate-prepared',
        work_statement='Prepare exact review and delivery of the current Intent. No new output or successful delivery is claimed.')
    source_rows, source_metadata, source_target = target_materials(view, record, 'source')
    adapted = copy.deepcopy(record)
    adapted['node_id'] = 'work:R03-package-import-target'
    adapted['name'] = 'Candidate adaptation of the selected Work'
    target_rows, target_metadata, target = target_materials(view, adapted, 'target')
    rows = {**source_rows, **target_rows}
    key, path, _ = MF.provision(root, rows, {**source_metadata, **target_metadata}, scoped=False)
    policy = source.parse(path.read_bytes())
    workspace = Path(policy['workspace']['root'])
    manifest = source.parse((workspace / 'workspace.json').read_bytes())
    workspace_binding = {'ref': 'workspace:' + manifest['workspace_ref'], 'sha256': policy['workspace']['manifest_sha256']}
    actor = {'principal_ref': policy['principal_ref'], 'role_assignment_refs': [],
             'agent_instance_ref': None, 'assignment_ref': None, 'session_ref': None}
    selected_cut = cut(view)
    def store(value):
        raw = compact(value)
        digest = source.sha(raw)
        atomic(workspace / 'objects' / (digest + '.json'), raw)
        return {'ref': 'workspace-object:' + manifest['workspace_ref'] + ':' + digest, 'sha256': digest}
    def proposal(target, name, evidence):
        return {'schema_version': 'lab-change-proposal/v1-candidate', 'proposal_ref': name,
            'actor': actor, 'scope_ref': view.data['config']['scope_ref'], 'base_cut': selected_cut,
            'source_profile_binding': {'ref': view.handle.manifest['profile_binding']['path'],
                                       'sha256': view.handle.manifest['profile_binding']['sha256']},
            'workspace_binding': workspace_binding, 'targets': [target], 'schema_bindings': [],
            'connection_proposals': [], 'evidence_bindings': evidence, 'idempotency_key': KEY,
            'challenge_route': view.data['config']['challenge_route'], 'authority_effect': 'none'}
    source_proposal = store(proposal(source_target, 'proposal:R03-package-source', []))
    engine = T.Transfer(PUB.TRANSFER_SOURCE)
    base = lambda h: {k: h[k] for k in ('scope_ref', 'identity_ref', 'version_ref', 'carrier_ref', 'byte_sha256')}
    materials = {}
    def material(ref, raw, dependencies, header=None):
        selected = T.pin(ref, raw)
        materials[ref] = T.Material(T.encoded(selected), raw, T.encoded(dependencies), T.encoded(header) if header else None)
        return selected
    def schema(carrier):
        selected, raw = schema_original(view, carrier)
        material(selected['ref'], raw, [])
        return selected
    dependencies = []
    with model.model_read_batch(view):
        for requested in (view.data['config']['scope_ref'], R.GOAL + '@' + R.VERSION, R.INTENT + '@' + R.VERSION):
            matches = [s for s in view.subjects.values() if requested in (s['identity'], s['version_ref'])
                       and s['effective_state'] in ('admitted-current', 'local-admitted-current')]
            assert len(matches) == 1, requested
            subject = matches[0]
            header = model.artifact_ref(view, subject)
            raw, _, _, _ = model.record_bytes(view, subject)
            dependencies.append(material('package:retained:' + header['version_ref'], raw,
                [schema(header['carrier_ref'])], header))
    for selected in (source_target['candidate_binding'], source_target['decision_core_binding']):
        dependencies.append(material(selected['ref'], source_rows[selected['ref']], []))
    dependencies.append(schema(source_target['artifact']['carrier_ref']))
    source_raw = source_rows[source_target['content']['content_ref']]
    material(source_target['content']['content_ref'], source_raw, dependencies, base(source_target['artifact']))
    selected_materials = tuple(materials[k] for k in sorted(materials))
    graph = engine.graph(selected_materials)
    roots = [base(source_target['artifact'])]
    closure = engine.closure(graph, roots, [])
    contract = {'schema_version': 'lab-package-export-contract/v2-candidate', 'source_cut': selected_cut,
        'artifact_refs': roots, 'dependency_bindings': closure, 'source_admission_basis': [],
        'source_posture': 'controlled-candidate', 'maximum_package_bytes': T.MAX_PACKAGE_BYTES,
        'authority_effect': 'none', 'actual_owner_outcome': None}
    contract_raw = T.encoded(contract)
    contract_binding = T.pin('fixture:package-export-contract', contract_raw)
    review = {'schema_version': 'lab-package-privacy-review/v2-candidate', 'source_cut': selected_cut,
        'export_contract_binding': contract_binding, 'materials': [graph[k]['binding'] for k in sorted(graph)],
        'material_encodings': [{'binding': graph[k]['binding'], 'encoding': graph[k]['encoding']} for k in sorted(graph)],
        'include_session_memory': False, 'include_private_credentials': False,
        'authority_effect': 'none', 'actual_owner_outcome': None}
    review_raw = T.encoded(review)
    review_binding = T.pin('fixture:package-privacy-review', review_raw)
    export_request = {'schema_version': 'lab-package-export-request/v1-candidate', 'request_ref': 'fixture:package-export',
        'actor': actor, 'source_cut': selected_cut, 'artifact_refs': roots, 'dependency_bindings': closure,
        'privacy_review_binding': review_binding, 'include_private_credentials': False, 'include_session_memory': False,
        'export_contract_binding': contract_binding, 'authority_effect': 'none'}
    export_raw = T.encoded(export_request)
    facts = T.ExportFacts(T.encoded(actor), T.encoded(selected_cut), T.encoded(contract_binding),
                          T.encoded(review_binding), selected_materials)
    archive = engine.export(export_raw, facts, contract_raw, review_raw)
    archive_binding = T.pin('candidate-package:R03-import-fixture', archive)
    output = workspace / 'packages'
    output.mkdir(mode=0o700)
    scope = 'package-output:R03-import-fixture'
    root_identity = PUB.identity(output.stat())
    scope_raw = PUB.encoded({'schema_version': 'lab-owned-package-root/v1-candidate', 'output_root': str(output),
        'output_root_scope_ref': scope, 'principal_ref': policy['principal_ref'],
        'output_root_identity': root_identity, 'authority_effect': 'none', 'actual_owner_outcome': None})
    atomic(output / '.scope.json', scope_raw)
    scope_binding = PUB.pin('package-scope:R03-import-fixture', scope_raw)
    publication_request = T.pin(export_request['request_ref'], export_raw)
    publisher = PUB.Publisher(output, scope, root_identity, scope_binding, policy['principal_ref'],
        engine, view.custody_signed_sources.guard, lambda: True, T.MAX_PACKAGE_BYTES, 2)
    publication = publisher.publish(archive, archive_binding, publication_request, selected_cut)
    decoded = engine.verify_archive(archive, archive_binding)
    mapping_rows, disposition_rows = [], []
    for row in decoded['materials']:
        header = row['artifact']
        if header is None:
            continue
        is_root = header['version_ref'] == source_target['artifact']['version_ref']
        mapping_rows.append({'source': header, 'target': target['artifact'] if is_root else None,
            'target_bytes_b64': base64.b64encode(target_rows[target['content']['content_ref']]).decode() if is_root else None})
        disposition_rows.append({'source': header, 'disposition': 'adapt' if is_root else 'retain-source',
            'reason': 'Adapt the exact controlled candidate Work; retain exact current signed-source dependency originals.'})
    mapping = store({'schema_version': 'lab-package-import-mapping/v1-candidate', 'source_package_binding': archive_binding,
        'target_base_cut': selected_cut, 'items': mapping_rows, 'authority_effect': 'none', 'actual_owner_outcome': None})
    disposition = store({'schema_version': 'lab-package-import-disposition/v1-candidate', 'source_package_binding': archive_binding,
        'target_base_cut': selected_cut, 'items': disposition_rows, 'authority_effect': 'none', 'actual_owner_outcome': None})
    provenance = store({'schema_version': 'lab-candidate-import-provenance/v1-candidate', 'source_package_binding': archive_binding,
        'source_cut': selected_cut, 'mapping_binding': mapping, 'disposition_binding': disposition,
        'automatic_admission': False, 'source_retirement': False, 'authority_effect': 'none'})
    target_proposal = proposal(target, 'proposal:R03-package-import-target', [provenance])
    target_proposal_binding = store(target_proposal)
    plan = {'schema_version': 'lab-package-import-plan/v1-candidate', 'target_base_cut': selected_cut,
        'source_package_binding': archive_binding, 'source_publication_request_binding': publication_request,
        'source_generation_ref': publication['generation_ref'], 'mapping_binding': mapping, 'disposition_binding': disposition,
        'source_proposal_binding': source_proposal, 'target_proposal_binding': target_proposal_binding,
        'provenance_binding': provenance, 'output_root': str(output), 'output_root_scope_ref': scope,
        'output_root_identity': root_identity, 'scope_binding': scope_binding, 'max_package_bytes': T.MAX_PACKAGE_BYTES,
        'max_generations': 2, 'authority_effect': 'none', 'actual_owner_outcome': None}
    plan_binding = store(plan)
    policy.update(schema_version='lab-local-package-import-policy/v1-candidate', allowed_operations=list(PACKAGE_SUPPORTED),
        purpose='durable-metadata-and-exact-package-import', package_control={'plan_binding': plan_binding})
    # Finalize the independent grant before creating/authenticating a channel.
    policy_raw = compact(policy)
    path.write_bytes(policy_raw)
    message = {'schema_version': 'lab-package-import-request/v1-candidate', 'request_ref': 'request:R03-package-import',
        'actor': actor, 'source_package_binding': archive_binding, 'source_admission_basis': [],
        'target_base_cut': selected_cut, 'mapping_binding': mapping, 'disposition_binding': disposition,
        'candidate_workspace_binding': workspace_binding, 'automatic_admission': False, 'authority_effect': 'none'}
    return key, path, source.sha(policy_raw), message, target_proposal, plan, archive
