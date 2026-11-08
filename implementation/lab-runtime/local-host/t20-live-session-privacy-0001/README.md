# T20 public Session-output privacy check

`scan.py` replays the exact independently reviewed API42 Session receipt and
checks its four public API replies, report and bounded State view with the
hash-selected T20 credential-field scanner. It rejects a populated credential
field, private-key block or private runtime locator in that retained public
output. It also rejects populated camel-case private-key material,
authorization and cookie fields, and Bearer, Basic and Token schemes. The
selected T22 cold verifier entrypoint runs from its prehashed bytes through a
private pipe, and must also pass; its imported helpers remain host-loaded.
Nine focused positive
and mutation tests run normally and with `-O`.

From the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t20-live-session-privacy-0001/scan.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t20-live-session-privacy-0001 -p test_scan.py -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t20-live-session-privacy-0001 -p test_scan.py -q
```

This is a check of retained public fixture output. It does not inspect
transient private controls, encoded secrets, protected Source8 bodies, or the
final shared runtime; T20 remains open.

`RESULT.json` and `RESULT-0002.json` retain the narrower predecessors.
`RESULT-0003.json` is the current result with authorization and cookie checks
and an explicit ceiling on imported helper origin.
