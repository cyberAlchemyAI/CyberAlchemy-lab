[Documentation home](../README.md)

<a id="library-reading-guide"></a>

Start here

<a id="library-reading-guide-title"></a>

### How to use this library

The Lab organizes work through meanings, record requirements, evidence and decisions. The essays explain the connections. This catalog gives you the exact records behind that explanation.

If you’re new to the model, [follow the incident](../tutorials/incident-walkthrough.md) first. It shows what the agent reads and records. The [concept comparisons](../concepts/comparisons.md) help when similar names obscure different responsibilities.

Begin with [Authority begins with meaning](../essays/01-authority-begins-with-meaning.md#essay-1), then [What the Lab organizes](../essays/04-what-the-lab-organizes.md#essay-4) and [An agent’s working session](../essays/06-an-agents-working-session.md#essay-6). [What is operational today](../essays/08-what-is-operational-today.md#essay-8) describes the implementation evidence in this captured snapshot.

| Your question | Where to look |
| --- | --- |
| What does this term mean? | [Definitions](definitions.md#catalog-definitions): introduction, exact governing statement and limits. |
| What must a record contain? | [Record formats](artifact-types.md#catalog-types): the type contract, its meaning definitions and schema. |
| Can these two kinds of records be connected? | [Connection rules](relation-kinds.md#catalog-relations): the exact allowed source–target pair and required details. [Endpoint kinds](endpoint-kinds.md#catalog-endpoints) help locate the relevant rules. |

### Acceptance, versions and the date of this catalog

**Accepted** means a decision admitted an exact version within scope. **Selected current** means the inspected registry includes it in its current selection. Deployment, activation and successful use still need their own evidence.

Identity distinguishes records; version identifies a revision. Equal display names leave identity to be checked. Three definition names appear in both Lab and Craft workflow scopes, with labels identifying the entry you’re reading.

An accepted version might still have “candidate” in its older name. Its recorded acceptance governs standing. Earlier accepted versions remain in history when selection moves to a successor.

A type can be accepted while an instance is proposed. A schema’s `status` field describes validated record structure. The type registry’s decision and each instance’s standing remain separate.

The catalog retains sources captured on **8 October 2026**. Its totals concern selected registries, rather than all files or features. Introductions and essays explain those records while leaving authority to its governing selection. Each entry retains exact statements and source links.

Project State can keep proposals, evidence and unresolved matters with their own status. Accepting the state supplies no automatic acceptance for every included record or source.

### Terms you will meet in the records

**Scope**

Where a meaning, rule or permission applies, and its limits.

**Contract and schema**

A contract states requirements. A schema expresses structural rules in a machine-readable form. Meeting a schema does not by itself prove truth or grant permission.

**Reference and binding**

A reference identifies another record; a binding explicitly associates particular records or versions. The binding’s own contract determines what that association means.

**Canonical**

In representation rules, the designated machine form with its declared approved origin. This is separate from semantic authority. A generated result can have a canonical type without becoming a second writable source of meaning; accepted definitions govern meaning through their own scope and decisions.

**Projection or view**

Information derived from selected source records for a particular question. An ontology view presents concepts and connections; a context view prepares information for work. Their source selections and omissions matter.

**Qualifier**

An extra detail required on a connection, such as version, scope, role, period or evidence.

**Invariant**

A condition the model requires to hold across the cases it covers. Stating an invariant does not prove that every implementation satisfies it.

**Residue and claim ceiling**

Residue is required matter that remains unresolved or unpreserved. A claim ceiling is the strongest conclusion the available record or evidence justifies.

**Replay and cursor**

Replay reconstructs a recorded state from its event history. A cursor identifies a position in that history.

**Fingerprint or digest**

A content identifier calculated from a record’s bytes, often using SHA-256. It supports checking which contents were captured; it does not establish their truth.

### How to read the machine field names

Keys such as `source_ref` stay exact so you can compare the explanation with the schema. _ref points to another record, and `_version_ref` selects an exact revision. The schema identifies permitted reference kinds.

In JSON schema, `required` lists mandatory fields, `properties` describes them, `enum` restricts alternatives and `$ref` points to a schema section. A discriminator identifies type through a field and value. These are reading clues. The complete contract and schema govern the requirements.
