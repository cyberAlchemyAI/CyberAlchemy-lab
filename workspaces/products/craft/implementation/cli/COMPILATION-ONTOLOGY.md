# Composition ontology input

`domainspec.composition-ontology/v1` is the compiler-owned evidence format for a
`domainspec.project-composition/v1` source. Direct system models and AlchLang
lowering use the same typed contracts and the same validation/generation path.

The shape retains `source`, `nodes`, `references`, `composition_trace` and the
existing optional module-import evidence. `source_format` is explicitly either
`domainspec-json` or `alchlang`. `status` remains `generated-scaffold`,
`ontology_admitted` remains false and `authority_effect` remains `none`.
An authored JSON contract may derive this scaffold without claiming admission.
The source hash binds `source_text`; node locations and dependency evidence bind
that source. All identities, typed contracts, property meanings, integration
bindings and dependency roles must match the compiled composition exactly.
For `domainspec-json`, `source_text` must parse as the exact declarative contract
in the composition; changing that source independently is rejected.

`normalizeCompositionOntology` only adapts the format; it does not validate or
approve the model. `compileProjectComposition` performs the semantic checks.
The legacy `alchlang.derived-ontology/v1` input adapts as `source_format: alchlang`.
Legacy artifacts retain their original bytes. New AlchLang lowering uses the
public adapter and emits the shared schema. Direct JSON compositions emit
`source.json`; AlchLang compositions retain `source.alch`.

`planCompiledProjectBuild` accepts an already validated `CompiledProjectGraph`
and generates from its nodes, relationships and typed closures without project
source I/O. Only unchanged graph objects returned by this process's compiler are
accepted; deserialized, fabricated or edited graphs must be compiled again from
their project sources. The ordinary `planProjectBuild` loads the graph for generation and
checks source currentness afterward. Snapshot planning establishes behavior for
the captured source version; it does not claim that files remain current later.

Equivalent models share behavior and dependencies. Certificates and ontology
artifacts retain source-specific hashes; source changes must change those hashes.
The compiler does not independently parse AlchLang or prove business meaning.

## Project output projection

`domainspec.project-layout/v1` is an opt-in projection of a checked reconciled
whole-project plan. It changes artifact placement and the target language's
module references; it does not reinterpret the compiled graph. TypeScript and
Python receive a single source root with feature-local `domain` and
`application` layers plus shared generated domain support. Rust receives one
Cargo package with the same feature layers and compiler-generated module
wiring.

Projection recomputes artifact hashes, import targets, and module hashes after
path and import rewriting. Its receipt binds the original checked view hash,
the project-layout definition hash, and the complete projected artifact
inventory. Exact verification therefore rejects stale imports, missing files,
extra files, or bytes from another layout. Native compilation remains a
separate stronger verification step.

The existing flat output and `domainspec.application-layout/v1` remain distinct
projections. A project-layout request without a reconciled whole-project
selection fails instead of falling back to a legacy generator.

## Supported boundary

Both source formats remain accepted inputs to the shared composition model.
Neither is retired or silently preferred by this package. Format adaptation is
pure; project validation and the explicitly selected target compiler remain the
semantic authority for generated artifacts. Unsupported carriers or incomplete
bindings fail before output rather than being inferred.
