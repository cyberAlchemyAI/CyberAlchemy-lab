<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Measurement Method Fixture

- Identity: `measurement-method:definition-normalization-residue-entropy`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Authority Treatment**: `non-governing`
- **Challenge Route**: `route:measurement-challenge`
- **Claim Ceiling**: `The method defines one finite residue-entropy observable. It does not supply a result, prove novelty, or determine authority.`
- **Claim Status**: `review`
### Conditions

```json
[
  "The source set and normalization revision are fixed",
  "Every unresolved term belongs to exactly one declared residue class"
]
```

- **Entropy Register**: `finite-probabilistic`
- **Interpretation**: `Higher entropy means unresolved terms remain distributed across more distinguishable classes in this normalization run; it is not generic disorder or automatic promotion.`
- **Kind**: `measurement-method`
- **Mathematical Reading**: `H(R) = sum over unresolved term classes of -rho(x) log rho(x).`
- **Name**: `Definition normalization residue entropy`
- **Observable Kind**: `shannon-entropy`
- **Owner Ref**: `role:artifact-type-owner`
- **Owner Route**: `role:measurement-owner`
- **Procedure**: `Classify every unresolved source term after normalization, compute its empirical probability mass, then calculate Shannon entropy over the finite class set.`
- **Property**: `residue entropy`
- **Residue Type Ref**: `residue:unresolved-source-term`
- **Scope Kind**: `probabilistic`
- **Scope Ref**: `scope:cyberalchemy-lab-model-review`
- **Source Operation Ref**: `operation:normalize-source-terms-to-definition-identities`
- **Uncertainty Rule**: `Report bootstrap interval over source-term resamples and preserve the class counts.`
- **Unit**: `nats`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
