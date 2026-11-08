# T20 local candidate package privacy slice

`scan.py` rebuilds the exact disposable T25 candidate, checks its retained SHA-256 and replay, and scans the archive's 681 original public files, 799 additions, and JSON controls with the hash-pinned T20 sensitive-content rules. It rejects selected private-state paths, private-key blocks, populated JSON credential fields, and direct or augmented non-JSON credential assignments with nonempty values. Empty or commented sensitive YAML keys fail closed. The two exact selected `password=None` PEM loader calls are treated as empty. The 78 name-only placeholders must be empty.

One original public O06 proposal is named `private-source-use.json`. The path rule would reject its title even though it is an explicitly selected public policy proposal. Its single exact SHA-256 is excepted from the **path-name** check; its JSON and private-key content checks still run. Changed bytes refuse. This exception does not admit arbitrary private paths.

Run from the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t20-candidate-package-privacy-0001/scan.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t20-candidate-package-privacy-0001 -p test_scan.py -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t20-candidate-package-privacy-0001 -p test_scan.py -q
```

[RESULT.json](RESULT.json) reports only counts, source pins, and zero matches for the selected classes. The scanner does not inspect protected Source8 bodies, encoded secrets outside its recognizers, transient API40 private controls, or human publication surfaces. It is a local candidate check, not a full privacy qualification.
