# Source-authored error presentation

`error-crm.profile.json` selects the original finite `craft.error-presentation/v1` consumer. `error-crm.alch` uses ordinary Calculation/Policy to choose an ErrorSpec, then the outside `ToErrorPresentation` Mapping builds the response description. `Build` returns all twelve typed rows. Its record invariants express count, uniqueness and valid category/status pairs; the consumer additionally compares rows with the complete actual reason enum.

`error-crm-domain.alch` is a self-contained fixture snapshot of the CRM reason enum. It is not an alternate canonical business model. Real application generation supplies or captures the actual business type source and binds the selected table to the original producer/Entry/application owner. A same-name enum or matching string is not enough; its exact checked nominal enum shape and producer must match.

The result has normalized finite numeric HTTP statuses and stable source/table identities. It contains only selected public code/message/category fields, not provider bodies, stack traces, tokens, source payloads or mutable retry authority. Auth/platform outcomes remain with their original owners. The table cannot grant access, convert an unknown write into no-effect or schedule a second provider call.

Using the matching working compiler:

```sh
alchlang profile check-source error-crm.profile.json --source-root .
alchlang profile compile-source error-crm.profile.json --source-root . --out /absolute/new-selection
```

The compiled selection preserves the original source closure and rejects altered descriptor/source bytes on reopen. Selecting it at a public HTTP or async boundary requires the original checked application join; compilation alone does not start a server or change any provider state.

## Open Questions

Bounded static message text is not a proof that the author chose non-sensitive words. Operator-authored messages must be appropriate for public exposure. Live provider/model qualification, hosting, TDE, EVF, deployment and publication remain deferred. See `docs/ERROR-PRESENTATION.md` for supported implementation and storage/version boundaries.
