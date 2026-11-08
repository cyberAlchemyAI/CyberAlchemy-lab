# Lab local Docker environment

The active [local implementation stream](../../../docs/plans/0011-lab-runtime-completion/runs/0001-execution/IMPLEMENTATION-STREAM-20261022.md) tracks the full engineering product. This command runs its current fixture demonstration; it is a working starting point while the remaining runtime tasks are implemented and tested.

For a short operator walkthrough, see [Run the local Docker Lab](../../../docs/lab/runtime/tutorials/local-docker-product.md).
For package and test entrypoints, see the [developer guide](DEVELOPER.md).

Run the complete **disposable local product demonstration** from the
repository root with one command:

```bash
implementation/lab-runtime/local-host/run-local-product.sh
```

The [22 October final run](working/t07-contained-package-20261022/RELEASE-v3.json)
and [independent review](working/t07-contained-independent-review-0003/REVIEW.md)
pass this disposable local package and cleanup. The broader 36-task runtime
remains tracked in the implementation stream above.

It builds/runs the four-phase Source→Reader→Mapper→Context fixture and the
admitted-v1 Work journey in sequence, then removes both containers. Both run
as container UID/GID 20001:20001 and have no persistent application state. The launcher
requires Docker Compose and Python 3, gives each invocation a unique image tag,
rebuilds it without cached layers before either run, and removes that tag at exit. The
image uses a digest-pinned Python 3.12.15 linux/amd64 base and a complete
SHA-256 wheel lock. The [package release pin](package-release.json) binds the
source manifest, Dockerfile, dependency lock, Compose file, and launcher. The
launcher stages the exact pinned public input package
into a temporary build context, then each container checks every packaged
input before running. It copies no owner-only host file or key into the image:
the one owner-only canonical registry is checked against and staged from its
byte-identical public immutable postimage; 78 inventory names that are never
read are represented by empty placeholders. Building needs network access to
fetch the pinned image and wheels; fixture execution has no network. This is a
runnable fixture product; the original protected roles and host qualification
have separate acceptance evidence below.

The same command first signs a disposable Source, verifies it as Reader, maps
15 nodes and 10 edges, and binds all 25 references in a Context view. It then
runs the Work journey. The [independent run review](CHAIN-FIXTURE-INDEPENDENT-EFFECT-REVIEW-0001.md)
observed exit 0 and no residual container. This is a fixture proxy; it does
not execute the historical Source8, Reader, Mapper or Context role packages.

The image creates a dedicated **container** account (UID/GID 20001) and installs
the v1 CLI dependencies. The fixtures run as that account against the selected
read-only image package, with no host checkout mount. Compose
disables the network, drops capabilities, uses a private temporary directory,
and runs the reviewed disposable local Work journey. Its fixture key and store
exist only inside that container's temporary directory and are removed after
the run. The service has no persistent volume and opens no port.

This is a reproducible fixture environment. The image's 20001 account is not
an independently enrolled
WSL host service UID. A container started by this user's
Docker daemon does not prove exclusive host cgroup custody, capable-peer
exclusion, protected source/issuer inputs, or the actual LC-U03-02/LC-U05-03
oracles. Do not use this fixture's keys or receipts as production authority.

The [local implementation stream](../../../docs/plans/0011-lab-runtime-completion/runs/0001-execution/IMPLEMENTATION-STREAM-20261022.md)
continues engineering and tests without owner/admission/release prerequisites.
The original protected host qualification remains a separate acceptance scope
documented in the historical [gate contract](../../../docs/plans/0011-lab-runtime-completion/runs/0001-execution/acceleration-audit-20261018/implementation-plan-0001/GATES.md).

Here, **Source8** is the project's version-8 participation source and its
related source/profile records; `8` is a version label, not a user count.
“Source8 authorities” is shorthand for the Source signer and scoped Reader
and Context issuer grants needed to authenticate protected operations. Mapper
uses the selected Source and Reader bindings; this repository does not define
a separate generic Mapper certificate issuer. The
checked-in `current-participation-v8` period ended on 13 October 2026; its
public metadata does not activate a fresh protected family. No such issuer or
grant is needed for the Docker fixture: the command above creates disposable
local test identity.

