"""Pure 27-role relocation planner; it performs no family write or import."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .path_contract import (OUTPUT_PARENT, SNAPSHOT_PARENT, STORAGE_ROOT, ContractError,
                            bind_output, canonical_path, family_path, instance_name,
                            require, validate_intent)

INTERFACE = PurePosixPath('product/lab/release-candidates/v1/interface')
NATIVE_REL = INTERFACE / 'runtime-dependencies-v2-completion-0001/installations/0004/bin/lab-context-native-reader'
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
OLD_NATIVE = '/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader'
SOURCE_DEPENDENCIES = {
    'custody_loader': {'path': str(INTERFACE / 'custody-correction-v4/loader.py'),
                       'sha256': 'f1953bf08d36756810fbc7ec051df5d0e362f745e84644223b9dddd0df1b13ef'},
    'custody_reader_adapter': {'path': str(INTERFACE / 'custody-correction-v4/reader_adapter.py'),
                               'sha256': '6f57bf712f09ce162754cd5515432b3f99cc2191b021b271987e37bb19cb3f41'},
    'custody_pins': {'path': str(INTERFACE / 'custody-correction-v4/pins.json'),
                     'sha256': 'd59fc534f60483fe9df93b2e6d45431d00ccec082332fbf4e76a91b0944e6b4d'},
    'previous_episode': {'path': str(INTERFACE / 'current-participation-v5/episode-contract.json'),
                         'sha256': '73c2afe2663bb80da0cf3a8f52a2951346a47dcefb34c8c04ac05ca1e37f4559'},
    'previous_period': {'path': str(INTERFACE / 'current-participation-v5/packages/0001/period.json'),
                        'sha256': '5d2184e3491509b6c8d15939d97c6f95609d5277c61bb8f3f0bbd911ff3f35e3'},
}
RUNTIME_BRIDGE = {
    'path': 'implementation/lab-runtime/candidates/runtime-completion-0001/t35_external_v1/runtime_bridge.py',
    'sha256': '9e3c8aebcb735a2302fe911d149f1bde275bbbc4f1e3898dc8d7684349533699',
}
ORIGINS = {
    'source': 'legacy-session-fixture-source-v1-action-0148',
    'reader': 'legacy-session-fixture-reader-v1-action-0148',
    'mapped': 'legacy-session-fixture-mapped-v2-action-0148',
    'context': 'legacy-session-fixture-context-v1-action-0148',
}
ROLE_FILES = {
    'source': ('__init__.py', 'base.py', 'build.py', 'cold.py', 'records.py'),
    'reader': ('__init__.py', 'adapter.py', 'base.py', 'eligibility.py', 'inspection.py', 'model.py', 'reader.py'),
    'mapped': ('__init__.py', 'base.py', 'build.py', 'policy.json'),
    'context': ('__init__.py', 'base.py', 'build.py', 'control.py', 'generation.py',
                'lifetime-policy.json', 'protocols/evidence-contract.json',
                'protocols/failure-boundary.json', 'protocols/input-contract.json',
                'protocols/output-contract.json', 'protocols/policy.json'),
}
if sum(map(len, ROLE_FILES.values())) != 27:
    raise RuntimeError('closed 27-role source map differs')


@dataclass(frozen=True)
class ProductionLayout:
    intent: dict

    def __post_init__(self):
        validate_intent(self.intent)
        object.__setattr__(self, 'intent', copy.deepcopy(self.intent))
        object.__setattr__(self, '_intent_bytes', json.dumps(self.intent, sort_keys=True,
                                                            separators=(',', ':'), allow_nan=False).encode())

    def _unchanged(self):
        require(json.dumps(self.intent, sort_keys=True, separators=(',', ':'),
                           allow_nan=False).encode() == self._intent_bytes,
                'production layout intent mutated after selection')

    @property
    def family(self) -> PurePosixPath:
        self._unchanged()
        return family_path(self.intent['instance'])

    @property
    def snapshot(self) -> PurePosixPath:
        self._unchanged()
        return PurePosixPath(self.intent['input_snapshot_path'])

    @property
    def instance(self) -> str:
        self._unchanged()
        return self.intent['instance']


@dataclass(frozen=True)
class DisposableLayout:
    """Separate synthetic test authority; never accepted by a writer gate."""
    family: PurePosixPath
    snapshot: PurePosixPath
    instance: str

    def __post_init__(self):
        instance_name(self.instance)
        canonical_path(str(self.family), absolute=True)
        canonical_path(str(self.snapshot), absolute=True)
        protected = (STORAGE_ROOT, SNAPSHOT_PARENT)
        require(self.family.name == self.instance and
                all(root != path and root not in path.parents
                    for path in (self.family, self.snapshot) for root in protected) and
                self.family != self.snapshot and self.family not in self.snapshot.parents and
                self.snapshot not in self.family.parents,
                'disposable layout cannot impersonate host authority')


def entries(layout: ProductionLayout | DisposableLayout) -> tuple[tuple[str, str, str], ...]:
    require(type(layout) in (ProductionLayout, DisposableLayout), 'typed layout selection required')
    rows = []
    for role, names in ROLE_FILES.items():
        for name in names:
            source = INTERFACE / ORIGINS[role] / name
            target = layout.family / role / name
            rows.append((role, str(source), str(target)))
    require(len(rows) == 27 and len({row[2] for row in rows}) == 27,
            'closed 27-role output map differs')
    return tuple(rows)


class _PathCalls(ast.NodeTransformer):
    """Rebind only `.relative_to(ROOT).as_posix()` output/input serialization."""

    def visit_Call(self, node):
        self.generic_visit(node)
        if (isinstance(node.func, ast.Attribute) and node.func.attr == 'as_posix' and
                not node.args and not node.keywords and
                isinstance(node.func.value, ast.Call)):
            inner = node.func.value
            if (isinstance(inner.func, ast.Attribute) and inner.func.attr == 'relative_to' and
                    len(inner.args) == 1 and isinstance(inner.args[0], ast.Name) and
                    inner.args[0].id == 'ROOT' and not inner.keywords):
                return ast.copy_location(ast.Call(func=ast.Name(id='_t35_binding_path', ctx=ast.Load()),
                                                  args=[inner.func.value], keywords=[]), node)
        return node


class _EffectCalls(ast.NodeTransformer):
    """Seal direct generated-role writes until the installed T02 gate exists."""

    METHODS = {'mkdir', 'write_bytes', 'write_text', 'unlink', 'touch', 'chmod', 'rmdir'}
    OS_CALLS = {'open', 'mkdir', 'makedirs', 'rename', 'replace', 'unlink', 'remove',
                'rmdir', 'chmod', 'chown', 'link', 'symlink'}

    def visit_Call(self, node):
        self.generic_visit(node)
        target = node.func
        seal = False
        if isinstance(target, ast.Attribute):
            if target.attr in self.METHODS:
                seal = True
            elif isinstance(target.value, ast.Name) and target.value.id == 'os' and target.attr in self.OS_CALLS:
                seal = True
            elif isinstance(target.value, ast.Name) and target.value.id == 'tempfile' and target.attr in ('TemporaryDirectory', 'mkdtemp'):
                seal = True
            elif isinstance(target.value, ast.Name) and target.value.id == 'subprocess' and target.attr in ('run', 'Popen', 'call'):
                seal = True
        if seal:
            return ast.copy_location(ast.Call(func=ast.Name(id='_t35_effect_refused', ctx=ast.Load()),
                                              args=[], keywords=[]), node)
        return node


def _helper(family: PurePosixPath, snapshot: PurePosixPath) -> list[ast.stmt]:
    code = f'''
def _t35_effect_refused():
    raise RuntimeError("Generated T35 role effects require the uninstalled T02 custody gate")

def _t35_binding_path(path):
    from pathlib import Path, PurePosixPath
    value = Path(path)
    name = value.as_posix()
    if not value.is_absolute() or "//" in name or any(x in (".", "..") for x in name.split("/")):
        raise ValueError("noncanonical generated binding path")
    family = PurePosixPath({str(family)!r})
    snapshot = PurePosixPath({str(snapshot)!r})
    item = PurePosixPath(name)
    if family in item.parents:
        return name
    if snapshot in item.parents:
        return str(item.relative_to(snapshot))
    raise ValueError("generated path outside external output and input snapshot")
'''
    return ast.parse(code).body


def render_python(raw: bytes, *, layout: ProductionLayout | DisposableLayout,
                  role: str, name: str) -> bytes:
    """Compile-check a prospective relocated role; no module is executed.

    The historical hardener and live Source/API import bridge are separate
    pending work. This output is a construction probe, not runnable authority.
    """
    require(type(layout) in (ProductionLayout, DisposableLayout) and
            role in ROLE_FILES and name in ROLE_FILES[role] and name.endswith('.py'),
            'closed Python role required')
    text = raw.decode('utf-8')
    prefix = 'completion-' + layout.instance
    text = text.replace('R03-legacy-session-fixture-0257', prefix)
    text = text.replace('_cal_legacy_', '_cal_' + layout.instance.replace('-', '_') + '_legacy_')
    # V8's HERE.parents[8] derives from its repository nesting and is wrong
    # under the external root. Every generated source root is the selected,
    # read-only, narrow input snapshot instead.
    text = text.replace('HERE.parents[5]', f'Path({str(layout.snapshot)!r})')
    text = text.replace('/home/vlad_/projects/CyberAlchemy-lab', str(layout.snapshot))
    text = text.replace(OLD_NATIVE, str(layout.snapshot / NATIVE_REL))
    for selected_role, old in ORIGINS.items():
        text = text.replace("HERE.parent/'" + old, "HERE.parent/'" + selected_role)
        text = text.replace("ADAPTER_ROOT.parent/'" + old,
                            "ADAPTER_ROOT.parent/'" + selected_role)
    # These are selected Source/API dependencies, never output siblings. The
    # narrow read-only snapshot mirrors repository-relative paths.
    for external in ('custody-correction-v4', 'current-participation-v5',
                     'api-v25', 'fact-read-scope-v1'):
        root = "(ROOT/'product/lab/release-candidates/v1/interface')"
        text = text.replace("HERE.parent/'" + external, root + "/'" + external)
        text = text.replace('HERE.parent/"' + external, root + '/"' + external)
    original_entry = 'product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148/reader.py#SelectedReader.open_signed'
    text = text.replace(original_entry,
                        str(layout.family / 'reader' / 'reader.py') + '#SelectedReader.open_signed')
    from .hardener import harden
    text = harden(role, name, text)
    tree = _EffectCalls().visit(_PathCalls().visit(ast.parse(text)))
    ast.fix_missing_locations(tree)
    insert_at = 1 if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str) else 0
    while insert_at < len(tree.body) and isinstance(tree.body[insert_at], ast.ImportFrom) and tree.body[insert_at].module == '__future__':
        insert_at += 1
    tree.body[insert_at:insert_at] = _helper(layout.family, layout.snapshot)
    ast.fix_missing_locations(tree)
    rendered = (ast.unparse(tree) + '\n').encode()
    compile(rendered, f'<T35-{role}-{name}>', 'exec', optimize=0)
    compile(rendered, f'<T35-{role}-{name}>', 'exec', optimize=2)
    require(b'/home/vlad_/projects/CyberAlchemy-lab' not in rendered,
            'generated role retains interactive checkout origin')
    return rendered


def stage_rows(layout: ProductionLayout | DisposableLayout, read_source) -> list[dict]:
    """Read selected template bytes and return exact 27 prospective rows."""
    require(type(layout) in (ProductionLayout, DisposableLayout) and callable(read_source),
            'selected layout and input reader required')
    result = []
    for role, source, target in entries(layout):
        raw = read_source(source)
        require(type(raw) is bytes, 'selected template bytes required')
        name = PurePosixPath(source).name
        if name.endswith('.py'):
            generated = render_python(raw, layout=layout, role=role, name=name)
        elif role == 'context' and source.endswith('/protocols/policy.json'):
            old = b'"reference": "protocol:R03-legacy-session-fixture-0257-policy/v1"'
            require(raw.count(old) == 1, 'exact original Context policy reference required once')
            generated = raw.replace(old, ('"reference": "protocol:completion-' +
                                         layout.instance + '-policy/v1"').encode())
        else:
            generated = raw
        result.append({'role': role, 'input': {'path': source, 'sha256': hashlib.sha256(raw).hexdigest()},
                       'output': bind_output(target, generated, family=layout.family) if type(layout) is ProductionLayout
                       else {'path': target, 'sha256': hashlib.sha256(generated).hexdigest()},
                       'bytes': generated})
    require(len(result) == 27, 'closed stage row count differs')
    return result


def selected_stage_rows(selection) -> list[dict]:
    """Production-planning read path: every template must be in the pinned snapshot."""
    from .held_paths import SelectedSnapshot
    require(type(selection) is SelectedSnapshot, 'Root-pinned read-only snapshot required')
    layout = ProductionLayout(selection.intent)
    native = selection.intent['code_bindings'].get('native_mapper')
    require(native == {'path': str(NATIVE_REL), 'sha256': NATIVE_SHA} and
            selection.rows.get(str(NATIVE_REL)) == native,
            'exact selected native mapper absent from Root input manifest')
    selection.read_executable(native, mode=0o755)
    bridge = selection.intent['code_bindings'].get('runtime_bridge')
    require(bridge == RUNTIME_BRIDGE and selection.rows.get(bridge['path']) == bridge,
            'exact snapshot-selected generated-role bridge absent')
    selection.read(bridge, maximum=256 * 1024)
    for key, binding in SOURCE_DEPENDENCIES.items():
        selected = selection.intent['code_bindings'].get('source_dependency_' + key)
        require(selected == binding and selection.rows.get(binding['path']) == binding,
                'exact selected source dependency absent: ' + key)
        selection.read(binding)
    def selected(name):
        require(name in selection.rows, 'template absent from pinned snapshot selection')
        return selection.read(selection.rows[name])
    return stage_rows(layout, selected)
