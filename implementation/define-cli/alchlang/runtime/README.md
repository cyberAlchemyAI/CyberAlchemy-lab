# Define host adapter

This directory owns the existing CLI, source-pinned Work journal, exact-byte Pack
port, example requests and runtime regression tests. The maintained AlchLang model
lives one level above, in `modules/` and the root composition files.

`frozen-source.json` pins the exact source digest required by existing journals.
`frozen-source.mjs` checks the archived snapshot's SHA-256, extracts only its three
compiler inputs into ignored cache, checks each input hash, and verifies the
original model fingerprint before compilation. The frozen source is a
compatibility input, not a second editable model.

Changing the maintained model does not authorize a journal migration. The CLI
continues to use the frozen replay engine until an explicit compatibility/cutover
change is implemented and verified. The `sources` command displays the maintained
model, while `doctor` identifies the replay engine and its exact source digest.

Run the host regression checks with the selected shared Node:

```bash
"$(node --input-type=module -e "import {node} from './implementation/define-cli/alchlang/runtime/build.mjs'; process.stdout.write(node)")" --test implementation/define-cli/alchlang/runtime/tests/define.test.mjs
```
