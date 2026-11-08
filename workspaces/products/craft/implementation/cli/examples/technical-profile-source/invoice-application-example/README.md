# Business-only invoice draft application

This example selects `Profiles.InvoiceApplication` and keeps supplier verification,
PO/receipt reconciliation, quantities, tax, currency, totals and monetary approval
in ordinary Alch policies, mappings and operations. `PrepareDraftPosting` composes
reconciliation and typed enforcement; there is no JavaScript business predicate.

The reusable profile supplies document/source bindings, the original text parser,
model extraction, protected execution admission, Xero DRAFT command encoding and
original effect/inspection ownership. Actual human approval binds the original
paid model input/output, complete disclosed context, source/object version,
current disclosure policy and destination. Dispatch windows remain private.
No payment operation is selected.

`fixtures/business-cases.json` contains 15 clean domain cases. The environment is
an inert local-fixture identity, not credentials or a real-provider qualification.
Hosts still supply original resources, SDK credentials and private source records;
a new customer does not write gateway/model/provider callback glue.

## Open Questions

Real Xero/provider qualification, hosting, deployment, publication, TDE and EVF
remain outside this local implementation objective. The shared design owns any
further scope: `goals/plans/craft-service-profile-extensions-2026-11-02/DESIGN.md`.
