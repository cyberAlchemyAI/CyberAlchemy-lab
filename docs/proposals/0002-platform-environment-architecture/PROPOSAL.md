<!-- Generated from proposal.json. Do not edit this projection directly. -->

# Platform environment architecture

- Proposal: `CAL-PROP-0002`
- Schema: `cyberalchemy-lab-architecture-proposal/v0`
- Status: `draft`
- Decision posture: `not-selected`
- Authority effect: `none`
- Artifact type: `candidate:architecture-proposal/v0` (`candidate-unadmitted`)

> This is a non-effectful architecture candidate. It does not authorize implementation, installation, migration, publication, release, or deployment.

## Evidence

- `domainspec-core:toolchains/node-typescript/toolchain.json` — `observed-pinning-and-containerization-precedent`
- `domainspec-core:.arcanum/runtime/config.json` — `observed-host-adapter-and-profile-precedent`
- `domainspec-core:cyberAlchemy-v2/implementation/ontology-runtime/profile.json` — `observed-runtime-profile-precedent-only`
- `domainspec-core:projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json` — `observed-portable-base-profile-precedent`
- `domainspec-core:projects/domainspec-v2/impl/system-integration/profiles/provider-neutral-v1/profile.json` — `observed-provider-neutral-profile-precedent`

## Decision Question

How should CyberAlchemy Lab define, resolve, install, activate, and verify languages, toolchains, runtimes, tools, host adapters, and environments without relying on mutable global state or confusing semantic profiles with installed binaries?

## Recommendation

Add a platform plane with five canonical axes: languages, runtimes, tools, profiles, and locks. Keep versioned declarations in Git, materialize content-addressed local state under .cyberalchemy, project host-specific generated surfaces to their native paths, and produce exact installation and activation receipts.

## Semantic Separation

- Language semantics are not a compiler, interpreter, package manager, or execution runtime.
- A language is declared and activated; a toolchain resolves or installs the compilers, interpreters, package managers, and supporting tools that realize it.
- A runtime supplies an execution substrate such as a native process, container, browser, or agent host.
- A tool is an executable capability with exact source, build, distribution, dependency, and invocation contracts.
- A profile composes policy and references; it does not itself install bytes.
- A lock resolves every moving reference to an exact version and digest.
- An environment profile is the single activation entry point that composes language, toolchain, runtime, host, resource, network, and filesystem policies.

## Platform Tree

```text
CyberAlchemy-lab/
├── platform/
│   ├── languages/
│   │   ├── portable/v1/
│   │   │   ├── language.json
│   │   │   └── LANGUAGE.md
│   │   ├── typescript/v1/
│   │   ├── python/v1/
│   │   ├── rust/v1/
│   │   └── lean/v1/
│   ├── runtimes/
│   │   ├── native-process/v1/
│   │   ├── container/v1/
│   │   ├── node-process/v1/
│   │   ├── python-process/v1/
│   │   ├── browser/v1/
│   │   └── agent-host/
│   │       ├── codex/v1/
│   │       ├── claude/v1/
│   │       └── copilot/v1/
│   ├── tools/
│   │   ├── artifact-generator/v1/
│   │   ├── artifact-validator/v1/
│   │   ├── craft-compiler/v1/
│   │   ├── lean/v1/
│   │   ├── lake/v1/
│   │   ├── profile-resolver/v1/
│   │   └── installer/v1/
│   ├── profiles/
│   │   ├── languages/
│   │   ├── toolchains/
│   │   │   └── lean-meta-types-v1/v1/
│   │   ├── runtimes/
│   │   ├── hosts/
│   │   └── environments/
│   │       └── meta-type-formalization-v1/v1/
│   ├── locks/
│   │   ├── development.lock.json
│   │   ├── ci.lock.json
│   │   ├── release.lock.json
│   │   └── meta-type-formalization-v1.lock.json
│   └── schemas/
│       ├── language.schema.json
│       ├── runtime.schema.json
│       ├── tool.schema.json
│       ├── profile.schema.json
│       ├── environment.schema.json
│       └── installation-receipt.schema.json
├── evidence/
│   └── receipts/
│       ├── installations/
│       ├── toolchains/
│       ├── runtimes/
│       └── profiles/
└── .cyberalchemy/                 # generated local state; ignored by Git
    ├── store/
    │   ├── tools/
    │   └── runtimes/
    ├── active/
    │   ├── languages/
    │   ├── toolchains/
    │   ├── runtimes/
    │   ├── hosts/
    │   └── environment.json
    ├── bin/
    ├── state/
    ├── cache/
    └── tmp/
```