A separate disposable Source→Reader→Mapper Docker fixture now has three
independently reviewed one-shot results: [Source](SOURCE-ONLY-DOCKER-INDEPENDENT-EFFECT-REVIEW-0006.md),
[Reader](READER-ONLY-UNIFIED-INDEPENDENT-EFFECT-REVIEW-0006.md), and
[Mapper](MAPPER-ONLY-DOCKER-RELEASE-INDEPENDENT-EFFECT-REVIEW-0003.md).
The Mapper run produced a 55-file candidate package from the same selected
Source/Reader cut. These attempts are consumed and must not be rerun. The
Compose build and `lab-fixture` run were repeated on this WSL host on 20
October 2026; both exited 0, and the run printed `CyberAlchemy Lab — local Work
journey: PASS`, a successful fresh-process replay, and zero external effects.

The earlier Context stage received an independently reviewed one-shot staging
PASS, but its temporary `/tmp` family is no longer present on this host. Its
historical receipt cannot serve as a current mount or authority. The
[output validator](CONTEXT-OUTPUT-VALIDATOR-INDEPENDENT-STATIC-REVIEW-0003.md)
and [Docker finalization](CONTEXT-DOCKER-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md)
pass only effect-disabled static reviews. The current `chain-fixture` command
now runs a fresh disposable Source→Reader→Mapper→Context demonstration end to
end; the [21 October local product rerun](working/LOCAL-PRODUCT-ACCEPTANCE-20261021-0005.md)
exited 0 for both this chain and the `lab-fixture` Work journey. Those fixture
results do not qualify the separate original protected Source8 roles.

The newer durable disposable successor has independently reviewed one-shot
Source and Reader results and a [Mapper Docker effect review](context-successor-mapper-docker-independent-effect-review-0001/REVIEW.md).
Its Mapper package contains 55 files and binds 953 source rows. The
[Context final-stage selector](CONTEXT-SUCCESSOR-FINAL-STAGE-INDEPENDENT-STATIC-REVIEW-0004.md)
can inspect that real Mapper result. The [Context public stage](context-successor-stage-independent-effect-review-0001/REVIEW.md)
was written once and independently reviewed against the selected family:
1,570 files and 1,021 directories. The [original-role readiness review](context-original-role-readiness-independent-review-0002/REVIEW.md)
also found six missing current-family Context role files. Together with an
unissued AUTH file and unopened signed Reader scope, these prevent an original
Context role run for this successor. A separate
[public-only namespace probe](context-public-namespace-probe-effect-independent-effect-review-0003/REVIEW.md)
observed the five synthetic read-only mounts and handshake on this WSL host.
It used no protected input or Context role. Its earlier 0002 attempt failed
and remains preserved as consumed evidence; neither attempt may be rerun.

A later [six-mount public probe](context-public-policy-namespace-probe-effect-independent-effect-review-0003/REVIEW.md)
also passed independent effect review on this host. It observed six exact
read-only child mounts, including a synthetic policy path; writes to the
workspace and policy path returned `EROFS`, the parent observed its public
post-ACK outputs, and the container ID and name were absent afterward. Its
three attempts are consumed. This proves only the disposable public namespace
behavior under a trusted same-user ceiling. It did not issue a Context grant,
open a protected source, or execute the original Context role.

On 21 October 2026, a separate disposable successor's original Reader
signed-scope Docker attempt was consumed with an unknown child failure. The
[independent post-effect review](working/signed-scope-independent-review-0001/POST-EFFECT-REVIEW.md)
verified the claim and container cleanup, but found no signed attestation and
no evidence that the signed open completed. That attempt is not a success or a
retry target. The mutable [build area](working/README.md) continues the
original-role integration without changing those retained records.
