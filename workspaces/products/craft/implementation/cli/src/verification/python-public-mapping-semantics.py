"""Complete shared source-case replay for native Python public projections."""
import ast
import copy
import hashlib
import importlib
import inspect
import json
import pathlib
import sys
import types
from unittest.mock import patch


def require(ok, why):
    if not ok: raise ValueError('PYTHON_PUBLIC_MAPPING_SEMANTICS:' + why)


def run(data, predecessor, observer):
    controls, root = data['controls'], pathlib.Path(data['root'])
    selected = lambda r: r['state'] == 'ready' and r.get('adapter') == 'python-public-mapping'
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
        m, mapping = row['module'], row['mapping']
        payload = {'root': data['root'], 'module_root': str(pathlib.PurePosixPath(controls['runtime_dir']).parent),
                   'mapping': mapping, 'interfaces': row['interfaces'], 'model': controls['data_model'],
                   'graph_sha256': mapping['certificate']['graph_sha256'], 'field_compilation_sha256': mapping['field_compilation_sha256']}
        # Observe every direct Interface dependency even when its own case budget
        # is pending. No unobserved boundary is admitted through a Mapping import.
        observer(payload, m)
        native = importlib.import_module(m['import_name'])
        require(pathlib.Path(native.__file__).resolve() == (root / m['relative_path']).resolve(), 'module identity')
        call = getattr(native, m['callable'])
        require(owned.frozen(call) and facts.thaw(call.descriptor) == m['descriptor'], 'frozen checked binding')
        require(list(inspect.signature(call).parameters) == ['parameters'] and not inspect.iscoroutinefunction(type(call).__call__), 'native call shape')
        Fact = importlib.import_module(controls['runtime_dir'].replace('/', '.') + '.facts')._Fact
        runtime = operations.Runtime(row['recipes'])
        input_ids = set()
        def collect(v):
            if not isinstance(v, (dict, list)) and type(v) is not tuple: return
            if id(v) in input_ids: return
            input_ids.add(id(v))
            values = dict.values(v) if isinstance(v, dict) else list.__iter__(v) if isinstance(v, list) else iter(v)
            for x in values: collect(x)
        def projection(value):
            count, active = [0], set()
            def entries(v):
                require(type(v) is Fact and owned.frozen(v) and type(v.entries) is tuple, 'frozen projection fact')
                require(all(type(p) is tuple and len(p) == 2 and type(p[0]) is str for p in v.entries), 'projection entries')
                require(len(dict(v.entries)) == len(v.entries), 'unique projected fields')
                return dict(v.entries)
            def walk(v, depth=0):
                count[0] += 1
                require(count[0] <= 65536 and depth <= 64, 'projection capacity')
                if v is None: return ['null']
                if type(v) is bool: return ['boolean', 'true' if v else 'false']
                if type(v) is int: return ['bigint', str(v)]
                if type(v) is str: return ['string', v]
                require(id(v) not in input_ids and id(v) not in active, 'detached acyclic projection')
                active.add(id(v))
                try:
                    if type(v) is tuple: return ['array', [walk(x, depth + 1) for x in v]]
                    mapping = entries(v)
                    return ['record', [[k, walk(mapping[k], depth + 1)] for k in operations.keys(mapping)]]
                finally: active.remove(id(v))
            entries(value)
            require(id(value) not in input_ids, 'detached projection root')
            return [[name, walk(v)] for name, v in value.entries]
        for case in row['cases']:
            expected = dict(case['expected'])
            if expected['kind'] == 'value': expected['value'] = json.loads(expected['value'])
            if case['mode'] == 'mapping-descriptor':
                require(expected == {'kind': 'value', 'value': facts.thaw(call.descriptor)}, 'descriptor outcome')
                continue
            require(case['mode'] == 'mapping', 'case mode')
            runtime.touches.clear(); input_ids.clear()
            arg = runtime.build({'tag': 'ref', 'value': case['values'][0]})
            collect(arg); before = owned.fingerprint(arg)
            outputs = []
            for _ in range(2):
                audit_state['effects'].clear(); audit_state['armed'] = True
                try:
                    try: output = call(arg)
                    except TypeError as error: observed = {'kind': 'error', 'name': 'TypeError', 'message': str(error)}
                    else:
                        observed = {'kind': 'value', 'value': projection(output)}
                        require(all(output is not previous for previous in outputs), 'fresh projection result')
                        outputs.append(output)
                finally: audit_state['armed'] = False
                require(not audit_state['effects'] and not runtime.touches, 'effect or coercion during projection')
                require(owned.fingerprint(arg) == before, 'projection input mutation')
                require(observed == expected, 'outcome:' + row['selector'] + ':' + case['id'] + ':' + json.dumps({'expected': expected, 'observed': observed}, ensure_ascii=True))
        for change in (lambda: setattr(call, 'descriptor', {}), lambda: call.descriptor.__setitem__('selector', 'forged'), lambda: setattr(call, '__call__', None)):
            try: change()
            except (TypeError, AttributeError): pass
            else: raise ValueError('PYTHON_PUBLIC_MAPPING_SEMANTICS:mutable binding')
        original = pathlib.Path.read_bytes
        provider_path, facade_path = root / m['provider_path'], root / m['relative_path']
        provider, facade = original(provider_path), original(facade_path)
        for target in ('provider', 'facade'):
            tree = ast.parse(provider if target == 'provider' else facade)
            name = 'map_values' if target == 'provider' else '__call__'
            function = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
            function.body = [ast.Return(value=ast.Constant(value=None))]
            ast.fix_missing_locations(tree); compile(tree, '<public-mapping-substitution>', 'exec')
            changed = ast.unparse(tree).encode('utf8')
            altered = copy.deepcopy(m)
            changes = {facade_path: changed} if target == 'facade' else {provider_path: changed}
            if target == 'provider':
                old_provider, old_descriptor = altered['descriptor']['provider_sha256'], altered['descriptor']['descriptor_sha256']
                altered['descriptor']['provider_sha256'] = hashlib.sha256(changed).hexdigest()
                altered['descriptor']['descriptor_sha256'] = interface.digest({k: v for k, v in altered['descriptor'].items() if k != 'descriptor_sha256'})
                changes[facade_path] = facade.replace(old_provider.encode(), altered['descriptor']['provider_sha256'].encode()).replace(old_descriptor.encode(), altered['descriptor']['descriptor_sha256'].encode())
                compile(changes[facade_path], '<public-mapping-refreshed-facade>', 'exec')
            def substituted(file, *args, **kwargs):
                return changes[file] if file in changes else original(file, *args, **kwargs)
            with patch.object(pathlib.Path, 'read_bytes', substituted):
                try: observer(payload, altered)
                except ValueError as error: require('AST:' in str(error), 'substitution rejection cause')
                else: raise ValueError('PYTHON_PUBLIC_MAPPING_SEMANTICS:compiling substitution survived')
        by_selector[row['selector']] = {'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                                       'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': 3, 'compiling_substitutions': 2}
    for file, digest in result['toolchain_files'].items():
        require(hashlib.sha256(pathlib.Path(file).read_bytes()).hexdigest() == digest, 'toolchain changed')
    return {**result, 'rows': [by_selector[r['selector']] for r in controls['rows']]}
