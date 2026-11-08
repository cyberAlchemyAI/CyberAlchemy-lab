# Structural inventory

- [Summary](summary.json): exact commit, counts and grouping coverage.
- [Every tracked path](file-inventory.json): path, kind, bytes, SHA-256 and group.
- [Every Rust module](module-inventory.json): group, public symbols with lines,
  and lexical references.
- [Dependency references](dependency-edges.json): module edges and extraction limits.
- [Source citations](source-references.json): source path, verified line and lookup
  used by the report generator.

All 2,924 tracked paths are accounted for. Symlink hashes cover target text,
not followed contents. Rust grouping is a review navigation aid. Lexical edges
include conditional and test code, and do not prove a call graph or enforced
layering. Benchmark/data files are inventoried but not all executed or audited.
