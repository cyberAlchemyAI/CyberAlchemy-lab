# ORODI Alert Profile Definition Candidate

Status: candidate. Authority effect: none.

`ORODI-ALERT-PROFILE` defines the reusable semantic contract for ORODI alert
construction. It separates the meaning of an alert from the syntax used by an
alerting platform.

The construction shape proposed by this pack is:

```text
ORODI Alert Profile
  -> context-owned Alert Rule Set
  -> deterministic Platform Renderer
  -> Rendered Alert Artifact
  -> commissioning evidence
```

Alert evaluation and notification delivery are separate:

```text
Alert Evaluation != Notification Delivery
```

The profile preserves five evidence states: `normal`, `pending`, `firing`,
`no_data`, and `error`. Missing telemetry and evaluation failure both require
fail-closed operator attention, but they retain different meanings. Neither is
converted into healthy evidence.

The existing Body War Grafana rules are selected evidence for this candidate.
They are not the reusable standard, and this package does not modify or adopt
them.

## Validate

From the repository root:

```bash
python3 cyberAlchemy-v2/define/candidates/orodi-alert-profile/validate.py
```

The validator checks concept coverage, all three definition voices, state and
failure-meaning separation, notification separation, platform neutrality, and
the exact digests of selected sources.

## D65 boundary

This package is only the canonical-definitions candidate input. The following
remain separate owner decisions and successor artifacts:

1. immutable Product Capability adoption;
2. capability-local business ontology admission;
3. DomainSpec v2 authored source and admitted projection;
4. deterministic compiled graph and system ontology;
5. exact implementation binding for a compiler and first platform renderer;
6. conformance and commissioning evidence.

No file here enables a notification destination, uses credentials, performs an
operational action, publishes, releases, or deploys anything.
