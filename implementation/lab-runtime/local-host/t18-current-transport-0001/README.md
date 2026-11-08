# T18 current T06 transport slice

`boundary.py` executes the exact selected API40 T06 SDK `control.py` and
`framing.py` bytes in a temporary import scope. It pins the API40 Source and
profile, the SDK manifest and all six SDK source rows selected by that profile,
and the prior seven-call T06 live receipt. The latter contains a real Action
wrong-scope refusal after one owned counter increment, with the counter still
at one. This cut does not repeat that live effect.

The seven actual selected-framing cases cover raw request-byte preservation,
partial and oversized input frames, wire and frame budgets, an expired startup
deadline, and a response budget. The frame-budget case confirms exactly one
callback before the second frame is refused. The refusal cases do not call a
synthetic effect callback (except the first allowed frame in that budget case).
The service callback is a bounded local test double; no Lab branch or private
credential is constructed by this runner.

Run `python3 -m unittest discover -s implementation/lab-runtime/local-host/t18-current-transport-0001 -p test_boundary.py -v`, repeat with `python3 -O`, then run
`python3 implementation/lab-runtime/local-host/t18-current-transport-0001/boundary.py --verify`.
`RESULT-0002.json` is written once with `--write`, then cold replayed with
`--verify`; `RESULT.json` preserves the superseded first receipt. The writer
uses exclusive creation, no-follow, and file/directory sync. The output-budget
case now checks the selected guard's exact refusal text and a separate test
rejects an unrelated `ValueError`.
The result is a local framing check, not same-family T18 closure. It does not
establish cryptographic wrong-key or cross-branch proof refusal, live
revocation, credential zeroing, interrupted journal recovery, or Machine
security on this cut. No authority or canonical effect is produced.
