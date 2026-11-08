# Context local fixture: live-state loss observation

At 2026-10-20 15:04 UTC on WSL host `vlad`, the previously effect-reviewed Context staging attempt `/tmp/cal-context-family-20261020-0001`, its one-shot marker `/tmp/.cal-context-family-20261020-0001-one-shot.json`, and its external observer were absent. The predecessor Mapper, Reader and Source attempts selected by that stage were also absent. This is a present-state observation; the cause of removal is unknown. The WSL boot time was 2026-10-20 11:55:14 UTC, earlier than the recorded Context stage PASS at 14:35 UTC, so that boot alone does not explain the later absence.

The [independent stage effect review](CONTEXT-STAGE-RELEASE-INDEPENDENT-EFFECT-REVIEW-0001.md) remains evidence that the one-shot staging effect passed at its observed time. It is not a current filesystem or Docker mount. Its attempt name remains consumed, even though the marker has disappeared; it must not be reused or reconstructed as if unrun. Current Context authority issuance, finalization and original-role Docker launch refuse until a fresh selected Source→Reader→Mapper→Context family is constructed and independently reviewed. No grant or real Context run was performed after this loss observation.

The Compose local Work fixture is independent of these historical `/tmp` attempts and passed a fresh build and run on this host on 20 October 2026.
