"""Fixed selected original startup; no provisioning, fallback, or public grant.

Run inside a fresh contained single-threaded installed worker. The independently
selected host loader owns process/import/ABI custody. This module constructs the
original objects; it does not install that loader, issue permission, or qualify
an unrun actual startup from an inert fixture result.
"""
import importlib.abc
import importlib.util
import inspect
import os
import base64
from datetime import datetime, timezone
from pathlib import Path
import sys
import threading
import types
import time

from .protected import (HostCustody, HeldInputs, Refusal, StartupOutcome, STAGES,
                        binding, canonical, closed, digest, need, parse, public_boundary, cleanup_uncertain, reader_role_policy)


FAMILIES = {
    'optimized-0005': {
        'name': 'completion-current-participation:optimized-0005',
        'store': 'completion-optimized-source8-0005-optimized-0005',
        'delivery_pin': 'a7f8ef943ff91b33c9b1a635e9c45f14ccb6c5926eb723d0e99205f55b27f925',
        'mapping_pin': 'b0a12f7e3deab2a660eb92e8242533bdd3f1e58ceda79c7ceb76ff040a0ede45',
        'producer_attribute': 'source8_context_producer',
        'session_role': 'source8_sessions'},
    'legacy-source8-20261018-b': {
        'name': 'completion-legacy:legacy-source8-20261018-b',
        'store': 'completion-legacy-source8-20261018-b',
        'delivery_pin': '888a46401bbe019b03445241829d4ee141f22c6c36e322afa127a942655a35b2',
        'mapping_pin': 'b027e768a68fd785128bd8daf9c576250da91717d43774916419776ced09a6ec',
        'producer_attribute': 'legacy_context_producer',
        'session_role': 'legacy_sessions'}}

API = 'product/lab/release-candidates/v1/interface/api-integration-v30/'
ORIGINAL_ROLES = {
    'protocol': API + 'protocol.py', 'source': API + 'source_bridge.py',
    'auth': API + 'auth.py', 'service': API + 'service.py',
    'source8_sessions': API + 'current_context_sessions.py',
    'legacy_sessions': API + 'current_legacy_context_sessions.py',
    'completion': API + 'completion_bridges.py', 'release': API + 'installation_release.py',
    'protected_inputs': 'product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001/protected_inputs.py',
    'environment': 'product/lab/release-candidates/v1/interface/composite-environment-v1-completion-0001/environment.py',
    'semantic_graph': 'product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001/semantic_graph.py',
    'dependencies': 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/closure_hardened_0003.py',
    'r02': 'product/lab/release-candidates/v1/interface/api-integration-v16/r02_installer.py',
    'original_guard': 'product/lab/release-candidates/v1/interface/api-integration-v16/guard.py'}
REQUIRED_ROLES = set(ORIGINAL_ROLES) | {'semantic_graph', 'private_content'}
PUBLIC_POLICY_SHA = '35129f426ee6048e73366129ae4e9c0bf9ef5cb487717719337ad42dfbd410dc'
DEPENDENCY_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'


def cold_closure(custody, selected, closure_ids):
    """Retain all original table occurrences; require current executable bytes.

    Historical proof is counted/digested as metadata and never reinterpreted as
    current body/permission. The actual original ProtectedReader later enforces
    its own complete protected proof. Current source/profile/schema rows and all
    720 original runtime inputs require explicit independently selected physical
    origins before an original module can execute.
    """
    closed(selected, ('policy_file_id', 'policy_sha256', 'documents', 'origins',
                      'dependencies_file_id', 'dependencies_sha256', 'runtime_origins'))
    if custody.posture == 'actual':
        need(selected['policy_sha256'] == PUBLIC_POLICY_SHA
             and selected['dependencies_sha256'] == DEPENDENCY_SHA, 'ORIGINAL_COLD_SELECTION')
    policy_raw = custody.read(selected['policy_file_id'])
    need(digest(policy_raw) == selected['policy_sha256'], 'COLD_POLICY')
    policy = parse(policy_raw)
    need(policy['schema_version'] == 'lab-completion-public-source-role-policy/v1'
         and policy['authority_effect'] == 'none', 'COLD_POLICY')
    docs = {}; table_digest = __import__('hashlib').sha256(); counts = []
    need(set(selected['documents']) == {d['id'] for d in policy['documents']}, 'COLD_DOCUMENTS')
    for d in policy['documents']:
        file_id = selected['documents'][d['id']]
        need(file_id in closure_ids and custody.inputs.selected(file_id)['binding'] == d['binding'], 'COLD_DOCUMENT_BINDING')
        docs[d['id']] = parse(custody.read(file_id), 64 * 1024 * 1024)
    origins = {}
    for row in selected['origins']:
        closed(row, ('logical_path', 'file_id'))
        need(row['logical_path'] not in origins and row['file_id'] in closure_ids, 'COLD_ORIGIN_DUPLICATE')
        origins[row['logical_path']] = row['file_id']
    used = set()
    for table in policy['tables']:
        pointer = table['selector']
        need(pointer.startswith('/') and '/' not in pointer[1:], 'COLD_TABLE_SELECTOR')
        rows = docs[table['document_id']][pointer[1:]]
        if type(rows) is dict: rows = [rows]
        need(type(rows) is list and len(rows) == table['row_count'], 'COLD_TABLE_COVERAGE')
        table_digest.update(canonical({'table': table['id'], 'rows': rows}))
        counts.append((table['id'], len(rows)))
        if table['role'] in ('current-source-declaration', 'current-profile-declaration', 'current-schema-execution'):
            for row in rows:
                need(row['path'] in origins, 'COLD_ORIGIN_MISSING')
                file_id = origins[row['path']]; bound = custody.inputs.selected(file_id)['binding']
                need(bound['sha256'] == row['sha256']
                     and ('size_bytes' not in row or bound['size_bytes'] == row['size_bytes']), 'COLD_ORIGIN_CONTENT')
                # Preserve exact original locator; copies do not silently stand
                # in for the originals that constructors themselves reopen.
                actual = custody.inputs.path(file_id)
                expected = row['path'] if row['path'].startswith('/') else str(Path(custody.repository) / row['path'])
                need(actual == expected, 'COLD_ORIGIN_LOCATION')
                used.add(row['path'])
    need(set(origins) == used, 'COLD_ORIGIN_EXTRA')
    dependency_raw = custody.read(selected['dependencies_file_id'])
    need(digest(dependency_raw) == selected['dependencies_sha256'], 'COLD_DEPENDENCY_SELECTION')
    dependency = parse(dependency_raw, 64 * 1024 * 1024)
    rows = dependency['inputs']; runtime = selected['runtime_origins']
    need(type(runtime) is list and len(runtime) == len(rows), 'COLD_RUNTIME_COVERAGE')
    if custody.posture == 'actual': need(len(rows) == 720, 'COLD_ORIGINAL_720')
    for original, mapped in zip(rows, runtime):
        closed(mapped, ('original_row', 'file_id'))
        need(mapped['original_row'] == original and mapped['file_id'] in closure_ids, 'COLD_RUNTIME_ROW')
        member = custody.inputs.selected(mapped['file_id'])
        need(member['binding']['sha256'] == original['sha256']
             and member['binding']['size_bytes'] == original['size_bytes']
             and member['identity']['mode'] == original['mode'], 'COLD_RUNTIME_CONTENT')
        custody.read(mapped['file_id'])
    return {'metadata_tables': counts, 'metadata_digest': table_digest.hexdigest(),
            'runtime_inputs': len(rows), 'historical_body_qualification': False}


