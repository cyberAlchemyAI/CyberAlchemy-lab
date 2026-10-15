"""Public managed export adapter with independent host selection and read-only retry."""
import copy
import fcntl
import os
import stat
from pathlib import Path
from .protocol import HERE, ROOT, source, compact, binding
from .handlers import ApplicationError, cut
from .auth import now
from .workspace import safe, read_private
from . import artifact_model as model
from . import export_kernel as K

def identity(path):
    info = path.stat()
    return {'device': info.st_dev, 'inode': info.st_ino}

def validate_control(policy):
    """Current policy pins a private output root inside its owned workspace."""
    control = policy['export_control']
    root = Path(control['output_root'])
    workspace = Path(policy['workspace']['root'])
    source.require(root == workspace / 'exports' and root.is_absolute() and root.resolve() == root
                   and root.is_relative_to(Path('/tmp')) and not root.is_relative_to(ROOT), 'export root outside independently owned workspace')
    safe(root, 0o700)
    source.require(identity(root) == control['output_root_identity'], 'export root identity changed')
    raw = read_private(root / '.scope.json')
    expected = {'schema_version': 'lab-owned-export-root/v1-candidate', 'output_root': str(root),
                'output_root_scope_ref': control['output_root_scope_ref'], 'principal_ref': policy['principal_ref'],
                'output_root_identity': control['output_root_identity'], 'authority_effect': 'none', 'actual_owner_outcome': None}
    source.require(source.sha(raw) == control['manifest_sha256'] and source.parse(raw) == expected, 'exact export root manifest differs')
    source.require(control['renderer_binding'] == K.renderer_binding(), 'export grant selects a different renderer')
    return root

