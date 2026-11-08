# Optional operational expectations

A profile can declare observation points, known failure codes, supported offline evidence families and a bounded disclosure policy. The generated file describes what should be checked. It supplies no observations and starts no collector, service or workload.

The supported family names match the existing Operational Resilience WP5 inventory: telemetry, health-failure, workload, fault, canary-analysis, deployment-observation and rollback-observation. Infrastructure-plan and compatibility families require separate qualification. A supported family name does not make its normalizer or evaluator available in this CLI.

Declarations, offline validation, replay, current observations, telemetry accounting, eligibility and runtime admission are separate states. Generated records report only declared expectations; the other checks are not run and runtime admission is denied. Existing ORODI offline/replay tools require separately supplied pinned inputs. Never copy a passing fixture result into a live observation field. No ORODI declaration is needed for base service generation. A requested live or otherwise unsupported mechanism rejects explicitly.

## Open Questions

Actual normalizer/sink selection, independent observation, telemetry conservation, live eligibility and owner admission require their own supported contracts and qualification. Local hosting, TDE, EVF and publication remain deferred.
