# ISB-04 implementation plan

Status: completed owner-authorized bounded construction, 2026-09-07. Authority effect: none.

D65: [Define-backed meanings and scaffolds](../service-contracts-v1/README.md) ->
[selected service/route contract](../service-contracts-v1/service.example.json) ->
this unit -> service compiler and authored functions -> generated host regressions.
This is an explicit implementation request for the already-bounded ISB-04 target.

The existing multi-entry service compiler and its source remain supported.

1. Extend the existing `service-v1` profile with explicit `assembly public-routes-v1` with local function imports, typed native
   operation declarations, route method/path/input/response bindings, service
   limits and an imported compiled error policy. Resolve source paths and types;
   reject duplicate routes, missing references, mismatches and unsupported modes.
2. Generate a Node service callable, deterministic route/type manifest and source
   trace. Reuse declarative and pure-iteration builders. Require exact native
   operation bindings when constructing the handler; validate their JSON outputs.
3. Author health and inference response contracts and assemble the four existing
   public routes. Move routing, body/media/size handling and normalization into
   the generated service. Preserve provider dispatch and custody behind the typed
   inference binding. Reuse a generic Node socket/stream adapter.
4. Forward request cancellation through generated function and service boundaries;
   bound request body reads. Keep incremental SSE parsing, transitions and provider
   settlement in their existing implementations for ISB-05..07.
5. Pass all 59 existing regressions and new build/runtime negative witnesses,
   including missing bindings, type mismatches, unsupported stream targets,
   changed route definitions, response bounds and cancellation. Record evidence
   and advance both Craft plans to ISB-05 only after acceptance.

Operational support: the shared repository Rust/C toolchain is verified; the
existing sibling DomainSpec compiler binding and TypeScript compiler remain
build prerequisites. No live provider, deployment, storage purchase or tenant
security decision is needed for this unit. No causal blocker is known.

Write scope: Alch service compiler/runtime/CLI, generated-boundary cancellation,
inference service definitions/host/build adapters/tests, unit evidence and the
linked DomainSpec/Alch Craft plan surfaces. No frozen DomainSpec definitions or
compiler sources are selected for mutation.

## Open Questions

- Native operation implementation remains explicitly supplied until ISB-05..07;
  assembly cannot claim that provider, stream or custody policies are generated.
- JSON-or-SSE assembly validates transport mode; event payload/lifecycle typing
  remains ISB-06. Rust multi-route service generation is not selected.
- Tenant authentication and authorization remain ISB-09, last.
