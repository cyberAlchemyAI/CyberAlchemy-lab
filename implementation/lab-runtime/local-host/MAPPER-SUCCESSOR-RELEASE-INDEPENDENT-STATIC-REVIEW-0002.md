# Mapper successor release 0002 — independent static review

**Verdict: PASS for the frozen effect-disabled selection candidate. R01 is closed in this successor. Mapper stage/execution remain unselected and unrun.**

The candidate freeze matches `9177b066bad394cf1eb1b481cb988f267a3d093f85f94cb02ad8e67731c63ab2`. Its three member hashes match: `release.py` `70ae083e21e8f4139fb3cb1ed065feb1f40fff59a8c4b1f6a769d60fb85f0b47`, `test_release.py` `ed910a0179800087a9220c180c59ad0749f14715bf2c4436091d8e8debf4b684`, and handoff `a8957010d901171c1565d41ba7130af2045a9baaa4e1ac0fb0ab36b36d4d782b`. All 25 selected source/review bindings, including predecessor freezes and the earlier HOLD, matched before and after testing.

The only production-code change from 0001 is a six-line precheck: parse the external Reader record, require a dictionary and `type(exit_code) is int`, then require zero before invoking the predecessor selector. Accepted predecessor bytes remain untouched.

I independently reproduced the former counterexamples with the external record digest, synthetic Reader review, and outside review pin updated coherently. JSON `false` and `0.0` now refuse with `READER_EXTERNAL_OS_INTEGER_ZERO`, in normal Python and `-O`. Additional `true`, integer 1, integer -1, string `"0"`, and null cases also refuse. Integer zero succeeds; the exact positive plan digest remains `0d8a9773c6d1f41aba97a3d01dbf3b1bfcccd2c50c5d989ebbf747727d16c547`.

Both independent runs returned actual OS exit 0 and passed all five author tests plus seven additional coherent scalar negatives. The positive plan retains 991 unique rows: 986 Reader-stage rows plus five generated Mapper rows, with 37 private-package metadata rows assigned `0600`. No archive body was opened. The actual Source review remains pinned to `599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440`; future Reader evidence remains explicitly synthetic in these tests.

The public native ELF rehash matches `fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c`. The original verifier template matches `aa883d697a9cfec02a4671da2a76d10c5c4b23ef0a93e63c78f31ac0667ff23b`; it remains unadapted to the new effect and was not executed. Both effect entrypoints still refuse unconditionally, and the Docker envelope has no runnable argv.

Independent evidence is under `mapper-successor-release-independent-review-0002/`:

- `execution.json`: `d36c905675ac0370e0d786d4d7e3e14eb3c12072d9b205987eef274e285681a1` — exact command/environment, source driver, inputs and original stdout/stderr bindings.
- `normal.stdout`: `d8d6c0a2c2f832ac53659bc449774f65bfdcbb68d209794314a285fd1000ec20`
- `optimized.stdout`: `643e9c88792bf8f0cd5abf7559f6945e328a6284a73d439466a10cdc91eacfaa`
- `check.py`: `371b93dc58626ac2aa89aeebc5c7d620fff125556062e7612aa1fafd869af853`

This verdict establishes metadata-selection consistency only. It does not establish independent origin of caller-supplied Reader reviews, live period/custody, a closed cold effect loader, actual 991-file stage bytes, Docker confinement, native cold-read output, or original protected Source8 qualification. A separate reviewed effect release must supply those joins and rebind the original 55-leaf verifier. No candidate files were changed, no private archive was read, and no stage, Docker or Mapper effect ran.
