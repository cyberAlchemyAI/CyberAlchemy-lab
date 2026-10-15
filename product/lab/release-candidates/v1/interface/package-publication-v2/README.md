# Managed package publication v2 candidate

Filesystem kernel for later authenticated package export/import integration.
The actual host must supply independently selected roots, scope, principal,
permission/source guards and exact export/privacy controls. This module supplies
no authentication, Machine grant, semantic model validation or admission.

The root and scope manifest are independently pinned. No-follow descriptors,
private modes, UID, inode, hardlink, regular-file and size checks protect managed
files. Package originals are verified with frozen package transfer v3. Request,
scope and package bindings select an exclusive generation. Data and metadata are
fsynced before a durable marker; uncertain generations are preserved. Existing
generations can only be read and verified. No repair, overwrite or automatic
redispatch occurs. The original File Materialization Receipt contract is used.

The complete suite uses newly owned temporary filesystem fixtures. Its Actor,
source and permission callbacks are explicitly synthetic. Fault injection is
fixture evidence. No authenticated public call, real source replay, pilot,
permission or canonical admission is claimed. Public API integration is pending.

`read_package(package_binding, request_binding, source_cut, generation_ref)` reads
one published generation selected by independent host controls. It derives the
directory name from those controls, verifies the original archive and all three
metadata files, and checks source, permission and current root/generation identity
before returning. It acquires shared locks and creates no files or directories.
Absent, incomplete, changed or inaccessible generations require reconciliation.

All 33 predecessor fixture tests are retained, with 20 additional readback tests.
Import still needs an authenticated public handler, independently selected
mapping/disposition controls and target model validation. Passing these filesystem
tests establishes only the bounded component behavior.
