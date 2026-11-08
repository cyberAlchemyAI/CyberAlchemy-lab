#!/usr/bin/env python3
"""Read-only independent consistency and refusal tests for the T10 worksheet."""

import copy
import hashlib
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[6]
PACKET = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U10-01/decision-preparation-0001.json"
QUALIFICATION = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/initial-qualification-0001.json"
EXPECTED_SHA = "aed58b2dc2e8016dfaa7484b5aeff843ac761ef547276443c9f3f664709b615d"


def check(packet, originals):
    rows = packet["members"]
    if len(rows) != 29 or len(originals) != 29 or packet["prepared_members"] != 29:
        raise ValueError("incomplete inventory")
    if packet["accountably_selected_members"] != 0 or packet["materialization_allowed"] is not False or packet["authority_effect"] != "none":
        raise ValueError("false decision authority")
    refs = set()
    for i, (row, original) in enumerate(zip(rows, originals)):
        if row["index"] != i or row["member_ref"] != original["member_ref"] or row["member_ref"] in refs:
            raise ValueError("missing, reordered or duplicated member")
        refs.add(row["member_ref"])
        if row["original_body_binding"] != original["original_binding"]:
            raise ValueError("original body join changed")
        if row["selected_option"] is not None or row["actual_answering_principal_ref"] is not None or row["accountable_disposition_binding"] is not None or row["runtime_use_allowed"] is not False:
            raise ValueError("unearned disposition")
        if not row["decision_question"] or not row["requested_effect"] or not row["exclusions"] or not row["proposed_owner_roles"]:
            raise ValueError("missing semantic question or boundary")
        if row["original_refusal"] != "GovernedModel/v1 relation_refs.minItems=1; original relation_refs=[]":
            raise ValueError("original refusal obscured")
        for key in ("original_wrapper_binding", "original_disposition_binding", "original_body_binding", "option_evidence_binding"):
            binding = row[key]
            data = (ROOT / binding["path"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != binding["sha256"]:
                raise ValueError("input binding drift")
        wrapper = json.loads((ROOT / row["original_wrapper_binding"]["path"]).read_bytes())
        disposition = json.loads((ROOT / row["original_disposition_binding"]["path"]).read_bytes())
        if wrapper["relation_refs"] != [] or disposition["member_ref"] != row["member_ref"]:
            raise ValueError("original meaning drift")
        if disposition["original_member_semantics"]["requested_effect"] != row["requested_effect"]:
            raise ValueError("semantic effect drift")
        for b in row["candidate_postimage_bindings"]:
            if hashlib.sha256((ROOT / b["path"]).read_bytes()).hexdigest() != b["sha256"]:
                raise ValueError("candidate postimage drift")
        if row["category"] == "new-protocol-review-alternatives":
            if [x["choice_id"] for x in row["review_choices"]] != ["A-prospective-model", "B-retain-bound-control", "C-retain-v1-refusal"]:
                raise ValueError("three original alternatives changed")
            if not row["exact_option_meaning"] or not row["meaning_difference_from_original"]:
                raise ValueError("meaning difference absent")
        elif len(row["review_choices"]) != 2:
            raise ValueError("unreviewed option shape")
    if sum(r["category"] == "new-protocol-review-alternatives" for r in rows) != 11:
        raise ValueError("new option coverage changed")


class PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = PACKET.read_bytes()
        if hashlib.sha256(data).hexdigest() != EXPECTED_SHA:
            raise ValueError("decision packet digest drift")
        cls.packet = json.loads(data)
        cls.originals = json.loads(QUALIFICATION.read_bytes())["original_refusals"]

    def test_actual_complete_inert_worksheet(self):
        check(self.packet, self.originals)

    def test_omission_or_duplicate_is_refused(self):
        for change in (lambda p: p["members"].pop(), lambda p: p["members"].__setitem__(1, p["members"][0])):
            packet = copy.deepcopy(self.packet)
            change(packet)
            with self.assertRaises(ValueError):
                check(packet, self.originals)

    def test_disposition_and_meaning_forgery_is_refused(self):
        for key, value in (("selected_option", "A-prospective-model"), ("runtime_use_allowed", True), ("requested_effect", "admit everything")):
            packet = copy.deepcopy(self.packet)
            packet["members"][14][key] = value
            with self.assertRaises(ValueError):
                check(packet, self.originals)

    def test_original_and_option_byte_drift_is_refused(self):
        for key in ("original_body_binding", "option_evidence_binding", "candidate_postimage_bindings"):
            packet = copy.deepcopy(self.packet)
            binding = packet["members"][24][key]
            if isinstance(binding, list):
                binding = binding[0]
            binding["sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                check(packet, self.originals)


if __name__ == "__main__":
    unittest.main()
