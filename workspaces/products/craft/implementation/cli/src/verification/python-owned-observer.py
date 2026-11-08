"""Independent whole-module observer for statically composed owned values.

Recognizes the selected generated grammar from checked source contracts and
factory bindings. No emitter import, dynamic provider execution or invented
runtime interpretation. Behavioral controls are a separate required stage.
"""
import ast
import hashlib
import json
import keyword
import pathlib

SUPPORT = {'values.py': '01e2b483f8ab8d56499557430763ff351c08aac6c5a579a7c3d97a30922daa5d',
           'factories.py': 'b8341588a88c8a8ac75e68bc7d6345ccdae94b78c5c88fbaa096d1cd215d98bc',
           'references.py': 'db9e499517ad7736fec359c33ff644891cf2f9046506136d030b8f1b7288fa3c'}
FACTORY_CONTRACT = '3eeaf28f589af095624fd15b62621d15abc12839aa5b07ccf2f3f6847a452e0f'
PYTHON_PROFILE = '148cd333265563f6591ad6cd1cd7300b2fe0af3b9ec19de84ab4dab3162fbca4'


def require(ok, why):
    if not ok:
        raise ValueError('PYTHON_OWNED_OBSERVER:' + why)


def digest(value):
    # Source JSON has scalar metadata and portable identifiers, not floats.
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    encoded = ''.join(('\\u%04x' % ord(c)) if 0xD800 <= ord(c) <= 0xDFFF else c for c in encoded)
    return hashlib.sha256(encoded.encode()).hexdigest()


def symbol(selector):
    return ''.join(w.capitalize() for w in selector.split(':')[1].split('-'))


def field(name):
    return 'field__' + name if keyword.iskeyword(name) else name


def plain(declaration):
    return declaration['kind'] == 'Enum' and all(v['payload'] is None for v in declaration['contract']['variants'])


def tuple_code(items):
    items = list(items)
    return '(' + ', '.join(items) + (',' if items else '') + ')'


def relative(source, target):
    a, b = pathlib.PurePosixPath(source).parent.parts, pathlib.PurePosixPath(target).with_suffix('').parts
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]: n += 1
    return '.' * (len(a) - n + 1) + '.'.join(b[n:])


def equivalent(source, expected, selector):
    require(ast.dump(ast.parse(source), include_attributes=False) == ast.dump(ast.parse(expected), include_attributes=False), 'owned semantics/effects:' + selector)


