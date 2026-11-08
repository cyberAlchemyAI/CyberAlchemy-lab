"""Pure, provisional Context role constructor. Never runs a generated role."""
from __future__ import annotations

import ast
import hashlib
import json
import secrets
import sys
import types
from pathlib import Path, PurePosixPath

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
ENGINE = REPO / 'implementation/lab-runtime/candidates/runtime-completion-0001'
ORIGIN = REPO / 'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148'
INSTANCE = 'legacy-context-dev-20261020-0003'
FAMILY = PurePosixPath('/tmp/cal-context-construction-20261020-0003/family') / INSTANCE
SNAPSHOT = PurePosixPath('/tmp/cal-context-construction-20261020-0003/snapshot')
DESIGN_SHA = '308c697a2bc850c81b59d7a4b86a4b8cd31c97438d106aabb60362a5d16b890c'
REVIEW_SHA = '2510d7cdaf41c9c55dd1a4633f503aaf065547755e4ee8fff9afd05536cf3bdc'
HELD_SOURCE_SHA = '0d4f3103010e7baa3dc356dcc5ef00faea6255ab86d897f691e2c5a43f800a8d'
CODE_PINS = {
    '__init__.py': '51b5ebb11220f544d54359ab3e92c27d47d92635a9c2f44f9ba9ecceb7a74925',
    'base.py': 'a2ba4ff87d48c03d821d6168204e4efdc75d6d76cd8771b581e3bb29e23eb402',
    'build.py': '072a06b8b93ea301ab433389448c70ddab437c494316cac223d36c2ac46137b3',
    'control.py': '088412f6eb37ab05c1ea86c1f0caf51ea257743585c67ec897df8c0a1a15ea49',
    'generation.py': '1603cd607ab7eb82d1d434ce9e1fd8238985a48595ecad3f303557f4276190fb',
}
HELPER_PINS = {
    'role_stage.py': '8f8235588e2a62c973b25115af5e4b6080a301632db7098be4604d0c47d55fe8',
    'phase_rebind.py': 'e5435311b3021baa2c1c952ac3e8401181283b689aa3e2f4d146c161a5ad7f74',
    'hardener.py': 'b1d11bba6c4df68bf3a4aa69f801cafd5554aebccba8c215510185d9984c7bad',
    'path_contract.py': '9b77ff713c937495f9a5e3fe36d413a45e7185c98de1fed4b8c30b45c108f765',
}


class Refused(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise Refused(reason)


def raw_at(path: Path, expected: str | None = None) -> bytes:
    require(path.is_file() and not path.is_symlink(), f'unselected input type: {path}')
    raw = path.read_bytes()
    if expected is not None:
        require(sha(raw) == expected, f'input changed: {path}')
    return raw


def load_verified_held_source(raw: bytes):
    """Never import a cached held_inputs module or execute unverified bytes."""
    require(type(raw) is bytes and sha(raw) == HELD_SOURCE_SHA,
            'held input source differs before execution')
    name = '_ctx_held_verified_0003_' + secrets.token_hex(16)
    require(name not in sys.modules, 'held input private namespace preloaded')
    module = types.ModuleType(name)
    module.__file__ = str(HERE / 'held_inputs.py')
    module.__package__ = ''
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, 'exec', optimize=0), module.__dict__)
        require(sys.modules.get(name) is module, 'held input private module cache changed')
        return module.HeldPredecessors, module.Refused, module.PIN_PATHS
    except BaseException:
        sys.modules.pop(name, None)
        raise


HeldPredecessors, HeldRefused, HELD_PIN_PATHS = load_verified_held_source(
    raw_at(HERE / 'held_inputs.py', HELD_SOURCE_SHA))


def load_verified_sources(sources: dict[str, bytes]):
    """Verify every helper byte before executing any, then use a private package."""
    require(type(sources) is dict and set(sources) == set(HELPER_PINS) and
            all(type(sources[name]) is bytes and sha(sources[name]) == HELPER_PINS[name]
                for name in HELPER_PINS), 'helper source differs before execution')
    package_name = '_ctx_verified_0003_' + secrets.token_hex(16)
    require(not any(name == package_name or name.startswith(package_name + '.')
                    for name in sys.modules), 'private helper namespace preloaded')
    package = types.ModuleType(package_name)
    package.__path__ = []
    package.__package__ = package_name
    sys.modules[package_name] = package
    modules = {}
    try:
        for stem in ('path_contract', 'hardener', 'role_stage', 'phase_rebind'):
            name = package_name + '.' + stem
            module = types.ModuleType(name)
            module.__file__ = str(ENGINE / 't35_external_v1' / (stem + '.py'))
            module.__package__ = package_name
            sys.modules[name] = module
            code = compile(sources[stem + '.py'], module.__file__, 'exec', optimize=0)
            exec(code, module.__dict__)
            setattr(package, stem, module)
            modules[stem] = module
        require(all(sys.modules.get(package_name + '.' + stem) is module
                    for stem, module in modules.items()), 'verified helper cache changed')
        return modules['role_stage'], modules['phase_rebind']
    except BaseException:
        for name in list(sys.modules):
            if name == package_name or name.startswith(package_name + '.'):
                del sys.modules[name]
        raise


