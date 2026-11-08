"""Source-bound standing adapter for the API33-derived mixed host recut.

Only the Source-to-accounting join changes. The predecessor's historical
tables, coverage, native witness, reader, graph, and refusal rules are reused.
"""

import hashlib
import json
import os
from pathlib import Path
import stat
import types

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE_PATH = ('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T08/'
             'current-standing-host-integration-preparation-0001/private_content.py')
BASE_SHA = 'be08149f6a1be6a17f61afda725807bc0f72d388626de77c745859796b82fa2b'
ACCOUNT_SHA = 'c8984e89efb1a8a972bac5dbedf4a03a27ac8be77e1633f735a074b33fcd57cb'
STATE_ORIGINAL = 'authority/project-state-transitions/current.json'
STATE_SNAPSHOT = ('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T21/'
                  'paperclip-operator-guide-application-0001/baseline/authority/'
                  'project-state-transitions/current.json')
STATE_SHA = '8ba8ee25ccbf12721d800c693120a3452ddf1ec4427c6fdf1e0655beae31bc12'
GRAPH_RECORDS = frozenset((
    'authority/artifact-types/ontology-node/v2/fixtures/valid/record.json',
    'authority/artifact-types/ontology-cut/v1/fixtures/valid/record.json',
))


def _exact_base():
    path = Path(BASE_PATH)
    fd = os.open(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        leaf = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            if not stat.S_ISREG(os.fstat(leaf).st_mode):
                raise ValueError('predecessor private-content code is nonregular')
            with os.fdopen(os.dup(leaf), 'rb') as source:
                raw = source.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024 or hashlib.sha256(raw).hexdigest() != BASE_SHA:
                raise ValueError('predecessor private-content code differs')
            return raw
        finally:
            os.close(leaf)
    finally:
        os.close(fd)


_base = types.ModuleType('_cal_t08_frozen_private_content')
_base.__file__ = str(ROOT / BASE_PATH)
exec(compile(_exact_base(), _base.__file__, 'exec'), _base.__dict__)

# The two historical locators changed after the frozen port: an installed
# native successor replaced the temporary binary, and the live Project State
# advanced. Both old contents remain exact at independently named origins.
EXTRA_ALTERNATES = {
    _base.NATIVE_ORIGINAL: {
        'path': ('product/lab/release-candidates/v1/interface/'
                 'runtime-dependencies-v2-completion-0001/installations/0001/'
                 'bin/lab-context-native-reader'),
        'sha256': 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'},
    STATE_ORIGINAL: {'path': STATE_SNAPSHOT, 'sha256': STATE_SHA},
}


def check_coverage_current(original, coverage, entries, roots, repository, historical25):
    """Closed 24,503-row mapping with explicit five content-only alternates."""
    _base.need(type(coverage) is list and len(coverage) == len(original),
               'complete unique historical-content coverage required')
    seen = set()
    ids = set()
    alternates = 0
    for row in coverage:
        _base.closed(row, ('original_binding', 'file_id', 'kind', 'standing'))
        binding = _base.byte_pair(row['original_binding'])
        name = binding['path']
        fid = row['file_id']
        allowed_kind = (row['kind'] in _base.ALLOWED_KINDS or
                        (name in GRAPH_RECORDS and row['kind'] == 'governed-record'))
        _base.need(name not in seen and original.get(name) == binding['sha256'] and
                   type(fid) is str and fid not in ids and allowed_kind and fid in entries,
                   'historical coverage omitted/substituted/duplicated')
        seen.add(name)
        ids.add(fid)
        entry = entries[fid]
        _base.need(entry['sha256'] == binding['sha256'] and entry['kind'] == row['kind'],
                   'actual protected byte selection differs')
        physical = _base.selected_physical(entry, roots)
        if name in EXTRA_ALTERNATES:
            alternate = EXTRA_ALTERNATES[name]
            _base.need(row['standing'] == 'content-only-current-locator' and
                       binding['sha256'] == alternate['sha256'] and
                       physical == str(Path(repository) / alternate['path']) and
                       entry['logical_path'] == alternate['path'],
                       'exact successor historical alternate differs')
            if name == _base.NATIVE_ORIGINAL:
                _base.need(entry['size'] == 20243600 and entry['mode'] == 0o755,
                           'installed native alternate size/mode differs')
            alternates += 1
        elif name in _base.CONTENT_ALTERNATES:
            alternate, digest = _base.CONTENT_ALTERNATES[name]
            _base.need(row['standing'] == 'content-only-current-locator' and
                       (name in _base.HISTORICAL25_ALTERNATES or
                        name in _base.RECOVERED_CONTENT_ALTERNATES),
                       'selected content alternate differs')
            _base.need(physical == alternate and binding['sha256'] == digest and
                       entry['logical_path'] ==
                       (str(Path(alternate).relative_to(repository))
                        if Path(alternate).is_relative_to(repository) else alternate),
                       'selected content alternate physical route differs')
            if name in _base.RECOVERED_CONTENT_ALTERNATES:
                selected_root = roots[entry['root_id']]
                _base.need(all(selected_root.get(k) == v for k, v in _base.RECOVERY_ROOT.items()) and
                           all(entry.get(k) == v for k, v in _base.RECOVERY_ENTRIES[name].items()),
                           'recovered private content custody differs')
            alternates += 1
        else:
            _base.need(row['standing'] == 'exact-original-locator' and
                       physical == _base.original_physical(binding, repository) and
                       entry['logical_path'] == name,
                       'exact historical locator differs')
    _base.need(seen == set(original) and alternates == 5 and
               len(historical25) == 25 and set(historical25) <= set(original),
               'complete five-alternate historical mapping differs')
    selected25 = [r for r in coverage if r['original_binding']['path'] in historical25]
    _base.need(sum(r['standing'] == 'exact-original-locator' for r in selected25) == 23 and
               sum(r['standing'] == 'content-only-current-locator' for r in selected25) == 2,
               'current historical25 standing must be exact23 plus two alternates')
    return {'declared_unique_inputs': len(original), 'content_only_alternates': 5,
            'original25_content_only_alternates': 2,
            'separate_recovered_content_resolutions': 3}


_base.check_coverage = check_coverage_current
TABLE_PINS = _base.TABLE_PINS
TABLES = _base.TABLES
CLASSIFICATION = _base.CLASSIFICATION
CLASSIFICATION_TABLES = _base.CLASSIFICATION_TABLES
HISTORICAL25 = _base.HISTORICAL25
byte_pair = _base.byte_pair


class PrivateHistoricalContent(_base.PrivateHistoricalContent):
    """Adapt accounting to the exact signed Source/profile in the scope."""

    def current_standing(self):
        reader = self.reader
        anchor = reader.anchor
        _base.need(self.value['current_source_binding'] == anchor.source_binding and
                   self.value['current_profile_binding'] == anchor.profile_binding,
                   'signed current Source/profile differ from selected private scope')
        source_sha = anchor.source_binding['sha256']
        profile_sha = anchor.profile_binding['sha256']
        account_path = str(Path(anchor.source_binding['ref']).parent / 'INPUT-ACCOUNTING.json')
        source_rows = [r for r in reader.files.values()
                       if r['logical_path'] == anchor.source_binding['ref'] and
                       r['sha256'] == source_sha and r['kind'] == 'source-manifest']
        profile_rows = [r for r in reader.files.values()
                        if r['logical_path'] == anchor.profile_binding['ref'] and
                        r['sha256'] == profile_sha and r['kind'] == 'contract-profile']
        _base.need(len(source_rows) == len(profile_rows) == 1,
                   'one exact current Source and profile entry required')
        source = self.P.parse(reader.read(source_rows[0]['id'], 'source-manifest'))
        profile = self.P.parse(reader.read(profile_rows[0]['id'], 'contract-profile'))
        _base.need('input_accounting' not in source and
                   source['profile_binding'] == {'path': anchor.profile_binding['ref'],
                                                 'sha256': profile_sha},
                   'closed current Source shape/profile differs')
        selection = {'path': account_path, 'sha256': ACCOUNT_SHA}
        _base.need(sum(row == selection for row in source['files']) == 1,
                   'current Source must select exact accounting bytes once')
        selected_profile = {(row['path'], row['sha256']) for row in profile['files']}
        for binding in _base.ACCOUNTING_SOURCE_LINKS.values():
            _base.need((binding['path'], binding['sha256']) in selected_profile and
                       sum(row == binding for row in profile['files']) == 1,
                       'historical accounting4 provenance missing from current profile')
            matches = [r for r in reader.files.values()
                       if r['logical_path'] == binding['path'] and
                       r['sha256'] == binding['sha256']]
            _base.need(len(matches) == 1 and
                       matches[0]['id'] in self._proof_ids('/files', profile_rows[0]['id']),
                       'historical accounting4 provenance not selected as profile proof')
            raw = reader.read(matches[0]['id'], matches[0]['kind'])
            _base.need(hashlib.sha256(raw).hexdigest() == binding['sha256'],
                       'historical accounting4 provenance bytes changed')
        fid = self.value['current_accounting_file_id']
        row = reader.files[fid]
        _base.need(row['logical_path'] == account_path and row['sha256'] == ACCOUNT_SHA and
                   row['kind'] == 'execution-selection' and
                   fid in self._proof_ids('/files', source_rows[0]['id']),
                   'current Source-to-accounting typed proof differs')
        accounting = self.P.parse(reader.read(fid, 'execution-selection'))
        _base.closed(accounting, (*_base.ACCOUNTING_FIXED, 'additions', 'consumption'))
        # API30 refreshed this descriptive claim ceiling while retaining all
        # finite standing/native fields. The exact current file digest pins it.
        _base.need(accounting['claim_ceiling'] ==
                   'Task-local API30 exact input accounting; no Product placement.' and
                   {k: accounting[k] for k in _base.ACCOUNTING_FIXED if k != 'claim_ceiling'} ==
                   {k: v for k, v in _base.ACCOUNTING_FIXED.items() if k != 'claim_ceiling'},
                   'finite current24/1/2 maps or native deployment provenance changed')
        _base.need(type(accounting['additions']) is list and
                   type(accounting['consumption']) is list,
                   'closed current additions/consumption rows required')
        fid = self.value['installed_native_file_id']
        installed = reader.files[fid]
        native = _base.ACCOUNTING_FIXED['native_reprovision']
        expected = native['installed_binding']
        _base.need(installed['kind'] == 'host-dependency' and
                   installed['logical_path'] == expected['path'] and
                   _base.selected_physical(installed, reader.roots) == str(self.root / expected['path']) and
                   installed['sha256'] == expected['sha256'] and
                   installed['size'] == native['size_bytes'] and
                   installed['mode'] == 0o755 and installed['uid'] == os.geteuid() and
                   fid not in {r['file_id'] for r in self.value['coverage']},
                   'independent installed native witness cannot replace historical coverage')
        raw = reader.read(fid, 'host-dependency')
        _base.need(len(raw) == native['size_bytes'] and
                   hashlib.sha256(raw).hexdigest() == expected['sha256'],
                   'independent installed native full bytes differ')
        receipt = native['deployment_terminal_binding']
        receipts = [r for r in reader.files.values() if r['logical_path'] == receipt['path'] and
                    r['sha256'] == receipt['sha256'] and r['kind'] == 'history-proof']
        _base.need(len(receipts) == 1 and
                   hashlib.sha256(reader.read(receipts[0]['id'], 'history-proof')).hexdigest() == receipt['sha256'],
                   'independently selected deployment/source/copy provenance differs')
        return {'schema_version': 'lab-private-current-standing/v3-candidate',
                'restored_originals': 23, 'original_alternates': 2,
                'recovered_contents': 3, 'content_only_total': 5,
                'installed_native_witnesses': 1,
                'installed_native_binding': dict(expected),
                'deployment_terminal_binding': dict(receipt),
                'original_locator_identity_transferred': False,
                'authority_effect': 'none'}

    def verify_content(self):
        result = super().verify_content()
        result['formerly_unavailable_original_locators_now_selected'] = 23
        return result

    def _proof_ids(self, selector, table_id):
        rows = [r for r in self.reader.selector['proof_tables']
                if r['file_id'] == table_id and r['row_selector'] == selector]
        _base.need(len(rows) == 1, 'exact proof table required')
        return set(rows[0]['coverage_file_ids'])
