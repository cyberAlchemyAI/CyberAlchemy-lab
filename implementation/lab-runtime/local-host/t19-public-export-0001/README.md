# T19 public fixture export, local technical slice

The selected API36 `test_export_kernel.Exports` class cannot replay its built-in
`custody-participation` fixture in the current host process. API36's selected
source manifest pins Python 3.14.4, `jsonschema` 4.19.2 and `cryptography`
46.0.5. Its `source_bridge.custody_delivery()` selects
`current-context-delivery-v2-action-0148`, which opens
`current-participation-v5`. That Source manifest pins `jsonschema` 4.23.0.
The source's environment guard refuses before the historical Intent/Goal
material can be selected. Changing the package version in this process would
instead invalidate the unchanged API36 guard. This slice does not alter either
selected package or claim the historical custody test passed.

`run.py` constructs a separate technical selection from the two **public**
Intent/Goal fixture files listed with exact SHA-256 values in API36's selected
32,138-row contract profile. It checks the API36 source/profile/kernel/protocol
pins, runs its real source and schema guards, and calls the unchanged
`ExportHost`. Its source callback rechecks the selected public fixture bytes
at each export boundary. The private 0700 working root retains the published
generations for cold readback. `verify.py` independently reads their physical
files, manifests, receipts and publication markers.

The observed `RESULT.json` records two published modes (`byte-exact`,
`rendered`) with exact replay, three preclaim refusals (parent traversal,
absolute path, unmanaged overwrite), and preservation of a foreign file.
Run `python3 -B run.py` and then `python3 -B verify.py` from any directory.
The first run took 57.683 seconds here. Reruns use the exact existing
generation, and changed or pending generations are refused by the kernel.

This result supports a local technical AC07 implementation slice only. The
selected input is public profile-pinned fixture data, not the historical
signed custody source or the protected current Source8 family. It grants no
owner decision, current Agent participation, admission or canonical release.
Closing the original source-backed T19 route needs a compatible selected
source/API cut or a reviewed cross-environment Reader handoff that preserves
the signed source and current guard semantics.
