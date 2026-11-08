# Independent parcel quote fixture

This bounded test fixture reuses existing service, operation, schema, mapping
and error concepts. Quantity is an integer from one through ten. A shipment of
up to five parcels costs 1000 cents; a larger shipment costs 2000 cents. Currency
is USD. These are candidate fixture rules, not a commercial pricing commitment.

[service.alch](service.alch) declares GET `/health` and POST `/v1/quotes`.
[request.alch](request.alch) validates the input, [calculate.alch](calculate.alch)
authors the two prices, [receipt.alch](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/reuse/quote-service/receipt.alch) validates the operation result,
and [errors.alch](errors.alch) selects HTTP failures. No inference modules,
provider catalogs, model aliases, messages or token usage are imported.

## Open Questions

The parent [reuse artifact](../README.md#open-questions) owns remaining questions.
