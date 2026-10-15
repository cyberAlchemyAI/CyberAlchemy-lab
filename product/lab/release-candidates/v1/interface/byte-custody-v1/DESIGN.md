# Dependency byte custody

The existing Context preflight checks every dependency file and repeats ancestor
path checks for each file. This candidate opens each directory ancestor once
per verification pass with `O_DIRECTORY | O_NOFOLLOW`. Files are opened relative
to those anchored descriptors with `O_NOFOLLOW`, actually read and hashed.

Every file must be read. The pass checks each file's inode, size, modification
and change times before and after reading, and again on exit. All directory
paths must still select their captured directory inodes. Symlinks, replacement,
missing files, changed bytes and incomplete passes fail. Descriptors close on
all paths and cannot be reused across passes.

Absolute paths require the complete exact external dependency allowlist.
Relative paths remain under the supplied root. The candidate host byte ceiling
is 64 MiB per file; the inspected Context closure's largest input is 23,542,012
bytes. Larger future packages require a separately selected ceiling.

This is source-byte verification only. It stores no permission, authenticated
Actor, Agent memory, Session lifetime or clock result. The original Context
identity, environment, mapper, package, schema and source checks remain required
when this primitive is integrated. Permission, revocation and time remain live.

Qualification requires actual owned-filesystem refusal checks and measurement
against the original byte-custody loop on all 11,165 selected Context dependency
files, including its 66 explicitly selected external inputs. A component speed
measurement cannot qualify complete Context delivery, an API or an Agent.
