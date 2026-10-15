# Candidate relational formalization

Read [the first-phase result](RESULT.md) for the semantic model, proved statements, checked example, evidence and limitations. F0 consists of P01, P03, P04 and P05. Their `task-acceptance.json` records bind exact outputs, criteria and prerequisite evidence. The subsequent plan tasks remain not started.

The normative contract lives in `specification/l0/`; typed inputs and independent predicates in `core/`; the pure checker and controls in `reference-checker/l0/`; and general proofs, witnesses, replay and review evidence in `proofs/l0/`.

Run `python3 craft/formalization/candidates/relational-theorem-checker/v1/formal/validate_f0.py` from the repository root. The ignored `.toolcache/` contains the verified Lean 4.33.1 runtime for this workspace. The validator supports `--lean /path/to/pinned/bin/lean` and writes evidence only with `--write`. Source or proof changes require replay, semantic review and renewed task acceptance before successors proceed.