def engine():
    sources = {name: raw_at(ENGINE / 't35_external_v1' / name, HELPER_PINS[name])
               for name in HELPER_PINS}
    return load_verified_sources(sources)


def role_sources() -> dict[str, bytes]:
    role_stage, _ = engine()
    result = {}
    for name in role_stage.ROLE_FILES['context']:
        raw = raw_at(ORIGIN / name, CODE_PINS.get(name, ROLE_PINS.get(name)))
        if name.endswith('.json'):
            json.loads(raw)
        result[name] = raw
    require(len(result) == 11, 'Context role count changed')
    return result


ROLE_PINS = {
    'lifetime-policy.json': '57f1a7b4757b551aefd05ed6efeada6ce416988d14b3aab73a4119f2b3f31e4a',
    'protocols/evidence-contract.json': 'a2a07253f1c19bfe2d789d046516eee770cad3fa674ad7be8b9b523b1aac81d2',
    'protocols/failure-boundary.json': 'eab4efdf032d65b96f62fc7bd1e91c9ff06543099f3bbd37bd8fe24482a77e58',
    'protocols/input-contract.json': '1fca3d81b5977f80ecf27aeb0e99b25bcc4447ab9a92e85c2ba8b2deeb61f4fb',
    'protocols/output-contract.json': '7deef2d3248d8bc59fd419696af33700b427c0b9e71bc99c1aba463fae42823e',
    'protocols/policy.json': 'a0e3b1ec5b719b8291b7ceb6a261612a722e9a72b0cbf569e100ebee9c243fa2',
}


