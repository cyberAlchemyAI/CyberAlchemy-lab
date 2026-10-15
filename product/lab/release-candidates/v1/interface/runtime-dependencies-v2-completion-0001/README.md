# Explicit Linux execution dependency closure

This successor preserves the frozen v1 package and all original locator and
source-proof bindings. The original interpreter/native paths in `/tmp` are
currently absent. Their byte-identical retained public copies in v1 are selected
explicitly here; no signed original locator is rewritten or treated as live.

`closure.py` selects the original eight R02 wheels, retained CPython3.14.4/native
executables, public `/usr/lib/python3.14` standard library, SQLite extension,
and recursively declared ELF libraries. `readelf` inspects files without
executing them. The inspection tool is itself hash-bound. Site customization,
development symlinks, cache files and host site/dist packages are excluded;
the exclusions are visible in the selection. Every runtime and wheel ELF edge
must resolve to a selected node. Missing or altered bytes, wrong architecture,
unknown fields, omitted stdlib files or omitted wheel ELF nodes refuse.

Public system ABI bytes are classified as `host-dependency-public-system-bytes`
before copying. Private signing keys, grants/custody secrets, live databases and
operator state are excluded and require separately selected protected inputs.
The original API16 source manifest retains all 24,497 proof rows and is bound in
full; the smaller execution closure never replaces that provenance manifest.

Installation creates an exclusive new child under an independently identified
owned mode0700 parent. It retains partial failures and prior generations. It
copies original bytes with explicit modes, then verifies the complete installed
file set before running bounded cold probes. All Python module origins and
mapped files in those probes must remain inside the new installation.

The execution configuration is explicit: `LC_ALL=C`, Python `-I -X utf8 -B -S`,
no inherited ambient environment, and the selected local dynamic loader with
its cache disabled and the selected local library path. This retains UTF-8
text/file encoding without loading implicit host locale/gconv data. It is not a
claim that arbitrary locale configurations, GUI features, external DNS/network
or arbitrary third-party dynamic loads are supported.

Cold probes exercise actual SQLite transactions with UTF-8 text, the original
R02 package versions, JSON Schema validation, Ed25519 signing/verification,
compression, and native ABI entrypoint refusal. They do not prove native
history replay, protected-input provisioning, final API17 startup, service
activation or deployment on another host. The legacy `NativeReadStore` invokes
the native executable directly with inherited environment; its successor
launcher/host selection must be integrated separately before transferring the
local-loader proof.

The selected public bytes are reproducibly staged on this exact Linux/x86_64,
glibc2.43 host. The coordinator must bind the v2 selection digest and separately
frozen installed native/interpreter locators into API17; original source pins
and old receipts cannot qualify changed code or new locators.
