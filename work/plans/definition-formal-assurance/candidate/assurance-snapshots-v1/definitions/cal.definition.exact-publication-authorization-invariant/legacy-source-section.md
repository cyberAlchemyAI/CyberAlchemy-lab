## CAV2-D57: Exact Publication Authorization

Status: active
Term: exact publication authorization
Aliases: two-step publication authorization, source-owner release authorization, exact-output publication approval, private-by-default release
Promoted: 2026-08-22 from accepted `GATE-08`; definition only, with no present publication effect

### Normative Definition

Exact publication authorization is the CyberAlchemy v2 rule that private
material may cross a publication boundary only after two separate decisions:

1. every source owner authorizes an exact candidate slice, its allowed claims,
   audience, channel, privacy policies, and requested publishing principal; and
2. after private generation and privacy validation, that publishing principal
   approves the exact final output bytes, digest, audience, channel, and claim
   ceiling.

The first decision permits creation and review of a private publication
candidate. It does not permit unknown future bytes to be published. The second
decision applies only to the exact output it binds. Any change to the sources,
claims, policies, generator, output bytes, audience, channel, or publishing
principal requires the applicable decisions to be repeated.

All material is private by default when no valid exact authorization exists.
Generation, validation, proof, obligation discharge, CAV2 promotion, or domain
adoption does not grant publication permission.

### Formal Interpretation

```text
PublicationAuthorization =
  (release_authorizations, exact_output_approval, publication_receipt?)

publishable(output, audience, channel)
  <-> every contributing source has a valid exact release authorization
      and privacy_validation(output) = pass
      and exact_output_approval binds
          (output bytes, output digest, audience, channel, claim ceiling)

generated(output) =/=> publishable(output, audience, channel)
validated(output) =/=> publishable(output, audience, channel)
promoted(output)  =/=> publishable(output, audience, channel)
```

Source owners and the publishing principal are separate authority roles. A
generator or validator may check that bindings exist and match; it cannot act as
either owner unless a separate authority decision explicitly assigns that role.

### Schema

Schema handle: `CAV2-D57-SCHEMA` — tracked in [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md).
Status: tracked (documentary).
Bound to: `CAV2-D57` exact publication authorization.

```text
ReleaseAuthorization =
  (source_owner, owning_system, source_refs, source_classifications,
   allowed_surface, forbidden_surface, claim_ceiling, audience,
   channel, policy_refs, publishing_principal, authorization_ref,
   validity_conditions, revocation_route)

ExactOutputApproval =
  (release_authorization_refs, generator_ref, generation_input_refs,
   policy_refs, privacy_validation_receipt_ref, output_ref,
   output_byte_length, output_digest, audience, channel, target,
   claim_ceiling, limitation_notice, publishing_principal,
   decision, decision_ref, validity_conditions, revocation_route)

PublicationReceipt =
  (output_digest, audience, channel, target_locator,
   publishing_principal, published_at, authorization_refs,
   observed_result)
```

All identities, versions, policies, decisions, source objects, inputs, outputs,
and receipts are owner-qualified, version-exact, and digest-bound where bytes
exist. `decision` is `approve | refuse`. A publication receipt records an
observed boundary crossing; it does not supply missing permission or make a
claim true.

### Operational Interpretation

Use this definition when someone wants to turn private DomainSpec, CAV2,
proof-substrate, Mint, Cedar, Datalog, Lean, research, evidence, or generated
material into a public-safe output. First ask each source owner exactly what may
be used and said. Generate and check the candidate privately. Then ask the named
publishing principal about the final bytes, not a template or promise. If any
bound input or output changes, return to the relevant decision.

### Plain-Language Intuition

Permission to prepare a public draft is not permission to publish it. Owners
first approve the ingredients and limits; a publisher later approves the exact
finished file and destination.

### Domain-Context Voice

In CyberAlchemy v2 this definition keeps the private authority spine and its
domain evidence private while still allowing a later, deliberately bounded
public explanation or result. A generated documentation page remains a private
projection until both decisions exist. Public Arcanum receives no private prose,
proof internals, engine mechanisms, research, or validation material merely
because a generator or checker succeeded.

### Boundary

Exact publication authorization is not classification authority, adoption,
promotion, proof, truth, freshness, privacy validation, deployment, or release by
itself. It does not create a universal classification vocabulary: each source
owner retains its own meanings, and a projection carries exact owner-qualified
references without reinterpreting them. It authorizes no present public output;
every actual publication still needs exact permissions and a boundary-crossing
receipt.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../../SOURCE-MAP.md](../../SOURCE-MAP.md)
- [../boundaries.md](../boundaries.md)
- [../../../research/2026-08-20-domainspec-v2-cav2-proof-obligation-substrate/development/refinement-runs/20260821T145409Z-proof-substrate-next-steps/stages/10-gate-01-top03-refresh/apply-corrected/owner-decisions/GATE-08-DECISION.md](../../../research/2026-08-20-domainspec-v2-cav2-proof-obligation-substrate/development/refinement-runs/20260821T145409Z-proof-substrate-next-steps/stages/10-gate-01-top03-refresh/apply-corrected/owner-decisions/GATE-08-DECISION.md)
