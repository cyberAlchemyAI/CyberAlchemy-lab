# type.context-request

Defines one bounded request against exact Context and policy versions.

Exact inputs -> candidate checks -> review evidence -> owner adoption.

Fields: context_ref, policy_ref, anchor_refs, question, budget

Candidate record and graph consistency only; references bind exact input files, but identity, ownership, observations and execution assertions are not authenticated. No record is admitted or executed.

References are validated inside the bound example graph. Support nodes are explicitly fixture-only and do not prove real runs or grants.

Approval meaning: adopt this exact candidate contract and its stated limits for a named scope. The batch itself authorizes no adoption, publication, deletion, identity verification or runtime cutover.