def installed_runtime(custody, selected, closure_ids):
    """Current installed worker observations, not a native-child ABI oracle."""
    if custody.posture == 'fixture':
        need(selected is None, 'FIXTURE_RUNTIME_CEILING'); return
    closed(selected, ('executable_file_id', 'bytecode_prefix_file_id', 'preloaded_modules', 'mapped_file_ids'))
    need(sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1 and sys.flags.no_site == 1,
         'INSTALLED_PYTHON_FLAGS')
    for name in (selected['executable_file_id'], selected['bytecode_prefix_file_id']):
        need(name in closure_ids, 'INSTALLED_RUNTIME_SELECTION'); custody.read(name)
    executable = custody.inputs.path(selected['executable_file_id'])
    actual = os.stat('/proc/self/exe'); expected = custody.inputs.selected(selected['executable_file_id'])['identity']
    need(actual.st_dev == expected['device'] and actual.st_ino == expected['inode']
         and sys.executable == executable, 'INSTALLED_EXECUTABLE')
    prefix = custody.inputs.path(selected['bytecode_prefix_file_id'])
    need(sys._xoptions.get('pycache_prefix') == prefix and sys.pycache_prefix == prefix,
         'INSTALLED_CACHE_POLICY')
    # The selected prefix is a regular file, so interpreter cache lookup cannot
    # use an attacker-populated directory. -I ignores environment-only controls.
    actual_modules = {name: module for name, module in sys.modules.items()
                      if getattr(module, '__file__', None) is not None}
    need(set(selected['preloaded_modules']) == set(actual_modules), 'INSTALLED_PRELOAD_CLOSURE')
    for name, module in actual_modules.items():
        file_id = selected['preloaded_modules'][name]
        need(file_id in closure_ids and module.__file__ == custody.inputs.path(file_id), 'INSTALLED_PRELOAD_ORIGIN')
        custody.read(file_id)
    mapped = {}
    for file_id in selected['mapped_file_ids']:
        need(file_id in closure_ids, 'INSTALLED_MAP_SELECTION')
        path = custody.inputs.path(file_id); need(path not in mapped, 'INSTALLED_MAP_ALIAS')
        mapped[path] = file_id; custody.read(file_id)
    with open('/proc/self/maps', 'rb') as f: raw = f.read(4 * 1024 * 1024 + 1)
    need(len(raw) <= 4 * 1024 * 1024, 'INSTALLED_MAP_BOUND')
    for line in raw.decode('utf-8').splitlines():
        fields = line.split(None, 5)
        if len(fields) < 6 or not fields[5].startswith('/'): continue
        need(fields[5] in mapped and '\\' not in fields[5], 'INSTALLED_MAP_ORIGIN')