## Canonical To Materialized Paths

- Language declaration: platform/languages/<language-id>/v1/language.json; generated view: LANGUAGE.md; active binding: .cyberalchemy/active/languages/<language-id>.json.
- Language profile: platform/profiles/languages/<profile-id>/v1/profile.json.
- Tool declaration: platform/tools/<tool-id>/v1/tool.json; optional owned source: platform/tools/<tool-id>/v1/src/; installed bytes: .cyberalchemy/store/tools/<tool-id>/<content-digest>/; executable projection: .cyberalchemy/bin/.
- Toolchain profile: platform/profiles/toolchains/<profile-id>/v1/profile.json; active binding: .cyberalchemy/active/toolchains/<profile-id>.json.
- Runtime declaration: platform/runtimes/<runtime-id>/v1/runtime.json; materialized bytes: .cyberalchemy/store/runtimes/<runtime-id>/<content-digest>/.
- Runtime profile: platform/profiles/runtimes/<profile-id>/v1/profile.json; active binding: .cyberalchemy/active/runtimes/<profile-id>.json.
- Host profile: platform/profiles/hosts/<host-id>/v1/profile.json; generated host surfaces are projected only to the host's native repository paths.
- Environment profile: platform/profiles/environments/<environment-id>/v1/profile.json; activation record: .cyberalchemy/active/environment.json.
- Resolved lock: platform/locks/<environment>.lock.json.
- Installation receipt: evidence/receipts/installations/<run-id>.json.

## Host Projection Paths

- .agents/skills/ for repository-local Codex skill projections.
- .claude/skills/ for optional Claude skill projections.
- .github/skills/ and .github/copilot-instructions.md for optional Copilot projections.
- $CODEX_HOME/skills is a personal external effect and requires separate explicit authorization.
- .codex/commands is legacy-only and is never a default projection target.

## Environment Profile Contract

- Exact environment ID and version.
- Exact language-profile references.
- Exact toolchain-profile references.
- Exact runtime-profile references.
- Exact host-profile references.
- Resource policy for CPU, memory, storage, and time.
- Network policy, including whether resolution or installation may access the network.
- Filesystem read/write policy and allowed roots.
- Exact lockfile reference and digest.
- No latest tags, ambient fallback, unbounded PATH discovery, or directory-name inference.

## Installation Lifecycle

- Resolve: validate the environment profile and close all references against the exact lock.
- Plan: emit .cyberalchemy/state/installations/<run-id>/plan.json before changing local install state.
- Materialize: place verified bytes in content-addressed store paths; never mutate global tool installations by default.
- Activate: write small bindings under .cyberalchemy/active and executable shims under .cyberalchemy/bin.
- Project host surfaces: generate only the selected host adapters into their exact repository-native paths.
- Verify: run version, digest, capability, isolation, and negative checks.
- Receipt: record profile and lock digests, installed paths, validation outcomes, network effects, filesystem effects, and rollback instructions.

## Toolchain Policy

- Prefer pinned, container-backed development toolchains for TypeScript/Node, Python, Rust, and Lean when host independence materially improves reproducibility.
- Bind container images by immutable digest, not mutable tags.
- Pin package-manager and compiler/interpreter versions in environment locks.
- Key dependency caches by exact lockfile digest; caches are accelerators and never authority evidence.
- Do not require host-checkout node_modules or mutable global language packages.
- Keep browser execution as a separate runtime profile with its own binary and cache bindings.
- Treat agent hosts as adapters/runtimes, never as language semantics or authority owners.

