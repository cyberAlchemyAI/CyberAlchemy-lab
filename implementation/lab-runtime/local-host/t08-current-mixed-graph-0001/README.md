# Current API33 mixed graph import cut

`run.py` is a disjoint technical fixture for the frozen seventh API33 source
manifest (`e400703a…`) and profile (`c86a0415…`). It selects the unchanged
public original ontology-node and ontology-cut record files from the current
profile, plus their original schemas, descriptors, registry, catalog, and
foundation declaration files. The original semantic verifier accepts those
two native records as one declared edge: the cut's exact `node_refs` includes
the selected node. The other original reference slots remain explicit
current-context dispositions. The signed fixture's source cut is technical;
it is not an admitted Source8 cut or owner decision.

The fast `test_small_graph.py` exercises the actual original
`ProtectedHostBridge.verify_semantics` and original `ProtectedReader` over
those exact original public bytes, with two nodes, one edge, two carrier
profiles and seven foundation declarations. It refuses a source proof row
substituted as semantic policy, a wrong host module digest, changed selected
policy bytes, and an omitted semantic edge. Two tests pass under normal
Python and `-O`.

The full `run.py` additionally builds a signed Reader selector that contains
all seventh source/profile proof rows and points graph rows at their real
repository paths. Its first attempt was stopped after 129 seconds of CPU to
leave capacity for the active T02 99-case suite; that uninstrumented attempt
may have entered a Reader sweep and produced no verdict. The coordinated
single-positive run is terminal PASS in `working/RESULT.json` (SHA-256
`138b14f3d32dc6f6c90e5903a15647479c4f8f0362860a1f9618bc4689c0c24d`).
The original `semantic_graph.verify_graph` entered `reader.boundary()` for
full entry and exit checks over 32,228 selected files, including 32,227
source/profile proof occurrences, and returned 2 nodes, 1 edge, 2 profiles,
and 7 foundation declarations. `working/RUN.log` records the graph phase at
250.55 seconds. It refused a wrong host module digest without another Reader
boundary. The two small-selector tests still pass normally and under `-O`.

The small tests execute Reader entry/exit only over their small technical
selector. The terminal graph result executed whole Reader entry/exit on its
seventh selector. Direct `verify_semantics` did not execute the current host
guard or private historical-content port. The separate seventh full Reader pass is recorded at
`../t08-current-mixed-bridge-0001/seventh-review-0001/`, with its own limited
claim. T08 completion and release approval remain open.

The selected private historical-content port treats API16 source/profile as
historical proof tables, but its `current_standing()` also requires the
current source manifest to expose `input_accounting`. The frozen seventh
API33 source manifest has no such field. A complete `verified_boundary()`
cannot be inferred from direct graph success without a reviewed current-port
successor or an independently selected compatible current-source contract.
