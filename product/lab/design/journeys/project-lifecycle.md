# Lab project lifecycle — proposed user/agent journeys

Status: **proposed**. Created: 2026-11-04.
Product reference for every journey: `product:cyberalchemy-lab`.

These are product design accounts using
[`cal.definition.user-journey@1.0.0-candidate.1`](../../../../authority/definitions/candidates/0017-user-journey/definitions/user-journey/v1/definition.json).
The exact definition's original-file SHA-256 is
`693045f6c86f0faa8b168d072e473bbb48f1e75cb71d440fc559c7440f147fe7`.
Its [generated explanation](../../../../authority/definitions/candidates/0017-user-journey/definitions/user-journey/v1/DEFINITION.md)
provides the associated boundaries and review obligations. That meaning remains
a repository candidate.

Each journey identifies an actor pursuing an outcome through the Lab product,
with an explicit situation, interactions, decisions, handoffs and possible outcomes.
These accounts propose behavior; they are not executable workflows, permission
grants, admission decisions or records of successful user execution. Evaluation of
all six journeys remains **not observed**.

## Scope and navigation

The running illustration is a request to create a context-management project for
preserving useful knowledge between agent sessions. Its workspace and any resulting
Product are illustrative. The proposed workspace model gives each new project its
own product records, authority, definitions, ontology, models, Work and artifact
bindings, while sharing pinned runtime dependencies. Lab creation Work records
creation and handoff; subsequent domain Work belongs to the new project.

