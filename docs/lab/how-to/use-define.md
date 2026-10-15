# Use Define to clarify the meaning needed for work

Define produces a candidate Definition Pack for one goal and named consumer. It reads the Lab's selected Project State, current definitions and ontology views. Proposed meanings remain subject to owner review.

## 1. Check and inspect

From the repository root:

```bash
./define/define doctor
./define/define inspect cal.definition.definition
./define/define ontology Authority
```

`doctor` checks the selected runtime fingerprints and current context. If a provider changes, inspect that change and rebind deliberately; do not regenerate a manifest to silence unexpected drift.

## 2. Clarify meaning

```bash
./define/define chat 'Investigate why an account export is missing rows'
```

The conversation confirms scope and reviews each meaning. For example, “complete export” must use the same account, filters and source snapshot for expected and returned identifiers. It does not mean accurate values, customer satisfaction or permission to close an incident.

For preparation without a model, use the [scripted incident example](../../../implementation/define-cli/v1/README.md#prepare-and-compile-an-incident-example). An unanswered concept remains open. Reviewed language checks assess grounding, distinctions between terms and classification-axis coupling; they do not establish canonical acceptance.

## 3. Prepare the actual Lab record

A Definition Pack is not the complete Lab Definition carrier. Use [Prepare a definition for review](prepare-definition.md) to align its scientific/formal meaning, plain explanation and domain-context explanation, retain boundaries and source evidence, and name the applicable owner.

An already prepared Lab runtime proposal can be inspected through:

```bash
./define/define review --store /path/to/provisioned/lab-store --proposal /path/to/proposal.json
```

This prepares review only. It neither signs approval nor changes the Lab store. The specialized candidate review packages retain their separate contracts.

## 4. Hand off a ready candidate

The [CLI](../../../implementation/define-cli/v1/README.md) can compile a language-reviewed, current, unexpired Lab-bound pack through its selected Alch/Craft semantic profile. The output is candidate evidence, not implementation permission or proof of a consumer's outcome.

Read [the audit](../../../implementation/define-cli/v1/AUDIT.md) for exact verification and remaining model/adoption work.
