"""Independent conformance over captured native records and pre-admission targets."""
import base64,json,sys,hashlib
from jsonschema import Draft202012Validator
q=json.load(sys.stdin)
output=json.loads(base64.b64decode(q["output_material"]))
fixture=json.loads(base64.b64decode(q["fixture_material"]))
records={r["version_ref"]:r for r in output["records"]}
assert len(records)==len(output["records"]),"duplicate-record-version"
for wanted in fixture["expected"]:
 actual=records[wanted["version"]]
 assert actual["body"]==wanted["body"],"record-original-body-mismatch"
 assert actual["carrier"]==wanted["carrier"],"record-carrier-mismatch"
 assert actual["standing"] in ["admitted-current","local-admitted-current"],"record-not-current"
 Draft202012Validator(fixture["schemas"][wanted["carrier"]]).validate(actual["body"])
assert output["source_cut"]==fixture["source_cut"]
print(json.dumps({"status":"PASS","records":len(fixture["expected"]),"scope":"Exact pre-admission bodies, registered schemas, carriers, standing and source cut."}))
