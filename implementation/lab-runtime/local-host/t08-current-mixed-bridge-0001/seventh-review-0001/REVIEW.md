# Seventh API33 current source/profile cold review

The selected seventh API33 source manifest is
`e400703a2ace9ea1899d7abf15023632a83235e1e15f5459970b1ed8d12a37dd`;
its profile is
`c86a04159a99d607f15f42078ae64b108ef5007e121f830d54174f0167b8813a`.
Compared with the archived sixth package, the profile changes only two
selection decisions: `authority/project-state-transitions/current.json`
is re-pinned from `8ba8ee25…` to its observed `12937950…` bytes, and the
mutable `/usr/lib/x86_64-linux-gnu/liblzma.so.5.8.3` duplicate row is removed.
The stable installed `runtime-dependencies-v2` liblzma row remains selected;
its file was independently read with SHA-256 `64550dc7…`, mode `0644`, size
215,448 bytes. The source manifest changes only its profile file row and
profile binding to the new profile digest. Source row counts remain 207;
profile row counts change from 32,020 to 32,019.

The original `ProtectedReader` signed technical fixture checked 32,225
physical files and 32,227 ordered proof rows at both entry and exit, reading
3,311,672,473 selected bytes per boundary. Both boundaries passed. Entry
took 98.520 seconds, exit 77.745 seconds, whole run 186.152 seconds.
`READER-RESULT.json` SHA-256 is
`58cb3a4e596d0addb1867277b1a697eaf4df3a81db280b9f829e05566a7c3c80`.
The construction reused the unchanged original Reader code and supplied
only the seventh source/profile digests at launch; it did not change either
selected package or the prior T08 fixture file.

Verdict: selected seventh bytes were physically consistent at both Reader
boundaries during this observation. This is a technical source cut only; it
does not execute the graph or host guards, decide owner outcomes, or qualify
T08/T02 as complete.
