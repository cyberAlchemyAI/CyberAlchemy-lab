# Impeccable capability map for the Lab website

The complete repository is cloned at `/home/vlad_/projects/impeccable`, commit `2f98774f86bc05563876643db37e6c37c322850f`. The maintained skill source is `skill/SKILL.src.md`; provider distributions are generated from it. Package version is 4.5.2; the pinned engine is 0.1.14. This map accounts for all 24 command entries and the supporting tools without requiring every optional or incompatible intervention to be run.

## All commands

Names below are agent workflows, invoked as `/impeccable <command>` after installation. They are not all literal shell subcommands. Use `skill/scripts/impeccable` for engine verbs such as context and detect.

| Command | Use in this plan | Target and concrete output |
| --- | --- | --- |
| `init` | W0, persistent workflow setup | Website product facts, audience assumptions and constraints in scoped PRODUCT.md; confirm material gaps before writing |
| `document` | W0 | Capture the existing two surface systems, tokens and role usage in DESIGN.md; absence of a file does not erase the incumbent identity |
| `shape` | W0/W3 planning method | Surface job, path, states, structure and acceptance criteria; a formal shape run includes its interview/confirmation, which this source-grounded plan does not claim to have completed |
| `extract` | W4 | Consolidate repeated tokens/components into the current system where the same intent recurs, generally at least three uses |
| `critique` | Optional formal independent design review before a major slice | Evaluate hierarchy and cognitive load independently from detector evidence; follow its isolated-assessment and applicable delegation requirements if invoked. This planning inspection is not a completed formal critique run |
| `audit` | W2/W6/release | Measurable accessibility, performance, responsive and implementation findings; retain verified evidence and manual residues |
| `polish` | W7 | Final whole-journey alignment, spacing, state and consistency pass after substantive work |
| `bolder` | Optional W3/W4 marketing refinement | Strengthen a named weak hierarchy or example entrance without replacing the approved hero or extending brand primitives silently |
| `quieter` | W4 reading refinement | Reduce competing panels, accents and repetitive furniture while keeping headings, labels and wayfinding |
| `distill` | W3/W4 | Remove redundant pitches and excessive lookup preamble while preserving terms, scope and complete records |
| `harden` | W1/W6 | Time/URL availability combinations, search recovery, long text, disabled scripts, disclosure fragments and control interruption |
| `onboard` | W3 | Optional newcomer path to one concrete incident/model example; no mandatory tour or account wizard |
| `animate` | Optional W7 | Explain selection/inspector and feedback continuity; no delays before reading, and a useful reduced-motion alternative |
| `colorize` | W4 | Clarify action, selection and status through existing semantic tokens; no wholesale palette replacement |
| `typeset` | W4 | Keep the large readable scale; fix measured small roles, long helper lines, weight/fallback and hierarchy |
| `layout` | W2–W4 | Phone navigation, earlier useful entry points, heading rhythm and semantic grouping across widths |
| `delight` | Optional W7 | One useful moment in lookup, map inspection or event ideas, grounded in product character |
| `overdrive` | Separate optional experiment | Guided incident/map demonstration only after core work; static fallback and measurable benefit required |
| `clarify` | W1/W3/W5/W6 | Current event availability, task labels, search state and recovery; preserve factual/legal/domain meaning |
| `adapt` | W2/W4/W6 | Phone, tablet, wide screens, zoom, input methods and print where useful; responsive structure, not scaled screenshots |
| `optimize` | W5 | Attribute cold/warm search costs and improve the measured bottleneck without losing complete portable delivery |
| `live` | Optional bounded local prototype | Explore one selected element in an isolated HTML prototype or local checkout, then port the accepted change into the actual Python templates/assets |
| `generate` | Optional alternative to manual live picking | Generate up to three variants of a named element, e.g. mobile header or catalog entrance; preserve identity and accept only the chosen variant |
| `craft` | Deprecated alias; no separate task | Upstream now treats this as ordinary new visual work. Do not confuse this command with CyberAlchemy's Craft product |

## Supporting resources and tooling