def render() -> dict[str, dict]:
    role_stage, phase_rebind = engine()
    layout = role_stage.DisposableLayout(FAMILY, SNAPSHOT, INSTANCE)
    source = role_sources()
    rows = {}
    for name, old in source.items():
        if name.endswith('.py'):
            new = role_stage.render_python(old, layout=layout, role='context', name=name)
            compile(new, f'<context-{name}>', 'exec', optimize=0)
            compile(new, f'<context-{name}>', 'exec', optimize=2)
            require(role_stage.render_python(old, layout=layout, role='context', name=name) == new,
                    'non-deterministic renderer')
            require('_t35_effect_refused' in new.decode(), 'effect refusal missing')
            require('/home/vlad_/projects/CyberAlchemy-lab' not in new.decode(), 'checkout path retained')
            require(str(SNAPSHOT) in new.decode(), 'selected snapshot missing')
            require(sha(old) == CODE_PINS[name], 'preimage differs')
        elif name == 'protocols/policy.json':
            token = b'"reference": "protocol:R03-legacy-session-fixture-0257-policy/v1"'
            require(old.count(token) == 1, 'policy reference preimage differs')
            new = old.replace(token, ('"reference": "protocol:completion-' + INSTANCE + '-policy/v1"').encode())
            require(new.replace(('"reference": "protocol:completion-' + INSTANCE + '-policy/v1"').encode(), token) == old,
                    'policy inverse differs')
        else:
            new = old
        rows[name] = {'preimage_sha256': sha(old), 'render_sha256': sha(new), 'render_bytes': new,
                      'path': str(FAMILY / 'context' / name)}
    for name in phase_rebind.PHASE_FILES['context']:
        text = rows[name]['render_bytes'].decode()
        counts = {key: text.count(phase_rebind.ORIGINAL_PINS[key])
                  for key in phase_rebind.PHASE_PREDECESSORS['context']}
        expected = {key: phase_rebind.EXPECTED_COUNTS[('context', name)].get(key, 0)
                    for key in phase_rebind.PHASE_PREDECESSORS['context']}
        require(counts == expected, f'predecessor occurrence vector differs: {name}')
        rows[name]['predecessor_occurrences'] = counts
    require(sum(sum(r.get('predecessor_occurrences', {}).values()) for r in rows.values()) == 5,
            'five predecessor selectors required')
    # Structural checks are on AST, not on execution of generated modules.
    base = ast.parse(rows['base.py']['render_bytes'])
    controls = ast.parse(rows['control.py']['render_bytes'])
    names = [n.value for n in ast.walk(base) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    require(any('_cal_' + INSTANCE.replace('-', '_') in n for n in names), 'unique module namespace missing')
    require('mapped' in names and 'api-v25' in names and 'fact-read-scope-v1' in names,
            'selected sibling/API/Fact Scope resolution missing')
    require(any(isinstance(n, ast.Name) and n.id == 'AUTH' for n in ast.walk(controls)),
            'historical authorization selector absent')
    return rows


def project_held_predecessors(rows: dict[str, dict], held: HeldPredecessors) -> dict[str, bytes]:
    """Pure pin projection only from an open, exact same-family FD selection."""
    role_stage, phase_rebind = engine()
    require(set(rows) == set(role_stage.ROLE_FILES['context']) and
            type(held) is HeldPredecessors and not held.closed and held.family == str(FAMILY),
            'exact rendered Context roles and held-FD selection required')
    selected = render()
    require(all(type(rows[name]) is dict and rows[name].get('render_bytes') == selected[name]['render_bytes'] and
                rows[name].get('preimage_sha256') == selected[name]['preimage_sha256']
                for name in selected), 'full selected renderer preimage/postimage differs')
    predecessor = held.bindings
    require(type(predecessor) is dict and set(predecessor) == set(phase_rebind.PHASE_PREDECESSORS['context']),
            'four observed Source/Mapper predecessors required')
    require(len({binding.get('sha256') for binding in predecessor.values() if type(binding) is dict}) == 4 and
            all(type(binding) is dict and binding.get('sha256') not in phase_rebind.ORIGINAL_PINS.values()
                for binding in predecessor.values()), 'duplicate or historical predecessor digest')
    for name, binding in predecessor.items():
        expected_path = str(FAMILY / phase_rebind.PIN_PATHS[name])
        require(type(binding) is dict and set(binding) == {'path', 'sha256'} and
                binding['path'] == expected_path, 'predecessor is outside selected family')
        raw = held.read(binding['path'])
        require(type(raw) is bytes and sha(raw) == binding['sha256'],
                'predecessor is not held at declared digest')
    layout = role_stage.DisposableLayout(FAMILY, SNAPSHOT, INSTANCE)
    originals = {n: rows[n]['render_bytes'] for n in phase_rebind.PHASE_FILES['context']}
    projected = phase_rebind.rebind(layout, 'context', originals, predecessor)
    for name, after in projected.items():
        restored = after.decode()
        before = originals[name].decode()
        for key, binding in predecessor.items():
            old = phase_rebind.ORIGINAL_PINS[key]
            new = binding['sha256']
            require(new != old, 'stale predecessor pin refused')
            require(restored.count(new) == phase_rebind.EXPECTED_COUNTS[('context', name)].get(key, 0),
                    'pin postimage occurrence differs')
            restored = restored.replace(new, old)
        require(restored.encode() == originals[name], 'pin substitution inverse differs')
        before_ast = ast.parse(before)
        restored_ast = ast.parse(restored)
        require(ast.dump(before_ast, include_attributes=False) ==
                ast.dump(restored_ast, include_attributes=False), 'non-pin AST edit')
    return projected


def historical_closure_candidates() -> dict:
    """Audit all historical row names without opening any row body."""
    raw = raw_at(ORIGIN / 'source-manifest.json')
    manifest = json.loads(raw)
    rows = manifest['files']
    require(len(rows) == 1804 and len({row['path'] for row in rows}) == 1804,
            'historical Context manifest cardinality differs')
    require(manifest['environment'] == {'python': '3.14.4', 'jsonschema': '4.23.0',
                                         'cryptography': '46.0.5'}, 'environment selection differs')
    candidates = []
    for row in rows:
        path = PurePosixPath(row['path'])
        require(not path.is_absolute() and '..' not in path.parts and
                isinstance(row['sha256'], str) and len(row['sha256']) == 64,
                'historical dependency row malformed')
        if path.name == 'branch.snapshot':
            state = 'protected_archive_excluded'
        elif 'legacy-session-fixture-' in row['path'] or 'current-participation-' in row['path']:
            state = 'historical_family_requires_projection'
        else:
            state = 'unselected_candidate'
        candidates.append({'path': row['path'], 'historical_sha256': row['sha256'],
                           'state': state})
    return {'historical_manifest_sha256': sha(raw), 'rows': candidates}


def final_source_manifest(*_args, **_kwargs):
    raise Refused('fresh independently reviewed Mapper package and complete Context closure not selected')


def completion_contract() -> dict:
    return {
        'status': 'effect-disabled-contract-only', 'manifest_profile': 'lab-actual-context-delivery-package/v1-candidate',
        'manifest_fields': 8, 'leaves': 40, 'manifest_rows': 39,
        'sequence': ['39-leaf-durable-ACKs', 'RELEASE_PRIVATE-ACK', 'build-result-durable-ACK',
                     'manifest-durable-EMIT-ACK', 'FINISH_SENT_ONCE',
                     'FINISH-mediator-validation-writer-close',
                     'FINISH-ACK', 'checked-client-close', 'original-summary'],
        'finish_calls': 1, 'summary_before_checked_client_close': False,
        'unknown_on_ack_or_close_failure': True, 'effect': 'NOT_RUN',
    }
