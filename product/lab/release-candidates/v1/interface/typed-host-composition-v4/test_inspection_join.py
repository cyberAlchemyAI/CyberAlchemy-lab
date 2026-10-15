"""Pure exact identity joins; no catalog, permission or owner fixture exists."""
import copy
import unittest
from .selection import SelectionFault, inspection_join


def sample():
    header = {'scope_ref': 'fixture:scope', 'identity_ref': 'relation:fixture',
              'version_ref': 'relation:fixture@2', 'carrier_ref': 'cal.artifact-type.relation-kind/v2',
              'byte_sha256': 'a' * 64}
    domain_a, domain_b = [{'ref': 'fixture:domain:' + label, 'sha256': letter * 64}
                          for label, letter in [('a', 'b'), ('b', 'c')]]
    report = {'ref': 'fixture:noncollapse', 'sha256': 'd' * 64}
    target = {'operation': 'revise', 'artifact': copy.deepcopy(header),
              'predecessor': {**header, 'version_ref': 'relation:fixture@1', 'byte_sha256': 'e' * 64}}
    proposal = {'proposal_ref': 'fixture:proposal', 'scope_ref': header['scope_ref'], 'targets': [target]}
    inspection = {'proposal_ref': proposal['proposal_ref'], 'relation_kind_ref': header['identity_ref'],
                  'successor_version_ref': header['version_ref'], 'predecessor_version_ref': target['predecessor']['version_ref'],
                  'unique_question': 'What exact fixture connection is being declared?', 'axis_ref': 'axis:fixture',
                  'noncollapse_report_binding': report,
                  'allowed_endpoint_pairs': [{'qualifier_schema_binding': domain_a}, {'qualifier_schema_binding': domain_b}]}
    message = {'relation_kind_candidate': copy.deepcopy(header),
               'unique_semantic_question': inspection['unique_question'], 'axis_ref': inspection['axis_ref'],
               'noncollapse_report_binding': copy.deepcopy(report), 'qualifier_domain_bindings': [domain_a, domain_b]}
    return message, proposal, inspection


class InspectionJoinChecks(unittest.TestCase):
    def setUp(self):
        self.message, self.proposal, self.inspection = sample()

    def check(self):
        return inspection_join(self.message, self.proposal, self.inspection)

    def test_01_exact_join_preserves_inputs(self):
        before = copy.deepcopy((self.message, self.proposal, self.inspection))
        self.assertEqual(self.check(), self.proposal['targets'][0])
        self.assertEqual((self.message, self.proposal, self.inspection), before)

    def test_02_new_candidate_has_exact_null_predecessor(self):
        self.proposal['targets'][0].update(operation='admit', predecessor=None)
        self.inspection['predecessor_version_ref'] = None
        self.assertEqual(self.check(), self.proposal['targets'][0])

    def test_03_another_proposal_refused(self):
        self.inspection['proposal_ref'] = 'fixture:other-proposal'
        with self.assertRaisesRegex(SelectionFault, 'another exact proposal'):
            self.check()

    def test_04_another_successor_refused(self):
        self.inspection['successor_version_ref'] = 'fixture:other-successor'
        with self.assertRaisesRegex(SelectionFault, 'successor differs'):
            self.check()

    def test_05_another_predecessor_refused(self):
        self.inspection['predecessor_version_ref'] = 'fixture:other-predecessor'
        with self.assertRaisesRegex(SelectionFault, 'predecessor revision differs'):
            self.check()

    def test_06_undeclared_public_axis_refused(self):
        self.message['relation_kind_candidate']['actual_owner_outcome'] = 'admitted'
        with self.assertRaisesRegex(SelectionFault, 'original exact Relation Kind'):
            self.check()

    def test_07_ambiguous_target_refused(self):
        self.proposal['targets'].append(copy.deepcopy(self.proposal['targets'][0]))
        with self.assertRaisesRegex(SelectionFault, 'missing or ambiguous'):
            self.check()

    def test_08_withdrawal_cannot_be_a_relation_candidate(self):
        self.proposal['targets'][0]['operation'] = 'withdraw'
        with self.assertRaisesRegex(SelectionFault, 'missing or ambiguous'):
            self.check()

    def test_09_another_axis_refused(self):
        self.message['axis_ref'] = 'axis:other'
        with self.assertRaisesRegex(SelectionFault, 'axis or noncollapse'):
            self.check()

    def test_10_another_question_refused(self):
        self.message['unique_semantic_question'] = 'Another question'
        with self.assertRaisesRegex(SelectionFault, 'question, axis'):
            self.check()

    def test_11_changed_noncollapse_binding_refused(self):
        self.message['noncollapse_report_binding']['sha256'] = 'f' * 64
        with self.assertRaisesRegex(SelectionFault, 'noncollapse evidence differs'):
            self.check()

    def test_12_domain_order_refused(self):
        self.message['qualifier_domain_bindings'].reverse()
        with self.assertRaisesRegex(SelectionFault, 'ordered qualifier domain'):
            self.check()

    def test_13_another_relation_identity_refused(self):
        self.inspection['relation_kind_ref'] = 'relation:another'
        with self.assertRaisesRegex(SelectionFault, 'identity or successor'):
            self.check()

    def test_14_target_contract_metadata_preserves_five_public_axes(self):
        self.proposal['targets'][0]['artifact']['candidate_contract_binding'] = {'ref': 'fixture:contract', 'sha256': 'f' * 64}
        self.assertEqual(self.check(), self.proposal['targets'][0])
        self.assertEqual(len(self.message['relation_kind_candidate']), 5)

    def test_15_domain_duplicates_do_not_add_another_axis(self):
        self.inspection['allowed_endpoint_pairs'].append(copy.deepcopy(self.inspection['allowed_endpoint_pairs'][0]))
        self.assertEqual(self.check(), self.proposal['targets'][0])

    def test_16_selected_target_scope_must_equal_proposal(self):
        self.message['relation_kind_candidate']['scope_ref'] = 'fixture:other-scope'
        self.proposal['targets'][0]['artifact']['scope_ref'] = 'fixture:other-scope'
        with self.assertRaisesRegex(SelectionFault, 'scope, identity'):
            self.check()
