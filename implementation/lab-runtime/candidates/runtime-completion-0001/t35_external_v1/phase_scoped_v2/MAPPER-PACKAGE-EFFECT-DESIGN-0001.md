# LC-U02-05 disposable Mapper package construction, design 0001

Status: **HOLD for effect implementation**. `mapper_package_plan_0001.py` is
inert. It pins and inspects the historical Mapper builder, current generated
role, selected native CLI source and runtime bridge, and checks proposed native
arguments and package leaf names. It does not create or qualify a package.

The historical `mapped/build.py` executes `guard(pin)`, creates
`mapped/packages/0001`, projects the current signed Source/Reader cut, seals
semantic events, seals governance events, writes numbered event files and a
request, performs two cold native reads, and emits `native-output.json`,
`mapping.json`, `build-result.json`, and `manifest.json`. A 35-event historical
package has 75 leaves including the manifest. This is a shape example, not a
substitute for fresh signed data. The selected CLI has exactly two forms:
`seal-fixture <input>` and `<semantic-dir> <governance-dir> <request.json>`.
The proposed four calls are two seals followed by two identical cold reads.
The pure plan renders a full exact Bubblewrap/loader argv for each: four
read-only selected native/ABI mounts plus one read-only input or package mount,
with no writable mount in a native child. It does not verify that Bubblewrap
accepts the proposed nested directory mounts or that the copied ELF produces
the nonempty outputs.

The present generated role is deliberately incapable of that effect. Its
`build()` package-directory creation, `emit()` directory/open calls, and
`seal()` temporary-directory/input-write calls are rewritten to
`_t35_effect_refused()`. Its `call()` uses `runtime_bridge.run_native`, which
unconditionally refuses. These are multiple independent blockers. Simply
making the family writable or monkeypatching the refusal would discard the
selected-input and effect boundary. A second incompatibility is structural:
the original builder requires `0001` **absent** before it calls `mkdir`, while
a sandbox with only `mapped/packages/0001` writable requires that directory
to exist before launch. A versioned, exact-preimage builder adapter must
replace that create step with a held empty-directory assertion. The adapter
must not open a general file or subprocess capability.

The next effect controller should build one fresh Source→Reader→Mapper family
as in v5, hold predecessor byte identities through every child, and add a
fourth Mapper package child only after guard/refusal observations. The package
child receives the selected snapshot, predecessor family and generated role
bytes read-only, plus only a precreated empty
`mapped/packages/0001` read-write bind. Its adapter delegates each package
leaf to a mediator that accepts only an exact relative leaf under `0001`,
creates it no-replace through a held directory fd, fsyncs and reads it back.
The mediator receives the two in-memory seal payloads and writes private
bounded native inputs outside the family; no temporary input is left in the
package. Native children see those inputs or the package read-only, the
selected copied ELF/ABI read-only, and no protected roots. They receive no
writable mount. They have bounded stdout/stderr, exact argv checks, a deadline,
held process-group closure, and scratch retention on UNKNOWN. The mediator
validates the two sealed event arrays, the two byte-identical cold reads,
request/cut joins, output bounds and no-authority fields before returning
bytes to the builder. It never accepts arbitrary paths or commands.

After the builder exits, the controller verifies a closed numbered
semantic/governance file set and exactly the five other package leaves;
verifies per-leaf digests, manifest entries, source/Reader/Mapper bindings,
native outputs and package result; rechecks all predecessor bytes; rejects
any Context leaf or activation artifact; and publishes one sanitized,
no-replace receipt. A failure or uncertain child/group state retains scratch
and refuses a PASS. Any later Context work needs a distinct selected binding
and invocation; the historical Context path calls `MAPPED.guard`, requires
the Mapper manifest pin, and replays the native cut. This package slice does
not grant Context, host permission, Source8 protected authority or activation.

Effect implementation must first resolve the adapter's exact generated-byte
preimage, its mediated IPC and held-fd write protocol, size/count bounds from
fresh signed input, the native nonempty-event output schema, sandbox
overmount behavior, package-directory initial-state contract, process closure
and receipt publication. Pure tests here establish only static topology and
argument/name rejection. The earlier empty-input smoke covers only native
serialization. Protected containment still requires the LC-U03-02 cgroup
oracle; original-process-group observation cannot exclude escaped sessions.
