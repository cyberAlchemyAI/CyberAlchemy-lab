# Explicit pure computation source examples

These sources retain `profile application-v1` and explicitly select the additive
`alchlang.computation/v1-candidate` capability, the ordered metered semantics and
`full-computation` stage. Use `alchlang computation` with the installed Craft
peer. The generic source compiler rejects this successor syntax.

A source declares its domain, owner, complete resource limits, every record and
pure computation, and `compute main` selecting an actual Calculation. No native
callback or arbitrary program JSON is authored. UInt64 literals are exact decimal
integers; wire inputs and outputs use decimal strings. All String and List types
carry explicit payload/cardinality bounds. Anonymous typed binders are lexical
syntax; Craft checks scope, types, declaration kinds, purity and the call DAG.

Each `<name>.alch.computation.json` companion binds exact source bytes, capability,
semantics and owner, plus the exact kind, meaning and declaration source digest of
every authored declaration. Copy both files together. Missing, stale, extra,
duplicate or wrong-kind companion rows reject. Review the source and its authored
meaning before updating a companion; a digest is a currentness check and cannot
prove that a person approved the interpretation.

| Source | Authored computation | Expected input result |
| --- | --- | --- |
| `summary.alch` | Declared Rule and Mapping, stable filter/map, ordered seeded record fold | `{count:"2",total:"1250"}` |
| `summary-count-two.alch` | Meaningful model edit adding two to count instead of one | `{count:"4",total:"1250"}` with `summary.input.json` |
| `map.alch` | List-returning transformation, preserving duplicates | `["3","3","1"]` |
| `finite-loop.alch` | Positive end-exclusive range, indexed fold, bounded repeat | `"7"` |
| `condition-loop.alch` | Bounded while and bounded until | `"6"` |
| `policy.alch` | Named pure Policy using Rule predicates and Calculation actions, then typed match | `"4"` |
| `state-machine.alch` | Named pure StateMachine producing an immutable proposed outcome | `{intents:["approved"],state:"1",tag:"transition",machine:"approval",branch:"transition:0",reason:"matched"}` |
| `state-machine-match.alch` | Match an explicitly typed immutable Outcome and read its proposed state | `"1"` |
| `sort.alch` | Stable numeric priority followed by explicit natural string sorting | `item2,item10,item1` |
| `sort-lexical.alch` | Same inputs with explicit Unicode scalar lexical label ordering | `item10,item2,item1` |

Run an installed package command with absolute paths:

```sh
alchlang computation check /absolute/path/summary.alch
alchlang computation build /absolute/path/summary.alch --out /absolute/path/generated-summary
alchlang computation verify /absolute/path/summary.alch --out /absolute/path/generated-summary
alchlang computation run /absolute/path/summary.alch --input /absolute/path/summary.input.json
```

For a newly authored source, run the installed helper:

```sh
node node_modules/@cyberalchemy/alchlang/examples/computation/draft-companion.mjs \
  --source "$PWD/work/v1/sum.alch" \
  --out "$PWD/work/v1/sum.alch.computation.candidate.json"
```

The helper writes only a new proposal. It derives source/declaration hashes from
the readable parser, preserving your declared kinds, meanings and owner. Review
the source and proposal, adopt the selected bytes under the companion filename,
then use `alchlang computation check` for full semantic checks. The helper does not
approve meaning or perform Craft type/reference/cycle checking. Keep the helper
at its installed package path even when you copy source/input examples elsewhere.

The [complete creation/edit recipe](../../docs/COMPUTATION.md#create-your-own-calculation)
authors a sum returning 5, changes its body and meaning to return 10, demonstrates
stale source/artifact rejection, and drafts a fresh companion without replacing
earlier sources or outputs. The summary count2→count4 pair remains a retained
example; the same recipe applies to your own summary edit.

The readable expression syntax includes infix arithmetic/comparisons, explicit
checked arithmetic functions, `if`, typed `let`, record constructors, declared
calls, `map`, `filter`, seeded `fold`, `indexed-fold`, `repeat`, `range`,
`for` (the exact indexed-fold normalization), `while-bounded`, `until-bounded`, `sort` with explicit `key(...,direction,mode)`,
`policy` with `case`/`default`, `match`, and `state-machine` with ordered
`transition`/`default`. Strings require `"payload":String[bound]`. Named Policy
and StateMachine declarations own their descriptors, with the same explicit
name in their expression. Outcomes use `Outcome<stateType,intentType,maxIntents>`.
Each outcome retains its machine, selected branch and reason. A matched branch is
`transition:<zero-based-ordinal>` with reason `matched`; a fallback branch is
`otherwise` with `no-match-stay` or `no-match-reject`. These fields distinguish
rejection from an accepted proposal. The intents are data; computing them does
not dispatch operations or effects.

## Open Questions

The [computation guide](../../docs/COMPUTATION.md#open-questions) owns
independent installed-package and generated native qualification, public proof
claims, and any future syntax or semantics successor. These examples establish the authored surface only; proof, deployment
and external provider behavior require their own evidence.
