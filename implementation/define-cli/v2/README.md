# Define v2 preparation candidate

Version: **0.2.0-rc.1**. This is an explicit successor implementation. **The complete operational release is not yet qualified.** The default `define/define` launcher still selects the preserved v1 implementation.

Define v2 constructs a task's Definition Pack, keeps local values and reported assessments inside it, and exports an exact reconstructable package. It does not execute domain assessments, admit meanings or approve a release.

## Run the incident example

From the repository root, use a new parent directory:

```bash
DEFINE_EXAMPLE_ROOT=$(mktemp -d /tmp/define-v2-example.XXXXXX)
./define/define-v2 doctor
./define/define-v2 example --output "$DEFINE_EXAMPLE_ROOT/input"
./define/define-v2 capture-snapshot \
  --request "$DEFINE_EXAMPLE_ROOT/input/request.json" \
  --output "$DEFINE_EXAMPLE_ROOT/capture"
./define/define-v2 prepare \
  --request "$DEFINE_EXAMPLE_ROOT/input/request.json" \
  --capture "$DEFINE_EXAMPLE_ROOT/capture" \
  --output "$DEFINE_EXAMPLE_ROOT/package"
./define/define-v2 inspect-package "$DEFINE_EXAMPLE_ROOT/package"
./define/define-v2 reconstruct-local "$DEFINE_EXAMPLE_ROOT/package" \
  --output "$DEFINE_EXAMPLE_ROOT/restored"
```

This actually produces:

- A reference to the repository-selected Authority meaning, with its original source bytes and captured registry basis.
- One local proposed complete-export criterion, explicitly bounded to a synthetic incident.
- One application with snapshot **S**, account **A**, filters **F** and expected row identities **E**. Filter keys have explicit fixture semantics.
- One **reported synthetic FAIL**: four observed rows against five expected rows. Define preserves that report; it does not perform or qualify the comparison.
- Exact request, capture and preparation report members, plus the selected original input bytes.
- A digest-bound manifest with the complete required member set.

The Pack can be inspected and its parameters examined. Its reported assessment remains unverified, and current owner review/governing application remain blocked. An exit code of zero means the named preparation/inspection completed; inspect the separate readiness results before selecting a later use.

No model call or credentials are needed for this example. The v1 conversational command remains available through `./define/define chat` and keeps its existing protocol. V2 authoring currently requires explicit structured input; it does not silently convert v1 chat output into the new contract.

## Commands and boundaries

| Command | Implemented behavior |
| --- | --- |
| `doctor` | Verify exact selected runtime files. Reports live-host qualification separately. |
| `example --output NEW` | Write attributable synthetic incident preparation input. |
| `schema request\|capture\|pack` | Export the closed executable schema. |
| `capture-snapshot --request FILE --output NEW` | Capture selected original repository/local bytes as historical input. No live Session or permission is claimed. |
| `prepare --request FILE --capture DIR --output NEW` | Construct a frozen Pack/report and full required input closure, or refuse unsupported/invalid inputs. |
| `inspect-package DIR` | Verify required closure and exact embedded bindings. |
| `reconstruct-local DIR --output NEW` | Restore verified exact required bytes to a new local directory. No governing record selection is inferred. |
| `observe-use DIR --requested-use USE --consumer ID --output NEW` | Record a separate later local observation. Changed intended use blocks; frozen Pack bytes remain unchanged. |
| `materialize DIR --output NEW` | For explicit selections only, require a complete Definition/v2 body, exact field lineage, consistent formal statement/boundaries/notation, bound schema/generator and an explicit owner-route label. Generate Markdown with the selected generator. The label is not qualified owner standing. |
| `compile DIR` | Refuse Pack/v2 as an unsupported legacy compiler input before effects. V1 compilation remains separate. |
| `retain-package`, `read-retained`, `stage-review`, `inspect-local-operation` | Require an independently installed, exact host selection and its actual supported native operation. No repository-snapshot, fixture-grant or historical-authorization fallback exists. |

Applications to external meanings without an explicit supported parameter declaration and mechanical contract are refused. No parameter schema is inferred from prose or notation. Claimed qualified external assessment execution is also refused until an actual producer/Method qualification adapter is selected. These limits are visible rather than silently weakened.

