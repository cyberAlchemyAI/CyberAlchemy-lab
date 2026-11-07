"""Authenticated same-cut candidate import; no source or target admission.

Independent policy selects a managed generation, complete mapping/disposition and
source/target proposals. Source candidate roots and target proposals use the
unchanged native prospective validator. Retained artifacts must match actual
current signed-source originals. General foreign/admitted-source import remains
an explicit implementation obligation; this handler refuses that unsupported use.
"""
import base64
import copy
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker
from .protocol import HERE, ROOT, source, compact, binding
from .handlers import ApplicationError, cut
from .workspace import read_private, safe, privacy
from . import artifact_model as model
from .guarded_candidate import selection, calculation, B
from .auth import now

PUBLICATION = HERE.parent / 'package-publication-v2'
PUBLICATION_PIN = 'f84a7d09b96111ee62ed8319c95476c7aa7f21e6de93bfa979cad3a2016ad2a6'
NAME = '_cal_API53_package_publication_v2'
if NAME not in sys.modules:
    manifest_raw = (PUBLICATION / 'source-manifest.json').read_bytes()
    source.require(source.sha(manifest_raw) == PUBLICATION_PIN, 'independent publication selection differs')
    manifest = json.loads(manifest_raw)
    for row in manifest['files'] + manifest['input_bindings']:
        source.original(row)
    spec = importlib.util.spec_from_file_location(NAME, PUBLICATION / 'publication.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = module
    spec.loader.exec_module(module)
PUB = sys.modules[NAME]
source.require(Path(PUB.__file__).resolve() == PUBLICATION / 'publication.py', 'unselected managed publication module')
T = PUB.T


def validate_control(policy, schemas):
    source.require(policy['schema_version'] == 'lab-local-package-import-policy/v1-candidate',
                   'independent package import policy required')
    selected = policy['package_control']['plan_binding']
    root = Path(policy['workspace']['root'])
    manifest = source.parse(read_private(root / 'workspace.json'))
    source.require(selected['ref'] == 'workspace-object:' + manifest['workspace_ref'] + ':' + selected['sha256'],
                   'package plan object namespace differs')
    raw = read_private(root / 'objects' / (selected['sha256'] + '.json'))
    source.require(source.sha(raw) == selected['sha256'], 'independent package plan bytes changed')
    plan = source.parse(raw)
    source.require(schemas.protocol_valid('urn:cyberalchemy-lab:internal:package-import-plan:v1-candidate', plan),
                   'closed package import plan required')
    output = Path(plan['output_root'])
    source.require(output == root / 'packages', 'package root is outside independently selected workspace')
    safe(output, 0o700)
    source.require(PUB.identity(output.stat()) == plan['output_root_identity'], 'package root identity changed')
    scope_raw = read_private(output / '.scope.json')
    expected = {'schema_version': 'lab-owned-package-root/v1-candidate', 'output_root': str(output),
        'output_root_scope_ref': plan['output_root_scope_ref'], 'principal_ref': policy['principal_ref'],
        'output_root_identity': plan['output_root_identity'], 'authority_effect': 'none', 'actual_owner_outcome': None}
    source.require(source.sha(scope_raw) == plan['scope_binding']['sha256'] and source.parse(scope_raw) == expected,
                   'independent package scope differs')
    return plan


def schema_original(view, carrier):
    contract = view.data['projection']['contracts'][carrier]
    selected = {'ref': contract['schema_path'], 'sha256': contract['schema_sha256']}
    raw = view.originals.get(selected['ref'])
    if type(raw) is not bytes:
        raw = source.original({'path': selected['ref'], 'sha256': selected['sha256']})
    source.require(source.sha(raw) == selected['sha256'], 'original carrier schema differs')
    return selected, raw


class PackageImport:
    def __init__(self, host):
        service = importlib.import_module(__package__ + '.service')
        auth = importlib.import_module(__package__ + '.auth')
        source.require(type(host) is service.Service and type(host.channel) is auth.ReaderChannel,
                       'actual selected Service and authenticated operator channel required')
        self.host, self.vault, self.schemas = host, host.vault, host.schemas
        self.transfer = T.Transfer(PUB.TRANSFER_SOURCE)

    def read(self, selected):
        raw = self.vault.object_read(selected) if selected['ref'].startswith('workspace-object:') else self.vault.material(selected)
        source.require(source.sha(raw) == selected['sha256'], 'independent package control bytes differ')
        privacy(source.parse(raw))
        return raw

    def publisher(self, plan, deadline):
        parent = self.host.handlers.view.custody_signed_sources
        delivery = source.custody_delivery()
        source.require(type(parent) is delivery.reader.adapter.SignedSources, 'actual original signed source required')
        def source_guard():
            source.require(self.host.handlers.current(), 'original import target source changed')
        def permission():
            self.host.channel.guard()
            source.require(validate_control(self.host.channel.policy, self.schemas) == plan, 'independent package controls changed')
            return now() < deadline
        return PUB.Publisher(plan['output_root'], plan['output_root_scope_ref'],
            plan['output_root_identity'], plan['scope_binding'], self.host.channel.context['principal_ref'],
            self.transfer, source_guard, permission, plan['max_package_bytes'], plan['max_generations'])

    def validate_proposal(self, selected, outer, writer):
        raw = self.read(selected)
        proposal = source.parse(raw)
        source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate', proposal),
                       'independently selected native proposal differs')
        context = self.host.channel.guard()
        actor = {key: context[key] for key in ('principal_ref', 'agent_instance_ref', 'assignment_ref', 'session_ref')}
        actor['role_assignment_refs'] = context['role_assignment_bindings']
        source.require(proposal['actor'] == actor, 'native proposal Actor differs from verified channel')
        report, details = self.host.candidates.validate(proposal, selected, outer, raw, evidence_writer=writer)
        if report['result'] != 'pass' or report['gaps']:
            raise ApplicationError('closure-missing', 'Original prospective model validation did not close the selected candidate proposal.')
        return proposal, report, details

    def evaluate(self, message, outer, key, deadline, writer):
        context = self.host.channel.guard()
        plan = validate_control(self.host.channel.policy, self.schemas)
        observed = self.host.handlers.selected_cut({'source_cut': message['target_base_cut']}, outer)
        if observed != cut(self.host.handlers.view) or observed != plan['target_base_cut']:
            raise ApplicationError('stale-cut', 'Import requires the independently selected current target cut.')
        for field in ('source_package_binding', 'mapping_binding', 'disposition_binding'):
            if message[field] != plan[field]:
                raise ApplicationError('unauthorized', 'Import control differs from independent host selection.')
        if message['candidate_workspace_binding'] != self.vault.control_binding:
            raise ApplicationError('unauthorized', 'Import does not select the independently owned candidate workspace.')
        publisher = self.publisher(plan, deadline)
        try:
            package_raw, publication_receipt = publisher.read_package(plan['source_package_binding'],
                plan['source_publication_request_binding'], observed, plan['source_generation_ref'])
        except PUB.RecoveryRequired as error:
            raise ApplicationError('recovery-required', 'Independently selected published package requires read-only reconciliation.') from error
        package = self.transfer.verify_archive(package_raw, plan['source_package_binding'])
        if package['source_cut'] != observed or package['source_posture'] != 'controlled-candidate' or package['source_admission_basis']:
            raise ApplicationError('unsupported-version', 'Foreign or admitted-source import requires its own implemented source authority resolver.')
        view = self.host.handlers.selected_view
        existing = tuple(sorted({s['identity'] for s in view.subjects.values()
            if s['effective_state'] in ('admitted-current', 'admitted-historical', 'local-admitted-current', 'local-admitted-historical')}))
        actor = {k: context[k] for k in ('principal_ref', 'agent_instance_ref', 'assignment_ref', 'session_ref')}
        actor['role_assignment_refs'] = context['role_assignment_bindings']
        facts = T.ImportFacts(compact(actor), compact(observed), compact(plan['source_package_binding']),
            compact(plan['mapping_binding']), compact(plan['disposition_binding']),
            compact(self.vault.control_binding), view.data['config']['scope_ref'], existing)
        accounting = self.transfer.account_import(compact(message), facts, package_raw,
            self.read(plan['mapping_binding']), self.read(plan['disposition_binding']))
        source_proposal, source_report, source_details = self.validate_proposal(plan['source_proposal_binding'], outer, writer)
        roots = [target['artifact'] for target in source_proposal['targets']]
        source.require(all(target['operation'] == 'admit' and target['artifact']['carrier_ref'] == 'cal.artifact-type.work/v1'
                           for target in source_proposal['targets']), 'only original fully resolved Work source candidates are supported')
        base = lambda h: {k: h[k] for k in ('scope_ref', 'identity_ref', 'version_ref', 'carrier_ref', 'byte_sha256')}
        source.require(package['artifact_refs'] == [base(h) for h in roots], 'archive roots differ from verified source proposal')
        artifacts = {row['artifact']['version_ref']: row for row in package['materials'] if row['artifact'] is not None}
        material_bindings = {row['binding']['ref']: row for row in package['materials']}
        source.require(len(artifacts) == sum(row['artifact'] is not None for row in package['materials']), 'duplicate source version')
        root_versions = {h['version_ref'] for h in roots}
        for version, row in artifacts.items():
            original = base64.b64decode(row['original_bytes_b64'], validate=True)
            if version in root_versions:
                target = next(t for t in source_proposal['targets'] if t['artifact']['version_ref'] == version)
                source.require(row['artifact'] == base(target['artifact']) and original == self.vault.material(
                    {'ref': target['content']['content_ref'], 'sha256': target['content']['byte_sha256']}), 'source candidate original differs')
                for selected in (target['candidate_binding'], target['decision_core_binding']):
                    source.require(selected['ref'] in material_bindings and material_bindings[selected['ref']]['binding'] == selected
                        and base64.b64decode(material_bindings[selected['ref']]['original_bytes_b64'], validate=True) == self.read(selected),
                        'original source candidate metadata/core dependency missing')
            else:
                subject = self.host.handlers.resolve_exact(row['artifact'])
                source.require(subject['effective_state'] in ('admitted-current', 'local-admitted-current'), 'retained source dependency is not current')
                raw, _, _, _ = model.record_bytes(view, subject)
                source.require(original == raw, 'retained artifact does not match signed-source original bytes')
            schema_binding, schema_raw = schema_original(view, row['artifact']['carrier_ref'])
            schema_row = material_bindings.get(schema_binding['ref'])
            source.require(schema_row is not None and schema_row['binding'] == schema_binding and
                base64.b64decode(schema_row['original_bytes_b64'], validate=True) == schema_raw,
                'required original carrier schema dependency missing')
            source.require(schema_binding in row['dependencies'], 'carrier schema is not declared as an artifact dependency')
        for ref in source_report['reference_checks']:
            source.require(ref['posture'] == 'resolved' and ref['resolved_ref'] is not None, 'source reference closure missing')
            header = base(ref['resolved_ref'])
            dependency = artifacts.get(header['version_ref'])
            source.require(dependency is not None and dependency['artifact'] == header, 'resolved source reference original omitted from package')
            origin = artifacts.get(ref['source_version_ref'])
            source.require(origin is not None and dependency['binding'] in origin['dependencies'], 'resolved source dependency edge omitted')
        target_proposal, target_report, target_details = self.validate_proposal(plan['target_proposal_binding'], outer, writer)
        if target_proposal['idempotency_key'] != key:
            raise ApplicationError('invalid-contract', 'Independently selected target proposal key differs from import operation key.')
        mapped = [row for row in accounting['items'] if row['target'] is not None]
        source.require([row['target'] for row in mapped] == [target['artifact'] for target in target_proposal['targets']],
                       'complete mapping differs from exact native target proposal')
        for row, target in zip(mapped, target_proposal['targets']):
            source.require(target['operation'] == 'admit' and target['predecessor'] is None, 'import cannot hide a represented revision or withdrawal')
            original = self.vault.material({'ref': target['content']['content_ref'], 'sha256': target['content']['byte_sha256']})
            source.require(original == base64.b64decode(row['target_bytes_b64'], validate=True), 'mapped original target differs')
        provenance_raw = self.read(plan['provenance_binding'])
        provenance = source.parse(provenance_raw)
        expected_provenance = {'schema_version': 'lab-candidate-import-provenance/v1-candidate',
            'source_package_binding': plan['source_package_binding'], 'source_cut': package['source_cut'],
            'mapping_binding': plan['mapping_binding'], 'disposition_binding': plan['disposition_binding'],
            'authority_effect': 'none', 'automatic_admission': False, 'source_retirement': False}
        source.require(provenance == expected_provenance and plan['provenance_binding'] in target_proposal['evidence_bindings'],
                       'returned target proposal does not retain exact source provenance')
        accounting['target_model_validation_pending'] = False
        accounting_binding = writer.object(compact(accounting))
        observation = {'schema_version': 'lab-private-package-import-observation/v1-candidate',
            'source_package_binding': plan['source_package_binding'], 'publication_receipt': publication_receipt,
            'source_validation_report_binding': source_details['report_binding'],
            'target_validation_report_binding': target_details['report_binding'],
            'accounting_binding': accounting_binding, 'provenance_binding': plan['provenance_binding'],
            'source_admission_verified': False, 'canonical_admission_applied': False,
            'authority_effect': 'none', 'actual_owner_outcome': None}
        observation_binding = writer.object(compact(observation))
        evidence = [*source_details['evidence'], source_details['report_binding'],
            *target_details['evidence'], target_details['report_binding'], accounting_binding, observation_binding]
        distinct = []
        for selected in evidence:
            if selected not in distinct:
                distinct.append(selected)
        return copy.deepcopy(target_proposal), distinct

    def preflight(self, message, outer, key, deadline):
        with selection(self.host):
            buffer = B.EvidenceBuffer(self.vault.manifest['workspace_ref'], lambda raw: privacy(source.parse(raw)))
            try:
                self.evaluate(message, outer, key, deadline, buffer)
            finally:
                buffer.discard()

    def prepare(self, message, request, outer, key, deadline):
        with calculation(self.host) as buffer:
            domain, evidence = self.evaluate(message, outer, key, deadline, buffer)
        return domain, evidence

    def readback(self, message, outer, key, deadline, recorded):
        with selection(self.host):
            buffer = B.EvidenceBuffer(self.vault.manifest['workspace_ref'], lambda raw: privacy(source.parse(raw)))
            try:
                domain, _ = self.evaluate(message, outer, key, deadline, buffer)
                source.require(domain == recorded, 'recorded import result differs from exact verified candidate')
            finally:
                buffer.discard()
        return copy.deepcopy(recorded)
