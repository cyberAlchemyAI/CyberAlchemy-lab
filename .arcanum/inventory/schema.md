# Inventory schema

## Scope

The repository working tree is inventoried using Git's file selection:

- Include all tracked files and non-ignored untracked files that exist.
- Exclude Git internals, ignored files, empty directories, and the generated
  inventory outputs (`inventory.json`, `content-map.jsonl.gz`, and
  `content-search.sqlite3`, including transient SQLite journal/WAL sidecars)
  so they cannot inventory themselves.
- Include the generated index, schema, documentation, and builder on the next
  refresh; no source area is excluded by name.
- Do not follow symlinks. Hash their link-target text.

Ignored files commonly include local credentials, caches, build outputs, and
temporary files according to the repository `.gitignore`. This index is a
repository content inventory, not a disk image or a listing of empty folders.

## Manifest fields

Each `files[]` record in `inventory.json` contains:

| Field | Meaning |
| --- | --- |
| `path` | Repository-relative POSIX path. |
| `kind` | `file` or `symlink`. |
| `tracking` | `tracked` or `untracked` in the current Git working tree. |
| `size_bytes` | File byte length, or encoded link-target length for symlinks. |
| `sha256` | SHA-256 of file bytes or encoded link-target text. |
| `extension` | Lowercase suffix, or `[no extension]`. |

`directories[]` contains a file count and extension counts for every path
prefix. `summary` contains total counts and byte size, top-level counts, and
extension counts. Paths and records are sorted for reproducibility.

## Maintenance

`tooling/inventory/build_inventory.py` generates and validates the path
inventory. `tooling/inventory/build_content_map.py` maps source structures and
builds the FTS5 index. Generated files are `index.md`, `inventory.json`,
`content-map.jsonl.gz`, and `content-search.sqlite3`; regenerate rather than
editing them by hand. The content map has one record per repository file and
one record per archive member, including nested TAR and ar members. Its
structural fields are format-aware; its full-text index covers decoded text,
extracted PDF text, and printable strings recovered from binary records.
Binary bytes stay in the source and are referenced by digest. Update this
schema and the generators together if selection or fields change.
Record each deliberate refresh in `log.md`.

This package indexes and summarizes repository material. It does not grant
authority to source evidence, candidates, or generated inventory records.

## Curated status views

Files under `queries/` are source-linked navigation views over authoritative
repository records. They may summarize counts, lifecycle state, decision
sequences, and unresolved boundaries, but every material statement must point
to the governing registry, decision, plan, or evidence package. These views do
not replace source authority and must distinguish candidate, approved,
admitted, activated, executed, and completed states.