| ID | Journey | Primary actor | Desired outcome | Status |
| --- | --- | --- | --- | --- |
| [J01](#j01--create-and-initialize-a-project) | Create and initialize a project | Prospective project owner | An independently owned workspace ready for its first Work | proposed |
| [J02](#j02--start-or-resume-project-work) | Start or resume project work | Project collaborator | Continue the intended Work with relevant, attributable context | proposed |
| [J03](#j03--introduce-or-change-a-definition) | Introduce or change a definition | Definition author | A meaning at the appropriate scope, with explicit review and standing | proposed |
| [J04](#j04--join-an-existing-project) | Join an existing project | New teammate | Use shared project records and contribute within assigned access | proposed |
| [J05](#j05--delegate-bounded-work-to-an-agent) | Delegate bounded work to an agent | Work owner | Obtain an attributable result from a bounded agent assignment | proposed |
| [J06](#j06--recover-from-interruption-or-changed-context) | Recover from interruption or changed context | Collaborator or operator resuming Work | Establish what happened and continue without losing work or duplicating effects | proposed |

## J01 — Create and initialize a project

- **Status:** proposed.
- **Product:** `product:cyberalchemy-lab`.
- **Primary actor:** a prospective project owner.
- **Supporting actors:** the Lab agent, nominated founding owner and runtime operator.
- **Starting situation:** the user has a new idea and no workspace for that project.
- **Desired outcome:** a separately identified workspace with accepted ownership,
  initial project state and a clear place to begin discovery.
- **Illustrative intent:** “I want a context-management project that preserves useful
  knowledge between agent sessions.”

### Proposed interactions and handoffs

| Moment | User or owner interaction | Agent / product response |
| --- | --- | --- |
| Understand the intent | Describes the problem and corrects the agent's interpretation. | Drafts a brief with intended users, initial goals, scope and open questions. |
| Prepare a workspace | Sees where the project will live and which owner is nominated. | Opens creation Work in the Lab and prepares project-specific records, the shared base layout and pinned runtime dependencies. |
| Accept founding ownership | The nominated owner reviews and accepts the exact founding declaration. | Shows the identity, owner roles, policy and scope being established; keeps the workspace pending until acceptance is established. |
| Initialize | Sees initialization progress and any gaps. | Establishes the project's own authority bootstrap, initial state and histories through the selected runtime route. |
| Hand over | Opens the new project and chooses its first discovery Work. | Records the workspace reference and creation receipts in Lab Work, then selects the child project's context. |

### Decisions and alternative outcomes

- If the creator and founding owner differ, the agent routes acceptance to the
  nominated owner. Folder creation does not accept ownership on their behalf.
- Product discovery can begin before deciding whether to create a new Product or
  reference an existing one. A new Project does not require a new Product identity.
- If ownership, source contracts or runtime initialization remain unresolved, the
  product shows “workspace prepared; initialization pending.” Candidate design work
  may continue within the available scope.
- If handoff recording fails after the project bootstrap commits, J06 reconciles
  the existing result before another creation attempt.

### Expected resulting records

Lab creation Work, project brief and goals, workspace binding, owner acceptance,
bootstrap/state references and a handoff receipt. The child project owns subsequent
domain Work. Creation provenance supplies no implicit continuing Lab authority.

## J02 — Start or resume project work

- **Status:** proposed.
- **Product:** `product:cyberalchemy-lab`.
- **Primary actor:** a collaborator starting or returning to project Work.
- **Supporting actors:** the agent, Define CLI and Lab runtime.
- **Starting situation:** a project exists; relevant decisions and artifacts may
  outlive the previous chat or agent session.
- **Desired outcome:** continue the intended activity using relevant project state,
  meanings, evidence and unresolved questions.
- **Illustrative intent:** “Continue designing how an agent remembers decisions.”

### Proposed interactions and handoffs

| Moment | User interaction | Agent / product response |
| --- | --- | --- |
| Select the activity | Opens a workspace and identifies the Work, or chooses among plausible matches. | Resolves the workspace binding and verifies the Work belongs to the selected Project. |
| See the context | Sees the active Project, Work, source freshness, included candidates and intended next action. | Define selects relevant goals, state, decisions, definitions, pinned imports, ontology views and evidence. |
| Continue | Corrects assumptions or adds information relevant to the Work. | Preserves distinctions between recorded decisions, source evidence and working assumptions; prepares the next bounded proposal. |
| Finish the session | Sees saved outputs, remaining questions and the next decision. | Records durable results in the project and closes temporary session resources. |

### Decisions and alternative outcomes

- A Work reference from another project produces a selection mismatch that must be
  resolved. The agent does not silently switch to the Lab's context.
- Missing material or unchecked shared-head freshness appears as a gap. Snapshot
  inspection or draft preparation can continue where their requirements are met.
- A changed head or expired view triggers fresh context selection. Existing draft
  work is retained and affected assumptions are identified.
- If several Work items fit, the user makes one meaningful selection before the
  agent proceeds with dependent work.

### Expected resulting records

The selected context/capture reference, explicit source and definition revisions,
updated Work decisions, candidate outputs and unresolved questions. A later session
reconstructs continuity from those records rather than previous session scratch memory.

## J03 — Introduce or change a definition

- **Status:** proposed.
- **Product:** `product:cyberalchemy-lab`.
- **Primary actor:** a collaborator authoring or refining a meaning.
- **Supporting actors:** the agent, Define CLI, applicable semantic owner and runtime.
- **Starting situation:** Work depends on an undefined, ambiguous or unsuitable term.
- **Desired outcome:** an attributable meaning at the right scope, with explicit
  standing, review obligations and effects on consumers.
- **Illustrative intent:** “We need to define what a memory item is.”

### Proposed interactions and handoffs

| Moment | Author or owner interaction | Agent / product response |
| --- | --- | --- |
| Find existing meaning | Reviews relevant existing definitions and their scope. | Searches local definitions and declared imports, retaining exact source revisions. |
| Choose scope | Confirms whether the meaning is task-specific, project-wide or a contribution upstream. | Proposes the placement and owner route appropriate to the intended reuse. |
| Draft | Reviews the statement, examples, exclusions and remaining questions. | Define prepares the candidate, source attribution, affected references and exact review material. |
| Decide | The applicable owner or explicitly authorized delegate makes the required decision. | The runtime verifies the authority and exact proposal before applying any authorized change. |
| Continue use | Sees which revision is admitted, which is proposed, and what consumers are affected. | Keeps ordinary selection separate from explicit candidate evaluation and records any resulting updates. |

### Scope and placement decisions

| Intended use | Proposed placement / handoff |
| --- | --- |
| Meaning useful only inside this Work | The Work's `define/definitions/` |
| Meaning intended for reuse across this project | The project's `authority/definitions/<term>/vN/` |
| Improvement to a shared imported definition | A contribution routed to its owning workspace |

Reusable definitions may begin directly in the project's authority area as
candidates. Candidate posture stays inside the definition record; revision folders
remain. An admitted v1 can stay selected while v2 is explicitly evaluated as a candidate.

### Alternative outcomes

- Reuse a suitable existing meaning with its exact identity and revision.
- Keep ambiguity open when the required source or semantic information is missing.
- Retain a proposal without admission when review or authority is unavailable.
- Route an upstream proposal to its owner while retaining the project's existing
  import pin. Local evaluation does not silently update that shared definition.

### Expected resulting records

An explicit concept disposition, candidate definition or task meaning, applicable
source lineage, proposed index changes, review package and any actual decision and
commit receipt. Editing a status field alone does not establish admission.

## J04 — Join an existing project

- **Status:** proposed.
- **Product:** `product:cyberalchemy-lab`.
- **Primary actor:** a new teammate.
- **Supporting actors:** an inviting collaborator or owner, the agent and runtime.
- **Starting situation:** the teammate has a project invitation or cloned repository
  and wants to inspect or contribute to existing Work.
- **Desired outcome:** establish the project's identity, reconstruct accessible
  context and contribute within the teammate's actual access and role assignments.
- **Illustrative intent:** “I cloned context-management. Help me work on retrieval.”

### Proposed interactions and handoffs

| Moment | Teammate interaction | Agent / product response |
| --- | --- | --- |
| Establish the project | Uses the team's trusted onboarding information to identify the intended project. | Resolves its workspace binding and verifies the selected founding identity and history against that trust. |
| Prepare local use | Sees required dependencies and any access gaps. | Checks pinned runtime dependencies, fetches permitted referenced artifacts and rebuilds local query caches. |
| Choose Work | Opens retrieval-related Work and reviews its current context. | Selects attributable project records, decisions and evidence through J02. |
| Contribute | Supplies their own identity for operations that require it. | Prepares or submits changes only within the teammate's applicable access and assignments. |

### Decisions and alternative outcomes

- Read access supports inspection of accessible records; authoring access supports
  candidate preparation. Semantic decisions and runtime operations require their
  applicable grants.
- The invitation may include a role assignment, but cloning alone creates no owner
  assignment. Owner private keys are not copied to a teammate.
- Reading and preparing Work should not require manual project SQLite migrations.
  The local cache is rebuilt from recoverable project records and artifacts.
- Unavailable artifacts or unchecked remote freshness remain visible. A permitted
  historical snapshot can support limited work without being presented as current.

### Expected resulting records

A verified workspace selection, local dependency/cache state, the teammate's
applicable identity and role references, and any subsequent Work proposals. Joining
does not create a new project genesis or a competing authority history.

## J05 — Delegate bounded work to an agent

- **Status:** proposed.
- **Product:** `product:cyberalchemy-lab`.
- **Primary actor:** the person or role accountable for the Work.
- **Supporting actors:** the assigned agent, Define CLI and runtime; a decision owner
  when the next action requires one.
- **Starting situation:** an existing Work item can be delegated with an explicit
  goal, constraints, available sources and completion criteria.
- **Desired outcome:** an attributable result produced within the assignment, with
  evidence, uncertainty and the next decision clearly presented.
- **Illustrative intent:** “Compare three retrieval approaches and prepare a
  recommendation. Don't admit any definitions.”

### Proposed interactions and handoffs

| Moment | Work-owner interaction | Agent / product response |
| --- | --- | --- |
| Assign | States the outcome, boundaries and completion criteria. | Records the assignment against the selected Project and Work and resolves its available context. |
| Investigate | Receives meaningful findings or a question when missing information blocks progress. | Compares the approaches, records evidence and counterevidence, and creates permitted candidate models or meanings. |
| Prepare the result | Reviews a recommendation and its limitations. | Saves the result and artifact references in the project, showing proposed changes and unresolved obligations. |
| Hand over | Makes the next required decision or delegates another bounded activity. | Closes the assignment with its observed result and routes any action requiring additional authority. |

### Decisions and alternative outcomes

- For the illustrative request, the agent may prepare definition candidates but
  cannot admit them under that assignment.
- An explicit policy may delegate particular admission actions to an agent. The
  runtime verifies the actual grant for the action rather than deriving permission
  from the agent's context or assignment label.
- A comparison can conclude that no approach meets the criteria. That finding and
  its evidence remain useful outputs; a recommendation is not forced.
- If a required source or action is unavailable, the agent records the gap and
  continues independent work that fits the assignment.

### Expected resulting records

An agent assignment, selected context references, comparison evidence, proposed
changes, output artifact references and a completion or gap report. Structural
validation, Work satisfaction, semantic admission and product usefulness remain
separately assessed outcomes.

## J06 — Recover from interruption or changed context

- **Status:** proposed.
- **Product:** `product:cyberalchemy-lab`.
- **Primary actor:** a collaborator or operator resuming interrupted Work.
- **Supporting actors:** the agent, runtime and applicable decision owner.
- **Starting situation:** a process was interrupted, another collaborator changed
  the project, or a local view no longer reflects the selected durable state.
- **Desired outcome:** establish what happened, preserve the user's work and resume
  from the correct project state without duplicate effects.
- **Illustrative intent:** “The command timed out. Did the change go through?”

### Proposed interactions and handoffs

| Moment | User interaction | Agent / product response |
| --- | --- | --- |
| Reopen | Identifies the interrupted Work or operation. | Preserves drafts and original request/operation references; explains what remains known or uncertain. |
| Establish the outcome | Sees “committed,” “not committed,” or “outcome unresolved,” with the applicable evidence. | Inspects authoritative history and retained results before proposing another effect. |
| Reconcile | Reviews any changes needed because the project advanced. | Selects fresh context, identifies affected assumptions and routes renewed approval where approved inputs have changed. |
| Restore local views | Sees committed work even if a cache or export is catching up. | Rebuilds derived views from durable records without repeating the committed action. |
| Resume | Continues the Work with an explicit next action. | Records recovery findings and hands back the reconciled result or remaining blocker. |

### Alternative paths

| Situation | Proposed response and outcome |
| --- | --- |
| Context changes during preparation | Preserve the draft, refresh context and identify affected assumptions. |
| Another teammate commits first | Reconcile against the new head and renew approval where the exact approved inputs change. |
| A commit may have completed before timeout | Inspect the original operation and history. Keep the outcome unresolved until evidence establishes it; do not blindly redispatch. |
| The commit succeeds but a local projection fails | Rebuild the projection and report its lag; retain the successful commit. |
| A required artifact is missing | Identify the unavailable dependency and affected use. Continue only activities whose requirements are met. |

### Expected resulting records

An operation outcome observation, recovery findings, preserved draft/base references,
any revised proposal and approval, and refreshed derived views. Recovery restores
durable project context; previous Session scratch memory need not survive.

## Evaluation and evidence boundaries

All six journeys remain **proposed** with **no observed user-journey evaluation**.
Their User Journey definition is also a repository candidate. Neither placement in
the product folder nor reference to that meaning supplies admission or permission.

The [Define / Lab local integration report](../../../../define/development/lab-integration/v1/REPORT.md)
provides limited technical evidence for candidate materialization, native local
review/commit, idempotency, fresh context lookup and exact reconstruction. It is
component evidence relevant to J02, J03, J05 and J06; it does not validate these
journeys as a whole, independent project bootstrap, team onboarding, shared remote
storage or human product usefulness.

The [existing v1 release-candidate acceptance](../../release-candidates/v1/PRODUCT-ACCEPTANCE.md)
has its own three owner journeys and evidence obligations. These six design accounts
are not substituted for that release's acceptance or execution history.

For a first product prototype, start with J01, J02 and J05 to examine creation,
context selection and delegation together, then J03, J04 and J06 for meaning changes,
team sharing and recovery. Future observations should reference the exact journey
revision and record actor, starting situation, attempts, deviations, outcomes and
evidence separately, leaving the distinction between design and observation explicit.
