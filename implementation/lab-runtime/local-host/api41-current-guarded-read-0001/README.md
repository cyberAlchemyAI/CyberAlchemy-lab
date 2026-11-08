# API41 current Source8 guarded reads

API41 is a disjoint successor to API40. It corrects the current native Source8 reader selector to require the actual `SelectedReader` class at its selected module path. The frozen API40 and running API33 source remain unchanged. API41 remains on the common jsonschema 4.19.2 environment; it does not revive the expired historical Source5/4.23 source.

The inherited snapshot-header mutation refusal executed 1/1 on current native Source8 in 84.681s. The selected class and module-origin refusals executed 2/2 in 63.311s. Their exact source, profile, test, and log hashes are recorded in `working/targeted-result-0002.json` and `working/targeted-reader-negatives-result-0001.json`. These results are bounded to three actual tests, not a whole guarded-read class or T16/T18 completion.

When shared CPU is available, run all seven current-source tests:

```sh
env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 python3 -B -u implementation/lab-runtime/local-host/api41-current-guarded-read-0001/test_current_guarded_reads.py > implementation/lab-runtime/local-host/api41-current-guarded-read-0001/working/all-current-guarded-reads-0001.log 2>&1
```

The separate Machine replay at `../api41-current-machine-replay-0001/` links to the frozen API33 99-case result when that run becomes terminal.
