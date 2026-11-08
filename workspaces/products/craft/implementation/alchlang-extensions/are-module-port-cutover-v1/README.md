# ARE Module Port cutover contract

`cutover.alch` declares the startup cutover semantics before their host
implementation. The compiler produces the ontology, Craft graph and project,
DomainSpec projection, runtime prelude, and finite fixture evidence in
`generated/`.

The cutover contract requires exact activation selection and a passing admitted
Rust binding receipt before static Module Port composition. Any unreadable,
drifted, substituted, malformed, or failing input blocks the complete module
set without fallback. Successful verification grants no adapter effect,
publication, release, deployment, or external-hook authority.

The compiled bundle is construction evidence only. It does not itself adopt the
referenced Constitution, admit the cutover implementation, or activate a host
integration.

Build from the repository root:

```sh
node language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js check language/capabilities/alchlang/plans/general-compiler-v1/extensions/are-module-port-cutover-v1/cutover.alch
node language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js ontology language/capabilities/alchlang/plans/general-compiler-v1/extensions/are-module-port-cutover-v1/cutover.alch
node language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js build language/capabilities/alchlang/plans/general-compiler-v1/extensions/are-module-port-cutover-v1/cutover.alch --out language/capabilities/alchlang/plans/general-compiler-v1/extensions/are-module-port-cutover-v1/generated
```

## Open Questions

- Should a later admitted host profile use a prebuilt verifier artifact instead
  of the repository toolchain launcher?