## Lean Evidence Lane

```json
{"sequencing_decision_ref":"CAL-DECISION-0003-LEAN-SEQUENCING:LEANS-2","posture":"parallel-non-blocking-after-accepted-semantic-snapshot","declarations":["platform/languages/lean/v1/","platform/tools/lean/v1/","platform/tools/lake/v1/","platform/profiles/toolchains/lean-meta-types-v1/v1/","platform/profiles/environments/meta-type-formalization-v1/v1/","platform/locks/meta-type-formalization-v1.lock.json"],"boundary":"These paths define a candidate provider environment. They neither install Lean nor make theorem completion a predecessor of Craft identity.","failure_posture":"A failed or deferred Lean check leaves the FormalClaim evidence unresolved while preserving any separately accepted semantic snapshot."}
```

## Runtime Categories

- Platform runtime: shared execution substrate or adapter declared under platform/runtimes.
- Capability runtime: a product realization owned inside contexts/<context-id>/instances/<capability-instance-id>/implementation/runtime/.
- A capability runtime references platform declarations and profiles; it does not copy or redefine them.
- A runtime registration binds exact package roots, profiles, adapters, validators, and owner routes but has no authority effect by presence alone.

## Generated State Policy

- There is no root generated/ directory.
- Machine-generated local installation and activation state lives under the ignored .cyberalchemy/ tree.
- Compiled graphs and system ontologies remain under each capability instance's specification/generated/ because they are local projections of authored source.
- Human artifact projections remain beside their canonical machine source because they are part of the artifact boundary and are checked for drift.
- Host projections live at host-native roots because consumers require those paths; their exact canonical inputs remain in platform profiles and tool declarations.

## Verification Obligations

- Reject unlocked, floating, or digest-mismatched dependencies.
- Reject an active binding that does not close against the selected environment profile and lock.
- Reject materialized bytes outside declared store roots.
- Reject host projections not derivable from exact canonical inputs.
- Reject a receipt that omits network, filesystem, version, digest, or rollback effects.
- Run an offline reinstall from a warm content-addressed store and compare activation outputs byte-for-byte.
- Run a clean-store install under the declared network policy and compare the resulting lock closure and receipts.
- Prove that removing one active binding does not delete shared content-addressed bytes still referenced by another environment.

## Required Decisions

- Select the initial supported languages, including Lean for the bounded formal-evidence lane, and whether portable is a real base profile or only a profile convention.
- Select the initial development environment profile and exact toolchain strategy for each language; select exact Lean and Lake versions only before CML-05, not as a prerequisite for Craft identity.
- Select network and filesystem policies for development, CI, and release separately.
- Select the installer, profile resolver, artifact generator, and validator artifact types before implementation.
- Select which agent hosts are supported and which projections are repository-local versus personal external effects.
- Select the first capability runtime only after its product, ontology, authored specification, compiled graph, system ontology, implementation binding, and conformance predecessors are evaluable.

## Typed residue

### No platform schemas, profiles, locks, installer, or content-addressed store implementation exists in CyberAlchemy Lab.

- Owner needed: CyberAlchemy Lab platform owner
- Effect: No runtime, language, or tool is currently installed or activated by this proposal.

### Exact initial versions and image digests are not selected.

- Owner needed: CyberAlchemy Lab toolchain owner
- Effect: No environment lock can yet be accepted.

### The bootstrap proposal renderer is not the proposed artifact generator.

- Owner needed: CyberAlchemy Lab projection toolchain owner
- Effect: These proposal projections demonstrate direction only and do not prove the future generator.

## Claim ceiling

This draft records a platform planning candidate. It installs or activates nothing, selects no versions, grants no network or filesystem authority, proves no runtime or toolchain conformance, satisfies no CAV2-D65 construction binding, and does not authorize implementation, publication, release, deployment, or v1.0.0.

