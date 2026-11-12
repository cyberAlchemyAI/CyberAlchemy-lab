"""Independent check over captured output and an authority-derived fixture."""
import base64,json,sys
request=json.load(sys.stdin)
package=json.loads(base64.b64decode(request["output_material"]))
registry=json.loads(base64.b64decode(package["registry"]["bytes_base64"]))
fixture=json.loads(base64.b64decode(request["fixture_material"]))
contract=json.loads(base64.b64decode(request["contract_material"]))
assert len(contract["contracts"])==10
entries={e["definition_id"]+"@"+e["version"]:e for e in registry["entries"]}
assert len(entries)==len(registry["entries"])
expected=fixture["expected"]
check=fixture["check"]
if check=="membership":
 assert set(entries)==set(expected)
elif check=="original-bodies":
 for version,fact in expected.items():
  assert entries[version]["body"]["sha256"]==fact["sha256"]
  assert entries[version]["body"]["bytes"]==fact["bytes"]
  assert entries[version]["carrier"]["ref"]==fact["carrier"]
elif check=="standing":
 assert registry["current_lookup"]==fixture["current_lookup"]
 for identity,version in registry["current_lookup"].items():
  assert entries[version]["standing"]=="admitted-current"
 for version,entry in entries.items():
  if registry["current_lookup"].get(entry["definition_id"])!=version:
   assert entry["standing"]=="admitted-retained"
elif check=="generation":
 import hashlib
 generation=package["generation"]
 assert generation["source"]==fixture["model_source"]
 assert generation["manifest_sha256"]==fixture["manifest_sha256"]
 captured=generation["files"]
 for name,fact in captured.items():
  raw=base64.b64decode(fact["bytes_base64"])
  assert hashlib.sha256(raw).hexdigest()==fact["sha256"]
 assert hashlib.sha256(base64.b64decode(captured["manifest.json"]["bytes_base64"])).hexdigest()==generation["manifest_sha256"]
 assert package["chain"]==["definitions","artifacts","ontology","business-system bridge ontology","system-ontology","AlchLang","generation"]
else:raise AssertionError("unknown independently qualified check")
print(json.dumps({"status":"PASS","check":check,"versions":len(entries)}))
