# Inert executable origin inspection

`inspect_elf` consumes already selected immutable bytes and an independently
selected SHA-256. It supports bounded ELF64 little-endian x86-64 Linux/System-V
headers and load segments, exact dynamic names, interpreter, SONAME and GNU
version requirement/definition tables. It does not execute the file or invoke
readelf, a loader or an original installer. Unknown dynamic requirements, loader
flags, class/machine/endianness, malformed versions, ambiguous virtual-address
mapping, missing terminators and out-of-range segments refuse.

RPATH/RUNPATH, `$ORIGIN`/other dynamic-name substitutions, audit/filter/auxiliary
loading and alternate loader search flags refuse. A future reviewed loader
policy would be required to support these. `compare_abi_versions` compares only
fresh parser results produced inside the selected environment consumer: each
DT_NEEDED name has one exact selected SONAME origin and all declared required
version names occur in that origin's version definitions. It is not a public
trust adapter for caller-supplied observation dictionaries.

The selected original libc/libm/librt contain x86-64 marked-PLT declarations.
These are checked as a complete, bounded address/size/entry-size structure and
retained explicitly as an unverified runtime requirement. The field meanings
are documented in the [glibc implementation commit](https://sourceware.org/pipermail/glibc-cvs/2024q1/083835.html).
Packed relative-relocation declarations likewise require all three fields and
an exact bounded eight-byte entry structure; this does not simulate relocation.

Every result keeps `runtime_abi_verified: false`. Structural dynamic references
and version-name membership do not prove actual symbol resolution, relocation,
loader compatibility, CPU instruction requirements, current modes/custody or
runtime success. Those obligations remain explicit, including marked-PLT and
packed relocation support where present. No requirement disappears merely
because the parser does not implement its runtime semantics.

The original integration test inspects all77 selected public ELF byte inputs
from the existing public runtime copy under exact original digest/size bindings.
It compares the complete original transitive dependency declarations and version
requirements, then rechecks every byte binding. It neither imports those modules
nor runs those binaries, and its root observation supplies no actual host proof.