## What a configured Lab host means

A configured host is a **local Lab runtime plus its selected state, code, native authority verifier and operator permissions**. It does not require a separate server. Configuring it requires actual deployment inputs; running the incident example does not create them.

`host.py` consumes exactly one independently installed private `cal.define.lab-adapter-selection/v1` file. It pins the host, extension, protocol, source profile, schemas and complete dependency selection. It invokes only that selected host entrypoint, with a fresh nonce and exact request binding. Credentials remain with the host. A configuration file alone is not permission: the host must verify the actual issuer/principal/key/scope, operation, period, revocation and current source at the native boundary.

The current repository API17 reference still contains historical authorization checks. **No API17 authentication/routing override or qualified host deployment is supplied by this package.** The gateway cannot make those checks current by itself. This is a remaining platform integration requirement before the full reviewed design can be released.

`qualified-hosts.json` is intentionally empty and source-pinned. The gateway refuses an unqualified host **before executing its entrypoint**. A caller-created selection file, claimed authority posture or self-consistent digest set cannot add a qualified host. Adding the reviewed exact successor is a separate source/qualification/adoption step.

The host-side modules available for embedding are:

- `review.py`: original-byte native target/control construction, independent pure native simulation, immutable workspace inputs and an outer idempotent staging journal. It does not authenticate a new channel or execute `proposal.review` by itself.
- `custody.py`: bounded, anchored content-addressed objects, fsync/no-replace completion, receipt pins, idempotency and fresh-access cold reconstruction. Requires a host-owned gate and preselected private root; no CLI initializes an authority/store automatically.
- `resolve.py`: closed exact Work → Source/Evidence Set → retained-root traversal through a host-provided exact native lookup and schema validator. Candidate inspection remains explicit.

Synthetic test gates are defined only in tests. Passing those tests does not qualify real permissions or publication. The CLI does not expose test-key provisioning, owner signing or native apply operations.

## Persistence and privacy

Package members retain original bytes; new control records use sorted compact UTF-8 JSON with a final newline. Original-file, embedded-entry, Pack, manifest, native target and native core-file digests remain distinct.

Every required member must resolve before complete reconstruction. Traversal, unsafe URI forms, symlinks, duplicate IDs/keys, ambiguous selectors, unsupported precision, undeclared parameters and existing output destinations refuse. Honest open questions and reported failures survive reconstruction.

Retention rights default to unresolved. `capture-snapshot --permit-retention` is an explicit local assertion about the selected inputs; it grants no host permission. Private-key/credential/session-memory pattern checks are conservative refusal checks, not a proof that arbitrary content contains no secrets. An actual privacy/export review remains necessary where required. A required forbidden member blocks retention; bytes are never sanitized under an unchanged digest.

The retained store is host-owned and external to Git and review workspaces. Its receipt commits custody only. A separate governing Source/Work transaction must occur through the qualified native owner/application route before Project State can select those records. Neither publication nor deletion/garbage collection is performed here.

## Verify

Linux, Python 3.11+ and the selected dependencies in `requirements.txt` are required. This candidate was tested on Python 3.14.4. Atomic no-replace directory publication requires Linux `renameat2`; unsupported filesystems/platforms refuse.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s implementation/define-cli/v2/tests -v
python3 implementation/define-cli/v2/audit.py
./define/define-v2 doctor
```

The native-helper tests use a temporary synthetic Lab branch, public test data and no owner application. The v1 suite separately exercises its real Craft compiler path and native app-server startup without a model turn.

`contracts.py` is the executable format source. `schemas/` is generated by the explicit maintainer packaging step `python3 implementation/define-cli/v2/seal.py`. That step must follow source review; CLI execution never refreshes drift pins. Runtime integrity is a local consistency check, not a signature or release approval.

## Release standing

See [the release report](../../../define/development/runtime-v2-release/v1/RELEASE.md) for exact qualification results and remaining work. The [reviewed design](../../../define/proposals/0008-revised-runtime-integration-design/README.md) remains the target; local fixture coverage is not substituted for its live host, independent review, governing publication or fresh-Session acceptance cases.