def private_preflight(custody, startup, private):
    """Cold joins only. Original signature/proof validators still run unchanged."""
    closed(private['anchor'], ('principal_ref', 'public_key_b64', 'source_binding', 'profile_binding',
                              'source_cut', 'operation', 'selector_binding', 'grant_binding',
                              'selector_locator', 'grant_locator'))
    anchor = private['anchor']
    need(anchor['principal_ref'] == startup['principal_ref'] and anchor['operation'] == startup['operation']
         and anchor['source_cut'] == startup['source_cut']
         and anchor['profile_binding']['sha256'] == startup['profile_sha256'], 'PRIVATE_ANCHOR_SCOPE')
    for key in ('source_binding', 'profile_binding', 'selector_binding', 'grant_binding'):
        row = anchor[key]; closed(row, ('ref', 'sha256'))
        need(type(row['ref']) is str and 0 < len(row['ref']) <= 4096 and type(row['sha256']) is str
             and len(row['sha256']) == 64 and set(row['sha256']) <= set('0123456789abcdef'), 'PRIVATE_BINDING')
    for key in ('selector', 'grant', 'policy', 'bridge', 'descriptor', 'query_raw', 'package_selection'):
        file_id = private[key + '_file_id']
        need(type(file_id) is str and file_id in startup['modules']['closure_file_ids'], 'PRIVATE_CLOSURE')
        custody.read(file_id)
    for key in ('selector', 'grant'):
        row = custody.inputs.selected(private[key + '_file_id'])
        need(row['binding']['kind'] == 'protected-input' and row['identity']['mode'] == 0o600
             and row['binding']['sha256'] == anchor[key + '_binding']['sha256'], 'PRIVATE_CONTROL_BINDING')
    package = custody.inputs.selected(private['package_selection_file_id'])['binding']
    need(custody.inputs.path(private['package_selection_file_id']) == str(Path(private['package_directory']) / 'selection.json')
         and package['sha256'] == private['package_sha256'], 'PRIVATE_PACKAGE_BINDING')
    when = datetime.fromisoformat(private['effective_deadline_utc'].replace('Z', '+00:00'))
    need(when.tzinfo is not None and when.utcoffset().total_seconds() == 0, 'PRIVATE_DEADLINE')
    if custody.posture == 'actual':
        need(datetime.now(timezone.utc) < when and when.timestamp() <= custody._scope['expires_unix'], 'PRIVATE_DEADLINE')
        need(len(base64.b64decode(anchor['public_key_b64'], validate=True)) == 32, 'PRIVATE_ISSUER')
        selector = parse(custody.read(private['selector_file_id']), 64 * 1024 * 1024)
        grant = parse(custody.read(private['grant_file_id']))
        need(len(base64.b64decode(grant['signature_b64'], validate=True)) == 64, 'PRIVATE_SIGNATURE_SHAPE')
        for key in ('source_binding', 'profile_binding', 'source_cut', 'principal_ref', 'operation'):
            need(selector[key] == grant['payload'][key] == anchor[key], 'PRIVATE_GRANT_SCOPE')
        roots = {r['id']: r for r in selector['roots']}
        need(len(roots) == len(selector['roots']) and 0 < len(roots) <= 64
             and type(selector['files']) is list and 0 < len(selector['files']) <= 65536, 'PRIVATE_SELECTOR_BOUND')
        members = {custody.inputs.path(k): custody.inputs.selected(k) for k in startup['modules']['closure_file_ids']}
        for row in selector['files']:
            path = str(Path(roots[row['root_id']]['path']) / row['path'])
            need(path in members, 'PRIVATE_UNSELECTED_MEMBER')
            selected = members[path]
            need(selected['binding']['sha256'] == row['sha256'] and selected['binding']['size_bytes'] == row['size']
                 and all(selected['identity'][k] == row[k] for k in ('device', 'inode', 'uid', 'mode')),
                 'PRIVATE_MEMBER_SCOPE')
        for key in ('selector', 'grant'):
            locator = anchor[key + '_locator']; selected = custody.inputs.selected(private[key + '_file_id'])
            need(str(Path(roots[locator['root_id']]['path']) / locator['path']) == custody.inputs.path(private[key + '_file_id'])
                 and locator['size'] == selected['binding']['size_bytes']
                 and all(locator[k] == selected['identity'][k] for k in ('device', 'inode', 'uid', 'mode')),
                 'PRIVATE_CONTROL_LOCATOR')


def callable_seal(module):
    """Capture class/function identity and code, including class method changes."""
    result = []
    def item(name, value):
        if isinstance(value, (staticmethod, classmethod)): value = value.__func__
        if isinstance(value, types.FunctionType):
            result.append((name, id(value), id(value.__code__),
                           code_digest(value.__code__),
                           id(value.__defaults__), id(value.__kwdefaults__)))
        elif isinstance(value, type) and value.__module__ == module.__name__:
            result.append((name, id(value), tuple(id(x) for x in value.__bases__)))
            for key, member in vars(value).items():
                if isinstance(member, (types.FunctionType, staticmethod, classmethod)):
                    item(name + '.' + key, member)
    for name, value in vars(module).items(): item(name, value)
    return tuple(sorted(result))


def code_digest(code):
    """Stable code identity without marshal's reference/interning encodings."""
    def constant(v):
        if isinstance(v, types.CodeType): return ['code', structure(v)]
        if v is Ellipsis: return ['ellipsis']
        if type(v) is bytes: return ['bytes', v.hex()]
        if type(v) is tuple: return ['tuple', [constant(x) for x in v]]
        if type(v) is frozenset: return ['frozenset', sorted((constant(x) for x in v), key=canonical)]
        if type(v) is float: return ['float', v.hex()]
        if type(v) is complex: return ['complex', v.real.hex(), v.imag.hex()]
        if type(v) is int: return ['int', str(v)]
        need(v is None or type(v) in (str, bool), 'CODE_CONSTANT')
        return [type(v).__name__, v]
    def structure(c):
        return [c.co_argcount, c.co_posonlyargcount, c.co_kwonlyargcount, c.co_nlocals,
                c.co_stacksize, c.co_flags, c.co_code.hex(), [constant(x) for x in c.co_consts],
                list(c.co_names), list(c.co_varnames), list(c.co_freevars), list(c.co_cellvars),
                c.co_filename, c.co_name, c.co_qualname, c.co_firstlineno,
                c.co_linetable.hex(), c.co_exceptiontable.hex()]
    return digest(canonical(structure(code)))


