"""Exclusive publication successor: read exact managed generations without writes."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, NEW = BASE / 'package-publication-v1', BASE / 'package-publication-v2'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def methods(raw):
    return {n.name: ast.dump(n, include_attributes=False)
            for n in ast.walk(ast.parse(raw))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


READBACK = '''
    def read_package(self, package_binding, request_binding, source_cut, generation_ref):
        """Read one independently selected generation; never create or repair files.

        The host supplies bindings and source cut from its own selected control.
        The caller cannot choose a filesystem path or turn this into upload access.
        The returned source bytes still require target mapping and model validation.
        """
        package_binding, request_binding, source_cut = copy.deepcopy((package_binding, request_binding, source_cut))
        self.transfer.valid('urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding', package_binding)
        self.transfer.valid('urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding', request_binding)
        selection = {'output_root_scope_ref': self.scope_ref, 'package_binding': package_binding,
                     'request_binding': request_binding, 'source_cut': source_cut}
        generation = 'pkg-' + sha(encoded(selection))
        expected_ref = self.scope_ref + '/generations/' + generation
        require(type(generation_ref) is str and generation_ref == expected_ref,
                'independently selected generation differs')
        try:
            with directory(self.root) as root:
                self.guard(root)
                fcntl.flock(root, fcntl.LOCK_SH | fcntl.LOCK_NB)
                names = set(os.listdir(root))
                require(all(name == '.scope.json' or name.startswith('pkg-') and len(name) == 68
                    and all(c in '0123456789abcdef' for c in name[4:]) for name in names), 'unmanaged root entry')
                require(generation in names, 'selected generation absent')
                fd = child_dir(root, generation)
                try:
                    generation_identity = identity(os.fstat(fd))
                    fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
                    require(set(os.listdir(fd)) == {'package.json', 'manifest.json', 'receipt.json', 'PUBLISHED.json'},
                            'pending or unexpected generation contents')
                    original = read(fd, 'package.json', self.max_output_bytes)
                    # Rebuild every expected metadata byte from the authenticated
                    # host's selection and the verified original archive.
                    _, manifest_raw, receipt, receipt_raw, marker = self.describe(
                        original, package_binding, request_binding, source_cut)
                    require(read(fd, 'manifest.json', 1048576) == manifest_raw, 'manifest changed')
                    require(read(fd, 'receipt.json', 1048576) == receipt_raw, 'receipt changed')
                    require(read(fd, 'PUBLISHED.json', 1048576) == marker, 'publication marker changed')
                    # A held descriptor cannot hide a replaced generation name.
                    current = child_dir(root, generation)
                    try:
                        require(identity(os.fstat(current)) == generation_identity, 'current generation identity changed')
                    finally:
                        os.close(current)
                    self.guard(root)
                    return original, copy.deepcopy(receipt)
                finally:
                    os.close(fd)
        except RecoveryRequired:
            raise
        except Exception as error:
            raise RecoveryRequired('selected generation could not be verified; read-only reconciliation required') from error
'''


def main():
    parent = json.loads((OLD / 'source-manifest.json').read_bytes())
    proof = json.loads((OLD / 'receipts/checks-0001.json').read_bytes())
    assert proof['result'] == 'PASS' and proof['real_filesystem_fixture_cases'] == 33
    for row in parent['files'] + parent['input_bindings']:
        assert bind(ROOT / row['path']) == row, row['path']
    NEW.mkdir(exist_ok=False)
    for name in ('publication.py', 'test_publication.py', 'checks.py', 'README.md'):
        with (NEW / name).open('xb') as stream:
            stream.write((OLD / name).read_bytes())
    path = NEW / 'publication.py'
    text = path.read_text()
    start = text.index('    def publish(')
    package_start = text.index('        require(type(package_raw)', start)
    publication_start = text.index('        started = existing_only', start)
    description = text[package_start:publication_start]
    description = description.replace("        generation = 'pkg-' + sha(encoded(selection))\n", "        generation = 'pkg-' + sha(encoded(selection))\n")
    prefix = '''    def describe(self, package_raw, package_binding, request_binding, source_cut):
        """Verify originals and derive the single expected publication record."""
'''
    descriptor = prefix + description + '        return generation, manifest_raw, receipt, receipt_raw, marker\n\n'
    publish = text[start:package_start] + '''        generation, manifest_raw, receipt, receipt_raw, marker = self.describe(
            package_raw, package_binding, request_binding, source_cut)
''' + text[publication_start:]
    path.write_text(text[:start] + descriptor + publish + READBACK)
    assert methods((OLD / 'test_publication.py').read_bytes()) == methods((NEW / 'test_publication.py').read_bytes())
    for path in NEW.glob('*.py'):
        ast.parse(path.read_bytes())
    print(json.dumps({'result': 'AUTHORED', 'retained_predecessor_cases': 33,
                      'public_handlers_added': 0, 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
