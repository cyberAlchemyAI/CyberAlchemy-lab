"""Compiler-owned native syntax/module observer; not a domain behavior proof."""
import ast
import hashlib
import importlib
import json
import pathlib
import sys


def digest(file):
    return hashlib.sha256(pathlib.Path(file).read_bytes()).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def binding_names(target):
    if isinstance(target, ast.Name):
        return [target.id]
    require(isinstance(target, ast.Tuple), 'unsupported assignment target')
    require(all(isinstance(t, ast.Name) for t in target.elts), 'flat assignment required')
    return [t.id for t in target.elts]


def main(data):
    root = pathlib.Path(data['root']).resolve(strict=True)
    rows = data['modules']
    require(len({r['relative_path'] for r in rows}) == len(rows), 'unique modules')
    compiled, observed = [], []
    for row in rows:
        file = root / row['relative_path']
        require(file.resolve(strict=True) == file and file.is_relative_to(root), 'real module path')
        require(digest(file) == row['sha256'], 'source identity')
        text = file.read_text(encoding='utf-8')
        compile(text, row['relative_path'], 'exec', dont_inherit=True, optimize=0)
        compiled.append(row['relative_path'])
        tree = ast.parse(text)
        names, imports = set(), []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    names.update(binding_names(target))
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                names.update(binding_names(node.target))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    local = alias.asname or alias.name.split('.')[0]
                    names.add(local)
                    imports.append((alias.name, True, alias.name, local))
            elif isinstance(node, ast.ImportFrom):
                specifier = '.' * node.level + (node.module or '')
                for alias in node.names:
                    local = alias.asname or alias.name
                    names.add(local)
                    imports.append((specifier, False, alias.name, local))
        expected = [(i['specifier'], i['namespace'], n['name'], n['local'])
                    for i in row['imports'] if i['dependency'] != 'package-initializer'
                    for n in i['names']]
        require(sorted(names) == row['bindings'], 'native binding inventory:' + row['relative_path'])
        require(sorted(imports) == sorted(expected), 'native import inventory:' + row['relative_path'])
        observed.append(row['relative_path'])

    # Load the selected standard dependencies before observing interpreter inputs.
    for name in sorted({i['specifier'] for r in rows for i in r['imports']
                        if i['dependency'] == 'python-standard-library'}):
        importlib.import_module(name)
    tool_files = {str(pathlib.Path(m.__file__).resolve()): digest(m.__file__)
                  for m in list(sys.modules.values()) if getattr(m, '__file__', None)
                  and pathlib.Path(m.__file__).is_file()}
    sys.path.insert(0, str(root))
    imported = []
    for row in rows:
        relative = row['relative_path']
        name = relative[:-3].replace('/', '.')
        if name.endswith('.__init__'):
            name = name[:-9]
        module = importlib.import_module(name)
        require(pathlib.Path(module.__file__).resolve() == root / relative, 'imported module identity')
        for symbol in row['bindings']:
            require(symbol in vars(module), 'missing native binding:' + symbol)
        imported.append(relative)
    require(all(digest(file) == before for file, before in tool_files.items()), 'toolchain changed')
    require(all(digest(root / r['relative_path']) == r['sha256'] for r in rows), 'generated files changed')
    return {'schema_version': 'domainspec.python-native-observation/v1-candidate',
            'compiled_paths': compiled, 'observed_paths': observed, 'imported_paths': imported,
            'python_version': list(sys.version_info[:3]), 'toolchain_files': tool_files,
            'domain_behavior': 'not-performed'}


if __name__ == '__main__':
    print(json.dumps(main(json.load(sys.stdin)), sort_keys=True, separators=(',', ':')))
