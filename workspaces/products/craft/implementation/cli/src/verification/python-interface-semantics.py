"""Native public-boundary replay; no factory validation or member execution."""
import ast
import copy
import hashlib
import importlib
import json
import pathlib
import sys
import types
from unittest.mock import patch


def require(ok, why):
    if not ok: raise ValueError('PYTHON_INTERFACE_SEMANTICS:' + why)


def run(data, predecessor, observer):
    controls, root = data['controls'], pathlib.Path(data['root'])
    selected = lambda r: r['state'] == 'ready' and r.get('adapter') == 'python-interface'
    earlier = {**data, 'controls': {**controls, 'rows': [{**r, 'state': 'not_evaluable'} if selected(r) else r for r in controls['rows']]}}
    result = predecessor(earlier)
    by_selector = {r['selector']: r for r in result['rows']}
    audit_state = {'armed': False, 'effects': []}
    def audit(event, args):
        if audit_state['armed'] and (event in ('open', 'import', 'exec', 'compile') or event.startswith(('os.', 'socket.', 'subprocess.', 'ctypes.'))):
            audit_state['effects'].append(event)
    sys.addaudithook(audit)
    for row in controls['rows']:
        if not selected(row): continue
        m, contract = row['module'], row['contract']
        payload = {'root': data['root'], 'module_root': str(pathlib.PurePosixPath(controls['runtime_dir']).parent),
                   'interfaces': {row['selector']: {'contract': contract, 'source': m['descriptor']['source']}},
                   'model': controls['data_model'], 'graph_sha256': m['descriptor']['graph_sha256'],
                   'field_compilation_sha256': m['descriptor']['field_compilation_sha256']}
        observer(payload, m)
        native = importlib.import_module(m['import_name'])
        require(pathlib.Path(native.__file__).resolve() == (root / m['relative_path']).resolve(), 'module identity')
        Fact = importlib.import_module(controls['runtime_dir'].replace('/', '.') + '.facts')._Fact
        require(native.Interface._is_protocol and native.PublicContracts._is_protocol, 'structural boundary types')
        require(type(native.public_contracts) is types.MappingProxyType and type(native.endpoint_values) is types.MappingProxyType, 'immutable public surface')
        require(facts.thaw(native.descriptor) == m['descriptor'], 'descriptor source binding')
        require(facts.thaw(native.version_policy) == contract['version_policy'], 'version policy binding')
        for boundary in [*native.public_contracts.values(), *(b for endpoint in native.endpoint_values.values() for b in endpoint.values())]:
            require(type(boundary) is native.BoundaryValue and owned.frozen(boundary), 'frozen nominal boundary')
        runtime = operations.Runtime(row['recipes'])
        input_ids = set()
        def collect(v):
            if not isinstance(v, (dict, list)) and type(v) is not tuple: return
            if id(v) in input_ids: return
            input_ids.add(id(v))
            values = dict.values(v) if isinstance(v, dict) else list.__iter__(v) if isinstance(v, list) else iter(v)
            for x in values: collect(x)
        def view(root_value):
            count, active = [0], set()
            def walk(v, depth=0):
                count[0] += 1
                require(count[0] <= 65536 and depth <= 64, 'value capacity')
                if v is None: return ['null']
                if type(v) is bool: return ['boolean', 'true' if v else 'false']
                if type(v) is int: return ['bigint', str(v)]
                if type(v) is str: return ['string', v]
                require(id(v) not in input_ids and id(v) not in active, 'detached acyclic public value')
                active.add(id(v))
                try:
                    if type(v) is tuple: return ['array', [walk(x, depth + 1) for x in v]]
                    require(type(v) is Fact and owned.frozen(v) and type(v.entries) is tuple, 'immutable public fact')
                    require(all(type(p) is tuple and len(p) == 2 and type(p[0]) is str for p in v.entries), 'public field entries')
                    mapping = dict(v.entries)
                    require(len(mapping) == len(v.entries), 'unique public fields')
                    return ['record', [[k, walk(mapping[k], depth + 1)] for k in operations.keys(mapping)]]
                finally: active.remove(id(v))
            return walk(root_value)
        for case in row['cases']:
            mode, values = case['mode'], case['values']
            expected = dict(case['expected'])
            if expected['kind'] == 'value': expected['value'] = json.loads(expected['value'])
            runtime.touches.clear(); input_ids.clear()
            arg = runtime.build({'tag': 'ref', 'value': values[0]}) if mode in ('interface-value', 'interface-version') else None
            collect(arg); before = owned.fingerprint(arg)
            audit_state['effects'].clear(); audit_state['armed'] = True
            try:
                if mode == 'interface-descriptor':
                    descriptor = facts.thaw(native.descriptor)
                    actual = {k: descriptor[k] for k in expected['value']}
                    actual['schema_version'] = 'domainspec.named-interface-descriptor/v1-candidate'
                    observed = {'kind': 'value', 'value': actual}
                elif mode == 'interface-version-descriptor':
                    observed = {'kind': 'value', 'value': {**facts.thaw(native.version_policy), 'definition_sha256': native.descriptor['version_definition_sha256'], 'authority_effect': native.descriptor['authority_effect']}}
                elif mode == 'interface-surface':
                    observed = {'kind': 'value', 'value': {'public': sorted(native.public_contracts), 'endpoints': sorted(native.endpoint_values)}}
                elif mode == 'interface-version':
                    accepted = native.accepts_consumer_version(arg)
                    require(type(accepted) is bool, 'version result type')
                    observed = {'kind': 'value', 'value': accepted}
                else:
                    require(mode == 'interface-value', 'case mode')
                    boundary = native.public_contracts[values[2]] if values[1] == 'public' else native.endpoint_values[values[2]][values[3]]
                    outcomes = []
                    for _ in range(2):
                        try:
                            normalized = boundary.normalize(arg)
                        except TypeError as error:
                            outcome = {'kind': 'error', 'name': 'TypeError', 'message': str(error)}
                            try: boundary.key(arg)
                            except TypeError as key_error: require(str(key_error) == str(error), 'key rejection')
                            else: raise ValueError('PYTHON_INTERFACE_SEMANTICS:key accepted rejected input')
                        else:
                            key = boundary.key(arg)
                            require(type(key) is str and boundary.key(normalized) == key, 'stable normalized key')
                            outcome = {'kind': 'value', 'value': {'normalized': view(normalized), 'key': key}}
                        outcomes.append(outcome)
                    require(outcomes[0] == outcomes[1], 'repeatable boundary')
                    observed = outcomes[0]
            finally: audit_state['armed'] = False
            require(not audit_state['effects'] and not runtime.touches, 'effect or coercion during public normalization')
            require(owned.fingerprint(arg) == before, 'public input mutation')
            require(observed == expected, 'outcome:' + row['selector'] + ':' + case['id'] + ':' + json.dumps({'expected': expected, 'observed': observed}, ensure_ascii=True))
        boundary = next(iter(native.public_contracts.values()))
        binding_controls = [lambda: setattr(boundary, '_protocol', None),
                            lambda: native.public_contracts.__setitem__('__unexpected__', boundary),
                            lambda: native.descriptor.__setitem__('selector', 'forged')]
        for change in binding_controls:
            try: change()
            except (TypeError, AttributeError): pass
            else: raise ValueError('PYTHON_INTERFACE_SEMANTICS:mutable binding')
        provider = root / m['relative_path']
        original = pathlib.Path.read_bytes
        content = original(provider)
        for target in ('normalize', 'accepts_consumer_version'):
            tree = ast.parse(content)
            function = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == target)
            function.body = [ast.Return(value=ast.Constant(value=True if target == 'accepts_consumer_version' else None))]
            ast.fix_missing_locations(tree); compile(tree, '<interface-substitution>', 'exec')
            changed = ast.unparse(tree).encode('utf8')
            require(changed != content, 'effective substitution')
            altered = copy.deepcopy(m); altered['artifact_sha256'] = hashlib.sha256(changed).hexdigest()
            def substituted(file, *args, **kwargs):
                return changed if file == provider else original(file, *args, **kwargs)
            with patch.object(pathlib.Path, 'read_bytes', substituted):
                try: observer(payload, altered)
                except ValueError as error: require('AST:' in str(error), 'substitution rejection cause')
                else: raise ValueError('PYTHON_INTERFACE_SEMANTICS:compiling substitution survived')
        by_selector[row['selector']] = {'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                                       'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': 3, 'compiling_substitutions': 2}
    for file, digest in result['toolchain_files'].items():
        require(hashlib.sha256(pathlib.Path(file).read_bytes()).hexdigest() == digest, 'toolchain changed')
    return {**result, 'rows': [by_selector[r['selector']] for r in controls['rows']]}
