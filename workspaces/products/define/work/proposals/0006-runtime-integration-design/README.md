# Define runtime integration design

Status: proposed implementation design for review. Authority effect: none. No implementation, semantic admission, runtime selection, owner grant or application is performed by this package.

## Outcome

An investigator can prepare one task Pack against exact Lab sources, keep values/applications/evidence together, and send explicitly selected reusable meanings to the existing Lab review route. Authorized effects are applied by the Lab host and reconstructed through a fresh selected state and session.

```mermaid
flowchart LR
  H[Selected Lab context and exact sources] --> P[Define preparation]
  P --> K[Task Pack]
  K --> S[Explicit materialization selection]
  S --> R[Lab change and owner review]
  R --> A[Lab authorized application]
  A --> V[Fresh State and Context/Ontology Views]
```

The Pack is the normal output. Standalone Definition candidates are produced only when selected. Applications and assessments are addressable entries inside the Pack; they do not receive one file or shared admission per task.

## Read the design

| Question | Document |
| --- | --- |
| What are the components, ownership boundaries and chosen runtime target? | [System design](DESIGN.md) |
| What data crosses each boundary? | [Contract design](CONTRACTS.md) |
| How do preparation, review, publication and failures work? | [Flows and failure behavior](FLOWS.md) |
| What happens in the incident example? | [Worked examples](EXAMPLES.md) |
| What is the smallest first delivery and what follows it? | [Implementation layers](IMPLEMENTATION-LAYERING.md) |
| How does this cover the remaining work and existing79-item plan? | [Coverage and verification design](COVERAGE.md), [work crosswalk](work-crosswalk.json) |
| Which exact repository sources informed this design? | [Source baseline](source-baseline.json) |
| Which decisions are technical proposals and which effects remain pending? | [Decision register](decisions.json) |
| What was checked before presentation? | [Author design review](REVIEW.md), [document validation](validation.json) |

## Design choices

- Keep the current v1 CLI frozen; implement the successor in a separate proposed `implementation/define-cli/v2/` package. The launcher changes only at an explicit adoption boundary.
- Use the selected API17 protocol through a host adapter. The captured maintained operator revision3 is the integration reference, not an automatic activation or a claim of full runtime qualification.
- Keep the JavaScript CLI thin. Python owns strict decoding, exact-byte hashing, new Pack generation, validation and Definition materialization. Original authority/source bytes never round-trip through JavaScript Number conversion.
- Reuse the Lab's context, ontology, change, review, owner and publication contracts. Define is a producer; it owns neither the governing store nor owner identity.
- Import available assessments with exact producer/evidence bindings. Define does not execute arbitrary formulas, generated code or domain assessment methods during preparation.
- Keep preparation, owner review and authorized application as distinct operations with exact artifacts and currentness checks.

## Immediate next delivery

**L0: a complete local incident Pack preview from explicitly frozen inputs**, using the strict new contracts and a recorded source/context cut. Its status is snapshot-only candidate preparation. It does not claim a live Session, admitted new meaning or successful host integration.

**L1 then connects the same kernel to a real selected host** and proves fresh read-only preparation under the actual context/session permissions and expiry. L2 adds guarded selected materialization/review; L3 adds authorized application, read-back and realization qualification. See the [layer boundaries](IMPLEMENTATION-LAYERING.md).

The existing79-item plan remains the work identity ledger. This design supplies concrete architecture and a current-model overlay; it does not declare those items implemented or reopen the accepted semantic wording.
