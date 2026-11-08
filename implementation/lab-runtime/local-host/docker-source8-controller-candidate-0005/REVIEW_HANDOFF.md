# Independent review handoff: Source8 Docker controller v5

Review this disjoint candidate against the [v4 independent findings](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T33/docker-source8-controller-v4-independent-review-0001/REVIEW.md). V4 and its receipts remain unchanged.

Check the preselection-to-writer interval: all three event subprocesses start before selected-volume creation; the mixed stream anchors on the exact preselection container; a foreign create or selected-volume RW mount after that marker is refused even before the two later type-specific barriers. The tracked initializer is the only temporary RW grant before the writer; its stopped container is removed and inspected absent before writer admission. Check the two-stream terminal and destroy skew intervals, and the postcustody mixed-stream marker, which occurs after final selected-resource checks. The clean mixed replay must include the selected volume's create, writer create and RW mount, selected-volume destroy, and postcustody marker. An incomplete buffered line or live/replay mismatch must return UNKNOWN.

Evidence to reproduce:

- `python3 -m unittest -q test_v5_boundaries.py test_post_terminal.py test_clock_counterexample.py` and the `python3 -O` equivalent: 15/15 inert cases passed in both modes. `python3 run_controller.py --plan` passed.
- `test-result-8ce80393ef284ae5.json` (SHA-256 `124a2e6e8acb279a8e7789f0d482eed06e5989808dbaad062ce4d0961986805b`): all four disposable cases passed their expected clean or UNKNOWN disposition. Clean mixed live/replay count 34/34; selected-volume 10/10; container 14/14.
- `postrun-cleanup-8ce80393ef284ae5.json` (SHA-256 `587d4711d5885aba3642045c8684e9801232490fd3a52d706622a9914c67b9a4`): no exact-label resources remain for any of the four case IDs.
- `test-failed-5fdd97c5f1e4b3ff-precleanup.json` and its disposition preserve the first fail-closed attempt caused by the tracked initializer's stopped RW reference. They are not substituted for the passing replay.

Frozen code hashes: `manifest.json` `98449cf6fb2d28efebcebf1b872513ca6cbecf831d42906a60cfb2e24bdb5c75`; `run_controller.py` `eff68b92a2477ed46677bdbc3bb45a664340d734a255a9076779d5932c768d2a`; `control.py` `674c655cbd07cfbab070383b1543af4579ebef575b489f7a7be78b0b066e9d1a`; `test_v5_boundaries.py` `6ffdd0b1e92394db46b3b70772212681b68f81df70c785e52915bf4ea598875c`. The six payload hashes are pinned in the manifest.

Keep the verdict bounded to the selected synthetic Docker daemon and its trusted administrators. Protected activation is disabled. Do not mutate authority admission paths or read historical protected archives or issuer materials during this review.
