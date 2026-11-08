# Define / Lab local integration

An explicit connector between standalone Define request/Pack v3 and the current
Lab v2 native runtime. Run it as `./define/define lab ...` or `./define/define-lab ...`.
The existing v1, v2 and standalone commands retain their contracts.

## Local operator setup

Provision a **new external directory** with a named principal. Its parent must exist.
The setup creates a fresh Ed25519 key, a native local store and a signed 24-hour
operator grant. Private keys never enter the repository or the store. The grant
binds this checkout, connector bytes, source snapshot, local UID, project and scope.

```bash
./define/define lab doctor
./define/define lab setup --home /absolute/private/define-lab-operator \
  --principal 'person:<vrondelli>' --store-id define-lab-user-journey
./define/define lab status --home /absolute/private/define-lab-operator
```

This establishes the requested user's **local operator scope**. The principal is
local-user-declared; external identity verification, canonical repository role
activation and public release qualification are not inferred. Local grants cover
only definition and artifact-instance admissions, not Artifact Type changes,
revisions, withdrawals, canonical repository admission or external publication.
The legacy v2 gateway and its qualification catalog are unchanged; this connector
does not claim to be a qualified deployment of that gateway or protected Source8.

Run `renew --home ... --hours 24` explicitly to renew a current-source operator.
Renewal invalidates prior captured contexts. Creating an owned `REVOKED` file in
the operator directory immediately blocks operations. Source/dependency changes
require explicit successor selection; renewal never silently rebases a store.

## Exercise User Journey

Use a new working directory whose parent exists. The example authors a genuine
candidate using the repository's new User Journey Definition/v2 and the native
Product definition; no model call or synthetic permission issuer is used.

```bash
./define/define lab example --home /absolute/private/define-lab-operator \
  --output /absolute/work/input
./define/define lab prepare --home /absolute/private/define-lab-operator \
  --input /absolute/work/input --permit-retention --output /absolute/work/package
./define/define lab review --home /absolute/private/define-lab-operator \
  --package /absolute/work/package --id user-journey-0001 --output /absolute/work/review
```

`example` closes its native Session after capturing selected source-bound views.
Its signed context binds the project, scope, source snapshot, current native head,
operator grant and expiration. Session scratch memory is never retained. The core
Pack remains a standalone local-snapshot Pack; the signed context is explicit
evidence, not a forged host-member/current-permission claim inside that protocol.

`prepare` verifies context before and after preparing exact bytes. Retention rights
remain unresolved unless the caller supplies `--permit-retention`. `review` retains
the complete permitted Pack, materializes the complete Definition with field-level
lineage, and constructs native Definition, Source and Work targets. Native review
independently validates those targets. `mapping.json` distinguishes original file
digests from the native record encoding. No v3 Pack is passed to a v2 Pack parser.

The review has **no owner outcome**. Inspect the candidate and review before
selecting the separate local authorization/application commands:

```bash
./define/define lab authorize --home /absolute/private/define-lab-operator \
  --proposal /absolute/work/review/proposal.json --output /absolute/work/approval
./define/define lab apply --home /absolute/private/define-lab-operator \
  --proposal /absolute/work/review/proposal.json --approval /absolute/work/approval/approval.json
./define/define lab reconstruct --home /absolute/private/define-lab-operator \
  --work work:define-lab:user-journey-0001@candidate.1 --output /absolute/work/restored
```

Authorization signs the exact native proposal and expected head, using the
explicitly provisioned local operator. Application creates a real signed local
native transaction. This is not an actual canonical repository owner outcome or
an independent semantic-fidelity review. The authored definition remains a
repository candidate. A retry of the same committed proposal/approval returns the
original native transaction; changed inputs under the same identity refuse.

A fresh invocation reconstructs from committed Work -> exact Source -> digest-bound
retained Pack and signed custody receipt. It verifies every member using standalone
Define. It restores exact frozen bytes, not Session memory or current-use permission.
Unknown native/write outcomes must be inspected before another operation is issued.

## Validation and boundaries

```bash
python3 -B authority/definitions/candidates/0017-user-journey/render.py
python3 -B implementation/define-cli/lab-integration/v1/seal.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s implementation/define-cli/lab-integration/v1/tests -v
```

Rendering and sealing are explicit maintainer operations after source review.
Commands never refresh integrity pins. The runtime remains source-linked to this
checkout and its admitted Lab baseline. Independent project bootstrap, a portable
installed connector, team artifact-server configuration, external issuers and full
operational release qualification are additional scopes. Existing installations,
keys, stores and failed pilot evidence are preserved.
