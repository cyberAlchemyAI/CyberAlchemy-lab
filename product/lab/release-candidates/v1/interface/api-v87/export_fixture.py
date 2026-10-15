"""Owned current export grants; no canonical owner or Agent permission."""
import copy
from datetime import timedelta
from pathlib import Path
import uuid
from .protocol import *
from . import metadata_fixture as F
from .file_exports import identity
from .handlers import cut
from .workspace import atomic
from . import artifact_model as M
from . import export_kernel as K
from .auth import now

def selection(view):
    artifacts = []
    with M.model_read_batch(view):
        for _, subject in sorted(view.subjects.items()):
            if subject['carrier_ref'] in ('cal.artifact-type.intent/v1', 'cal.artifact-type.goal/v1') and subject['source'].get('encoding') == view.handle.custody.ENCODING:
                artifacts.append(M.artifact_ref(view, subject))
    source.require(len(artifacts) == 2, 'actual two-body Intent/Goal export selection required')
    return {'schema_version': 'lab-owned-export-selection/v1-candidate', 'selection_ref': 'selection:R03-public-intent-goal-export',
            'source_cut': cut(view), 'artifact_refs': artifacts, 'managed_relative_paths': ['selected/00.json','selected/01.json'], 'authority_effect': 'none'}

def provision(root, selected, *, max_generations=4):
    selected = copy.deepcopy(selected)
    review = {k: selected[k] for k in ('selection_ref','source_cut','artifact_refs')}
    review.update(include_session_memory=False, authority_effect='none')
    review_raw = compact(review)
    review_binding = binding('privacy-review:' + selected['selection_ref'], review_raw)
    selected_raw = compact(selected)
    selected_binding = binding('candidate:export-selection', selected_raw)
    rows = {selected_binding['ref']: selected_raw, review_binding['ref']: review_raw}
    key, path, _ = F.provision(root, rows, {}, scoped=False)
    policy = source.parse(path.read_bytes())
    output = Path(policy['workspace']['root']) / 'exports'
    output.mkdir(mode=0o700)
    scope = 'owned:export:' + uuid.uuid4().hex
    info = identity(output)
    manifest = {'schema_version': 'lab-owned-export-root/v1-candidate', 'output_root': str(output),
                'output_root_scope_ref': scope, 'principal_ref': policy['principal_ref'],
                'output_root_identity': info, 'authority_effect': 'none', 'actual_owner_outcome': None}
    raw = compact(manifest)
    atomic(output / '.scope.json', raw)
    policy.update(schema_version='lab-local-export-candidate-policy/v1-candidate',
                  purpose='durable-metadata-and-managed-file-export', allowed_operations=list(EXPORT_SUPPORTED),
                  export_control={'output_root': str(output), 'output_root_scope_ref': scope, 'output_root_identity': info,
                                  'manifest_sha256': source.sha(raw), 'selection_binding': selected_binding,
                                  'privacy_review_binding': review_binding, 'renderer_binding': K.renderer_binding(),
                                  'max_generations': max_generations, 'max_output_bytes': 1048576})
    raw = compact(policy)
    path.write_bytes(raw)
    return key, path, source.sha(raw)

def call(service, selected, *, key='fixture:public-export', mode='byte-exact'):
    context = service.channel.context
    actor = {k: context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
    actor['role_assignment_refs'] = context['role_assignment_bindings']
    control = service.channel.policy['export_control']
    message = {'schema_version': 'lab-file-materialization-request/v1-candidate', 'request_ref': 'request:public-selected-export',
               'actor': actor, 'source_cut': copy.deepcopy(selected['source_cut']), 'selection_ref': selected['selection_ref'],
               'artifact_refs': copy.deepcopy(selected['artifact_refs']), 'output_root_scope_ref': control['output_root_scope_ref'],
               'mode': mode, 'renderer_binding': control['renderer_binding'] if mode == 'rendered' else None,
               'managed_relative_paths': list(selected['managed_relative_paths']), 'overwrite_unmanaged_files': False,
               'include_session_memory': False, 'privacy_review_binding': copy.deepcopy(control['privacy_review_binding']), 'authority_effect': 'none'}
    return {'schema_version': 'lab-api-call/v2-candidate', 'expected_contract_profile_binding': service.schemas.profile_binding,
            'call_id': 'call:export:' + uuid.uuid4().hex, 'operation': 'files.materialize', 'caller_context_ref': context['context_ref'],
            'expected_source_cut': copy.deepcopy(selected['source_cut']), 'deadline': (now() + timedelta(minutes=10)).isoformat(),
            'max_response_bytes': 1048576, 'idempotency_key': key, 'message': message}