class FileExports:
    def __init__(self, readers, vault, schemas):
        self.readers, self.vault, self.schemas = readers, vault, schemas
    def preflight(self, message, outer, deadline, *, count_budget=True):
        channel = self.readers.channel
        channel.guard()
        if channel.policy['schema_version'] != 'lab-local-export-candidate-policy/v1-candidate':
            raise ApplicationError('unauthorized', 'This independently provisioned host has no file-export permission.')
        grant = channel.policy['export_control']
        root = validate_control(channel.policy)
        observed = self.readers.selected_cut(message, outer)
        view = self.readers.selected_view
        raw = self.vault.material(grant['selection_binding'])
        selection = source.parse(raw)
        source.require(set(selection) == {'schema_version','selection_ref','source_cut','artifact_refs','managed_relative_paths','authority_effect'}
                       and selection['schema_version'] == 'lab-owned-export-selection/v1-candidate' and selection['authority_effect'] == 'none', 'closed independent export selection required')
        if selection['source_cut'] != observed or message['source_cut'] != observed:
            raise ApplicationError('stale-cut', 'Export selection is not bound to this exact selected signed source cut.')
        if (message['selection_ref'] != selection['selection_ref'] or message['artifact_refs'] != selection['artifact_refs']
                or message['managed_relative_paths'] != selection['managed_relative_paths']
                or message['output_root_scope_ref'] != grant['output_root_scope_ref']
                or message['privacy_review_binding'] != grant['privacy_review_binding']):
            raise ApplicationError('unauthorized', 'Export request differs from independent selection, paths, privacy review or output scope.')
        if observed != cut(self.readers.view):
            raise ApplicationError('stale-cut', 'This host export selection is bound to its current retained source cut.')
        parent = self.readers.view.custody_signed_sources
        delivery = source.custody_delivery()
        source.require(type(parent) is delivery.reader.adapter.SignedSources and type(view) is delivery.reader.Inspection,
                       'original signed source and exact prefix type required for export')
        def source_guard():
            parent.guard()
            source.require(view.handle is parent.view.handle and view.originals == parent.view.originals
                           and view.subjects == view.data['projection']['subjects']
                           and all(view.data[k] == parent.view.data[k] for k in ('config','baseline','projection','transactions'))
                           and all(view.data['head'][k] == parent.view.data['head'][k] for k in ('sequence','transaction_digest')),
                           'export prefix differs from bound original signed parent')
        source_guard()
        materials = []
        with model.model_read_batch(view):
            for header in selection['artifact_refs']:
                subject = self.readers.resolve_exact(header)
                original, locator, encoding, _ = model.record_bytes(view, subject)
                materials.append(K.Material(compact(header), original, locator, encoding))
        review_raw = self.vault.material(grant['privacy_review_binding'])
        selected = K.Selection(selection['selection_ref'], compact(observed), tuple(materials), review_raw)
        if selected.privacy_binding != grant['privacy_review_binding']:
            raise ApplicationError('invalid-contract', 'The independent privacy review reference or bytes differ.')
        context = channel.context
        actor = {k: context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
        actor['role_assignment_refs'] = context['role_assignment_bindings']
        def current_permission():
            channel.guard()
            validate_control(channel.policy)
            return now() < deadline
        host = K.ExportHost(root, grant['output_root_scope_ref'], actor, selected, self.schemas,
                            source_guard, current_permission, grant['max_output_bytes'], grant['output_root_identity'])
        try:
            host.plan(message)
        except Exception as error:
            if 'budget' in str(error):
                raise ApplicationError('budget-exceeded', 'Complete managed output exceeds the independently provisioned byte budget.') from error
            raise ApplicationError('invalid-contract', 'Exact export closure, renderer, privacy or output budget could not be verified.') from error
        if count_budget:
            # Publication reserves an immutable directory; uncertain reservations
            # count against the independent host quota and cannot be overwritten.
            generations = [p for p in root.iterdir() if p.name not in ('.scope.json', '.generation.lock')]
            if len(generations) >= grant['max_generations']:
                raise ApplicationError('budget-exceeded', 'Independently granted managed-generation quota is exhausted.')
        return host, observed
    def materialize(self, message, request, outer, deadline, original_message):
        host, observed = self.preflight(message, outer, deadline, count_budget=False)
        if now() >= deadline:
            raise ApplicationError('indeterminate', 'Deadline expired after the operation claim; inspect it before reconciliation.')
        with K.directory(host.root) as root_fd:
            info = os.fstat(root_fd)
            source.require({'device': info.st_dev, 'inode': info.st_ino} == host.root_identity, 'opened quota root identity differs')
            lock_fd = os.open('.generation.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=root_fd)
            try:
                info = os.fstat(lock_fd)
                source.require(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o600
                               and info.st_uid == os.getuid() and info.st_nlink == 1, 'unsafe export quota lock')
                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as error:
                    raise ApplicationError('recovery-required', 'Another managed export owns the generation quota lock; inspect this claimed operation.') from error
                self.preflight(message, outer, deadline)
                domain = host.materialize(message)
            finally:
                os.close(lock_fd)
        observation = {'schema_version': 'lab-private-file-export-observation/v1-candidate',
                       'api_request_binding': request, 'original_api_message_byte_sha256': source.sha(original_message),
                       'kernel_receipt': copy.deepcopy(domain), 'source_cut': observed,
                       'export_control_binding': binding('host-export-control:' + self.readers.channel.host, compact(self.readers.channel.policy['export_control'])),
                       'output_root_identity': self.readers.channel.policy['export_control']['output_root_identity'],
                       'authority_effect': 'none', 'actual_owner_outcome': None}
        evidence = self.vault.object(compact(observation))
        domain['request_binding'] = request
        return domain, [evidence]
    def readback(self, message, outer, deadline, recorded):
        host, _ = self.preflight(message, outer, deadline, count_budget=False)
        if not self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:file-materialization-receipt:v1-candidate', recorded):
            raise ApplicationError('integrity-failed', 'Recorded file-export result does not match its exact receipt contract.')
        if recorded['posture'] == 'published':
            try:
                actual = host.materialize(message, existing_only=True)
                expected = {**recorded, 'request_binding': K.pin(message['request_ref'], compact(message))}
                source.require(actual == expected, 'recorded export differs from observed existing managed generation')
            except Exception as error:
                raise ApplicationError('recovery-required', 'Published generation is missing, changed or obstructed; recorded key cannot redispatch it.') from error
        # An uncertain recorded outcome remains uncertain. Inspecting it never
        # calls the kernel effect path or creates a replacement generation.
        return copy.deepcopy(recorded)
