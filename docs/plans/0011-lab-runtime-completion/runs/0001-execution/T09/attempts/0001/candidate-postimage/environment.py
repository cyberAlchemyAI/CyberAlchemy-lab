"""Explicit composite/R02 environment selection; no admission or activation."""
import copy
import fcntl
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
from jsonschema import Draft202012Validator

VERSION = 'lab-composite-install-environment/v3-candidate'
ORIGINAL_COMPOSITE = {'path': 'product/lab/release-candidates/v1/release-validation/0001/runtime16-draft-0276/environment-contract.json',
                      'sha256': '79393346ec5b58517febe7518d4268ea1804fba1bf2061f4b3bcc69b44de3506'}
ORIGINAL_CLASSIFICATION = {'path': 'product/lab/release-candidates/v1/release-validation/0001/environment-contract.json',
                           'sha256': 'ae389483f4fbe398b82d7421bd2bc1e1b3864ebc216c932d3f85448da9c8a2e3'}


def require(value, reason):
    if not value:
        raise ValueError(reason)


def closed(value, fields):
    require(type(value) is dict and set(value) == set(fields), 'closed environment fields required')


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


class CompositeEnvironment:
    """Modules supplied by a pinned trusted bootstrap, never by public callers."""
    def __init__(self, descriptor, pin, repository, r02, dependencies, original_guard):
        self.path = Path(descriptor); self.pin = pin; self.root = Path(repository)
        self.r02 = r02; self.common = r02.environment_guard.__globals__
        self.dependencies = dependencies; self.original_guard = original_guard
        self.read = r02.read; self.parse = r02.parse
        raw = self.read(self.path); require(sha256(raw).hexdigest() == pin, 'independent composite pin mismatch')
        self.value = self.parse(raw)
        closed(self.value, ('schema_version', 'authority_effect', 'actual_owner_outcome', 'r02_selection',
                            'original_composite_binding', 'historical_classification_binding',
                            'execution_dependencies', 'host_native_binding', 'host_ABI_library_bindings',
                            'retained_full_proof', 'module_bindings'))
        require(self.value['schema_version'] == VERSION and self.value['authority_effect'] == 'none'
                and self.value['actual_owner_outcome'] is None, 'candidate composite only')

    def binding(self, row):
        closed(row, ('path', 'sha256'))
        path = Path(row['path'])
        if not path.is_absolute():
            path = self.root / self.r02.relative(row['path'])
        raw = self.read(path)
        require(sha256(raw).hexdigest() == row['sha256'], 'selected environment input bytes changed: ' + str(path))
        return raw

    def structure(self):
        value = self.value
        selected = value['r02_selection']
        closed(selected, ('schema_version', 'json_pointer', 'environment'))
        require(selected['schema_version'] == 'lab-R02-composite-subdocument-selection/v1-candidate'
                and selected['json_pointer'] == '/R02_environment', 'explicit versioned R02 selector required')
        expected_keys = {'implementation', 'interpreter_sha256', 'libc', 'machine', 'python_version',
                         'sqlite_version', 'system'}
        closed(selected['environment'], expected_keys)
        require(value['original_composite_binding'] == ORIGINAL_COMPOSITE and
                value['historical_classification_binding'] == ORIGINAL_CLASSIFICATION,
                'whole unchanged original composite/classification required')
        original = self.parse(self.binding(value['original_composite_binding']))
        require(original['schema_version'] == 'lab-final-runtime-environment-draft/v2-candidate',
                'unselected original composite version')
        require(selected['environment'] == original['R02_environment'], 'selected exact R02 subdocument differs')
        classification = self.parse(self.binding(value['historical_classification_binding']))
        require(classification['schema_version'] == 'lab-final-runtime-environment-contract/v1-candidate'
                and classification['protected_repository_and_host_dependencies_required'] is True
                and len(classification['protected_dependencies']) > 0,
                'full original private/protected classification absent')
        proof = value['retained_full_proof']
        closed(proof, ('source_binding', 'profile_binding', 'source_rows', 'profile_rows',
                       'qualification', 'original_locator_aliases'))
        require(proof['qualification'] == 'unresolved-original-full-proof'
                and proof['original_locator_aliases'] == [], 'historical proof cannot be replaced by an alias')
        require(proof['source_binding'] == original['API_source_binding'] and
                proof['profile_binding'] == original['API_profile_binding'], 'complete original proof selectors differ')
        source = self.parse(self.binding(proof['source_binding']))
        profile = self.parse(self.binding(proof['profile_binding']))
        require(source['files'] == original['complete_source_bindings'] and
                profile['files'] == original['complete_profile_bindings'] and
                len(source['files']) == proof['source_rows'] == original['source_rows'] and
                len(profile['files']) == proof['profile_rows'] == original['profile_rows'],
                'complete original source/profile rows changed or elided')
        modules = value['module_bindings']
        require(type(modules) is list and len({row['path'] for row in modules}) == len(modules),
                'closed unique module input selection required')
        actual = {str(Path(self.r02.__file__).resolve()),
                  str(Path(self.dependencies.__file__).resolve()),
                  str(Path(self.original_guard.__file__).resolve()),
                  str(Path(self.common['__file__']).resolve())}
        selected_paths = set()
        for row in modules:
            self.binding(row); selected_paths.add(str((self.root / row['path']).resolve()))
        api = self.root / 'product/lab/release-candidates/v1/interface/api-integration-v16'
        deps = self.root / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001'
        expected_paths = {str(api / name) for name in ('__init__.py', 'r02_common.py', 'r02_installer.py', 'guard.py')}
        expected_paths |= {str(deps / name) for name in ('closure.py', 'closure_hardened_0003.py', 'checked_io.py', 'stage_io.py')}
        require(selected_paths == expected_paths, 'complete actual module closure required')
        require(actual <= selected_paths, 'actual installer/dependency/guard origins not selected')
        dependencies = value['execution_dependencies']
        closed(dependencies, ('selection_binding', 'installed_root', 'execution_configuration'))
        raw = self.binding(dependencies['selection_binding']); selected_dependencies = self.parse(raw)
        require(selected_dependencies['environment'] == selected['environment'], 'composite runtime environment differs')
        require(dependencies['execution_configuration'] == selected_dependencies['execution_configuration'],
                'composite runtime configuration differs')
        root = Path(dependencies['installed_root'])
        require(root.is_absolute() and root.resolve() == root, 'exact installed dependency root required')
        # Preserve every current native/ABI requirement, independently of R02 equality.
        native = value['host_native_binding']; closed(native, ('path', 'sha256', 'mode'))
        native_rows = [row for row in selected_dependencies['inputs'] if row['kind'] == 'native-executable']
        require(len(native_rows) == 1 and native == {'path': str(root / native_rows[0]['destination']),
                'sha256': native_rows[0]['sha256'], 'mode': native_rows[0]['mode']},
                'complete selected native requirement differs')
        expected_abi = [{'path': str(root / row['destination']), 'sha256': row['sha256'], 'mode': 0o644}
                        for row in selected_dependencies['inputs'] if row['kind'] == 'host-abi']
        for row in expected_abi:
            if row['path'].endswith('/ld-linux-x86-64.so.2'):
                row['mode'] = 0o755
        require(value['host_ABI_library_bindings'] == expected_abi and bool(expected_abi),
                'complete selected ABI requirements differ or omitted')
        schema = self.parse(self.read(Path(__file__).with_name('environment.schema.json')))
        Draft202012Validator.check_schema(schema)
        require(not list(Draft202012Validator(schema).iter_errors(value)), 'closed composite schema violation')
        return selected_dependencies

    def guard(self, package, package_pin):
        selected = self.structure()
        row = self.value['execution_dependencies']['selection_binding']
        path = self.root / row['path']
        self.dependencies.preflight(path, row['sha256'])
        self.dependencies.verify_installed(self.value['execution_dependencies']['installed_root'], selected)
        for item in [self.value['host_native_binding'], *self.value['host_ABI_library_bindings']]:
            raw = self.read(item['path'])
            require(sha256(raw).hexdigest() == item['sha256'] and
                    stat.S_IMODE(Path(item['path']).stat().st_mode) == item['mode'], 'native/ABI bytes or modes differ')
        # Genuine unchanged R02 validation, including actual interpreter, SQLite,
        # wheel membership/hashes and complete installed payload byte closure.
        package_selection, _ = self.r02.package_bytes(package, package_pin)
        require(package_selection['environment'] == self.value['r02_selection']['environment'],
                'package selected R02 environment differs')
        require(self.read(self.path) == encoded(self.value), 'exact composite descriptor changed')
        return {'schema_version': 'lab-composite-environment-verification/v1-candidate',
                'composite_binding': {'path': str(self.path), 'sha256': self.pin},
                'R02_environment': copy.deepcopy(package_selection['environment']),
                'execution_selection_binding': row, 'host_native_binding': self.value['host_native_binding'],
                'host_ABI_library_bindings': self.value['host_ABI_library_bindings'],
                'full_original_proof_qualified': False, 'original_locator_aliases': [], 'authority_effect': 'none'}

    def require_full_original_proof(self):
        # Deliberately run the unchanged full guard. Missing original locators or
        # any original proof failure propagates; no narrowed guard or catch-and-pass.
        self.structure()
        return self.original_guard.verify(self.value['retained_full_proof']['source_binding']['sha256'])

    def transition(self, operation, package, package_pin, destination, scope, expected_active):
        require(operation in ('install', 'upgrade', 'rollback'), 'unknown installation operation')
        destination = scope.destination(destination); root = destination.parent
        require(not destination.name.startswith('.'), 'canonical generation required')
        lock = os.open(root / '.composite-install.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            active_path = root / 'active-composite.json'
            current = self.parse(self.read(active_path)) if os.path.lexists(active_path) else None
            require(current == expected_active, 'exact active environment preimage changed')
            require((operation == 'install') == (current is None), 'install/upgrade predecessor mismatch')
            verification = self.guard(package, package_pin)
            if current is not None:
                closed(current, ('schema_version', 'generation', 'package_path', 'package_sha256',
                                 'composite_binding', 'R02_environment', 'authority_effect'))
                require(current['schema_version'] == 'lab-composite-installed-active/v1-candidate'
                        and current['authority_effect'] == 'none', 'closed retained generation required')
                require(current['composite_binding'] == verification['composite_binding'] and
                        current['R02_environment'] == verification['R02_environment'],
                        'predecessor selected a different composite environment')
                prior = scope.destination(root / current['generation'])
                self.r02.verify_install(prior, current['package_path'], current['package_sha256'])
            receipt_path = root / (destination.name + '.environment.json')
            if operation == 'rollback':
                require(destination.is_dir() and receipt_path.is_file(), 'rollback requires retained generation and environment receipt')
                old = self.parse(self.read(receipt_path))
                require(old['verification'] == verification and old['package_sha256'] == package_pin,
                        'rollback retained environment/package selection differs')
            else:
                require(not os.path.lexists(destination) and not os.path.lexists(receipt_path), 'new generation collision')
                self.r02.install(package, package_pin, destination, scope)
            installed = self.r02.verify_install(destination, package, package_pin)
            self.guard(package, package_pin)
            receipt = {'schema_version': 'lab-composite-installation-receipt/v1-candidate',
                       'generation': destination.name, 'package_sha256': package_pin,
                       'verification': verification, 'installed': installed, 'authority_effect': 'none',
                       'actual_owner_outcome': None, 'runtime_activations': 0, 'full_Lab_qualified': False}
            if operation != 'rollback':
                self.r02.emit(receipt_path, receipt)
            active = {'schema_version': 'lab-composite-installed-active/v1-candidate',
                      'generation': destination.name, 'package_path': str(package), 'package_sha256': package_pin,
                      'composite_binding': verification['composite_binding'],
                      'R02_environment': verification['R02_environment'], 'authority_effect': 'none'}
            require((self.parse(self.read(active_path)) if active_path.exists() else None) == expected_active,
                    'active preimage changed before commit')
            pending = root / ('.active-composite-' + destination.name + '.json')
            self.r02.emit(pending, active); os.replace(pending, active_path)
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            return {'receipt': receipt, 'active': active, 'operation': operation, 'authority_effect': 'none'}
        finally:
            os.close(lock)
