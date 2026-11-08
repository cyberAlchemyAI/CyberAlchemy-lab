# Full API40 source-guard subset diagnostic — privacy HOLD

The original API40 source manifest selects 207 `product/` files totaling about 28.5 MiB. An in-memory deterministic 207-file archive passed a fresh-root execution of the selected original `guard._verify_files`: 207/207 current bytes; removing or changing the selected contract profile was refused for the exact expected reason. Its observed in-memory archive SHA-256 was `d974183567e6c0d4b453e70a57c2cae9ce97544044d2de6b611604a848726aca`.

The selected T20 public-byte scanner then flagged three original source paths: `private-plan-v2.schema.json` (private-state path class), `test_installation_release.py` (credential assignment class), and `test_preparation.py` (private-key block class). No contents or keys are reproduced here. I removed the newly created `SOURCE-GUARD.zip` immediately; it is absent. `package.py --create` now refuses with a privacy HOLD, while `--verify` runs the source-guard diagnostic wholly in memory. Six tests pass normally and with `python3 -O -B`.

This diagnostic cannot become a public portable API40 package by copying all 207 original source rows. The disjoint `t25-api40-status-runtime-guard-0001` technical recut omits the flagged rows and retains only seven named `lab.status` prerequisites. Neither slice runs the original API40 Service or qualifies the complete portable closure.
