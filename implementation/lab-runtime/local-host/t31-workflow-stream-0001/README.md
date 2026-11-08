# T31 local workflow output stream

`inventory.py` reads the ten original WorkflowDefinitions and the selected API30
registry. It checks the exact definition hashes, 28 transition identities,
endpoints, and complete nonempty output-carrier sets. There are no zero-output
or scope-excluded transitions in the original ten definitions.

`run.py` executes two original candidate Work producers in separate Python
processes and retains their output bytes in `run-0001/`:

- **Engineering assessed:** W03 designed the correction, ran the bounded
  source-correction Tool, independently checked its observed behavior, and
  materialized a Work Outcome Assessment. The assessed WorkflowRun names the
  exact assessment ArtifactRef, and the later candidate Work record references
  that revision. The assessment is **unsupported** because the historical W02
  native executable needed for the 42-case default regression is absent; this
  run makes no supported-engineering or Work-satisfaction claim.
- **Research evaluated:** W04 ran six actual replay child processes over the
  selected archived source, assessed the predeclared finite hypothesis, and
  materialized a Finding and Evaluation. The evaluated WorkflowRun binds the
  observed phase event and leaves Work satisfaction unset; the later candidate
  Work record references both exact output revisions. The observed hypothesis
  disposition was **negative**. No general performance improvement follows.

The cold verifier recalculates original output bytes, checks the original
carrier descriptors and schemas, verifies WorkflowRun event linkage and later
Work references. It checks the entire retained result, including false-qualification
claim fields. These references do not prove a later consumer performed behavioral
work with the outputs. Tests refuse a zero-output substitute, wrong carrier,
changed output bytes and false qualification claims. The original example's intermediate formal AgentSession
record files are removed after each worker returns; no keys or Session RAM are
retained here.

| Original template | Declared output transitions | Locally observed terminal output transitions | Remaining |
| --- | ---: | ---: | ---: |
| intent-framing | 2 | 0 | 2 |
| agent-context | 2 | 0 | 2 |
| engineering | 3 | 1 | 2 |
| research | 3 | 1 | 2 |
| failure-assessment | 3 | 0 | 3 |
| challenge-handling | 3 | 0 | 3 |
| operational-learning | 3 | 0 | 3 |
| review-admission | 3 | 0 | 3 |
| ontology-migration | 3 | 0 | 3 |
| product-adoption-release | 3 | 0 | 3 |
| **Total** | **28** | **2** | **26** |

To verify the retained run:

```bash
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t31-workflow-stream-0001 -p 'test_*.py' -v
python3 -B implementation/lab-runtime/local-host/t31-workflow-stream-0001/verify.py implementation/lab-runtime/local-host/t31-workflow-stream-0001/run-0001
```

To execute a new run, pass a new absent directory to `run.py`. It never
overwrites a prior episode. The exact original producer observations are local
fixture evidence only. T31 remains open until all 28 applicable transitions
have output-bearing native WorkflowRun transactions and cold replay under the
current signed source, with original producer/consumer, permission, recovery,
and negative-carrier/scope evidence.
