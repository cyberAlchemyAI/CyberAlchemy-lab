<!-- Generated from product-test.json. Do not edit. -->

# Ontology-as-a-Product product test

- Result: `PASS`
- Candidate: `CAL-ONTOLOGY-AS-PRODUCT-CANDIDATE-0001`
- Checks: `14/14`
- Candidate digest: `ca6164f064e553c63bce6754623de58e29e5c939d6cba2c310d6edf5f7950fbe`
- Material digest: `597de8781fffb4a44518338c017b76a6f41bc4474e85922429eed66de328e55e`

## Checks

- `PASS` — `OAP-01-SOURCE-CLOSURE`: all seven exact prototype dependencies match their bound digests
- `PASS` — `OAP-02-PRODUCT-IDENTITY`: Product identity, core output, and no-authority posture are explicit
- `PASS` — `OAP-03-PRODUCT-ONTOLOGY-SEPARATION`: Product Ontology represents three distinct Product graph roles
- `PASS` — `OAP-04-GENERATED-LABELS`: Ontology-as-a-Product and Product Ontology remain generated labels
- `PASS` — `OAP-05-CLOSED-SCHEMAS`: source and package instances validate against closed Draft 2020-12 schemas
- `PASS` — `OAP-06-RUST-TESTS`: all Rust library and CLI tests pass
- `PASS` — `OAP-07-DETERMINISTIC-BUILD`: two independent builds equal the committed package byte-for-byte
- `PASS` — `OAP-08-PACKAGE-VALIDATE`: the built package validates with three nodes, two relations, and no authority effect
- `PASS` — `OAP-09-BOUNDED-RETRIEVAL`: list/get retrieve declared nodes and unknown identities fail closed
- `PASS` — `OAP-10-RUST-PROJECTION`: Rust projection equals the committed generated human view
- `PASS` — `OAP-11-HOSTILE-FIXTURES`: duplicate identity, dangling endpoint, and authority inflation fixtures all fail closed without output
- `PASS` — `OAP-12-GENERATED-HUMAN-VIEWS`: all seven human projections equal their canonical machine records
- `PASS` — `OAP-13-MATERIAL-CLOSURE`: candidate declares exactly 17 existing unique material files
- `PASS` — `OAP-14-CANDIDATE-BOUNDARY`: candidate is ready for testing but not approved or authoritative

## Try it

```bash
cargo run --manifest-path product/products/ontology/v1/runtime/Cargo.toml --quiet -- validate product/products/ontology/v1/fixtures/valid/ontology-package.json
cargo run --manifest-path product/products/ontology/v1/runtime/Cargo.toml --quiet -- list product/products/ontology/v1/fixtures/valid/ontology-package.json
cargo run --manifest-path product/products/ontology/v1/runtime/Cargo.toml --quiet -- get product/products/ontology/v1/fixtures/valid/ontology-package.json demo.output
```

## Residue

- Legacy cav2.ontology-product source-registry drift remains open for source-preserving migration.
- Governance v3, Ontology Lifecycle v3, and their Context Map remain candidate-unadmitted.
- No human Product approval decision is recorded.

## Claim ceiling

PASS proves this exact private thin candidate deterministically builds, validates, retrieves, and projects one governed ontology package while rejecting the exercised identity, endpoint, and authority failures. It does not prove general user value, production durability, context admission, runtime adoption, Product approval, publication, release, deployment, or migration completion.
