# Shared Lab integration

`define lab workspace ...` delegates directly to `implementation/lab-runtime/lab.py`. Define is the existing Product workspace `product/define`, with zero linked Projects and the inherited shared runtime. Use explicit selected Project/store bindings for Project-owned effects. The actual native host performs review, authorization and apply; this adapter neither grants permissions nor creates native owner outcomes.

The removed connector's implicit migration Project, fixture store initialization and User Journey shortcut are not current interfaces. Use `define example`, supply actual context, and follow the native candidate package workflow. See README.md and work/development/alchlang-only/SHARED-RUNTIME-VERIFICATION.json.
