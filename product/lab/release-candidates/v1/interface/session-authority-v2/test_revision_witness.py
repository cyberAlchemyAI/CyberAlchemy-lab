"""Byte/cut/selector witness checks; fixtures do not establish signed authority."""
import copy
from dataclasses import replace
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eligibility as e
sys.path.insert(0, str(HERE.parent / 'session-authority-v1'))
from fixtures import Fixture


class RevisionWitnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory(prefix='cal-R03-revision-witness-');self.addCleanup(self.tmp.cleanup)
        self.fixture = Fixture(Path(self.tmp.name))
        self.row = next(r for r in self.fixture.records if r.artifact['carrier_ref'] == 'cal.artifact-type.product-identity/v2')
        self.schema = next(s for s in self.fixture.schemas if s.carrier_ref == self.row.artifact['carrier_ref'])
        self.ref = {**self.row.artifact, 'version_ref': self.row.artifact['identity_ref'] + '@separate-signed-revision'}
        self.witness = e.SignedRevisionWitness(copy.deepcopy(self.fixture.cut), copy.deepcopy(self.ref), self.row.original,
            e.digest(self.row.original), '', 'original-file-bytes')

    def resolve(self, witness=None, rule='verified-source-revision', raw=None):
        raw = self.row.original if raw is None else raw
        row = e.SourceRecord(self.ref, raw, self.row.posture, self.row.source_ref, witness)
        spec = replace(self.schema, version_binding_rule=rule)
        source = e.ExactSources(self.fixture.sources.scope_ref, self.fixture.cut, [row], [spec], self.fixture.guard)
        return source.get(self.ref)

    def test_default_equality_rule_is_preserved(self):
        with self.assertRaisesRegex(e.EligibilityFault, 'body version differs'):
            self.resolve(rule='body-version-equals-reference')

    def test_explicit_rule_preserves_both_original_version_values(self):
        record, body = self.resolve(self.witness)
        self.assertEqual(body, e.parse(self.row.original))
        self.assertEqual(record.original, self.row.original)
        self.assertNotEqual(record.artifact['version_ref'], record.artifact['identity_ref'] + '@' + body['version'])

    def test_explicit_rule_requires_selected_witness(self):
        with self.assertRaisesRegex(e.EligibilityFault, 'witness required'): self.resolve()

    def test_public_dictionary_is_not_a_trusted_witness(self):
        with self.assertRaisesRegex(e.EligibilityFault, 'witness required'): self.resolve({'artifact': self.ref})

    def test_witness_wrong_cut_rejected(self):
        with self.assertRaisesRegex(e.EligibilityFault, 'cut or reference differs'):
            self.resolve(replace(self.witness, source_cut={**self.fixture.cut, 'commit_sequence': 1}))

    def test_witness_wrong_Artifact_Reference_rejected(self):
        with self.assertRaisesRegex(e.EligibilityFault, 'cut or reference differs'):
            self.resolve(replace(self.witness, artifact_ref={**self.ref, 'version_ref': self.ref['identity_ref'] + '@other'}))

    def test_original_enclosing_hash_rejected_when_changed(self):
        with self.assertRaisesRegex(e.EligibilityFault, 'enclosing original'):
            self.resolve(replace(self.witness, enclosing_sha256='0' * 64))

    def test_whole_file_cannot_substitute_other_equivalent_encoding(self):
        body = e.parse(self.row.original);raw = json.dumps(body).encode()
        with self.assertRaisesRegex(e.EligibilityFault, 'whole-file revision witness differs'):
            self.resolve(replace(self.witness, enclosing_original=raw, enclosing_sha256=e.digest(raw)))

    def test_whole_file_requires_empty_selector(self):
        with self.assertRaisesRegex(e.EligibilityFault, 'whole-file revision witness differs'):
            self.resolve(replace(self.witness, selector='/record'))

    def inherited(self, selector='/proposal/targets/0/record'):
        body = e.parse(self.row.original)
        raw = (json.dumps(body, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()
        enclosing = (json.dumps({'proposal': {'targets': [{'record': body}]}}, indent=3) + '\n').encode()
        self.ref = {**self.ref, 'byte_sha256': e.digest(raw)}
        witness = e.SignedRevisionWitness(copy.deepcopy(self.fixture.cut), copy.deepcopy(self.ref), enclosing,
            e.digest(enclosing), selector, 'inherited-canonical-json-of-selected-original-value')
        return raw, witness

    def test_inherited_legacy_value_has_exact_declared_bytes(self):
        raw, witness = self.inherited()
        record, body = self.resolve(witness, raw=raw)
        self.assertEqual(record.original, raw)
        self.assertEqual(body, e.parse(self.row.original))

    def test_inherited_pointer_cannot_select_other_record(self):
        raw, witness = self.inherited('/proposal/targets/1/record')
        with self.assertRaisesRegex(e.EligibilityFault, 'index unavailable'): self.resolve(witness, raw=raw)

    def test_inherited_pointer_rejects_noncanonical_index(self):
        raw, witness = self.inherited('/proposal/targets/00/record')
        with self.assertRaisesRegex(e.EligibilityFault, 'index unavailable'): self.resolve(witness, raw=raw)

    def test_inherited_pointer_rejects_bad_escape(self):
        raw, witness = self.inherited('/proposal/targets/0/rec~2ord')
        with self.assertRaisesRegex(e.EligibilityFault, 'pointer escape'): self.resolve(witness, raw=raw)

    def test_unknown_witness_encoding_rejected(self):
        with self.assertRaisesRegex(e.EligibilityFault, 'unknown signed revision'):
            self.resolve(replace(self.witness, encoding='semantic-digest'))

    def test_unknown_version_binding_rule_rejected(self):
        with self.assertRaisesRegex(e.EligibilityFault, 'unknown carrier revision'):
            self.resolve(self.witness, rule='infer-from-name')

    def test_witness_cannot_bypass_source_currentness(self):
        self.fixture.bytes[next(iter(self.fixture.bytes))] += b' '
        with self.assertRaisesRegex(e.EligibilityFault, 'no longer current'): self.resolve(self.witness)


if __name__ == '__main__': unittest.main(verbosity=2)
