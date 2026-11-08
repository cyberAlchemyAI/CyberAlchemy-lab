# ARE Module Port packaged verifier contract

`packaged-verifier.alch` declares the L7 artifact identity and startup
semantics before their host implementation. Its compiled projections and
fixtures are finite construction evidence only.

The candidate binds one Linux x64 release binary to the exact admitted Rust
source set and target triple. Startup must verify the Alch build, artifact
manifest, platform, regular executable bytes, and SHA-256 digest before running
the verifier. Missing or invalid artifacts block without Cargo fallback or
partial Module Port composition.

Packaging does not install the artifact outside this repository, activate new
entry points, authorize effects, publish, release, or deploy anything.

## Open Questions

- Which separately built and tested artifact should represent another operating
  system or architecture?
- Should a future distribution envelope sign the artifact manifest in addition
  to its current exact local digest binding?