| Resource | What is available | Website application and boundary |
| --- | --- | --- |
| Skill and reference library | Canonical source, 24 command playbooks, visitor modes and workflow references | Use Persuade for entrances, Read for documents and Operate for embedded task controls; native iOS/Android guides do not apply to this mobile website |
| Context loader | `skill/scripts/impeccable context --target <path>` | Ran once against the maintained homepage template. Missing context files were reported; actual CSS/templates establish the current visual system. Plan W0 addresses target discovery and scope |
| Deterministic detector | 59 rules in `crates/live/assets/antipatterns.json`; HTML, text and rendered URL scans | Ran seven-file static scan and desktop/phone rendered scans of five routes. Raw findings are review inputs, not automatic defects or conformance proof |
| Design context and ignores | PRODUCT.md, DESIGN.md, optional design sidecar, scoped configs and inline ignores | Proposed in W0/W4; record only verified design truth. Use selector/rule-specific dispositions after validation, not blanket exclusions |
| CLI runtime | Rust engine; launcher downloads/finds its pinned binary; npm shim and platform packages | Launcher and detector worked from the external checkout. The website needs no npm/Rust dependency or framework migration |
| Browser extension and editor integrations | Extension, VS Code/Cursor/provider distribution assets and shared detector bundle | Optional developer convenience; do not add extension artifacts to the site's release or install global/editor settings merely to write this plan |
| Live iteration and generated variants | Local HTML support and framework adapters; browser overlay, selection, variants and accept/discard lifecycle | Compatible in principle with local HTML, but generated dist is not the source of truth. Prototype in isolation and port accepted changes to Python templates/CSS; clean up helper state and rebuild |
| Comp and asset tools | Concept, regions, raster comparison, component/asset review, font and image utilities | Useful only for a future approved replacement surface or new artwork. Existing orb, logo, icons and diagrams make asset generation unnecessary for the core plan |
| Hooks | Provider-native per-edit detection and deeper stop checks | Optional project-scoped adoption after baseline dispositions; scanning templates alone can miss final CSS/DOM, so retain post-build checks |
| Doctor, pin and update | Context/schema drift checks, command shortcuts and version maintenance | Pin the reviewed checkout now; later update deliberately. Do not repair project context or install hooks as an unrelated side effect |
| Agents and tests | Packaged asset/documentation/finish agents, engine/workflow tests, behavior fixtures and oracle goldens | Available for their named implementation workflows, not proof that the Lab website is correct. No model-backed tests or upstream contribution are required for this plan |
| Demos and review UI | Landing demo and component review tooling | Pattern/mechanics references only. Never transfer Impeccable product claims or a demo's brand onto CyberAlchemy |
| License and notices | Apache-2.0 repository license and third-party notice | Preserve license/notice obligations if copying or redistributing toolkit assets. Current plan references an external checkout; it does not vendor it |

The checkout also contains development, release and provider-maintenance machinery. Those support Impeccable itself; running all of its build/release/tests would not improve this static website. The separate private `impeccable-site` repository mentioned by upstream is not included or available through this clone.

## Reproduce the useful inspection

From `/home/vlad_/projects/CyberAlchemy-lab`, use the downloaded launcher:

```bash
/home/vlad_/projects/impeccable/skill/scripts/impeccable detect --json \
  website/dist/governance-lab-series/index.html \
  website/dist/governance-lab-series/hackathon.html \
  website/dist/governance-lab-series/start-here.html \
  website/dist/governance-lab-series/governance-lab-reference.html \
  website/dist/governance-lab-series/lab-reference-library.html \
  website/dist/governance-lab-series/reference/def-cal-definition-definition.html \
  website/dist/craft-documentation-proposal/craft-model.html
```

For rendered scans, serve the generated site locally and use `detect --json --viewport 390x1000 <local-url>` and a corresponding desktop size. On this host the browser required the existing cached Chromium executable and its existing shared-library directory, recorded in BASELINE.json. Exit 2 means findings; exit 1 means an operational failure. Do not treat either as a clean scan.

Install/link the skill into a selected provider only when beginning the persistent implementation workflow. Clone-and-use already satisfies this planning request without installing global hooks or changing the website's dependencies.
