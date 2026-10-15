## Key Findings

- The earlier exercises mostly tested choosing among available actions; they did not strongly test invention. Identical selections therefore cannot establish whether a method expands the candidate space. **[R1: “Executed experiments”; “Limits that remain after execution”]**
- The existing expansion chain already protects outcome, constraints, evidence, and tests. The missing addition is a set of **operators that change how a solution works**, followed by comparison against an explicit baseline. **[R2: “Attack to expand”]**
- Early compression is a specific risk: Distill can make proposals coherent while erasing the unusual feature worth investigating. Retain distinct mechanism families through an initial exploration window. **[R1: “What changed in the analysis,” item 6; R2: “Composition with the existing strategies”]**

**References:** R1 = `docs/proposals/hammer-bias-strategies/runs/2026-10-08-execute-all/SYNTHESIS.md`; R2 = `docs/proposals/hammer-bias-strategies/ANALYSIS-LENSES.md`.

## Gaps

There is no frozen novelty baseline, open generation benchmark, or demonstrated improvement in useful invention. The strategies below are designs for that investigation. Their examples are hypothetical sketches; analogies provide candidate mechanisms, not evidence that those mechanisms work.

## Local Tensions

- Richer description can resemble invention without changing a mechanism.
- Feasibility filtering can prematurely remove an unfamiliar but repairable idea.
- Speculation can produce apparent breakthroughs by silently dropping constraints.
- Compression can erase novelty; unlimited elaboration can protect incoherent proposals.

## Questions for Synthesis

Which changed relationship makes each candidate different? What observation would invalidate it? Can Distill preserve that relationship while shortening the proposal? Does the candidate remain different after comparison with the earlier sixteen strategies?

## Three bounded internal design passes

These were internal design passes, not separate exchanges or completed experiments.

1. **Generate:** Draft six operators acting on mechanism origin, component interfaces, affordances, representation, anomalies, and future capabilities.
2. **Critique:** Identify decorative analogies, combinations that merely bundle features, duplicate evidence-generation proposals, and speculation that cheats constraints.
3. **Repair:** Require a baseline-relative structural difference, one discriminating probe, explicit failure conditions, and delayed compression.

## Shared preparation

Freeze the incumbent and earlier proposals as graphs: components, actors, resources, state transitions, dependencies, timing, and constraints. Give every candidate a **novelty fingerprint**:

> baseline → changed relationship → resulting capability → preserved constraints

Novelty is relative to this declared corpus, not a claim of worldwide originality. “A better process” and renamed nodes do not qualify. A strategy may legitimately produce zero novel candidates.

Use two stores: feasible candidates satisfying hard constraints, and speculative branches that explicitly name relaxed premises. Only feasible candidates compete for immediate adoption.

## 1. Transfer a distant mechanism through a constraint map

**Operator:** Find an unlike domain with a useful relationship; transfer that relationship through an explicit correspondence.

**Example:** For joining two boards, explore lacing: alternating attachment points distribute tension through a flexible member. The transferred idea is a load path, not “woodworking is like sewing.”

**Structural change:** Concentrated penetrating fasteners become distributed tension connections.

**Fingerprint:** `local penetration → distributed tension path`; compare with all existing joining alternatives before accepting novelty.

**Smallest unit:** One source mechanism, a target mapping, one failed correspondence, and one candidate joint.

**Probe:** Make a small mock-up under the same load, assembly-time, reversibility, and material constraints as the baseline. Reject if the required load cannot be held.

**Failure conditions:** Similar vocabulary without a transferable relationship; unmapped material assumptions; an attractive source mechanism whose prerequisites are unavailable.

**Composition:** Robot Talks assigns source-mechanism, target-constraint, and transfer-breakpoint concerns. Lane Z develops the incumbent; Lane A develops the mapped mechanism. Distill only after the breakpoint report; preserve the correspondence that makes the transfer different.

## 2. Recombine mechanisms at their interfaces

**Operator:** Cross components from different candidate families, but require the combination to create a capability neither parent supplies alone.

**Example:** Combine a temporary alignment fixture with a reversible interlocking joint. The fixture establishes geometry; the interlock carries the final load. Their interface allows accurate assembly without leaving the fixture installed.

**Structural change:** Alignment and load retention become separate cooperating mechanisms.

**Fingerprint:** `one component aligns and retains → temporary alignment hands geometry to persistent retention`.

**Smallest unit:** Two parent mechanisms, the interface contract, and one predicted interaction benefit.

**Probe:** Compare the hybrid against each parent alone on assembly error, retention, and disassembly. The hybrid must demonstrate its proposed interaction, not merely add both costs.

