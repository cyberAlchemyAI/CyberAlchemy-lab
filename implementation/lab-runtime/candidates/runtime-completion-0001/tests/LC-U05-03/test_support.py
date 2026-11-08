"""Owned inert fixtures. Import only after the external complete input guard."""
import hashlib, importlib.util, json, os, stat, sys, tempfile, types
from pathlib import Path
from policy_compat import FIXTURE_SOURCE, policy as original_policy

R = Path('/home/vlad_/projects/CyberAlchemy-lab')
S = R / 'implementation/lab-runtime/candidates/runtime-completion-0001'
PACKAGE = '_lab_runtime_u0503_selected'
package = types.ModuleType(PACKAGE); package.__path__ = [str(S / 'bootstrap')]
if PACKAGE in sys.modules: raise ValueError('selected test namespace collision')
sys.modules[PACKAGE] = package
def load(name):
    path = S / 'bootstrap' / (name + '.py')
    spec = importlib.util.spec_from_file_location(PACKAGE + '.' + name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module); return module
P = load('protected'); B = load('environment')

COMMON = r'''
import json, os
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime
CFG = CONFIG_LITERAL
def event(name):
    with open(CFG['events'], 'a', encoding='utf-8') as f: f.write(name+'\n')
    if CFG.get('interrupt') == name: raise KeyboardInterrupt('owned fixture cleanup interruption')
    if CFG.get('fail') == name: raise RuntimeError('INERT_PRIVATE_MARKER /private/custody/locator')
class CustodyAnchor:
    def __init__(self, **kwargs): self.__dict__.update(kwargs)
class ProtectedReader:
    def __init__(self, selector, grant, anchor):
        event('protected-reader'); self.anchor=anchor
        if selector != b'selected-selector' or grant != b'selected-grant': raise ValueError('grant')
    def verify(self): event('protected-verify'); return {}
class Schemas:
    def __init__(self, *, expected_profile_sha256):
        event('schemas')
        if expected_profile_sha256 != CFG['profile']['sha256']: raise ValueError('profile')
        self.profile_binding = CFG['profile']
class SignedSources:
    def __init__(self): self.source_cut=CFG['cut']
class Inspection: pass
class PermissionBridge:
    def __init__(self, selected, channel, schemas):self.source=selected;self.channel=channel;self.schemas=schemas
class ContextSessions:
    def __init__(self, selected, channel, schemas):self.source=selected;self.bridge=PermissionBridge(selected,channel,schemas)
    def close(self): event('sessions-close')
class ReaderChannel:
    def __init__(self, path, expected_sha, schemas):
        event('channel'); self.challenge={'nonce':'inert-nonce'}
        self.context=None; self.policy=json.loads(Path(path).read_bytes()); _original_policy(self.policy)
    def authenticate(self, raw):
        event('authenticate'); proof=json.loads(raw)
        if proof != {'schema_version':'owned-inert-reader-proof','challenge':self.challenge,'actual_signature':None}: raise ValueError('proof')
        self.context={'principal_ref':CFG['principal']}
    def close(self): event('channel-close'); self.context=None; self.challenge=None
class Handlers:
    def close(self): event('handlers-close')
class Service:
    def __init__(self, view, channel, schemas):
        event('service'); self.channel=channel; self.schemas=schemas
        self.handlers=Handlers(); self.seen=set(); self.sessions=None if CFG.get('sessions_none') or CFG['role']=='installation-metadata' else ContextSessions(view.custody_signed_sources,channel,schemas)
        self.session_attachment=None
class CompositeEnvironment:
    def __init__(self, descriptor, pin, repository, r02, dependencies, guard): event('environment')
class CompletionBridge:
    def __init__(self, raw, independent_binding, repository, modules, environment):
        event('bridge')
        if set(modules) != {'protected_inputs','semantic_graph','environment','dependencies','private_content'}: raise ValueError('modules')
        if type(environment) is not CompositeEnvironment: raise ValueError('environment')
        self.binding=independent_binding
class BoundCompletionBridge:
    def __init__(self, bridge): self.selected=bridge
    def verify_environment(self, raw, package, pin): event('verify-environment')
class InstallationRelease:
    def __init__(self, host, operation, deadline):
        event('release')
        if host.channel.policy.get('installation_release_control') is None or host.sessions is not None: raise ValueError('original incompatible installation role')
        self.completion=BoundCompletionBridge(host.completion_bridge)
        if type(deadline) is not datetime:raise ValueError('original datetime deadline required')
        self.plan={'schema_version':'lab-installation-release-plan/v1-candidate' if CFG.get('plan_v1') else 'lab-installation-release-plan/v2-candidate',
                   'bridge_binding':host.completion_bridge.binding}
def compact(value): return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def frame_parse(raw):return json.loads(raw)
def instant(value):return datetime.fromisoformat(value.replace('Z','+00:00'))
reader=SimpleNamespace(adapter=SimpleNamespace(SignedSources=SignedSources), Inspection=Inspection)
MAPPED=SimpleNamespace(reader=reader)
def selected_mapping(pin):
    event('mapper')
    if pin != CFG['mapping_pin']: raise ValueError('mapping')
    return ({},{},{})
def generate(selected, channel, message, raw, pin, schemas):
    event('context-generate')
    if type(selected) is not SignedSources or type(channel) is not PermissionBridge or channel.channel.context is None or raw != b'{}' or pin != CFG['mapping_pin']: raise ValueError('context')
    return ({},[],{},{},None)
def build(*a): raise AssertionError('FORBIDDEN_PROVISION')
def provision(*a): raise AssertionError('FORBIDDEN_PROVISION')
class SourceScope:
    def __enter__(self):
        event('source-enter'); view=Inspection(); selected=SignedSources()
        view.custody_signed_sources=selected; view.legacy_signed_sources=selected
        setattr(view,CFG['producer_attribute'],D); return view
    def __exit__(self, typ, value, tb):
        event('source-exit')
        if any(x is not None for x in (typ,value,tb)): raise ValueError('exit arguments')
        return False
def replay_source(name, *, source_repo):
    if name != CFG['name']: raise ValueError('family')
    return SourceScope()
import sys
D=sys.modules[__name__]
DELIVERY_PIN=CFG['delivery_pin']; MAPPING_PIN=CFG['mapping_pin']
'''


