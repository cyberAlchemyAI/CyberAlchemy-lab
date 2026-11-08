<!-- Generated from candidates/0001-thin-end-to-end/candidate.json. Do not edit. -->

# Thin end-to-end Ontology Product candidate

- Candidate: `CAL-ONTOLOGY-AS-PRODUCT-CANDIDATE-0001`
- Version: `1.0.0-test-candidate.1`
- Status: `ready-for-product-testing`
- Authority effect: `none`

## Primary behavior

Transform one owner-selected source record into a deterministic governed ontology package and provide fail-closed validation, list/get retrieval, and a generated human projection.

## Acceptance criteria

- Equal source bytes build byte-identical ontology packages.
- The package validates against its closed schema and Rust semantic checks.
- Duplicate nodes, dangling relations, and non-none authority effects fail closed.
- List and get retrieve only declared nodes; unknown identities fail closed.
- Human views are generated and byte-current with their machine records.
- Product, Product Ontology, package output, Craft, contexts, and runtime identities do not collapse.

## Test

Run `PYTHONDONTWRITEBYTECODE=1 python3 product/products/ontology/v1/validate.py`.

Try the CLI:

- `cargo run --manifest-path product/products/ontology/v1/runtime/Cargo.toml --quiet -- validate product/products/ontology/v1/fixtures/valid/ontology-package.json`
- `cargo run --manifest-path product/products/ontology/v1/runtime/Cargo.toml --quiet -- list product/products/ontology/v1/fixtures/valid/ontology-package.json`
- `cargo run --manifest-path product/products/ontology/v1/runtime/Cargo.toml --quiet -- get product/products/ontology/v1/fixtures/valid/ontology-package.json demo.output`
- `cargo run --manifest-path product/products/ontology/v1/runtime/Cargo.toml --quiet -- project product/products/ontology/v1/fixtures/valid/ontology-package.json`

## Approval boundary

Product testing precedes one separate Product approval decision bound to the immutable candidate and product-test receipt digests.

## Claim ceiling

Ready for private Product testing only. This manifest does not itself prove tests pass, approve the Product, admit artifacts or contexts, adopt the runtime, publish, release, deploy, or retire source material.
