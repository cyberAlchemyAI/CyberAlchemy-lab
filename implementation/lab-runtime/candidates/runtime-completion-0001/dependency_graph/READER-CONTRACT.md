# Original-role reader checkpoint

`RoleReader(AnchoredReader, ReaderSelection, posture=..., permission=...)` binds
the accepted C01 primitive to the original T08 role vocabulary. Selection includes
full ByteBindings for policy, source and profile; the original source cut; and
the complete ordered table descriptors. Those are independently supplied caller
trust inputs. A changed candidate policy cannot replace them. Source/profile/cut
equality is explicit, including the profile digest recorded in the cut.

Original role authority is
`product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001/binding-kinds.json`
(SHA-256 `ad6beb88189743c359cd730a08ab282a0580db4a9905b84a502254d94cbff61a`).
The original thirteen roles remain distinct. Their fixed C01 storage classes are
defined in `ROLE_KINDS`: governed records are semantic or protected input; schema,
descriptor, policy, execution and environment inputs are execution or protected
input; history/recovery/source/profile/custody metadata are evidence or protected
input; public packages are public-package. No path spelling, hash match or proof
reference promotes a body into a governed record. Role classification is not
semantic eligibility: the subsequent native carrier/fragment/eligibility verifier
must establish that separately.

`read(file_id, expected_role, max_bytes=...)` validates limits before any boundary
or provider invocation. It delegates bytes, no-follow traversal, attachment,
digest, size and type checks to the unchanged accepted AnchoredReader. Outer
`boundary()` rechecks selected policy/source/profile on entry and exit. Each
protected fixture read separately checks current permission before and after
return from the provider. Public exceptions contain bounded codes, not bodies.
Every ordinary exception at the constructor, permission, read, inventory and
context-manager boundaries is replaced by a fresh `Refusal` with one fixed code;
unknown messages become `ROLE_READER_REFUSED`. Chained provider/OS/parser text and
private traceback frames are suppressed. Provider exception rendering is never
invoked. This concerns ordinary rendered errors; Python introspection of caught
exception internals and hostile provider execution remain outside this inert
adapter's isolation claim. Process interrupts are not swallowed.
`files` and `selection` return defensive copies. `public_summary()` contains only
counts, a policy digest and explicit inert claim ceilings.

Only two postures exist. `public-metadata` refuses protected body reads even if a
provider was accidentally supplied to the underlying reader. `owned-fixture`
requires `FixturePermission`, a separately pinned fixture grant with exact
subject/source/profile/cut/binding scope and a live deadline. Changed or expired
fixture permission refuses; it cannot enable an actual posture. The caller must
use the exact same selected `AnchoredReader` instance for permission and body
reads; construction and each boundary guard enforce this before any body read.
Matching logical root IDs and digests from another root/provider enrollment do
not transfer permission. In particular, a still-current grant under root A
cannot bypass revocation at an identically named root B.
The caller must
select the fixture provider code and roots independently, as the accepted reader
contract requires. This is an inert testing seam, not signed host enrollment or
actual protected custody. A caller-supplied object is never represented as proof
of an actual grant. Actual host support remains unavailable and requires a later
independently reviewed fixed provider under G01/G05; no adapter fallback exists.

`inventory(descriptors)` delegates to accepted `source_inventory.retain()` with
the separately retained descriptor list. It preserves full rows, repetitions,
ordering and unknown original metadata fields. Table documents must be selected
public metadata; a protected table document refuses instead of bypassing the
permission adapter. Row member locators are never dereferenced. The full original
22-table/241598-occurrence integration will be independently selected and checked
in the final unit evidence, using the accepted public projection without inventing
an actual source cut for its unselected protected bodies.

This checkpoint covers only the protected fixture and public metadata adapter.
The original T08 complete native semantic carrier/fragment/role closure and T09
environment consumption remain unfinished. T09 must identify the later complete
reviewed T08 successor, not mistake this intermediate checkpoint for acceptance.
