# T16 API40 first inherited regression probe

`probe.py` runs one inherited guarded-read case in the API40-selected host environment. Its `setUpClass` exits before the method because the historical participation adapter selects `jsonschema 4.23.0`, while API40 selects `4.19.2`. `RESULT.json` records zero executed tests and a setup error; it is not a passing regression result. The compatible environment or source-selection route must be resolved before this case can count. The full inherited suite remains open.

Run `python3 -B implementation/lab-runtime/local-host/t16-api40-regression-probe-0001/probe.py` from the repository root and compare its JSON output with `RESULT.json`.
