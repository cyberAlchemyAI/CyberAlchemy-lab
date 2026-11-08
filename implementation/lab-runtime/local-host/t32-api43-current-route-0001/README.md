# T32 selected current native recovery route

`run.py` selects the exact API43 Source/profile and its profile-listed native
wrapper, fixture serializer, child runner, production executable and observer
executable. It then executes one owned baseline native batch, kills a second
batch child after its first semantic event link, verifies that the committed
old cut remains readable, recovers in a fresh `GenerationStore`, cold-replays
all original semantic and governance events, and checks an exact idempotent
retry and untouched foreign sibling. The retained receipt contains only public
digests and bounded outcomes. It creates no Lab admission or authority effect.

Run from the repository root with the API43 selected jsonschema overlay:

```sh
PYTHONPATH=implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay \
  python3 -B implementation/lab-runtime/local-host/t32-api43-current-route-0001/run.py
```

The current runner writes `RUN-0002.json` without replacing any prior receipt;
`RUN-0001.json` is a diagnostic whose recovery used a new object in the same
process. The v2 runner invokes recovery in a separate process, then cold-reads
the result and verifies an exact retry. The existing [14-case native interruption matrix](../../../../product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001/README.md)
remains separate evidence for other checkpoint and foreign-residue cases. This
route is not yet an authenticated API operation, and process-kill evidence does
not imply host power-loss durability.
