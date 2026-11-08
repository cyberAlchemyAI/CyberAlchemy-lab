# All thirteen meta-types: source formation

`model.alch` authors all thirteen backend meta-types with `profile application-v1`.
`bindings.json` and `fixture/` supply the exact meaning and definition inputs.
They are synthetic example records with no production approval or authority effect.

With the core AlchLang and Craft packages installed, run:

```bash
node node_modules/@cyberalchemy/alchlang/examples/meta-types/formation.mjs
```

This invokes the packaged public `lowerApplicationDomain` API and Craft's
`compileProject` API. It checks graph formation for all thirteen types and
rejects collapsed references, wrong declaration targets, undeclared Calculation
inputs and a stale companion. It does not qualify executable Rules or formally
prove the synthetic claim.

The executable `rule-query/run.mjs` example additionally uses ordinary
`alchlang check`, `build` and `verify` commands to qualify a named Rule inside
list and optional Queries, and a read-bound Operation with explicit local
transaction bindings. See `rule-query/README.md`.

Run Craft's packaged `examples/reconciled-commerce/test-meta-types.mjs` for the
separate generated TypeScript behavior journey. Those authored JSON contracts
and its compiler profile are explicit; this formation example does not imply
that every AlchLang profile exposes the same runtime bindings.

## Open Questions

Collection Calculations, additional authoring/runtime combinations and public
distribution are separate completion increments. Local hosting, TDE and EVF
remain deferred.
