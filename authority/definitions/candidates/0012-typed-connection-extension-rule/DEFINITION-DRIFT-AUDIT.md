<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# Typed Connection Extension Rule Definition Drift Audit

> Candidate evidence; this view is not canonical.

## Summary

- Block: `0`
- Pass: `3`
- Total: `4`
- Warning: `1`

## Findings

### TCER-D1 (semantic-drift, resolved-in-candidate)

The relation model previously allowed wildcard endpoints, conflicting with the named-endpoint requirement of the admitted Typed Coupling Invariant.

Target: `authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json`

Remediation: Resolved in the relation candidate by replacing wildcards with exact ordered endpoint pairs; admission remains pending.

### TCER-D2 (ambiguity, resolved-in-candidate)

Separate source and target projections could be misread as authorizing their Cartesian product.

Target: `authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json`

Remediation: Make allowed_endpoint_pairs canonical and treat source_kinds and target_kinds as projections only.

### TCER-D3 (undefined-critical-term, open-owner-decision)

The extension rule existed only as relation-model prose and therefore lacked canonical semantic authority.

Target: `authority/definitions/candidates/0012-typed-connection-extension-rule/definitions/typed-connection-extension-rule/v1/definition.json`

Remediation: Review and, if accepted, admit cal.definition.typed-connection-extension-rule before Relation Kind admission.

### TCER-D4 (semantic-closure, resolved-in-revised-candidate)

The earlier candidate closed endpoint pairs but left carrier resolution, qualifier schema closure, local/global scope, canonical relation authority, contestability, and effective predecessor resolution outside the Definition.

Target: `authority/definitions/candidates/0012-typed-connection-extension-rule/definitions/typed-connection-extension-rule/v1/definition.json`

Remediation: The revised candidate makes those checks required before a connection can become effective.

## Claim ceiling

Definition-level drift evidence only; it does not admit the Definition or any endpoint connection.
