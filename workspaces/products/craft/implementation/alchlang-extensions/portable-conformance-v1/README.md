# Portable conformance candidate

One Alch source produces Node and native Rust functions, with DomainSpec-owned typed mappers and generated behavior. This candidate adds an explicit common semantic profile, source-located target rejection, a shipping-option module and reproducible comparison against pricing and shipping oracles.

Read [SPEC.md](SPEC.md) for definitions and ontology scaffolds, [PLAN.md](PLAN.md) for construction/operations separation, and [the language guide](../../alchlang/docs/PORTABLE-CONFORMANCE.md) for semantics and commands.

From this extension, after building DomainSpec and Alch with the repository's pinned Node toolchain:

```sh
node validation/run.mjs /tmp/new-portable-conformance
node validation/verify.mjs
```

This creates two complete target bundles per module and one aggregate report. The checked-in `validation/report.json` records the tested run; `validation/tests.json` records regression commands/results. `candidate.json` binds the candidate's source and evidence inventory. Historical extension candidates remain unchanged.

Controlled provider responses are fixtures. There is no claim of live provider interoperability, whole-language proof, product approval, ontology admission, release or deployment.