class Context:
    def __init__(self, selector, declarations, module_root, contract):
        self.selector, self.declarations, self.module_root, self.contract = selector, declarations, module_root, contract
        self.file, self.name = self.target(selector), symbol(selector)
        self.imports, self.classes = {}, []
        self.ordinal, self.fact_index = 0, 0

    def target(self, selector):
        d = self.declarations[selector]
        feature, node = selector.split(':')
        role = {'Enum': 'enums', 'Entity': 'entities', 'Value Object': 'value_objects'}[d['kind']]
        suffix = '_sum' if d['kind'] == 'Enum' and not plain(d) else ''
        return self.module_root + '/features/' + feature.replace('-', '_') + '/src/domain/' + role + '/' + node.replace('-', '_') + suffix + '.py'

    def shape(self, t, root=False):
        kind = t['kind']
        if kind == 'scalar':
            return {'String': ('STRING', 'str'), 'Bool': ('BOOL', 'bool'), 'UInt64': ('UINT64', 'int')}[t['name']]
        if kind == 'named':
            selector = t['selector']
            if selector not in self.imports:
                d, index = self.declarations[selector], len(self.imports)
                name, stem, native_type = symbol(selector), selector.split(':')[1].replace('-', '_'), '_Type' + str(index)
                target = self.target(selector)
                module = relative(self.file, target)
                if plain(d):
                    name = 'Concept_' + name if keyword.iskeyword(name) else name
                    emit = '_emit' + str(index)
                    code = f'from {module} import {name} as {native_type}, emit_{stem} as {emit}\n'
                    protocol = f'enum_value({native_type}, {emit}, {selector!r}, {digest(d["contract"])!r})'
                else:
                    component = '_Component' + str(index)
                    owned_type = name + ('Case' if d['kind'] == 'Enum' else 'Snapshot')
                    code = f'from {module} import {owned_type} as {native_type}, {name}ValueComponent as {component}\n'
                    protocol, emit = f'owned_value({component})', None
                self.imports[selector] = {'code': code, 'protocol': protocol, 'type': native_type, 'emit': emit, 'path': target}
            d = self.imports[selector]
            return d['protocol'], d['type']
        if kind in ('optional', 'list', 'set'):
            protocol, native = self.shape(t['element'])
            return kind + '_value(' + protocol + ')', '(' + native + ' | None)' if kind == 'optional' else 'tuple[' + native + ', ...]'
        require(kind == 'sum', 'owned type')
        ordinal = self.ordinal
        self.ordinal += 1
        prefix = self.name if root else '_' + self.name + 'Inner' + str(ordinal)
        names, variants = [], []
        for v in sorted(t['variants'], key=lambda v: v['name']):
            payload = self.shape(v['payload']) if v['payload'] is not None else None
            name = prefix + 'Variant' + v['name']
            names.append(name)
            body = '@_dataclass(frozen=True, slots=True, eq=False, init=False, weakref_slot=True)\n'
            body += f'class {name}(_OwnedCase):\n    variant: _Literal[{v["name"]!r}]\n'
            if payload: body += '    payload: ' + payload[1] + '\n'
            body += '    def __init__(self, *args, **kwargs):\n        raise TypeError("SUM_CONSTRUCTION_REQUIRES_COMPONENT")\n'
            self.classes.append(body)
            variants.append(repr(v['name']) + ': (' + name + ', ' + (payload[0] if payload else 'None') + ')')
        identity = self.selector if root else self.selector + '/inline/' + str(ordinal)
        return 'sum_value({' + ', '.join(variants) + '}, ' + repr(identity) + ', ' + repr(self.contract) + ')', ' | '.join(names)

    def fact(self, t, value):
        kind = t['kind']
        if kind == 'scalar': return value
        if kind == 'optional': return f'(None if {value} is None else {self.fact(t["element"], value)})'
        if kind in ('list', 'set'):
            item = 'fact' + str(self.fact_index)
            self.fact_index += 1
            return f'tuple({self.fact(t["element"], item)} for {item} in {value})'
        if kind == 'named':
            d = self.declarations[t['selector']]
            if plain(d):
                self.shape(t)
                return '{"variant": ' + self.imports[t['selector']]['emit'] + '(' + value + ')}'
            if d['kind'] == 'Enum': return self.fact({'kind': 'sum', 'variants': d['contract']['variants']}, value)
            return '{' + ', '.join(repr(p['name']) + ': ' + self.fact(p['type'], value + '.fields.' + field(p['name'])) for p in d['contract']['properties']) + '}'
        require(kind == 'sum', 'fact type')
        branches = []
        for v in t['variants']:
            payload = ', "payload": ' + self.fact(v['payload'], value + '.payload') if v['payload'] is not None else ''
            branches.append('({"variant": ' + repr(v['name']) + payload + '} if ' + value + '.variant == ' + repr(v['name']) + ' else ')
        return '(' + ''.join(branches) + '_invalid_fact()' + ')' * len(branches) + ')'

    def prelude(self):
        code = 'from __future__ import annotations\nfrom dataclasses import dataclass as _dataclass\nfrom typing import Literal as _Literal\n'
        code += 'from ' + relative(self.file, self.module_root + '/runtime/values.py') + ' import OwnedCase as _OwnedCase, STRING, BOOL, UINT64, optional_value, list_value, set_value, sum_value, owned_value, enum_value\n'
        return code + ''.join(v['code'] for v in self.imports.values()) + '\n'.join(self.classes)