class _SourceLoader(importlib.abc.Loader):
    def __init__(self, owner, row): self.owner = owner; self.row = row
    def create_module(self, spec): return None
    def exec_module(self, module):
        owner = self.owner; row = self.row
        owner._boundary('module-import')
        raw = owner._raw[row['file_id']]
        module.__file__ = owner.inputs.path(row['file_id'])
        module.__cached__ = None
        owner._owned[module.__name__] = module
        try:
            owner.effect_started = True
            exec(compile(raw, module.__file__, 'exec', dont_inherit=True), module.__dict__)
        finally:
            owner._boundary('module-import')
        owner._seals[module.__name__] = callable_seal(module)


class _Finder(importlib.abc.MetaPathFinder):
    def __init__(self, owner): self.owner = owner
    def find_spec(self, fullname, path=None, target=None):
        owner = self.owner
        row = owner._modules.get(fullname)
        if row is not None:
            spec = importlib.util.spec_from_file_location(fullname, owner.inputs.path(row['file_id']),
                loader=_SourceLoader(owner, row),
                submodule_search_locations=[str(Path(owner.inputs.path(row['file_id'])).parent)]
                if row['package'] else None)
            return spec
        # An unselected Python import must not fall through to ambient sys.path.
        # Builtin/frozen modules and already-loaded trusted startup stdlib remain
        # the installed host's separately selected interpreter closure.
        if fullname not in sys.builtin_module_names:
            frozen = importlib.machinery.FrozenImporter.find_spec(fullname)
            if frozen is None: raise Refusal('UNSELECTED_IMPORT')
        return None


class SelectedModules:
    """Fresh source-only loader with exact execution observations.

    Preloaded selected names refuse, including objects with forged origins.
    The scoped audit observer verifies every Python exec against selected source
    code or an independently selected exact generated-code digest. Original
    importlib loaders bypassing meta_path still undergo this check. Native
    extensions are never dynamically admitted here: installed host must preload
    their independently verified ABI closure before entering this scope.
    """
    def __init__(self, custody, selection):
        need(type(custody) in (HostCustody, FixtureCustody), 'CUSTODY_TYPE')
        self.custody = custody; self.inputs = custody.inputs; self._closed = False
        self._owned = {}; self._seals = {}; self._raw = {}; self._gate = {'owner': None}
        self._before = dict(sys.modules); self._modules = {}; self._paths = {}; self._roles = {}
        self.effect_started = False
        closed(selection, ('schema_version', 'posture', 'modules', 'closure_file_ids', 'generated_code_sha256'))
        need(selection['schema_version'] == 'lab-startup-module-selection/v1'
             and selection['posture'] == custody.posture
             and type(selection['modules']) is list and 0 < len(selection['modules']) <= 4096,
             'MODULE_SELECTION')
        need(type(selection['closure_file_ids']) is list
             and 0 < len(selection['closure_file_ids']) <= 65536
             and len(set(selection['closure_file_ids'])) == len(selection['closure_file_ids']), 'CLOSURE_SELECTION')
        self._closure = tuple(selection['closure_file_ids'])
        excluded = {custody._enrollment_id, custody._control_id} if type(custody) is HostCustody else {custody._permission}
        need(set(self._closure) == set(self.inputs._members) - excluded, 'COMPLETE_SUBJECT_CLOSURE')
        self._generated = set(selection['generated_code_sha256'])
        need(len(self._generated) <= 4096 and all(type(x) is str and len(x) == 64
             and set(x) <= set('0123456789abcdef') for x in self._generated), 'GENERATED_SELECTION')
        for row in selection['modules']:
            closed(row, ('name', 'file_id', 'package', 'role'))
            need(type(row['name']) is str and row['name'] and all(p.isidentifier() for p in row['name'].split('.'))
                 and row['name'] not in self._modules and row['name'] not in sys.modules
                 and type(row['package']) is bool and row['file_id'] in self._closure, 'MODULE_COLLISION')
            need(self.inputs.selected(row['file_id'])['binding']['kind'] in ('execution', 'public-package'),
                 'MODULE_KIND')
            self._modules[row['name']] = dict(row)
            path = self.inputs.path(row['file_id'])
            need(path not in self._paths, 'MODULE_ORIGIN_ALIAS')
            self._paths[path] = row
            if row['role'] is not None:
                need(row['role'] not in self._roles, 'MODULE_ROLE_DUPLICATE')
                self._roles[row['role']] = row['name']
                if custody.posture == 'actual' and row['role'] in ORIGINAL_ROLES:
                    need(path == str(Path(custody.repository) / ORIGINAL_ROLES[row['role']]), 'ORIGINAL_ORIGIN')
        need(set(self._roles) == REQUIRED_ROLES, 'MODULE_ROLE_CLOSURE')
        self._finder = _Finder(self)
        self._exec_codes = set()
        self._entered = False

    def _boundary(self, stage):
        self.custody.check(stage)
        self.inputs.guard()

    def preflight(self):
        self._boundary('closure')
        for name in self._closure:
            row = self.inputs.selected(name)
            raw = self.custody.read(name)
            if any(m['file_id'] == name for m in self._modules.values()):
                self._raw[name] = raw
                self._exec_codes.add(code_digest(compile(raw, self.inputs.path(name), 'exec', dont_inherit=True)))
        self._boundary('closure')

    def enter(self):
        need(not self._entered and not self._closed and threading.active_count() == 1, 'IMPORT_PROCESS')
        self.preflight()
        need(all(name not in sys.modules for name in self._modules), 'MODULE_COLLISION')
        gate = self._gate
        def audit(event, args):
            owner = gate['owner']
            if owner is None: return
            if event == 'exec':
                need(code_digest(args[0]) in owner._exec_codes | owner._generated,
                     'UNSELECTED_CODE_EXEC')
            elif event == 'import' and len(args) > 1 and args[1]:
                need(args[1] in owner._paths, 'UNSELECTED_NATIVE_IMPORT')
        # CPython audit hooks cannot be removed. After close this bounded hook
        # retains only gate{'owner':None}, and has no active behavior/authority.
        sys.addaudithook(audit)
        self._gate['owner'] = self
        sys.meta_path.insert(0, self._finder); self._entered = True
        return self

    def module(self, role):
        need(self._entered and not self._closed and role in self._roles, 'MODULE_ROLE')
        name = self._roles[role]
        module = __import__(name, fromlist=['*'])
        self.guard()
        return module

    def guard(self):
        self._boundary('module-import')
        need(self._finder in sys.meta_path, 'MODULE_FINDER_CHANGED')
        for name, before in self._before.items():
            need(sys.modules.get(name) is before, 'BASE_MODULE_CHANGED')
        for name, module in list(sys.modules.items()):
            if name in self._before: continue
            need(name in self._modules, 'UNSELECTED_MODULE')
            row = self._modules[name]
            need(type(module) is types.ModuleType and getattr(module, '__file__', None) == self.inputs.path(row['file_id'])
                 and module.__spec__ is not None and module.__spec__.origin == module.__file__, 'MODULE_ORIGIN')
            if name not in self._owned:
                # Original dynamic loaders were observed by the execution hook.
                self._owned[name] = module; self._seals[name] = callable_seal(module)
            need(self._owned[name] is module and self._seals.get(name, callable_seal(module)) == callable_seal(module),
                 'MODULE_OBJECT_CHANGED')
        for name in self._closure: self.custody.read(name)
        self._boundary('module-import')

    def close(self):
        if self._closed: return ()
        self._closed = True; self._gate['owner'] = None
        codes = []
        if self._entered:
            if self._finder in sys.meta_path: sys.meta_path.remove(self._finder)
            else: codes.append('MODULE_FINDER_CUSTODY_LOST')
        for name, module in reversed(tuple(self._owned.items())):
            if sys.modules.get(name) is module: del sys.modules[name]
            elif name in sys.modules: codes.append('MODULE_REPLACEMENT_PRESERVED')
        self._raw.clear()
        return tuple(codes)


