# T10 O05 local signed branch rebind

This disjoint successor rebinds the disposable current T12 technical Work branch to the selected O03 0004 loader SHA-256 `13f889f60430ebf53818bd9e4648e184dcbb23a2f3456ed01f0af014efa21676`, which restores `sys.path` after executing the nested scope. `branch.py` constructs an ephemeral signed local branch and retains only its five public store files. [run-0001/RESULT.json](run-0001/RESULT.json) binds the selected current query, new loader and signed transaction. [REPLAY-0001.json](REPLAY-0001.json) is parsed-JSON-equal to that result after a separate cold replay; it is byte-identical to [CONSTRUCT-0001.json](CONSTRUCT-0001.json), whose formatting differs from the retained run result. The prior 0001 branch and original O05 archive remain untouched.

```sh
python3 -B implementation/lab-runtime/local-host/t10-o05-current-signed-branch-0002/branch.py replay implementation/lab-runtime/local-host/t10-o05-current-signed-branch-0002/run-0001
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t10-o05-current-signed-branch-0002 -p 'test_branch.py' -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t10-o05-current-signed-branch-0002 -p 'test_branch.py' -q
```

The signer is a disposable local technical fixture. This does not admit repository authority, select a GovernedModel, reconstruct missing original O05 observations, or qualify the historical O05 event package as current.
