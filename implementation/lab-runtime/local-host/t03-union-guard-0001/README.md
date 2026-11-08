# T03 selected-family union verification experiment

`probe.py` is a disjoint, read-only candidate for the byte-integrity portion of the local API33 guard. It does not modify the selected native family or API33. It pins the native chain receipt and phase results, checks the Source-to-cold-to-Reader-to-Mapper-to-Context links, combines the four selected manifest file sets, rejects conflicting hashes, and uses the selected Source capture primitive to rehash every unique path at entry and exit. The Source period must be current at both boundaries.

`compose.py` is a second, non-accelerating conformance harness. It calls all selected original source, package, policy, and lease callbacks at entry and exit alongside the union byte check. Because those originals still perform repeated hashing, this is a behavior test and an integration seam, not a production optimization.

Run `python3 -B -m unittest test_probe test_compose -v` and `python3 -B -O -m unittest test_probe test_compose -v` from this directory. `python3 -B -I measure_comparison.py` creates a new measurement only after changing its exclusive output filename. The versioned `MEASUREMENT-0003.json` binds the measured probe code hashes and selected chain hash. Older measurements are historical and should not be used to characterize the current code.

See [REPORT.md](REPORT.md) for the measured bottleneck, negative controls, and integration limit.