**Failure conditions:** Feature bundles without interaction; incompatible tolerances; a simpler parent already provides the entire capability.

**Composition:** Robot Talks investigates parent capabilities and interface failures independently. Lane Z tests the stronger parent; Lane A tests the hybrid. Distill must retain the interface and interaction hypothesis, rather than compressing the proposal to “combine both.”

## 3. Search for unused affordances and by-products

**Operator:** Inventory properties and traces already present but unused; ask what additional operation each makes possible.

**Example:** A review queue already contains successive versions and rejection annotations. Instead of merely generating another summary, propose a comparator that locates which changed dependency invalidated an earlier accepted claim.

**Structural change:** Historical records become inputs to selective invalidation rather than passive archives.

**Fingerprint:** `archive → dependency-sensitive validity update`. If the earlier corpus already contains this mechanism, record reuse rather than novelty.

**Smallest unit:** One available trace, one inferred affordance, and one proposed operation.

**Probe:** Seed revisions with known invalidated and unaffected claims. Test whether the comparator identifies both correctly without silently reusing stale assurance.

**Failure conditions:** The required trace does not exist; timestamps are mistaken for causal evidence; the proposal is simply “measure more” with additional terminology.

**Composition:** Robot Talks separates artifact inventory, plausible affordances, and evidence limits. Lane Z uses the existing records conventionally; Lane A activates one latent affordance. Distill after the provenance check, preserving the exact input-to-operation relationship.

## 4. Change time, scale, or boundary while preserving the outcome

**Operator:** Re-express the same problem at another temporal resolution, unit size, or system boundary. Change one dimension at a time before recombining.

**Example:** A queue treats a revised submission as an entirely new object. Explore reviewed subclaims with explicit dependencies: only affected subclaims reopen when the submission changes. Final approval still satisfies the original assurance requirement.

**Structural change:** Whole-request reset becomes dependency-governed state transitions.

**Fingerprint:** `request-level restart → subclaim validity and explicit recomposition`.

**Smallest unit:** One changed unit of analysis, its recomposition rule, and a case where decomposition is forbidden.

**Probe:** Introduce a cross-cutting revision. Does the system reopen every dependent claim and still block approval when required?

**Failure conditions:** Hidden coupling defeats decomposition; atomic obligations are split illegally; coordination costs exceed saved work.

**Composition:** Robot Talks assigns temporal, granularity, and boundary concerns. Lane Z retains the original unit; Lane A changes one unit. Distill only after recomposition demonstrates that the original outcome remains intact.

## 5. Protect anomalies long enough to generate a new mechanism

**Operator:** Retain a stubborn outlier instead of averaging it away or immediately patching it. Generate mechanisms that explain both ordinary and anomalous cases.

**Example:** Suppose a fastened joint holds static loads but loosens under repeated expansion. The anomaly opens a joint that retains against separation while permitting movement along another axis.

**Structural change:** Rigid restraint becomes selective restraint across different directions.

**Fingerprint:** `all-direction fixation → direction-specific movement and retention`.

**Smallest unit:** One documented anomaly, competing explanations, and one candidate discriminating between them.

**Probe:** Compare ordinary and cyclic conditions. Test both desired movement and forbidden separation.

**Failure conditions:** A hypothetical anomaly is presented as observed; noise is mistaken for structure; the candidate merely relocates the failure.

**Composition:** Robot Talks preserves independent explanations. Lane Z attempts the best ordinary repair; Lane A develops an anomaly-led mechanism. Delay Distill until both explanations have faced the same counterexample. Preserve unresolved anomalies as residue.

## 6. Describe a future object, then derive its missing capabilities

**Operator:** Describe a concrete object performing an apparently unavailable capability; work backward to required operations and present-day partial implementations.

**Example:** “A joint that tells the assembler which part of its load path is failing.” Derive sensing, localization, interpretation, and a usable signal. A present-day candidate might provide only a visible deformation indicator.

**Structural change:** Passive retention gains an observable state tied to a specific failure mode.

**Fingerprint:** `unobserved deterioration → localized, interpretable indication`.

**Smallest unit:** One future-object scene, a capability dependency chain, and one presently testable capability.

**Probe:** Induce the targeted failure in a mock-up. Does the proposed indicator appear early enough and distinguish failure from harmless variation?

**Failure conditions:** Magical capabilities conceal missing dependencies; the indicator adds unacceptable weakness; speculative resources silently enter the feasible branch.

**Composition:** Robot Talks separates desired capability, dependency feasibility, and user interpretation. Lane Z offers the best present object; Lane A works backward from the future object. Distill the dependency chain after identifying the smallest testable capability—not into a slogan that conceals the missing technology.
