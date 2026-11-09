# Candidate governance rules

The exact machine entries are in [rules.json](rules.json). IDs and version are stable within this candidate cut. `pass` on a rule check means only that the specified evidence is present for that check; it does not admit a policy or authorize an effect.

| IDs | Control | Failure route |
| --- | --- | --- |
| ARN-G01–G04 | No implicit authority; recognized and current identity; role separation; conflict disclosure and recusal | Reject unauthorized action or hold unresolved identity/conflict |
| ARN-G05–G09 | Exact evidence cut; pre-reserved budget; independent review; W work criteria; separately adjudicated U research advance | Hold unresolved evidence or reject out-of-budget/invalid award |
| ARN-G10–G11 | Audited revenue and two treasury signers; separate IP/data/consent permission | Reject payout or hold rights use |
| ARN-G12–G14 | Prospective policy changes; narrow emergency pause; independent appeal with compensating correction | Reject retrospective change; pause affected effects; hold disputed payment |
| ARN-G15–G17 | Periodic reconciliation; separate funder instruments; disclosure and challenge standing | Record exception and assign owner before continuation |

Rule application order is: identify exact action and policy version → check recognized Principal and active scoped assignment → reject conflict/common control → check source and economic evidence → satisfy stage quorums and separation → respect challenge/delay windows → prepare the Lab Decision → apply only the declared effect → reconcile ledger and monitor. A later rule version does not reinterpret a past review or change an accepted task's bounty.

The `decision-rights.json` matrix specifies which role may occupy each stage for named actions. It does **not** claim that the role is currently assigned. For routine signed W transfers, the token contract would check ownership, allowance/authorization, nonce and balance under its admitted policy; holders do not convene a governance quorum for every transfer. U cannot be transferred between holders.

Any exception must name the exact rule, Product/Program scope, reason, expiry, affected parties, approving Principals, monitoring and challenge route. A generic “admin override” is absent from this candidate policy.
