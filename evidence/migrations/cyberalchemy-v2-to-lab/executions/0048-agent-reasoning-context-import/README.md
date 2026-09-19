# Agent Reasoning Engine — repaired candidate context import

Request -> select capability -> construct context -> derive a supported judgment.

The isolated candidate contains 136 business concepts and 153 business relations, 77 system concepts and 101 system relations, plus 67 bridge links. The repaired package validator passes. Two complete builds produced identical output, and a build from the restored store reproduces those artifacts.

The package integrates the two tested replacement evidence bindings from 0047 and the exact historical evidence recovered in 0045–0046. The current Product retains both reasoning and interaction-context capabilities; its schema now recognizes that exact membership. Its original single-capability Product evidence is retained separately with its original fingerprint. `repair-delta.json` records the three source-registry changes.

The normalized ontology uses the prepared candidate schema with limits of 1,000 concepts and relationships. **This schema successor is not admitted.** The existing admitted 100-item contract and registry remain unchanged. The import is explicitly a candidate under the successor schema; it must not be reported as passing the existing admitted ontology contract.

`package-snapshot.tar.gz` preserves the repaired package, selected evidence, compiler and definition inputs. `package-inputs.json` binds its 2,481 files. `import.py` restores this archive into `.local/ontology-context-import-0048/package/`, validates the full package and writes the candidate bundle. `verify.py` also checks invalid graph mutations, concept pointers and rebuild equivalence. The local tsx loader is an external build prerequisite; the archive is not an installed runtime.

Six source gaps and ten residue items remain explicit. The 81 fixture tests from 0047 support the replacement code versions; this does not establish whole-engine conformance, admit an implementation binding or authorize deployment. Source repositories and earlier frozen evidence remain unchanged.
