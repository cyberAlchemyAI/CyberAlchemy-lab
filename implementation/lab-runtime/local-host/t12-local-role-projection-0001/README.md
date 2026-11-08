# T12 local role input projection check

`test_role_projection.py` executes the selected governance-v5 `recognition` implementation against fresh schema-valid local Principal, Role and RoleAssignment inputs. It binds the exact governance-v5 source/profile and loaded module origin, runs the full source guard, and rechecks the three carrier schemas. It checks current resolution, future-start refusal, ended and elapsed assignment, revoked assignment, wrong scope, wrong assignee/Role, changed recognition, duplicate/missing owner pair, retired Role, inactive Principal, and changed selected bytes. Fourteen tests pass normally and under `-O`.

The selected native `role-assignment/v1` schema allows a finite `period.end` for an `ended` assignment but requires `null` while it is `active`. The elapsed `ended` record refuses at the state check. A still-active assignment with a finite past end is schema-invalid, so the runtime's finite-end expiry branch is not independently exercised. Direct `recognition()` resolves assignment and role identity. `test_checkpoint_join.py` passes its projected key map to the original signed checkpoint kernel: four normal and optimized tests cover a current signature, future and expired owner-key periods, and revoked assignment. Independent follow-up passed this narrow local engineering slice. It does not prove atomic fresh resolution by an authenticated host at checkpoint time, or a canonical human role effect; original T12 acceptance remains open.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -q test_role_projection
PYTHONDONTWRITEBYTECODE=1 python3 -O -B -m unittest -q test_role_projection
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -q test_checkpoint_join
PYTHONDONTWRITEBYTECODE=1 python3 -O -B -m unittest -q test_checkpoint_join
```
