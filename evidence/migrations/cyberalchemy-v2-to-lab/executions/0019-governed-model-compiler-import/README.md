# Compile Governed Domain Models imported as a candidate

Explicit domain meaning -> deterministic compilation plan -> traceable outputs and explicit unsupported gaps.

The source already supplies four policy references and three outcome references. Their exact ontology meanings now populate seven acceptance conditions. These cover semantics before templates, no meaning inferred from names, separation of portable core and domain adapters, preservation of authority limits, domain-neutral compilation, traceable output, and bounded extensions.

The import resolves three participant roles, one input contract, three output contracts, and four policy references. Existing declared owners and the explicit Product parent chain are retained. Contract resolution checks source semantic declarations; it is not executable compiler conformance.

[Result and exact mappings](result.json). [Current inventory](inventory.json). **31 imported candidates / 13 blocked / 1 excluded.** Current store: `.local/capability-inventory-import-0019/imports.json`. Learn Ontology Incident remains excluded.

[Verification](verification.json) covers deterministic replay, missing and duplicate requirement rejection, role mismatch rejection, exact queue transition, preserved prior imports, and combined graph validity. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0019-governed-model-compiler-import/verify.py` from the Lab root.

This imports the capability description, not compiler runtime code. No operational authority is granted.

## Open questions

Next blocked declaration: `CA2-CAP-ALCHLANG-EVALUATE-TYPED-BACKEND-CONTRACTS`; its recorded gap is a missing unambiguous Capability owner route. Runtime implementation and conformance remain outside this description import.
