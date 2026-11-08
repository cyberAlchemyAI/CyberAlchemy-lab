# ARE Module Port Signed Envelope v1

`signed-envelope.alch` is the canonical L8 language declaration for exact
payload binding, offline failure, trust-posture separation, and zero effect
authority. Its finite fixtures exercise semantic non-collapse and ordered,
distinct failure reasons.

Compile through the standard Alch pipeline:

```sh
node language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js check language/capabilities/alchlang/plans/general-compiler-v1/extensions/are-module-port-signed-envelope-v1/signed-envelope.alch
node language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js ontology language/capabilities/alchlang/plans/general-compiler-v1/extensions/are-module-port-signed-envelope-v1/signed-envelope.alch
node language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js build language/capabilities/alchlang/plans/general-compiler-v1/extensions/are-module-port-signed-envelope-v1/signed-envelope.alch --out language/capabilities/alchlang/plans/general-compiler-v1/extensions/are-module-port-signed-envelope-v1/generated
```

The resulting candidate is not ontology admission, release approval,
publication, installation, deployment, or effect authorization.

## Open Questions

- Which authority may select a real signing identity and custody system?
- Which separately built platform envelopes should be supported next?
