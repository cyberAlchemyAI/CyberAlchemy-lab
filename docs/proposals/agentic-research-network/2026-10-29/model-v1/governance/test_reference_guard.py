"""Synthetic decision-rights and separation-of-duties checks."""

import unittest

from reference_guard import Guard


class GovernanceGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = Guard.load()

    @staticmethod
    def assignment(principal, role, *, controller=None, kind="human", end=200000,
                   delegation=None):
        return {"principal_ref": principal, "role_ref": role,
                "scope_ref": "project:arn:research-network-001",
                "state": "active", "valid_from": 0, "valid_until": end,
                "actor_kind": kind, "controller_ref": controller or principal,
                "delegation_ref": delegation}

    def request(self, action_id):
        action = self.guard.actions[action_id]
        assignments = []
        roles = []
        proposer = "principal:proposer"
        roles.append(self.assignment(proposer, action["proposer_roles"][0]))
        stages = {}
        for stage, field in (("reviewers", "reviewer_quorum"),
                             ("approvers", "approver_quorum"),
                             ("executors", "executor_quorum")):
            stages[stage] = []
            for entry in action[field]:
                for index in range(entry["count"]):
                    principal = f"principal:{stage}:{entry['role_ref']}:{index}"
                    stages[stage].append(principal)
                    roles.append(self.assignment(principal, entry["role_ref"]))
        assignments.extend(roles)
        request = {"action_id": action_id,
                   "profile_version": self.guard.profile["version"],
                   "scope_ref": self.guard.profile["project_ref"],
                   "proposer": proposer, **stages,
                   "subject_principal": "principal:subject",
                   "proposed_at": 0, "now": 100000, "effective_at": 100000,
                   "duration_seconds": 3600,
                   "challenge_closed": True,
                   "conflicted_principals": [],
                   "original_decision_principals": [],
                   "evidence": {key: f"fixture:{key}" for key in action["required_evidence"]}}
        assignments.append(self.assignment("principal:subject", "role:arn-miner"))
        return request, assignments

    def test_every_candidate_action_has_a_satisfiable_synthetic_quorum(self):
        for action_id in self.guard.actions:
            with self.subTest(action_id=action_id):
                request, assignments = self.request(action_id)
                result = self.guard.assess(request, assignments)
                self.assertTrue(result.ok, result.reasons)
                self.assertEqual(result.authority_effect, "none")

    def test_miner_or_common_controller_cannot_fill_review_seats(self):
        request, assignments = self.request("work.award")
        assignments.append(self.assignment("principal:subject", "role:arn-evidence-reviewer"))
        request["reviewers"][0] = "principal:subject"
        result = self.guard.assess(request, assignments)
        self.assertIn("subject-in-reviewers", result.reasons)
        request, assignments = self.request("work.award")
        second = request["reviewers"][1]
        for item in assignments:
            if item["principal_ref"] == second:
                item["controller_ref"] = request["reviewers"][0]
        result = self.guard.assess(request, assignments)
        self.assertIn("common-control:reviewers", result.reasons)

    def test_expired_role_missing_evidence_and_open_challenge_refuse_award(self):
        request, assignments = self.request("work.award")
        for item in assignments:
            if item["principal_ref"] == request["approvers"][0]:
                item["valid_until"] = request["now"]
        request["evidence"].pop("budget_reservation")
        request["challenge_closed"] = False
        reasons = self.guard.assess(request, assignments).reasons
        self.assertIn("unassigned-or-expired:approvers", reasons)
        self.assertIn("missing-evidence:budget_reservation", reasons)
        self.assertIn("challenge-open", reasons)

    def test_policy_change_waits_and_cannot_be_retrospective(self):
        request, assignments = self.request("policy.change")
        request["now"] = 100
        request["effective_at"] = 50
        reasons = self.guard.assess(request, assignments).reasons
        self.assertIn("decision-delay-open", reasons)
        self.assertIn("retrospective-effect", reasons)

    def test_stablecoin_payout_needs_two_independent_signers(self):
        request, assignments = self.request("stablecoin.payout")
        request["executors"][1] = request["executors"][0]
        reasons = self.guard.assess(request, assignments).reasons
        self.assertIn("duplicate-executors", reasons)
        request, assignments = self.request("stablecoin.payout")
        for item in assignments:
            if item["principal_ref"] == request["executors"][1]:
                item["controller_ref"] = request["executors"][0]
        reasons = self.guard.assess(request, assignments).reasons
        self.assertIn("common-control:executors", reasons)

    def test_pause_duration_and_appeal_independence(self):
        request, assignments = self.request("emergency.pause")
        request["duration_seconds"] = 90000
        self.assertIn("invalid-pause-duration", self.guard.assess(request, assignments).reasons)
        request, assignments = self.request("appeal.resolve")
        request["original_decision_principals"] = [request["approvers"][0]]
        self.assertIn("original-panel:approvers", self.guard.assess(request, assignments).reasons)

    def test_agent_cannot_occupy_decision_seat_and_needs_delegation(self):
        request, assignments = self.request("work.award")
        reviewer = request["reviewers"][0]
        for item in assignments:
            if item["principal_ref"] == reviewer:
                item["actor_kind"] = "agent-operated"
        self.assertIn("ineligible-actor-kind", self.guard.assess(request, assignments).reasons)
        request, assignments = self.request("mining.task.offer")
        for item in assignments:
            if item["principal_ref"] == request["proposer"]:
                item["actor_kind"] = "agent-operated"
        self.assertIn("missing-agent-delegation", self.guard.assess(request, assignments).reasons)

    def test_conflict_recusal_and_unknown_action(self):
        request, assignments = self.request("research.advance.allocate")
        request["conflicted_principals"] = [request["reviewers"][0]]
        self.assertIn("conflict:reviewers", self.guard.assess(request, assignments).reasons)
        request["action_id"] = "mint-anything"
        self.assertEqual(self.guard.assess(request, assignments).reasons, ("unknown-action",))

    def test_malformed_request_fails_closed(self):
        request, assignments = self.request("work.award")
        request["evidence"] = []
        self.assertEqual(self.guard.assess(request, assignments).reasons,
                         ("invalid-evidence",))
        request, assignments = self.request("work.award")
        request["reviewers"] = [{"principal": "bad"}]
        self.assertIn("invalid-reviewers", self.guard.assess(request, assignments).reasons)
        request, assignments = self.request("work.award")
        request["conflicted_principals"] = "principal:reviewer"
        self.assertEqual(self.guard.assess(request, assignments).reasons,
                         ("invalid-conflict-or-panel-refs",))


if __name__ == "__main__":
    unittest.main()
