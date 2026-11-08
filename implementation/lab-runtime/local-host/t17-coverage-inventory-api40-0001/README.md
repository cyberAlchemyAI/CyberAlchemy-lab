# T17 API40 coverage inventory

`build_inventory.py` cold-maps the selected API40 protocol's 34 operations to available test-method candidates. It pins the API40, Action-v7, and Governance-v5 source/profile selections plus the historical T17 plan inputs. It physically rehashes every selected source-manifest row and refuses linked file origins. `INVENTORY-0001.json` is retained as the first review draft; `INVENTORY-0002.json` is the repaired immutable output. Run `python3 -B build_inventory.py --verify INVENTORY-0002.json` from this directory to compare a rebuilt inventory without writing.

The inventory identifies 26 positive and 22 negative source candidates, including 23 positives selected by the current cut's source manifest. Eight operations lack a positive source candidate and twelve lack a negative candidate. All per-operation common-dispatcher and same-lifetime causal proof flags remain false. This is a source inventory, not a run of all 34 operations or T17 qualification.

Five focused tests passed under normal and optimized Python. They check the exact 34-operation selection, changed-input and linked-ancestor refusal, retained-output comparison, and no overwrite of the versioned output.
