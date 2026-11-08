# T17 next live batch selection

`inventory.py` pins the T17 work-pack, the selected All34 plan, and the current API protocol. It proves that the protocol exposes the exact 34 selected operation names and that `session.open` and `session.close` are available for the smallest useful same-process positive/negative batch after `context.get` delivery.

`RESULT.json` grants no live T17 credit. Its seven read names are historical evidence from a different Source family; every fresh-family coverage flag remains false. The next run needs one frozen corrected Source8 family and API cut, actual Session open and close effects, and causal negative refusals with unchanged owned effects.

Replay with `python3 inventory.py` and `python3 -m unittest test_inventory.py`; also run the test under `python3 -O`. This inventory neither creates authority nor admits a source.
