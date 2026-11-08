# Durable workflow output bytes

`output_store.py` wraps the selected API30 workflow output journal with an owner-only content-addressed output directory. It validates every original body against its exact carrier descriptor/schema and scope before staging, stores bytes before journal claim, and rechecks those bytes at every delegated source/authority boundary. Cold replay and a later consumer reopen the physical output bodies and validate their hashes and schemas. A reference alone cannot satisfy the read.

The original API30 journal still owns claim, transaction, HEAD, retry and recovery semantics. A crash after claim remains indeterminate and never redispatches. A crash after immutable transaction can recover only while every original output still verifies. Uncommitted staged blobs do not become consumable outputs. There are zero canonical admissions.

Run from repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t31-durable-output-0001 -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -OB -m unittest discover -s implementation/lab-runtime/local-host/t31-durable-output-0001 -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -B implementation/lab-runtime/local-host/t31-durable-output-0001/template_fixture.py
```

Fifteen tests exercise exact retry, a separate-process consumer, missing or changed output before claim, missing/changed/linked/public-mode output at cold read, original-byte recovery, and interruptions after claim or immutable transaction. Independent review found a stage-to-commit gap; the repair wraps every journal guard with fresh output validation. Two causal tests remove output after claim and during recovery and require HEAD to remain at zero. Five additional tests cover retained original producer output, altered output/consumer records, and recomputed measurements.

`template_fixture.py` exercises all ten original WorkflowDefinitions and all 28 output-bearing transitions with their full output-carrier sets: 40 output instances. Every transition uses the original kernel and API30 journal, cold-opens the store, and consumes exact body bytes. The report explicitly records synthetic grants, producer receipts, input headers and evidence. Original public carrier examples are adapted only to the fixture scope and required Work subject. This demonstrates output custody and consumer mechanics; it does not execute the original engineering/research/native producers or establish their semantic lineage. Original T31 remains open.

The root is mode 0700; output bodies are mode 0600 single-link regular files. The intended owner is an exclusive managed-output writer. The adapter assumes no unrelated process with the same UID or administrator privileges changes managed blobs concurrently. Guard checks detect changes at explicit boundaries; they do not make filesystem operations atomic against a hostile same-UID writer between a check and HEAD replacement. A production API integration must supply the actual host guard, producer lineage and managed-store lifecycle. The runnable tests deliberately use a synthetic guard.

This workspace adapter pins the two directly selected API30 modules, the carrier catalog and its schema/descriptor documents, and the existing fixture builder. It does not pin or package the entire transitive API30 runtime. The fixture builder and API30 dependencies must exist in this workspace; the clean-checkout Docker product is a separate committed artifact. This adapter must enter that artifact's complete dependency closure before it can be described as a portable product feature.

`observed_replay.py` carries the exact retained engineering `implemented` and research `executed` output bodies into new local coordination fixtures and cold-consumes them. The engineering consumer checks the actual corrected-source digest, compiles those bytes without executing them, and reopens all seven evidence bodies. The research consumer recomputes entropy from the three observed labels and checks it against the consumed Measurement Result. The original `FLAG`, unsupported engineering outcome and inconclusive research outcome stay intact. No producer is rerun. The original producer emits a `workflow-design-run`; its original bytes are preserved and linked, while a distinct closed WorkflowRun is created using synthetic coordination witnesses. This does not turn the old design record into native execution evidence.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B implementation/lab-runtime/local-host/t31-durable-output-0001/observed_replay.py
```

The retained consumer independently pins both assessment bodies and all seven engineering evidence bodies. It refuses coordinated replacement of an evidence body and its self-declared assessment hash, and rejects relabeled research observations even when the label histogram gives the same entropy. These pins provide byte provenance; the arithmetic and schema checks provide separate consistency checks.