class FixtureCustody:
    """Owned inert algorithm fixtures only. Never accepted as HostCustody."""
    posture = 'fixture'
    def __init__(self, inputs, selection_sha256, permission_id, expected_permission, repository):
        need(type(inputs) is HeldInputs, 'FIXTURE_INPUTS')
        binding(expected_permission)
        need(inputs.selected(permission_id)['binding'] == expected_permission, 'FIXTURE_PERMISSION')
        self.inputs = inputs; self.selection_sha256 = selection_sha256
        self._permission = permission_id; self.repository = repository
        self._checks = 0
    def check(self, stage):
        need(stage in STAGES, 'FIXTURE_STAGE')
        value = parse(self.inputs.read(self._permission))
        closed(value, ('schema_version', 'selection_sha256', 'revoked', 'actual_authority', 'cleanup_permitted'))
        need(value['schema_version'] == 'lab-startup-owned-fixture-permission/v1'
             and value['selection_sha256'] == self.selection_sha256 and value['actual_authority'] is False
             and type(value['revoked']) is bool and type(value['cleanup_permitted']) is bool
             and (value['cleanup_permitted'] if stage == 'cleanup' else not value['revoked']), 'FIXTURE_PERMISSION')
        self._checks += 1
    def read(self, file_id, *, maximum=64 * 1024 * 1024):
        self.check('private-read')
        try: return self.inputs.read(file_id, maximum=maximum)
        finally: self.check('private-read')
    def reader_proof(self, challenge):
        self.check('reader-authentication')
        return {'schema_version': 'owned-inert-reader-proof', 'challenge': challenge,
                'actual_signature': None}


def _exact(value, cls):
    need(type(value) is cls, 'ORIGINAL_CLASS')
    return value