def observe(data, enum_observer, rule_observer, overrides=None):
    controls, root = data['controls'], pathlib.Path(data['root'])
    model = controls['data_model'] or {'declarations': [], 'bindings': []}
    declarations = {d['selector']: d for d in model['declarations']}
    module_root = str(pathlib.PurePosixPath(controls['runtime_dir']).parent)
    factories = {m['selector']: m for m in controls['factory_modules']}
    bindings = {b['selector']: b for b in controls['factory_bindings']}
    records = {s for s, d in declarations.items() if d['kind'] != 'Enum'}
    require(set(factories) == records and set(bindings) == records, 'factory coverage')
    rules = {m['selector']: m for m in controls['rule_modules']}
    overrides = overrides or {}
    read = lambda file: overrides[file] if file in overrides else (root / file).read_bytes()
    support = (['values.py'] if any(not plain(d) for d in declarations.values()) else []) + (['factories.py'] if records else []) + (['references.py'] if model['bindings'] else [])
    for file in support:
        require(hashlib.sha256(read(module_root + '/runtime/' + file)).hexdigest() == SUPPORT[file], 'owned support drift:' + file)
    rule_data = {'root': str(root), 'module_root': module_root, 'rule_model': controls['data_model'], 'rule_modules': controls['rule_modules'],
                 'nodes': {s: {'body': {'typed_contract': c}} for s, c in controls['rule_contracts'].items()}}
    # Once per closure member, never once per nested field or validator call.
    for m in rules.values(): rule_observer(rule_data, m, overrides.get(m['relative_path']))
    for selector, d in declarations.items():
        contract = digest(d['contract']) if d['kind'] == 'Enum' else digest({'contract': d['contract'], 'factory_contract': FACTORY_CONTRACT, 'python': PYTHON_PROFILE})
        ctx = Context(selector, declarations, module_root, contract)
        name, stem = ctx.name, selector.split(':')[1].replace('-', '_')
        if plain(d):
            native_name = 'Concept_' + name if keyword.iskeyword(name) else name
            enum_observer(root, {'selector': selector, 'relative_path': ctx.file, 'symbol': native_name, 'callable_stem': stem}, d['contract'], overrides.get(ctx.file))
            continue
        if d['kind'] == 'Enum':
            protocol, native = ctx.shape({'kind': 'sum', 'variants': d['contract']['variants']}, True)
            expected = ctx.prelude() + f'\n{name}Case = {native}\n{name}ValueComponent = {protocol}\ndef create_{stem}(value: dict[str, object]) -> {name}Case:\n    return {name}ValueComponent.normalize(value)\n'
            equivalent(read(ctx.file), expected, selector)
            continue
        m, binding = factories[selector], bindings[selector]
        require(m['relative_path'] == ctx.file and m['callable'] == 'create_' + stem + '_factory' and m['component_contract_sha256'] == contract, 'factory identity:' + selector)
        properties = sorted(d['contract']['properties'], key=lambda p: p['name'])
        shapes = [ctx.shape(p['type']) for p in properties]
        field_bindings = [b for b in model['bindings'] if b['owner'] == selector]
        references = bool(model['bindings'])
        require(('field_bindings' in m) == references and m.get('field_bindings', []) == field_bindings, 'reference metadata:' + selector)
        chosen = sorted({v['rule'] for v in binding['base_validators'] + [v for e in binding['extensions'] for v in e['validators']]})
        imports = ''.join('from ' + relative(ctx.file, rules[s]['relative_path']) + ' import ' + rules[s]['callable'] + ' as _rule' + str(i) + '\n' for i, s in enumerate(chosen))

        def validator(v):
            rule = rules[v['rule']]
            args = sorted(v['arguments'], key=lambda a: a['parameter'])
            fields = []
            for a in args:
                owner, code = d, 'fields'
                segments = a.get('path', [a.get('field')])
                for i, segment in enumerate(segments):
                    p = next(p for p in owner['contract']['properties'] if p['name'] == segment)
                    code += '.' + field(segment)
                    if i + 1 < len(segments):
                        require(p['type']['kind'] == 'named', 'required owned validator path')
                        owner = declarations[p['type']['selector']]
                        require(owner['kind'] != 'Enum', 'record validator path')
                        code += '.fields'
                fields.append(repr(a['parameter']) + ': ' + ctx.fact(p['type'], code))
            artifact = hashlib.sha256((root / rule['relative_path']).read_bytes()).hexdigest()
            receipt = {'rule': v['rule'], 'arguments': args, 'closure_sha256': rule['closure_sha256'], 'artifact_sha256': artifact}
            call = '_rule' + str(chosen.index(v['rule'])) + '({' + ', '.join(fields) + '})'
            return receipt, f'_Validator({v["rule"]!r}, {rule["closure_sha256"]!r}, {artifact!r}, lambda fields: {call})'

        base = [validator(v) for v in binding['base_validators']]
        extensions = [(e['id'], [validator(v) for v in e['validators']]) for e in sorted(binding['extensions'], key=lambda e: e['id'])]
        require(m['base_validators'] == [v[0] for v in base] and m['extensions'] == [{'id': i, 'validators': [v[0] for v in vs]} for i, vs in extensions], 'validator source binding:' + selector)
        require(m['dependencies'] == [{'selector': s, 'path': dep['path']} for s, dep in ctx.imports.items()], 'owned imports:' + selector)
        require(m['fields'] == [{'name': p['name'], 'native_name': field(p['name']), 'type': p['type'], 'identity': p['identity']} for p in properties], 'field metadata:' + selector)
        protocol = 'python.validated-extensible-entity-factory/v1' if d['kind'] == 'Entity' else 'python.owned-value-object-factory/v1'
        require(m['protocol_id'] == protocol, 'factory protocol:' + selector)
        body = ctx.prelude() + '\nfrom ' + relative(ctx.file, module_root + '/runtime/factories.py') + ' import OwnedSnapshot as _OwnedSnapshot, Validator as _Validator, factory_provider as _factory_provider, invalid_fact as _invalid_fact\n' + imports
        if references:
            body += 'from typing import Annotated as _Annotated\nfrom ' + relative(ctx.file, module_root + '/runtime/references.py') + ' import FieldBinding as _FieldBinding\n'
            body += name + 'FieldBindings = ' + tuple_code('_FieldBinding(' + ', '.join(repr(b[k]) for k in ['owner', 'field', 'kind', 'target']) + ', ' + tuple_code([repr(p) for p in b['projection']]) + ')' for b in field_bindings) + '\n'
        body += f'PROTOCOL_ID = {protocol!r}\nCOMPONENT_PROTOCOL_ID = "python.owned-value-component/v1"\nCOMPONENT_CONTRACT_SHA256 = {contract!r}\n'
        body += '@_dataclass(frozen=True, slots=True)\nclass ' + name + 'Fields:\n'
        for p, shape in zip(properties, shapes):
            index = next((i for i, b in enumerate(field_bindings) if b['field'] == p['name']), -1)
            annotation = shape[1] if index < 0 else f'_Annotated[{shape[1]}, {name}FieldBindings[{index}]]'
            body += '    ' + field(p['name']) + ': ' + annotation + '\n'
        body += f'@_dataclass(frozen=True, slots=True, eq=False, init=False, weakref_slot=True)\nclass {name}Snapshot(_OwnedSnapshot):\n    fields: {name}Fields\n    def __init__(self, *args, **kwargs):\n        raise TypeError("SNAPSHOT_CONSTRUCTION_REQUIRES_FACTORY")\n'
        keys = [p for p in properties if d['kind'] != 'Entity' or p['identity']]
        if d['kind'] == 'Entity': body += '    @property\n    def identity(self):\n        return ' + tuple_code(['self.fields.' + field(p['name']) for p in keys]) + '\n'
        specs = [f'({p["name"]!r}, {field(p["name"])!r}, {s[0]}, {p["type"]["kind"] == "optional"!r})' for p, s in zip(properties, shapes)]
        body += f'{m["callable"]}, {name}ValueComponent = _factory_provider({name}Snapshot, {name}Fields, '
        body += tuple_code(specs) + ', ' + tuple_code([repr(p['name']) for p in keys]) + ', ' + repr(selector) + ', COMPONENT_CONTRACT_SHA256, '
        body += tuple_code([v[1] for v in base]) + ', {' + ', '.join(repr(i) + ': ' + tuple_code([v[1] for v in vs]) for i, vs in extensions) + '}, ' + repr(d['kind'] == 'Entity') + ')\n'
        equivalent(read(ctx.file), body, selector)
    return {'selectors': sorted(declarations), 'factories': len(records), 'sums': sum(d['kind'] == 'Enum' and not plain(d) for d in declarations.values()),
            'plain_enums': sum(plain(d) for d in declarations.values()), 'rules': len(rules)}
