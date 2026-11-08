"""Verified owned workflow outputs, with an explicit non-admission posture.

A trusted host selects the journal, producing Actor/Work/Run/source, producer
receipts and transaction digest. Wire-supplied headers alone confer nothing.
Permission/current-source/time remain the host guard's responsibility.
"""
import base64
import copy
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
STORE = ROOT / 'implementation/lab-runtime/local-host/t31-durable-output-0001/output_store.py'
STORE_SHA = 'e7c30f149ab0a9be6bfc7c6a4eb9e4bbc54da45fabd1831f8670c66fe54c35c1'
if hashlib.sha256(STORE.read_bytes()).hexdigest() != STORE_SHA:
    raise ValueError('selected durable journal adapter differs')
name = '_t31_owned_selected_output_store'
if name not in sys.modules:
    spec = importlib.util.spec_from_file_location(name, STORE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
S = sys.modules[name]
if Path(S.__file__).resolve() != STORE:
    raise ValueError('selected journal module origin differs')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


@dataclass(frozen=True)
class Selection:
    """Private host inputs; serialized facts cannot mutate through shared dicts."""
    journal_root: str
    config_sha256: str
    source_cut: bytes
    actor: bytes
    work: bytes
    run_ref: str
    scope_ref: str
    producer_receipts: bytes
    producer_material: tuple

    @classmethod
    def from_host(cls, store, *, source_cut, actor, work, run_ref, scope_ref, producer_receipts, producer_paths):
        need(type(store) is S.OutputJournal and bool(producer_receipts),
             'selected owned output journal and actual producer evidence required')
        encode = S.J.K.encoded
        refs = [r['ref'] for r in producer_receipts]
        need(len(refs) == len(set(refs)) and set(producer_paths) == set(refs),
             'exact independent producer receipt original closure required')
        material = tuple((r['ref'], r['sha256'], str(Path(producer_paths[r['ref']]).absolute()))
                         for r in producer_receipts)
        return cls(str(store.root), store.journal.config_sha256, encode(source_cut),
                   encode(actor), encode(work), run_ref, scope_ref, encode(producer_receipts), material)


class OwnedCurrentness:
    def __init__(self, selection, *, host_guard):
        need(type(selection) is Selection and callable(host_guard), 'private selection and live host guard required')
        self.selection = selection
        self.host_guard = host_guard

    def _producer_guard(self):
        selected = self.selection
        receipts = json.loads(selected.producer_receipts)
        need(type(receipts) is list and bool(receipts)
             and all(type(r) is dict and set(r) == {'ref', 'sha256'} for r in receipts),
             'closed original producer receipt bindings required')
        need([(r['ref'], r['sha256']) for r in receipts] ==
             [(ref, sha) for ref, sha, _ in selected.producer_material],
             'selected producer original bindings differ')
        for _, digest, path in selected.producer_material:
            need(S.sha(S.read_owned(Path(path))) == digest,
                 'selected original producer receipt bytes differ')

    def resolve(self, header, *, sequence, transaction_sha256):
        """Return a currentness fact, never an admission or a revived Session."""
        self.host_guard()
        self._producer_guard()
        selected = self.selection
        store = S.OutputJournal(Path(selected.journal_root), selected.config_sha256)
        need(type(sequence) is int and sequence >= 1, 'exact committed transaction sequence required')
        head, _ = store.replay()
        need(sequence <= head['sequence'], 'unheaded output cannot become current')
        raw = S.read_owned(store.root / 'transactions' / f'{sequence:08d}.json')
        need(S.sha(raw) == transaction_sha256, 'independently selected output transaction differs')
        tx = S.O.parse(raw)
        config = store.journal.config
        event = tx['event']
        next_run = S.O.parse(base64.b64decode(tx['next_run_original_base64'], validate=True))
        actor, cut, work, receipts = (json.loads(value) for value in
                                    (selected.actor, selected.source_cut, selected.work, selected.producer_receipts))
        need(config['scope_ref'] == selected.scope_ref == header['scope_ref']
             and config['run_ref'] == selected.run_ref == event['run_ref'] == next_run['run_ref']
             and config['principal_ref'] == actor['principal_ref'], 'owned output scope/Run/Principal differs')
        need(event['actor'] == next_run['actor'] == actor and event['source_cut'] == next_run['source_cut'] == cut
             and next_run['work'] == work and work['scope_ref'] == selected.scope_ref,
             'owned output Actor/Source/Work differs')
        need(tx['producer_receipt_bindings'] == receipts and bool(receipts),
             'independently selected actual producer evidence differs')
        consumed = store.consume(sequence)
        matches = [(h, body) for h, body in consumed if h == header]
        need(len(matches) == 1, 'exact original committed output is unavailable')
        for later in range(sequence + 1, head['sequence'] + 1):
            next_tx = S.O.parse(S.read_owned(store.root / 'transactions' / f'{later:08d}.json'))
            for other in next_tx['output_artifact_refs']:
                need(not (other['identity_ref'] == header['identity_ref']
                          and other['carrier_ref'] == header['carrier_ref'] and other != header),
                     'owned output has a later committed revision')
        self.host_guard()
        self._producer_guard()
        # A guard may discover or cause a change: reopen before returning a fact.
        need(store.replay()[0] == head and store.consume(sequence) == consumed,
             'owned output or selected HEAD changed during guard')
        need(S.sha(S.read_owned(store.root / 'transactions' / f'{sequence:08d}.json')) == transaction_sha256,
             'owned transaction changed during guard')
        return {'artifact': copy.deepcopy(header), 'posture': 'owned-produced-current',
                'semantic_kind': store.carriers.rows[header['carrier_ref']]['semantic_kind'],
                'lineage_binding': {'ref': 'owned-workflow-transaction:' + selected.config_sha256 + ':' + str(sequence),
                                    'sha256': transaction_sha256}}
