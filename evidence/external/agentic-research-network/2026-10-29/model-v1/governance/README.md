# Actor and governance model v0.1

Status: **candidate, unadmitted**. This package maps who may propose, inspect, decide, execute and challenge each research and economic action. It creates no actual appointments, delegation, token-voting rights, treasury signature or Lab authority.

- [ACTORS.md](ACTORS.md): actor kinds, roles, obligations and exclusions.
- [GOVERNANCE.md](GOVERNANCE.md): decision lifecycle, separation of duties, emergency and appeal paths.
- [RULES.md](RULES.md): normative candidate rules and their evidence obligations.
- [decision-rights.json](decision-rights.json): machine-readable action-to-role matrix.
- [rules.json](rules.json): versioned rule registry.
- [roles/](roles/): candidate instances of the Lab's existing Role carrier.
- [policy.json](policy.json): candidate instance of the Lab's existing Policy carrier.
- [reference_guard.py](reference_guard.py): non-authorizing decision-rights check for synthetic requests.
- [test_reference_guard.py](test_reference_guard.py): conflict, quorum, role and timing scenarios.
- [validate.py](validate.py): schemas, scope, rule references, role records and matrix consistency checks; also run by the parent package validator.

The parent [economic model](../economics/FORMAL-MODEL.md) supplies task and ledger transitions. An economic transition would require an exact authorized Decision plus matching policy and evidence. The reference guard reports whether a candidate request meets this matrix; it **does not sign, admit or apply** any Decision. The economic simulation's `owner_decision=True` and `agreements_active=True` are fictional test inputs, not governance receipts.

The guard uses synthetic assignments and a project-scope check. It does not verify real identity, cryptographic evidence, revocation, Product-specific authority, contractual rights or actual on-chain execution; those need admitted records and an authorized implementation.

The distinction follows the Lab's admitted meanings: an Actor participates; a Principal is a recognized identity; a Role describes a responsibility and possible authority boundary; a Role Assignment binds a principal to a role; Delegation permits a bounded action; a Policy states rules; a Review evaluates; a Decision selects an outcome. An AI agent session can submit work through its recognized operator or delegated Principal, but its inference output and token balance do not grant decision authority.

The [NIST AI RMF Govern function](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) supports documenting roles, responsibilities, accountability and monitoring. The specific quorums and routes below are our candidate design, not NIST requirements.
