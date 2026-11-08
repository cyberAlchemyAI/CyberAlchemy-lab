# Portable family construction

This directory owns disjoint generic Source/Reader/Mapper/Context code and
per-install control metadata for the exact signed 4636 dataset. It modifies
neither API73 nor the active original family/native installation.

`PROJECTED-CODE-0003.json` maps 24 prepared Python files to their installed
logical paths **inside a fresh installed repository**. This keeps signed
material references and original record-index locators intact. The current
checkout's original t15 code remains unchanged. The generic code requires
the trusted `cal_installed_runtime_selection_v1` provider before import and
reads host identity, installation and manifest pins from its closed slots.

`METADATA-TEMPLATES.json` supplies 55 sealed family template inputs plus
their stable package-member projections. The constructor code pin in that
initial export was superseded by `CONSTRUCTOR-CODE-PINS-0005.json`; template
contents and template-member bindings are unchanged. The packager also adds
its API source/profile templates and an unqualified cold-receipt template.
The two generic role-loader/control helpers have distinct t25 paths, preserving
the old helper bytes used by historical schema-execution dependencies.

`metadata.Constructor(root, package_sha).initial()` operates only on an owned
fresh stage selected by its package manifest. It checks the fresh native
receipt/identity and original private archive digest, creates the actual host
role/archive handle, and refreshes explicit metadata file bindings. Stable
member digests come from the independently selected package manifest;
generated metadata digests come from their actual current bytes. Undeclared
file locators refuse. Materialization and the trusted bootstrap verify the
full physical stable closure before Source or runtime imports. It does
not rewrite arbitrary scalar digests, signed history, sealed native events,
the engine runtime profile or the 26 original Source Artifact bodies.

Initial exports contain explicit `None` for the API source/profile, Context
package/delivery and cold observation. Existing template files are never
called qualified future results. The provider permits only a construction
child to use this provisional selection; API runtime activation rejects it.

`construction_child.py` requires the trusted launcher to have activated the
exact private receipt with the construction purpose and matching repository.
It reuses that selection without activating another provider, performs
two actual independent native Source replays with original-byte parity and
cleanup checks, and rebuilds Context using the original producer. Only its
declared derived Context package outputs are removed before construction.
The child exits before the installer emits final pins and a ready receipt.
The final installer then calls `finalize()`, which refreshes the actual new
Context and native cold outputs without restoring template bytes, converges
the API source/profile/rebind pins and checks the 26 original Source bodies.
It returns bindings with an explicit unqualified ceiling. The installer seals
a separate ready receipt and qualifies a fresh process against the actual
installed bytes and native root.

Current verification is component/static only: eight metadata-capture/binding
tests, three code-projection/import-boundary tests and four construction
bootstrap boundary tests pass. Full construction,
native cold/Context replay and fresh-install qualification remain required.
