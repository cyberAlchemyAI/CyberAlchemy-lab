# Disjoint API34/T06 cold selection

The API34 successor at `product/lab/release-candidates/v1/interface/api-integration-v34-current-t06-0001` selects the existing current Source8 family, governance v5 on the T12 native Store, and versioned T06 SDK and branch producer. It preserves frozen API33 seventh unchanged. The builder is `build.py` (SHA-256 `fbd65407dfcea64d8e30bfdf550b090f93bed27a068b106b8a7037f1b9c392aa`).

Exact output bindings:

- API34 source manifest `4a47f51f9b93e7a51ed3fe4b59c340ac0c8f0dabc19eb851392dbd64b608b9bd` (207 rows).
- API34 contract profile `371e305e053cfcb88aa318149b8c47298af38f2d567599c6d935808a1be7d835` (32,092 rows).
- API34 integration members `1caa8e6dc18e7f34a5ec7d86a37c4673566fb3ed2ead267b2256adb939ddf527`; its governance member selects v5 source `8a215ad66e94179385bcb4dcac79eab5267ee6ac50e12e7b1dac21645301d337` and profile `7798fda1f9e7e4038425bc8aa6f227f2e22612affa4acb2c28c9a12d31531af3`.
- T06 SDK manifest `dcdce5fb77666b19cae377e0decbdbe27b848d970c81b817c8dccb62c4eee413`; branch driver selection `62b9ef33ee73d29b4bb5c8182f892238baac4cad6ca6309c4fa024637cd17504`.
- Rebind receipt `4f204337f09ebec56a7f3b4094085e5abb133d18fa4fd014fc29a60c2d9468e7`.

Cold validation: API34 source guard 207/207, Schemas guard, and complete anchored profile readback 32,092/32,092 passed. `test_successor.py` SHA-256 `55044f4060ffab47721eeeeb4ed59bd6a316abf1c6148131786faa85c9182866`: 8/8 normal and 8/8 optimized tests passed, including wrong Source/profile pin refusal and historical SDK refusal.

The isolated first preparation then passed using `run_prepare.py` SHA-256 `6e1dfdfd59ee43797eba4f0412d57a452b5aa39d81264c26e97cfbee61a91dcf`. Public receipt `RUN-PREPARE-0001.json` SHA-256 `4274eb7c474c6d9538268437dc38d917d4336d1f56c9f6a05044c39bc2fd5431` records stage exit 0 in 0.376s, preparation exit 0 in 35.148s, the private branch selection SHA `4c68ad16b2db1f710626b028129b1f571dfa3def2ecf9f11ee58e3af242f2bd4`, and unchanged public source pins. Readback confirmed Base/Action/governance branches, one Schemas instance, original Action preparation lease closed, 0700 private root and 0600 record. Private locator and logs remain under `/tmp/cal-T06-api34-control-0001` and the owned branch root. Its 900-second Action grant will expire; a later live child may require a fresh root. No composite child startup or whole API qualification is claimed.
