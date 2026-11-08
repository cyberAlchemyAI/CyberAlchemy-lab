"""Private diagnostic margin composition for the exact d95 Lesson API successor.

The private config is created only inside an owned /tmp root. This module does
not patch API callbacks, extend leases, or create application authority.
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0003'
API_SHA = '1b83e97f5cae120473ccc61d151d38bc0d99d2f1bb8a39f8a30ef8ceedb8184d'
PROFILE_SHA = '3a07464283b6f09aee1bb68ccaa6aa8022666f9ab23871da536947091bbc6413'
PERIOD = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-d95e3b741ca86f02/source/packages/0001/period.json'
PERIOD_SHA = '7409f858261a79bd249c76d63c9c47686f99efff9d5db9448fd1aff3ce7d4683'
DEPENDENCY = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
DEPENDENCY_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
INSTALLATION = ROOT / 'implementation/lab-runtime/local-host/t03-d95-margin-api-recut-0001/working/installation-0001'
INSTALLATION_ORIGIN = ROOT / 'implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001/installation.json'
INSTALLATION_SHA = '5821d37ce536e08c639493ceb8d165949e65cf5dd9771af5576a724082cca13b'
INSTALLATION_RECEIPT_SHA = '7f32ee98bfff06ae68c5c90e5874816b405acfb1d076d5edf33a220f059d54b5'
OVERLAY = ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001'
OVERLAY_SHA = '574bd9f1fc976755eb0bf075b2ec7c14d8c378e8c6b074fa4df0e50af3951bd7'
COMPOSITION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/observed-margin-adapter-0003/postimages/composition.py'
COMPOSITION_SHA = '165d9bcfe76c0ee20aef71907dc18d43abd2ccc5f33f8b4f1e44164d9c6e4393'
MODULES = ('service', 'workspace', 'auth', 'protocol', 'guard', 'session_attachment',
           'current_context_sessions', 'handlers', 'lesson_assessment', 'application_journal',
           'observed_margin', 'margin_capture', 'margin_kernel', 'margin_seal')
HELPERS = ('margin_capture', 'margin_kernel', 'margin_seal', 'observed_margin')
CURRENT_SOURCE_NAME = 'completion-current-participation:legacy-local-d95e3b741ca86f02'
APPLICATION_METHOD = API.parent / 'lesson-application-v4-completion-0001/preparation.py'
ASSESSMENT_METHOD = API.parent / 'lesson-assessment-v2-action-0148/preparation.py'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def binding(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected file missing or linked: ' + str(path))
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def need(value, message):
    if not value:
        raise ValueError(message)


def method_binding(path: Path) -> dict:
    selected = binding(path)
    return {'ref': selected['path'], 'sha256': selected['sha256']}


def check_operator_scope(policy: dict, parent_policy: dict, attachment: dict,
                         source_bindings: dict) -> str:
    """Reject a foreign or overbroad application/assessment Reader policy."""
    need(type(policy) is dict and type(parent_policy) is dict and type(attachment) is dict,
         'closed operator and parent scope required')
    need(policy.get('source_name') == parent_policy.get('source_name') == CURRENT_SOURCE_NAME and
         policy.get('principal_ref') == parent_policy.get('principal_ref') and
         policy.get('scope_refs') == parent_policy.get('scope_refs') and
         policy.get('authority_effect') == parent_policy.get('authority_effect') == 'none' and
         policy.get('actual_owner_outcome') is None and parent_policy.get('actual_owner_outcome') is None,
         'operator Source8 family, Principal, scope or effect differs')
    own = policy.get('source8_control')
    need(type(own) is dict and set(own) == set(source_bindings) | {'application_journal_scope'} and
         all(own.get(k) == value for k, value in source_bindings.items()) and
         own['period_binding'] == parent_policy['session_control']['period_binding'],
         'operator signed Source8 or period selection differs')
    kind = policy.get('schema_version')
    if kind == 'lab-local-lesson-application-policy/v2-candidate':
        selected = policy.get('application_control')
        need(type(selected) is dict and selected.get('method_binding') == method_binding(APPLICATION_METHOD) and
             selected.get('runtime_identities') == {
                 'session_ref': attachment.get('session_ref'),
                 'agent_instance_ref': attachment.get('agent_instance_ref')} and
             policy.get('session_control') is not None and own['application_journal_scope'] is None and
             'lesson.apply' in policy.get('allowed_operations', []),
             'application operator method, Session identity or journal scope differs')
        return 'application'
    if kind == 'lab-local-lesson-assessment-policy/v1-candidate':
        selected = policy.get('assessment_control')
        scope = own['application_journal_scope']
        need(type(selected) is dict and selected.get('method_binding') == method_binding(ASSESSMENT_METHOD) and
             policy.get('session_control') is None and type(scope) is dict and
             set(scope) == {'root', 'workspace_binding', 'manifest_sha256'} and
             'lesson.assess' in policy.get('allowed_operations', []),
             'assessment operator method or application journal scope differs')
        return 'assessment'
    raise ValueError('unselected Lesson operator policy kind')


def verify_selection(package_name: str) -> dict:
    """Cold source/environment check before private config or child service."""
    need(type(package_name) is str and package_name in sys.modules,
         'selected API package is not imported')
    package = sys.modules[package_name]
    need(Path(package.__file__).resolve() == API / '__init__.py',
         'selected API package origin differs')
    need(binding(API / 'source-manifest.json')['sha256'] == API_SHA and
         binding(API / 'contract-profile.json')['sha256'] == PROFILE_SHA and
         binding(PERIOD)['sha256'] == PERIOD_SHA and
         binding(DEPENDENCY)['sha256'] == DEPENDENCY_SHA and
         binding(INSTALLATION_ORIGIN)['sha256'] == INSTALLATION_SHA and
         binding(HERE / 'installation-receipt.json')['sha256'] == INSTALLATION_RECEIPT_SHA and
         binding(OVERLAY / 'source-manifest.json')['sha256'] == OVERLAY_SHA and
         binding(COMPOSITION)['sha256'] == COMPOSITION_SHA,
         'selected d95 margin input changed')
    overlay = json.loads((OVERLAY / 'source-manifest.json').read_bytes())
    rows = overlay['files']
    need(len(rows) == len({r['path'] for r in rows}), 'selected overlay member duplicate')
    for selected in rows:
        path = ROOT / selected['path']
        need(binding(path) == {'path': selected['path'], 'sha256': selected['sha256']}
             and path.stat().st_size == selected['size_bytes'],
             'selected jsonschema 4.19.2 overlay member differs')
    need(Path(sys.executable) == INSTALLATION / 'bin/python',
         'selected dependency installation interpreter required')
    own = json.loads((HERE / 'installation-receipt.json').read_bytes())
    need(own['owned_root'] == INSTALLATION.relative_to(ROOT).as_posix() and
         own['owned_root_mode'] == '0o700' and own['owned_member_count'] == 1010 and
         own['selected_dependency_sha256'] == DEPENDENCY_SHA and
         own['original_installation_sha256'] == INSTALLATION_SHA,
         'owned installed closure receipt differs')
    guard = importlib.import_module(package_name + '.guard')
    selected = guard.verify(API_SHA)
    paths = {row['path']: row['sha256'] for row in selected['files']}
    need(len(paths) == len(selected['files']) == 211,
         'selected d95 API closure cardinality differs')
    for path in (API / 'observed_margin.py', API / 'margin_capture.py', API / 'margin_kernel.py',
                 API / 'margin_seal.py', API / 'observed-margin-policy.schema.json',
                 API.parent / 'lesson-application-v4-completion-0001/preparation.py',
                 API.parent / 'lesson-assessment-v2-action-0148/preparation.py'):
        row = binding(path)
        need(paths.get(row['path']) == row['sha256'],
             'selected margin or Lesson method absent from exact API closure')
    return selected


class DiagnosticMargin:
    """Owned private selection and callable composition for both Lesson operators."""

    def __init__(self, package_name: str):
        self.selected = verify_selection(package_name)
        self.package_name = package_name
        self.modules = {name: importlib.import_module(package_name + '.' + name) for name in MODULES}
        need(all(Path(module.__file__).resolve() == API / (name + '.py') and
                 sys.modules.get(package_name + '.' + name) is module
                 for name, module in self.modules.items()),
             'selected module object/origin differs')
        self.temporary = tempfile.TemporaryDirectory(prefix='cal-T03-margin-d95-', dir='/tmp')
        self.root = Path(self.temporary.name)
        self.root.chmod(0o700)
        st = self.root.stat()
        self.root_identity = (st.st_dev, st.st_ino, st.st_uid, stat.S_IMODE(st.st_mode))
        instrumentation = binding(HERE / 'instrumentation.json')
        self.config = {
            'schema_version': 'lab-protected-observed-margin-runtime/v1-candidate',
            'authority_effect': 'none', 'mode': 'diagnostic-measurement',
            'api_directory': API.relative_to(ROOT).as_posix(),
            'api_source_binding': binding(API / 'source-manifest.json'),
            'profile_binding': binding(API / 'contract-profile.json'),
            'software_binding': binding(API / 'source-manifest.json'),
            'period_binding': binding(PERIOD),
            'dependency_selection_binding': binding(DEPENDENCY),
            'dependency_installation': INSTALLATION.relative_to(ROOT).as_posix(),
            'instrumentation_binding': instrumentation,
            'policy_binding': None, 'load_binding': None,
        }
        raw = (json.dumps(self.config, sort_keys=True, separators=(',', ':')) + '\n').encode()
        config_path = self.root / 'runtime.json'
        with config_path.open('xb') as output:
            os.fchmod(output.fileno(), 0o600)
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        self.selection_binding = {'path': 'runtime.json', 'sha256': sha(raw)}
        spec = importlib.util.spec_from_file_location('_cal_t03_d95_margin_composition_' + uuid.uuid4().hex,
                                                       COMPOSITION)
        composition = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = composition
        spec.loader.exec_module(composition)
        self.composition = composition
        self.capture = tuple((name, self.modules[name], str(API / (name + '.py')),
                              binding(API / (name + '.py'))['sha256'],
                              (API / (name + '.py')).read_bytes()) for name in HELPERS)

    def compose_margin(self, host, parent, lifecycle_modules, attachment):
        """Return one selected binding; call for application and assessor."""
        need(self.root.is_dir() and self.root.stat().st_ino == self.root_identity[1],
             'owned private margin root changed')
        need(type(lifecycle_modules) is dict and
             lifecycle_modules.get('service') is self.modules['service'] and
             lifecycle_modules.get('protocol') is self.modules['protocol'],
             'foreign lifecycle module context')
        kind = check_operator_scope(host.channel.policy_guard(), parent.channel.policy_guard(),
                                    attachment,
                                    importlib.import_module(self.package_name + '.source_bridge').source8_bindings(CURRENT_SOURCE_NAME))
        need(kind in ('application', 'assessment'), 'unselected Lesson operator')
        return self.composition.compose(host, parent, self.modules, attachment,
                                        control_root=self.root, root_identity=self.root_identity,
                                        selection_binding=self.selection_binding,
                                        helper_capture=self.capture)

    def close(self):
        self.temporary.cleanup()
        need(not self.root.exists(), 'private margin configuration survived cleanup')

    def public_receipt(self):
        return {'schema_version': 'lab-T03-d95-diagnostic-margin-selection/v1-candidate',
                'api_source_manifest_sha256': API_SHA, 'api_profile_sha256': PROFILE_SHA,
                'period_sha256': PERIOD_SHA, 'dependency_selection_sha256': DEPENDENCY_SHA,
                'dependency_installation_sha256': INSTALLATION_SHA,
                'owned_installation_receipt_sha256': INSTALLATION_RECEIPT_SHA,
                'jsonschema_overlay_sha256': OVERLAY_SHA,
                'composition_sha256': COMPOSITION_SHA,
                'instrumentation_sha256': binding(HERE / 'instrumentation.json')['sha256'],
                'private_configuration_sha256': self.selection_binding['sha256'],
                'mode': 'diagnostic-measurement', 'margin_enforced': False,
                'empirical_margin_qualified': False, 'authority_effect': 'none'}
