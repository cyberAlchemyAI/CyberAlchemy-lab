"""Private byte closure around the original API30 output journal.

This adapter adds durable output bytes and verified later reads. It does not
supply producers, permissions, workflow transitions, or repository admission.
"""
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v30'
PINS = {
    'workflow_output_journal.py': 'e0c358770d847f30c196b389e2b45fd9986a8ecf8dff155a0671f5582b81b010',
    'workflow_output_contracts.py': 'b2bf4e4a7e8e705a1c796b113bf73fd94af0cef831c44ec7ebeb1db434eb7cfa',
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def read_owned(path):
    """Read a bounded, private, single-link regular file without following links."""
    need(not any(p.is_symlink() for p in path.parents), 'linked output ancestor')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        st = os.fstat(fd)
        need(stat.S_ISREG(st.st_mode) and st.st_uid == os.getuid()
             and stat.S_IMODE(st.st_mode) == 0o600 and st.st_nlink == 1
             and st.st_size <= 16 * 1024 * 1024, 'private bounded original output required')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(16 * 1024 * 1024 + 1)
        need(len(raw) == st.st_size, 'output changed during read')
        return raw
    finally:
        os.close(fd)


def selected():
    for name, digest in PINS.items():
        path = API / name
        need(not path.is_symlink() and sha(path.read_bytes()) == digest,
             'selected output journal or contracts changed')
    name = '_t31_durable_api30'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, API / '__init__.py',
                                                       submodule_search_locations=[str(API)])
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return (importlib.import_module(name + '.workflow_output_journal'),
            importlib.import_module(name + '.workflow_output_contracts'))


J, O = selected()
CATALOG = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-transitions-0001/carrier-catalog.json'
CATALOG_SHA = 'b2709686d7a34ff704ebaa4c7dc78c18281208adfe2daeedf84fc5a0705e6ed8'


def original_carriers():
    raw = CATALOG.read_bytes()
    need(sha(raw) == CATALOG_SHA, 'selected carrier catalog changed')
    catalog = O.parse(raw)
    documents = {row[key]: (ROOT / row[key]).read_bytes()
                 for row in catalog['rows'] for key in ('schema_path', 'artifact_path')}
    return O.OriginalCarriers(raw, CATALOG_SHA, documents)


class OutputJournal:
    @classmethod
    def initialize(cls, root, run_raw, scope_ref, principal_ref):
        journal = J.Journal.initialize(root, run_raw, scope_ref, principal_ref)
        (journal.root / 'outputs').mkdir(mode=0o700)
        J.sync(journal.root)
        return cls(root, journal.config_sha256)

    def __init__(self, root, config_sha256):
        self.journal = J.Journal(root, config_sha256)
        self.root = self.journal.root
        folder = self.root / 'outputs'
        need(not folder.is_symlink() and folder.is_dir()
             and folder.stat().st_uid == os.getuid()
             and stat.S_IMODE(folder.stat().st_mode) == 0o700, 'private output folder required')
        self.carriers = original_carriers()
        self.replay()

    def _raw(self, header, transition):
        digest = header['byte_sha256']
        need(type(digest) is str and len(digest) == 64
             and all(c in '0123456789abcdef' for c in digest), 'exact output digest required')
        raw = read_owned(self.root / 'outputs' / digest)
        self.carriers.output(header, raw, scope_ref=self.journal.config['scope_ref'],
                             transition_ref=transition)
        return raw

    def _stage(self, plan, originals):
        headers = plan['event']['output_artifact_refs']
        need(len(headers) == len({h['version_ref'] for h in headers})
             and set(originals) == {h['version_ref'] for h in headers}, 'exact original byte closure required')
        for header in headers:
            raw = originals[header['version_ref']]
            self.carriers.output(header, raw, scope_ref=self.journal.config['scope_ref'],
                                 transition_ref=plan['event']['transition_ref'])
        # Validate all bytes before staging any. Uncommitted orphan blobs are not outputs.
        for header in headers:
            path = self.root / 'outputs' / header['byte_sha256']
            if not path.exists():
                try:
                    J.write_new(path, originals[header['version_ref']])
                except FileExistsError:
                    pass
            need(self._raw(header, plan['event']['transition_ref']) == originals[header['version_ref']],
                 'staged output original differs')

    def apply(self, plan, *, originals, request_binding, host_guard, crash_at=None):
        host_guard()
        self._stage(plan, originals)
        def output_guard():
            host_guard()
            for header in plan['event']['output_artifact_refs']:
                self._raw(header, plan['event']['transition_ref'])
        # Delegate claim, transaction, head, retry and recovery semantics to API30.
        tx = self.journal.apply(plan, request_binding=request_binding,
                                host_guard=output_guard, crash_at=crash_at)
        self.replay()
        return tx

    def replay(self):
        head, raw = self.journal.replay()
        for number in range(1, head['sequence'] + 1):
            tx = O.parse(read_owned(self.root / 'transactions' / f'{number:08d}.json'))
            for header in tx['output_artifact_refs']:
                self._raw(header, tx['event']['transition_ref'])
        return head, raw

    def consume(self, sequence):
        """Read only committed, schema-checked original bytes for a later consumer."""
        head, _ = self.replay()
        need(type(sequence) is int and 1 <= sequence <= head['sequence'], 'committed output sequence required')
        tx = O.parse(read_owned(self.root / 'transactions' / f'{sequence:08d}.json'))
        return [(header, self._raw(header, tx['event']['transition_ref']))
                for header in tx['output_artifact_refs']]

    def recover(self, key, fingerprint, *, host_guard):
        # Check bytes in an unheaded immutable transaction before advancing HEAD.
        claim = O.parse(read_owned(self.root / 'claims' / (self.journal.namespace(key) + '.json')))
        def output_guard():
            host_guard()
            for header in claim['plan']['event']['output_artifact_refs']:
                self._raw(header, claim['plan']['event']['transition_ref'])
        output_guard()
        tx = self.journal.recover(key, fingerprint, host_guard=output_guard)
        self.replay()
        return tx


if __name__ == '__main__':
    store = OutputJournal(Path(sys.argv[1]), sys.argv[2])
    values = store.consume(int(sys.argv[3]))
    print(json.dumps({'result': 'PASS-verified-original-output-consumption',
                      'outputs': [{'version_ref': h['version_ref'], 'sha256': sha(raw),
                                   'byte_size': len(raw), 'carrier_ref': h['carrier_ref']}
                                  for h, raw in values]}, sort_keys=True))
