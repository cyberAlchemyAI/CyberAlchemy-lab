# Evaluate Typed Backend Contracts imported as a candidate

Caller-supplied typed data -> declared query, calculation, mapping or rule -> deterministic result or rejection.

The capability evaluates supplied values or rows, preserving types and explicit conditions. A policy may select a target; selecting it does not execute or authorize that target. Database access, state mutation and external effects are excluded.

The source lacks a direct owner field. This import explicitly projects the compiler package's semantic owners onto the candidate, corroborated by the declared parent capability's matching owner roles. The exact construction binding verifies the capability source bytes. The Product follows its explicit parent chain.

Nine policies + four declared outcomes -> 13 acceptance conditions. [Result and mappings](result.json). [Current inventory](inventory.json). **32 imported candidates / 12 blocked / 1 excluded.** Store: `.local/capability-inventory-import-0020/imports.json`.

[Verification](verification.json) covers replay, invalid ownership/parent/binding/requirements rejection, queue isolation, prior import preservation and combined graph validation. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0020-typed-backend-import/verify.py` from the Lab root.

This imports the capability description. Compiler/runtime code was not imported or executed; source test evidence was not rerun. No operational authority is granted.

## Open questions

Next blocked declaration: CA2-REF-CAP-CUSTOMER-CREDIT-RELEASE. Source runtime conformance remains separate from this description import.
