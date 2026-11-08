# Public client and commands

`api.Client` composes the accepted decoder, fixed supervised worker, owned proof runs, saved inspector, explanation reader and shadow transaction API. It retains the rule-only `rich-positive-recursive-v2` profile and the twenty required obligations. New language features remain separate selected extensions; this interface does not enable them implicitly.

Construct the client with an explicit operator resource policy. `qualify(original_bytes)` passes the original bounded input to the fixed worker. It returns a closed `relational.public-qualification/v3` envelope containing the original owned qualification and a public diagnostic. A successful call issues a private event within that client. The envelope itself has `application_authorized: false`: saving it, copying it, validating its schema or loading it into another client does not create the live event.

`inspect(request, envelope)` checks exact saved evidence and reports recorded currentness. `describe(request, envelope, query)` explains the checked result. Refused qualification yields an incomplete explanation, with no complete closure, absence or readiness claim. A present explanation includes bounded source support and a derivation trace. Absence means absence from the complete finite profile, not falsity in the external world or every possible model.

For a well-typed present query, explanation first inspects the exact proof and then selects the corresponding atom from its bound closure. Consequently an epoch written as JSON `0.0` can retrieve the trace for the natural number `0`. A Boolean `false` remains an invalid natural-number query. This is a finite parser/reader regression, supported by an abstract theorem about typed atom equality; it is not a universal theorem about JSON decoding.

`bootstrap(new_store_root, original_identity_extension_bytes)` establishes a shadow genesis from a fresh full check where before equals after. `Store.review(request, original_bytes)` freezes the exact expected head, request and optional ordered mappings for later application. `apply(review_binding, original_bytes, store, mappings=...)` checks the proposal freshly, checks the exact successor independently, checks every supplied mapped context freshly, and uses the accepted one-time transaction handle to commit. The success contract requires concrete before/after heads and a committed transaction, with one generation increment and exact snapshot/registration correspondence. It remains a local candidate operation with `authority_effect: none`.

The public diagnostic preserves the underlying record. The exact legacy atomic-tool deadline message is classified as `unknown-resource`; an elapsed whole-application budget also yields `unknown-resource` rather than user cancellation. A user stop before the budget expires remains `cancelled`. Neither outcome is a complete proof or publication capability. A committed application is not retrospectively downgraded by elapsed time.

The CLI exposes `qualify`, `inspect`, `describe`, `bootstrap`, `apply` and `recover`. Each command requires `--policy`; inspection/explanation also require `--result`, application requires `--store` and `--review`, and a specific explanation accepts `--query`. Python `Store.review` creates the review binding. CLI application performs new live checks within its own invocation; an earlier CLI qualification does not transfer a private event to it. Optional mapped-context composition is available through the Python API.

Example from the repository root, with an operator policy saved separately:

```sh
python3 craft/formalization/candidates/relational-theorem-checker/v3/p09/cli.py qualify \
  craft/formalization/candidates/relational-theorem-checker/v3/p09/layout-request.json \
  --policy /absolute/path/to/policy.json
```

Exit zero identifies a successful qualification, current saved inspection, successful local shadow operation or completed explanation. Refused typed outcomes exit 3; command/argument errors exit 2. Output files use exclusive creation and must be inside the P09 candidate directory. They are evidence documents, not live handles. Required aggregate memory enforcement needs a writable delegated cgroup configured by the operator; this host refuses that policy before launch. Advisory RSS sampling is not a hard memory cap.
