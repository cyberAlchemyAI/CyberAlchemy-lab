# Technical model and profile-family components

A profile specifies implementation choices using existing Craft meta-types. The
commerce model declares Value Objects, Enums, an Entity, a Rule, a Mapping and a
technical Interface. Its `SelectShopImplementation` Mapping chooses families and
propagates validated configuration. The compiler executes that actual checked
Mapping before deriving a family package requirement.

The new v5 components are additive source implementations. They preserve the
existing profile evaluators, loaders and U0 cell. They are not exported by the
current installed SDK or registered as a ready native profile. EC12 owns that
build and capture.

## Model, graph and selection

`createCommerceTechnicalModelOwnerV5` uses the genuine Core source, semantic
stage, type and pure computation owners. It checks the actual application-selected
technical module and its imported definitions. Its typed technical graph retains
the existing meta-type IDs, original source identities/spans, checked definitions,
typed dependencies and technical Interface constraints.

This is the Core commerce source/type graph, not the legacy Markdown/JSON
`CompiledProjectGraph` brand. No graph handle is restored from a serialized view.
The model token is a private factory entry with genuine current original Core
parents. The source and profile-policy files must remain current.

The same direct native compiler used for business calculations compiles the
technical Mapping. Its real output selects the families. Parameters use exact
UInt64 wire values and the original bounded TablePrefix. No JS implementation of
`SelectShopImplementation`, business callback or handwritten result is substituted.

## Deriving a scoped family

The component API, from the CLI source workspace, follows this sequence:

```ts
const models = createCommerceTechnicalModelOwnerV5();
const families = createCommerceFamilyOwnerV5(models);
const model = await families.checkTechnicalSource(
  applicationRoot, 'profiles/implementation.alch',
);
const family = families.derive(model, {
  tablePrefix: 'shop_', requestBytes: 4096,
  responseBytes: 131072, bodyTimeoutMs: 2000,
}, {
  kind: 'pure-pricing',
  targets: [{module: 'Orders', role: 'Calculation', name: 'PayableTotal'}],
  omitted_capabilities: 'unsupported-not-silently-executed',
});
const requirement = families.inspect(family);
```

The shipped `technical-contract.json` is closed scope/slot policy data. It
connects source Mapping fields to finite primitive contracts. The pure scope
selects BoundedValues and PureComputation. An application scope retains all ten
native requirements, including dependencies on unbuilt adapters. It cannot make
those adapters available. A custom policy cannot add an effectful primitive to a
pure scope; derivation rejects that combination even when the primitive is known.

An isolated source/model variant can add an Enum family alias and bind it to an
existing primitive without changing compiler code. Parameters can also change
within the checked domain. Adding a new primitive, arbitrary template, callback,
transport implementation or SQL executor requires its own implementation; naming
one in a descriptor does not implement it. A source family must remain compatible
with its declared slot and every scope target must exist in checked source.

## Requirement data and resolved descriptor data

`NativeRequirementV5` has a closed requirement tag, primitive ABI, exact required
exports, producer tasks, supplying runtime and effect class. It has no fabricated
artifact hash, native version or availability flag. Auth Foundation preserves its
Node plus fixed captured Rust-child requirement.

`ResolvedNativeAssetDataV5` describes actual-resolution-shaped data separately.
The descriptor validator requires an exact version operand and matching actual
version, concrete identity/closure fields, platform/architecture and required
ABI/exports. Ranges, aliases and unspecified “locked” flags are rejected. Shape
validation alone does not prove that the described bytes exist or came from the
registered producer.

`createDerivedProfileCheckerV5` verifies v5 descriptor data against the exact
original model/family/Mapping/scope/options and optionally captures its physical
file. Its token is **checked descriptor data**, not a `CommerceProfileHandle` or
`CommerceNativeBasisHandle`. Its inspection always reports
`native_resolution_verified: false`. Tests use intentionally synthetic descriptor
data to verify this distinction; those fixtures are not native-resolution evidence.

The original v5 package schema requires resolved dependencies. An unresolved
family therefore remains a separate requirement object and cannot masquerade as
a resolved package by supplying an empty dependency list. Descriptor and policy
files use duplicate-aware bounded Core JSON parsing.

## Open Questions

Actual selected derived-package/native owner resolution, physical producer/tool
closure and public SDK loading remain EC12 and later native tasks. The real
table-prefix variant must eventually change generated SQL and physical tables at
EC34; a requirement or metadata difference does not establish that behavior.
Whole application generation/observations remain the original later plan tasks.
Formal claims remain optional. Local hosting, TDE, EVF and publication stay deferred.