class Fixture:
    def __init__(self, temp_root, *, family='optimized-0005', role='participation', config=None):
        self.tmp = tempfile.TemporaryDirectory(prefix='owned-startup-', dir=temp_root)
        self.root = Path(self.tmp.name); self.files = {}; self._held = []
        self.events = self.root / 'events.log'; self.package = '_owned_startup_' + self.root.name.replace('-', '_')
        selected = B.FAMILIES[family]
        cut = {'store_ref': selected['store'], 'branch_ref': 'branch:' + selected['store']}
        profile = {'ref': 'profile.json', 'sha256': P.digest(b'fixture-profile')}
        cfg = dict(selected, cut=cut, principal='fixture-principal', profile=profile, events=str(self.events), role=role)
        cfg.update(config or {})
        self.config = cfg; self.family = family; self.role = role
        self.put('pkg', 'code/__init__.py', b'', 'execution')
        self.put('common', 'code/common.py', (COMMON.replace('CONFIG_LITERAL', repr(cfg))+'\n'+FIXTURE_SOURCE).encode(), 'execution')
        modules = [{'name': self.package, 'file_id': 'pkg', 'package': True, 'role': None},
                   {'name': self.package + '.common', 'file_id': 'common', 'package': False, 'role': None}]
        for role in sorted(B.REQUIRED_ROLES):
            self.put(role, 'code/' + role + '.py', b'from .common import *\n', 'execution')
            modules.append({'name': self.package + '.' + role, 'file_id': role, 'package': False, 'role': role})
        for file_id, data in [('selector', b'selected-selector'), ('grant', b'selected-grant'),
                              ('policy', P.canonical(original_policy(self.role, family, cfg['principal'], cfg.get('reader_public_key','fixture-key-'+self.role)))), ('descriptor', b'{}'), ('bridge', b'{}'), ('query', b'{}')]:
            self.put(file_id, file_id + '.json', data, 'protected-input')
        if cfg.get('metadata'):
            value=original_policy(self.role,family,cfg['principal'],'fixture-key'); value['session_control']=None
            self.put('policy','policy.json',P.canonical(value),'protected-input')
        self.put('runtime', 'runtime.bin', b'owned-inert-runtime', 'execution')
        self.put('package_selection','selection.json',b'{}','evidence')
        runtime = {'path': str(self.root / 'runtime.bin'), 'sha256': P.digest(b'owned-inert-runtime'),
                   'size_bytes': len(b'owned-inert-runtime'), 'mode': 0o600, 'kind': 'interpreter', 'destination': 'bin/python'}
        self.put('runtime_manifest', 'dependencies.json', P.canonical({'inputs': [runtime]}), 'evidence')
        row = {'path': 'code/common.py', 'sha256': P.digest((self.root/'code/common.py').read_bytes())}
        self.put('document', 'document.json', P.canonical({'files': [row, row]}), 'evidence')
        document_binding = self.file_binding('document')
        policy = {'schema_version': 'lab-completion-public-source-role-policy/v1', 'authority_effect': 'none',
                  'documents': [{'id': 'current', 'binding': document_binding}],
                  'tables': [{'id': 'current-source', 'document_id': 'current', 'selector': '/files',
                              'row_count': 2, 'role': 'current-source-declaration'}]}
        self.put('cold_policy', 'cold-policy.json', P.canonical(policy), 'evidence')
        private = {'anchor': {'principal_ref': cfg['principal'], 'source_cut': cut,
                    'operation': 'installation.execute', 'profile_binding': profile,
                    'source_binding':{'ref':'fixture-source','sha256':'a'*64},'public_key_b64':'fixture-not-an-issuer',
                    'selector_binding':{'ref':'fixture-selector','sha256':P.digest(b'selected-selector')},
                    'grant_binding':{'ref':'fixture-grant','sha256':P.digest(b'selected-grant')},
                    'selector_locator':{},'grant_locator':{}},
                   'selector_file_id': 'selector', 'grant_file_id': 'grant', 'policy_file_id': 'policy',
                   'bridge_file_id': 'bridge', 'bridge_binding': {'ref': 'fixture-bridge', 'sha256': P.digest(b'{}')},
                   'descriptor_file_id': 'descriptor', 'package_directory': str(self.root),
                   'package_sha256': P.digest(b'{}'), 'package_selection_file_id':'package_selection',
                   'effective_deadline_utc': '2099-01-01T00:00:00Z',
                   'query_raw_file_id': 'query'}
        self.put('private', 'private.json', P.canonical(private), 'protected-input')
        self.selection = {'schema_version': 'lab-protected-startup-selection/v2', 'posture': 'fixture',
                          'family': family, 'role':self.role, 'operation': 'installation.execute', 'principal_ref': cfg['principal'],
                          'repository': str(self.root), 'private_file_id': 'private',
                          'profile_sha256': profile['sha256'], 'source_cut': cut,
                          'runtime':None,
                          'modules': {'schema_version': 'lab-startup-module-selection/v1', 'posture': 'fixture',
                                      'modules': modules, 'closure_file_ids': list(self.files), 'generated_code_sha256': []},
                          'cold': {'policy_file_id': 'cold_policy', 'policy_sha256': P.digest(P.canonical(policy)),
                                   'documents': {'current': 'document'},
                                   'origins': [{'logical_path': 'code/common.py', 'file_id': 'common'}],
                                   'dependencies_file_id': 'runtime_manifest',
                                   'dependencies_sha256': P.digest((self.root/'dependencies.json').read_bytes()),
                                   'runtime_origins': [{'original_row': runtime, 'file_id': 'runtime'}]}}
        self.reseal()
    def put(self, name, rel, raw, kind):
        path = self.root / rel; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw); path.chmod(0o600); self.files[name] = (rel, kind)
    def file_binding(self, name):
        rel, kind = self.files[name]; raw = (self.root/rel).read_bytes()
        return {'kind': kind, 'root_id': 'fixture', 'relative_path': rel,
                'sha256': P.digest(raw), 'size_bytes': len(raw)}
    def reseal(self):
        self.raw = P.canonical(self.selection); self.sha = P.digest(self.raw)
        permission = {'schema_version': 'lab-startup-owned-fixture-permission/v1', 'selection_sha256': self.sha,
                      'revoked': False, 'actual_authority': False, 'cleanup_permitted': True}
        self.put('permission', 'permission.json', P.canonical(permission), 'evidence')
        ancestors = [Path('/')] + [Path('/').joinpath(*self.root.parts[1:i]) for i in range(2, len(self.root.parts)+1)]
        def mount(path):
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
            try:return P.mount_id(fd)
            finally:os.close(fd)
        roots = [{'root_id': 'fixture', 'path': str(self.root), 'ancestors': [P.identity(p.stat()) for p in ancestors],
                  'mount_ids':[mount(p) for p in ancestors]}]
        members = [{'file_id': name, 'binding': self.file_binding(name), 'identity': P.identity((self.root/rel).stat()),
                    'mount_id':mount(self.root/rel)}
                   for name,(rel,kind) in self.files.items()]
        self.inputs = P.HeldInputs(roots, members); self._held.append(self.inputs)
        self.custody = B.FixtureCustody(self.inputs, self.sha, 'permission', self.file_binding('permission'), str(self.root))
    def startup(self): return B.Startup(self.custody, self.raw, self.sha)
    def event_list(self): return self.events.read_text().splitlines() if self.events.exists() else []
    def close(self):
        for value in self._held: value.close()
        for name in tuple(sys.modules):
            if name == self.package or name.startswith(self.package + '.'): del sys.modules[name]
        self.tmp.cleanup()
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
