# Local exact decision-state component

`decision_state.py` projects approve, reject, revise and defer over an exact
member body, scope, base digest and bundle digest. Approval is the only local
importable state. Rejection and revision close the old target; deferral permits
a later final choice. A revision records a distinct successor-body digest and
leaves that successor pending. Exact duplicate event IDs are idempotent;
changed bytes, reused IDs with changed choices, and post-final changes refuse.

This is a pure local engineering component for T26. It does not authenticate a
human, verify a RoleAssignment, persist a Decision, issue an authorization or
publish a package. T25 must supply the exact final bundle and T27 must
independently check authority and import effects. Run the focused tests with
`python3 -m unittest discover -s implementation/lab-runtime/local-host/t26-local-decision-state-0001 -p 'test_*.py'`.
