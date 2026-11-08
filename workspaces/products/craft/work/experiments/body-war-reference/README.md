# Body War reference application

Body War is a reference application of Craft operational-resilience concepts. Its source remains under the existing implementation home to preserve imports. The reference covers canary routing, telemetry, evaluation, rollback, observation, projection and local infrastructure definitions.

- [Application classification and source references](application.json)
- [Reference design](../../../implementation/operational-resilience/BODY-WAR-CANARY-LAB.md)
- [Current source validation instructions](../../../implementation/operational-resilience/BODY-WAR-CANARY-VALIDATION.md)
- [Craft Work](../../README.md)

Source presence is separate from current functional or runtime qualification. This import starts no service, Docker project, workload or rollback operation. Craft's generic product capabilities remain candidates; this application does not establish their production readiness.

The complete current no-effect suite passes 33 Node tests, 16 Python tests and contract/static validators. Its dependency contract checks the current Node version and exact TypeScript/TSX manifests; obsolete captured Poker Team/image metadata was removed. [Broader qualification](../../outcomes/current-verification/broader-qualification.json) records the result. These checks do not establish live reference operation.

## Open questions

Reference execution, image readiness, live telemetry, restoration and commissioning remain unqualified. No historical result or captured run is imported to fill those gaps.
