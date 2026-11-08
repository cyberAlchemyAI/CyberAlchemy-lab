# Interface validation sources

[openapi31-official.schema.json](openapi31-official.schema.json) is an unmodified copy of the [official OpenAPI 3.1 validation schema](https://spec.openapis.org/oas/3.1/schema/2022-10-07). Its exact digest is recorded in [the validation report](../receipts/interface-validation.json). The upstream specification and [upstream repository](https://github.com/OAI/OpenAPI-Specification) retain their authorship and licensing.

The OpenAPI schema checks specification structure. Each referenced payload schema is separately checked against JSON Schema Draft 2020-12 and resolved through a local reference registry. No schema identifier is fetched during these validations.

[The explorer report](../receipts/explorer-validation.json) records ten interaction checks across all 82 definitions. It uses Node with a minimal DOM event harness; it does not claim real browser rendering or accessibility testing.

Reproduce the checks from the repository root:

```bash
python3 -B craft/formalization/candidates/relational-theorem-checker/v1/interfaces/build_interfaces.py check
python3 -B craft/formalization/candidates/relational-theorem-checker/v1/interfaces/validate_interfaces.py
node craft/formalization/candidates/relational-theorem-checker/v1/interfaces/validate_explorer.mjs
```

The Python validator requires the local `jsonschema` and `referencing` packages. The explorer harness uses only Node built-in modules. All semantic checking, Lean proof validation, model satisfaction and actual API execution remain future DAG work.
