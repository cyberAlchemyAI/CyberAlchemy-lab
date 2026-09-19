# profile.model-instance-binding-evaluation

Model Instance Binding Evaluation Profile

Exact inputs -> candidate checks -> review evidence -> owner adoption.

Contract: {'artifact_type_ref': 'type.evaluation', 'name': 'Model Instance Binding Evaluation Profile', 'profile_id': 'profile.model-instance-binding-evaluation'}

Bounded pure evaluation of supplied inputs. Results are proposed review outcomes, not gate verdicts or permission. Authentication and actual effects remain outside this profile.

Read parameters.json and the valid/adverse example results before adoption. These are proposed policy settings, not previously approved operational policy. Boolean evidence and gate assertions are not authenticated.

Approval meaning: adopt this exact candidate contract and its stated limits for a named scope. The batch itself authorizes no adoption, publication, deletion, identity verification or runtime cutover.