class Startup:
    """One attempt, fixed original calls, exact cleanup ownership and no retry."""
    @public_boundary
    def __init__(self, custody, selection_raw, expected_sha256):
        need(type(custody) in (HostCustody, FixtureCustody), 'CUSTODY_TYPE')
        need(digest(selection_raw) == expected_sha256, 'STARTUP_SELECTION')
        selected_sha = custody._scope['selection_sha256'] if type(custody) is HostCustody else custody.selection_sha256
        need(selected_sha == expected_sha256, 'CUSTODY_SELECTION')
        value = parse(selection_raw, 64 * 1024 * 1024)
        closed(value, ('schema_version', 'posture', 'family', 'role', 'operation', 'principal_ref',
                       'repository', 'modules', 'private_file_id', 'profile_sha256', 'source_cut', 'cold', 'runtime'))
        need(value['schema_version'] == 'lab-protected-startup-selection/v2'
             and value['posture'] == custody.posture and value['family'] in FAMILIES
             and value['role'] in ('participation', 'installation-metadata')
             and (value['role'] != 'installation-metadata' or value['family'] == 'legacy-source8-20261018-b')
             and value['operation'] in ('installation.execute', 'release.prepare'), 'STARTUP_SELECTION')
        if type(custody) is HostCustody:
            need(all(value[k] == custody._scope[k] for k in ('family', 'role', 'operation', 'principal_ref'))
                 and digest(canonical(value['source_cut'])) == custody._scope['source_cut_sha256'], 'STARTUP_SCOPE')
            custody.repository = value['repository']
        need(value['repository'] == custody.repository and Path(value['repository']).is_absolute(), 'STARTUP_ROOT')
        self.custody = custody; self.value = value; self._selection_sha = expected_sha256; self._used = False
        self.modules = SelectedModules(custody, value['modules'])
        self._cleanups = []; self._completed = []; self._started = None; self._secondary = []

    def _stage(self, stage, call):
        self.custody.check(stage)
        self.modules.guard()
        self._started = stage
        try:
            value = call()
        except Exception:
            try:
                self.custody.check(stage); self.modules.guard()
            except Exception:
                self._secondary.append(stage.upper().replace('-', '_') + '_POSTGUARD_FAILED')
            raise Refusal('CONSTRUCTOR_FAILED') from None
        else:
            self.custody.check(stage)
            self.modules.guard()
        self._completed.append(stage); self._started = None
        return value

    def _cleanup(self, code, owner, attribute, args=()):
        method = getattr(owner, attribute)
        need(callable(method), 'CLEANUP_METHOD')
        function = getattr(method, '__func__', method)
        self._cleanups.append((code, owner, attribute, method, args,
                               getattr(function, '__code__', None)))

    @public_boundary
    def preflight(self):
        need(digest(canonical(self.value)) == self._selection_sha, 'STARTUP_SELECTION_DRIFT')
        self.custody.check('admission')
        self.modules.preflight()
        installed_runtime(self.custody, self.value['runtime'], self.value['modules']['closure_file_ids'])
        self.cold_observation = cold_closure(self.custody, self.value['cold'],
                                             self.value['modules']['closure_file_ids'])
        private_raw = self.custody.read(self.value['private_file_id'])
        private = parse(private_raw, 64 * 1024 * 1024)
        closed(private, ('anchor', 'selector_file_id', 'grant_file_id', 'policy_file_id',
                         'bridge_file_id', 'bridge_binding', 'descriptor_file_id',
                         'package_directory', 'package_sha256', 'package_selection_file_id', 'effective_deadline_utc',
                         'query_raw_file_id'))
        private_preflight(self.custody, self.value, private)
        policy = parse(self.custody.read(private['policy_file_id']))
        reader_role_policy(policy, self.value['role'], self.value['family'], self.value['operation'])
        need(policy['principal_ref'] == self.value['principal_ref'], 'ROLE_PRINCIPAL')
        self.custody.check('admission')
        return private

    def run(self):
        """Return only bounded public status; no protected values or raw errors."""
        need(not self._used, 'STARTUP_ONCE'); self._used = True
        primary = None; cleanup = []; effect = 'none'
        try:
            private = self.preflight()
            # No original code is imported until complete selected closure and
            # current custody have passed. Import itself may start effects.
            self._started = 'module-import'
            self.modules.enter()
            self._construct(private)
            self.custody.check('final-currentness'); self.modules.guard()
            effect = 'owned-inert' if self.custody.posture == 'fixture' else 'effect-started'
        except Exception as error:
            primary = (self._started or 'preflight').upper().replace('-', '_') + '_FAILED'
            if cleanup_uncertain(error):
                cleanup.append('OWNED_DESCRIPTOR_CLOSE_UNCERTAIN')
            if self.modules.effect_started or effect != 'none': effect = 'unknown'
        finally:
            active_primary = sys.exception(); interrupted = None
            try:
                for code, owner, attribute, method, args, original_code in reversed(self._cleanups):
                    try:
                        # Never invoke a replacement or silently adopt foreign state.
                        current = getattr(owner, attribute)
                        need(getattr(current, '__self__', None) is getattr(method, '__self__', None)
                             and (getattr(current, '__func__', None) is getattr(method, '__func__', None)
                                  if hasattr(method, '__func__') else
                                  type(current) is types.BuiltinMethodType and type(method) is types.BuiltinMethodType
                                  and current.__self__ is owner and current.__name__ == method.__name__ == attribute),
                             'CLEANUP_CUSTODY')
                        need(getattr(getattr(method, '__func__', method), '__code__', None) is original_code,
                             'CLEANUP_CODE_CHANGED')
                        if code not in ('CHANNEL_CLOSE_FAILED', 'SERVICE_SEEN_CLEAR_FAILED', 'BRIDGE_DETACH_FAILED'):
                            self.custody.check('cleanup')
                        result = method(*args)
                        if attribute == '__exit__': need(not result, 'SOURCE_EXIT_SUPPRESSION')
                    except BaseException as failure:
                        cleanup.append(code)
                        if not isinstance(failure, Exception) and interrupted is None:
                            interrupted = failure
            finally:
                # A single ordinary interruption must not skip module teardown.
                try:
                    cleanup.extend(self.modules.close())
                except BaseException as failure:
                    cleanup.append('MODULE_TEARDOWN_FAILED')
                    if not isinstance(failure, Exception) and interrupted is None:
                        interrupted = failure
            if cleanup: effect = 'unknown'
            if interrupted is not None:
                self._secondary.append('CLEANUP_INTERRUPTED')
                if primary is None and active_primary is None:
                    # Cleanup has completed; never report an interrupted run PASS.
                    raise interrupted
        return StartupOutcome(self.custody.posture, tuple(self._completed), primary,
                              tuple(cleanup), effect, False, tuple(self._secondary), self.value['role'])

    def _construct(self, private):
        m = self.modules.module
        protected = m('protected_inputs'); protocol = m('protocol'); source = m('source')
        auth = m('auth'); service = m('service'); completion = m('completion'); release = m('release')
        original_environment = m('environment'); dependencies = m('dependencies'); r02 = m('r02')
        original_guard = m('original_guard'); graph = m('semantic_graph'); content = m('private_content')
        self._started = None
        anchor = protected.CustodyAnchor(**private['anchor'])
        need(private['anchor']['principal_ref'] == self.value['principal_ref']
             and private['anchor']['source_cut'] == self.value['source_cut']
             and private['anchor']['operation'] == self.value['operation']
             and private['anchor']['profile_binding']['sha256'] == self.value['profile_sha256'], 'ANCHOR_JOIN')
        reader = self._stage('protected-reader', lambda: protected.ProtectedReader(
            self.custody.read(private['selector_file_id']), self.custody.read(private['grant_file_id']), anchor))
        _exact(reader, protected.ProtectedReader)
        self._stage('protected-reader', reader.verify)
        schemas = self._stage('schemas', lambda: protocol.Schemas(expected_profile_sha256=self.value['profile_sha256']))
        _exact(schemas, protocol.Schemas)
        need(schemas.profile_binding == private['anchor']['profile_binding'], 'SCHEMAS_PROFILE')
        family = FAMILIES[self.value['family']]
        resource = source.replay_source(family['name'], source_repo=Path(self.value['repository']))
        def enter_source():
            value = resource.__enter__()
            self._cleanup('SOURCE_EXIT_FAILED', resource, '__exit__', (None, None, None))
            return value
        view = self._stage('source', enter_source)
        producer = getattr(view, family['producer_attribute'])
        session_module = m(family['session_role'])
        need(session_module.D is producer and session_module.DELIVERY_PIN == family['delivery_pin']
             and session_module.MAPPING_PIN == family['mapping_pin'], 'FAMILY_PRODUCER')
        selected = getattr(view, 'custody_signed_sources', None)
        if self.value['family'] == 'legacy-source8-20261018-b':
            selected = getattr(view, 'legacy_signed_sources', selected)
        need(selected is not None and type(selected) is producer.reader.adapter.SignedSources
             and type(view) is producer.reader.Inspection
             and selected.source_cut == self.value['source_cut']
             and selected.source_cut['store_ref'] == family['store']
             and selected.source_cut['branch_ref'] == 'branch:' + family['store']
             and producer.reader is producer.MAPPED.reader, 'FAMILY_SOURCE')
        self._stage('mapper', lambda: producer.selected_mapping(family['mapping_pin']))
        policy = self.custody.inputs.selected(private['policy_file_id'])
        need(policy['binding']['kind'] == 'protected-input' and policy['identity']['mode'] == 0o600, 'POLICY_CUSTODY')
        self.custody.read(private['policy_file_id'])
        def make_channel():
            channel = auth.ReaderChannel(self.custody.inputs.path(private['policy_file_id']),
                                         policy['binding']['sha256'], schemas)
            _exact(channel, auth.ReaderChannel)
            self._cleanup('CHANNEL_CLOSE_FAILED', channel, 'close')
            return channel
        channel = self._stage('reader-channel', make_channel)
        proof = self.custody.reader_proof(channel.challenge)
        self._stage('reader-authentication', lambda: channel.authenticate(protocol.compact(proof)))
        need(channel.context['principal_ref'] == self.value['principal_ref']
             and ((channel.policy['session_control'] is not None) == (self.value['role'] == 'participation')), 'SESSION_PERMISSION')
        reader_role_policy(channel.policy, self.value['role'], self.value['family'], self.value['operation'])
        def make_host():
            host = service.Service(view, channel, schemas)
            _exact(host, service.Service)
            # Register each returned actual constituent before the post-boundary.
            self._cleanup('HANDLERS_CLOSE_FAILED', host.handlers, 'close')
            self._cleanup('SERVICE_SEEN_CLEAR_FAILED', host.seen, 'clear')
            if host.sessions is not None:
                self._cleanup('SESSIONS_CLOSE_FAILED', host.sessions, 'close')
            return host
        host = self._stage('context-sessions', make_host)
        if self.value['role'] == 'participation':
            need(host.sessions is not None and type(host.sessions) is session_module.ContextSessions
                 and host.session_attachment is None, 'SESSION_CONSTRUCTION')
            need(host.sessions.source is selected and type(host.sessions.bridge) is session_module.PermissionBridge
                 and host.sessions.bridge.source is selected and host.sessions.bridge.channel is channel,
                 'SESSION_PERMISSION_BRIDGE')
            query_raw = self.custody.read(private['query_raw_file_id'])
            # Original Context generator retains exact selected signed source,
            # mapper and ReaderChannel semantics; no build/provision helper is used.
            self._stage('context-query', lambda: producer.generate(host.sessions.source, host.sessions.bridge,
                protocol.frame_parse(query_raw), query_raw, family['mapping_pin'], schemas))
            return
        need(host.sessions is None and host.session_attachment is None
             and getattr(host, 'parent_host', None) is None, 'METADATA_HOST')
        descriptor = self.custody.inputs.selected(private['descriptor_file_id'])['binding']
        environment = self._stage('composite-environment', lambda: original_environment.CompositeEnvironment(
            Path(self.custody.inputs.path(private['descriptor_file_id'])), descriptor['sha256'],
            Path(self.value['repository']), r02, dependencies, original_guard))
        _exact(environment, original_environment.CompositeEnvironment)
        bridge_raw = self.custody.read(private['bridge_file_id'])
        modules = {'protected_inputs': protected, 'semantic_graph': graph, 'environment': original_environment,
                   'dependencies': dependencies, 'private_content': content}
        bridge = self._stage('completion-bridge', lambda: completion.CompletionBridge(
            bridge_raw, private['bridge_binding'], Path(self.value['repository']), modules, environment))
        _exact(bridge, completion.CompletionBridge)
        need(vars(host).get('completion_bridge') is None, 'FOREIGN_BRIDGE')
        host.completion_bridge = bridge
        # Detach only our own exact bridge; do not remove a foreign replacement.
        def detach():
            need(vars(host).get('completion_bridge') is bridge, 'BRIDGE_CUSTODY')
            del host.completion_bridge
        self._cleanup('BRIDGE_DETACH_FAILED', _Cleanup(detach), 'close')
        builder = self._stage('installation-release', lambda: release.InstallationRelease(
            host, self.value['operation'], auth.instant(private['effective_deadline_utc'])))
        _exact(builder, release.InstallationRelease)
        need(type(builder.completion) is completion.BoundCompletionBridge
             and builder.completion.selected is bridge
             and builder.plan['schema_version'] == 'lab-installation-release-plan/v2-candidate'
             and builder.plan['bridge_binding'] == private['bridge_binding'], 'COMPLETION_JOIN')
        if self.value['operation'] == 'installation.execute':
            self._stage('installation-release', lambda: builder.completion.verify_environment(
                self.custody.read(private['descriptor_file_id']), Path(private['package_directory']),
                private['package_sha256']))


