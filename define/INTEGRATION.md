# Define in the Lab

## What works now

The [Lab-owned Define CLI](../implementation/define-cli/v1/README.md) is a runnable candidate successor. Its active context, ontology and review dependencies are the existing **Lab operational runtime v2** interfaces. The selected compiler uses the current **Lab Craft public API**. Chat uses the installed Codex app-server directly.

```bash
./define/define doctor
./define/define chat 'Clarify the meaning needed for an incident investigation'
```

Read the [complete package and integration audit](../implementation/define-cli/v1/AUDIT.md), [interface contract](../implementation/define-cli/v1/CONTRACT.md) and [runtime binding](../implementation/define-cli/v1/runtime-manifest.json).

## Preserved import

Execution [0080](../evidence/migrations/cyberalchemy-v2-to-lab/executions/0080-define-package-import/README.md) captured the exact `cav2.define` **0.6.0-candidate** package and its separately located CLI. All 1,023 imported files remain unchanged under `source/cyberAlchemy-v2/`. The original import manifest and historical receipts describe that import, not the later successor implementation.

Earlier imports remain unchanged:

| Earlier selection | Scope |
| --- | --- |
| 0035 | Define Shared Meaning capability descriptions. |
| 0062 | Earlier business context. |
| 0063 | Frozen system model with its explicit compiler/runtime gaps. |
| 0064 | Frozen parent/child bridge context and recovered evidence. |

Against 0064, 34 overlapping files differ, 114 match and 112 current files were absent from that archive. Three predecessor paths are absent from the current selection. The [comparison](../evidence/migrations/cyberalchemy-v2-to-lab/executions/0080-define-package-import/predecessor-comparison.json) records exact identities; absence does not establish when a file was authored.

The current models remain separately owned: business 13 nodes / 12 relations, system 65 / 131, bridge two / 13. They were structurally audited; they were not registered as a new admitted global ontology.

## Integration decisions

| Concern | Selected behavior |
| --- | --- |
| Context | Existing source capture/freshness and Session views. Default inspection creates no store or key. |
| Ontology | Existing bounded graph query with diagnostics; no invented connections. |
| Definitions | Exact current Lab versions for reuse/specialization. Proposed meanings remain candidate. |
| Review | `Store.review` on an explicitly provisioned local branch. Exact cores and planned consequences; no authorization or apply. |
| Agent | Ephemeral read-only native app-server thread. Context comes from Project State and views. |
| Work-session persistence | Existing revisioned Define API retained; not persistent private machine-agent memory. |
| Compilation | Selected semantic-contract profile using the actual Lab Craft package/build identity. Pure intrinsics use Calculation. |
| Drift | Independent successor runtime manifest, plus Lab source/HEAD currentness and envelope expiry. |
| Output | Candidate files and staged build directories cannot replace existing targets. |

A Define-owned copy of the existing Session constructor fixes one duplicate input-reference defect when the subject is Project State. The source runtime remains unchanged. The specialized C10 review candidate still owns its thirteen-member successor contract; it is not treated as a generic Define reviewer.

## Audit standing

The selected runtime has no unresolved active relative imports. The candidate suite exercises actual context, graph, review and compiler interfaces. Native host initialization and ephemeral thread creation were checked without model inference. Live chat requires a working Codex login; no live model outcome is claimed by those fixtures.

The original source package remains **BLOCK** in its current upstream validator: stale source-map, CLI README and CLI package fingerprints, plus the business child's source-currentness failure. The system child reports FLAG for a wider backend compilation path that remains NOT_EVALUABLE. Historical source PASS receipts were not stretched to cover this successor. Its [audit receipt](../implementation/define-cli/v1/evidence/package-audit.json) distinguishes these results.

## Meaning and adoption still require review

Definition Packs are candidate input bundles. They are not automatically the Lab's three-voice Definition records, accepted Project State, construction authorization or consumer outcomes. The four package-vocabulary proposals, eleven v2 canonical bindings and twenty handled records remain imported source standing. The source overview's empty-registry claim is stale; the actual handled count is twenty.

Follow [Prepare a definition for review](../docs/lab/how-to/prepare-definition.md) to create the complete Lab carrier and obtain the applicable exact owner decision. Runtime adoption, canonical registry migration and admission are separate decisions. No keys, private stores, upstream material or admitted Lab runtime files were changed by this integration.

### Proposed completion plan

The **current planning revision** is the [amended integration work map](proposals/0005-amended-integration-plan/WORK-MAP.md). It applies the twelve audit findings, specifies human-owner trust, exact-byte source validation and coherent epoch publication, and separates preparation preview, guarded review and authorized application. Its Definition drafts, contracts and outcome guards remain pending the applicable owner decisions; implementation has not started under this revision.

The [semantic foundation and integration plan](proposals/0002-semantic-foundation-and-integration-plan/PLAN.md) separates two proposed meanings—CyberAlchemy Define and Definition Pack—from ten remaining integration gaps. It includes Definition/v2 drafts, exact existing semantic bindings, owner/scope enforcement obligations and a dependency plan. These are review materials; no new Definition, mapping contract or runtime has been admitted by the plan.

The [expanded work map](proposals/0003-integration-work-map/WORK-MAP.md) turns those ten areas into concrete work items with source files, outputs, dependencies, owner routes and completion criteria. Its detailed dependency graph separates early candidate preparation from later exact decisions and application, and includes source-epoch compatibility before the registry advances.
