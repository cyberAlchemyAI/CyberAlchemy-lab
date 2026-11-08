# T20 local T07 privacy conformance slice

`scan.py` selects the final T07 public source manifest, package-release pin,
runtime release receipt, run log and both live container inspection records by
exact SHA-256. It rebuilds the disposable Docker context with the existing
T07 stage function, runs the existing package verifier against that physical
context, and scans all 698 material bodies, three runtime code bodies, four
build inputs and 78 empty name-only placeholders. It confirms the owner-only
registry path was staged from the byte-identical public immutable registry.
No staged context or protected body is retained.

The scanner refuses private-state path segments, populated credential fields
in selected JSON (including hyphenated and camel-case spellings and numeric
values), private-key block markers, runtime log credential
assignments, and owned `/tmp/cal-...` locator disclosure. It checks that the
two pinned live Docker inspections report no mounts, no network, a read-only
root, dropped capabilities, no-new-privileges, and UID/GID 20001. The public
report contains counts and hashes only. Negative tests use synthetic strings
and verify refusal messages do not echo their values.

Observed `RESULT.json`: `PASS-LOCAL-TECHNICAL`, 783 selected package members,
two runtime inspections, and zero matches for those sensitive-content/path
classes. Seven tests pass normally and with `-O`:

```sh
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t20-local-privacy-0001 -p test_scan.py -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t20-local-privacy-0001 -p test_scan.py -q
```

This checks the T07 disposable **public fixture** and its pinned local runtime
outputs. It does not inspect protected Source8 bodies, prove absence of every
possible secret representation, qualify a final shared API family, or close
the later pilot/T25 package boundary. Any selected byte or receipt drift
refuses this scan and needs a new exact selection.