class _Cleanup:
    def __init__(self, action): self._action = action
    def close(self): self._action()


class Composition:
    """Sequential construction coverage, never simultaneously-live readiness."""
    @public_boundary
    def __init__(self, participation, metadata, selection_raw, expected_sha256):
        need(type(participation) is Startup and type(metadata) is Startup
             and participation is not metadata, 'COMPOSITION_TYPES')
        need(digest(selection_raw) == expected_sha256, 'COMPOSITION_SELECTION')
        value = parse(selection_raw)
        closed(value, ('schema_version', 'participation_sha256', 'metadata_sha256',
                       'family', 'operation', 'profile_sha256', 'source_cut'))
        need(value['schema_version'] == 'lab-startup-composition-selection/v1'
             and value['family'] == 'legacy-source8-20261018-b', 'COMPOSITION_FAMILY')
        self.roles = (participation, metadata); self.value = value; self._selection_sha = expected_sha256; self._used = False
        for role, startup in zip(('participation', 'installation-metadata'), self.roles):
            need(startup.value['role'] == role and all(startup.value[k] == value[k]
                 for k in ('family', 'operation', 'profile_sha256', 'source_cut')), 'COMPOSITION_JOIN')
            key = 'participation_sha256' if role == 'participation' else 'metadata_sha256'
            need(digest(canonical(startup.value)) == value[key], 'COMPOSITION_ROLE_SELECTION')
        need(participation.custody.posture == metadata.custody.posture
             and participation.custody is not metadata.custody
             and participation.value['principal_ref'] != metadata.value['principal_ref'], 'COMPOSITION_AUTHORITY')
        if participation.custody.posture == 'actual':
            need(participation.value['repository'] == metadata.value['repository']
                 and participation.custody._scope['attempt_id'] != metadata.custody._scope['attempt_id']
                 and participation.custody._channel_identity != metadata.custody._channel_identity, 'COMPOSITION_HOSTS')

    def _guard(self):
        need(digest(canonical(self.value)) == self._selection_sha, 'COMPOSITION_SELECTION_DRIFT')
        records = [role.preflight() for role in self.roles]
        policies = [parse(role.custody.read(private['policy_file_id']))
                    for role, private in zip(self.roles, records)]
        keys = [p['reader_public_key'] for p in policies]
        if self.roles[0].custody.posture == 'actual':
            keys = [base64.b64decode(key, validate=True) for key in keys]
            need(all(len(key) == 32 for key in keys), 'COMPOSITION_KEY_SHAPE')
        need(keys[0] != keys[1], 'COMPOSITION_KEYS')
        need(records[0]['anchor']['source_binding'] == records[1]['anchor']['source_binding']
             and records[0]['anchor']['profile_binding'] == records[1]['anchor']['profile_binding'], 'COMPOSITION_ORIGINAL_CUT')
        for role, private in zip(self.roles, records):
            need(private['anchor']['principal_ref'] == role.value['principal_ref'], 'COMPOSITION_ANCHOR')
            role.custody.check('final-currentness')

    def run(self):
        need(not self._used, 'COMPOSITION_ONCE'); self._used = True
        outcomes = []; primary = None
        try:
            self._guard()  # both full closures, before either effectful import
            for role in self.roles:
                self._guard()  # no surviving authority borrowed from prior role
                started = time.time_ns(); monotonic = time.monotonic_ns()
                result = role.run()
                outcomes.append({'role': role.value['role'], 'selection_sha256': role._selection_sha,
                                 'started_unix_ns': started, 'finished_unix_ns': time.time_ns(),
                                 'elapsed_monotonic_ns': time.monotonic_ns()-monotonic, 'outcome': result.public()})
                need(result.primary_code is None and not result.cleanup_codes, 'COMPOSITION_ROLE_FAILED')
            self._guard()  # fresh independent authorities after both cleanups
        except Exception:
            primary = 'COMPOSITION_FAILED'
        return {'schema_version': 'lab-startup-composition-outcome/v1', 'primary_code': primary,
                'roles': outcomes, 'sequential_constructor_coverage': primary is None,
                'simultaneously_live_contexts': False, 'composite_readiness': False,
                'actual_startup_qualified': False, 'authority_effect': 'none'}
