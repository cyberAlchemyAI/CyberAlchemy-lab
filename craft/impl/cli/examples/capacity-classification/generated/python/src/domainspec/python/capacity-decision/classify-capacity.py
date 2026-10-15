# domainspec-meta: {"baseline_digest":"bfbc335d151ab8b29150dc95f246c2bc0954cff179ece5ce51222b2d1455abda","baseline_id":"domainspec-meta-types-current-implemented@10","binding_sha256":"d8e6cdc2efbda45169c40d7452df525eefaa78df4122b387e7714122f5e4d524","language":"python","meta_type_id":"DS-D1.6","meta_type_label":"Calculation","provider_sha256":"29b655e415b14ad87d524b1b066492b407e1cc50120b760c3c1da9d7fc32d1f0","source_sha256":"c88603aa11c590a68113c04e537a59635e59d8ef2ea035c92a45d7583d3d99d0"}
# domainspec-body: {"description":"Classify a supplied snapshot: Accept when requested units are strictly below available units; otherwise Reject. This pure derivation reserves no capacity.","inputs":["snapshot"],"typed_contract":{"expression":{"condition":{"arguments":[{"parameter":"snapshot","value":{"op":"path","properties":[],"root":"snapshot"}}],"op":"rule_ref","selector":"capacity-decision:within-capacity"},"else":{"payload":null,"variant":"Reject"},"op":"if","then":{"payload":null,"variant":"Accept"}},"inputs":[{"name":"snapshot","type":{"kind":"named","selector":"capacity-decision:capacity-snapshot"}}],"ontology_calculation":"CAPACITY-CALC-CLASSIFY","result":{"kind":"named","selector":"capacity-decision:capacity-decision"},"schema_version":"domainspec.typed-calculation/v2"}}
# domainspec-relationships: []
# domainspec-calculation-semantics: "domainspec.typed-calculation/v2"
# domainspec-typed-closure-sha256: "05dbda85a04b79e541da93324fdecd6dc0b8590417b88c805b1ac4116b97a41c"
import json

_DOMAINSPEC_RULE_ROOT = "capacity-decision:classify-capacity"
_DOMAINSPEC_RULE_PROPERTIES = json.loads("{\"CAPACITY-SNAPSHOT#available_units\":\"available_units\",\"CAPACITY-SNAPSHOT#request_id\":\"request_id\",\"CAPACITY-SNAPSHOT#requested_units\":\"requested_units\"}")
_DOMAINSPEC_RULE_CONTRACTS = json.loads("{\"capacity-decision:within-capacity\":{\"expression\":{\"left\":{\"op\":\"path\",\"properties\":[\"CAPACITY-SNAPSHOT#requested_units\"],\"root\":\"snapshot\"},\"op\":\"lt\",\"right\":{\"op\":\"path\",\"properties\":[\"CAPACITY-SNAPSHOT#available_units\"],\"root\":\"snapshot\"}},\"ontology_rule\":\"CAPACITY-RULE-WITHIN-AVAILABLE\",\"parameters\":[{\"name\":\"snapshot\",\"type\":{\"kind\":\"named\",\"selector\":\"capacity-decision:capacity-snapshot\"}}],\"schema_version\":\"domainspec.typed-rule/v1\"}}")

def _domainspec_stable(value: object) -> str:
    if isinstance(value, set):
        return json.dumps(sorted(_domainspec_stable(item) for item in value), separators=(",", ":"))
    if isinstance(value, list):
        return json.dumps([_domainspec_stable(item) for item in value], separators=(",", ":"))
    if isinstance(value, dict):
        return json.dumps({key: _domainspec_stable(value[key]) for key in sorted(value)}, separators=(",", ":"))
    return json.dumps(value, separators=(",", ":"))

def _domainspec_value(expression: dict[str, object], environment: dict[str, object]) -> object:
    operation = expression["op"]
    if operation == "literal": return expression["value"]
    if operation == "variant": return expression["selector"]
    if operation == "to_set": return {_domainspec_stable(item) for item in _domainspec_value(expression["value"], environment)}
    current = environment[expression["root"]]
    for property_selector in expression["properties"]:
        field = _DOMAINSPEC_RULE_PROPERTIES[property_selector]
        current = [entry[field] for entry in current] if isinstance(current, list) else current[field]
    return current

def _domainspec_evaluate_expression(expression: dict[str, object], environment: dict[str, object]) -> bool:
    operation = expression["op"]
    if operation in ("all", "any"):
        values = (_domainspec_evaluate_expression(term, environment) for term in expression["terms"])
        return all(values) if operation == "all" else any(values)
    if operation == "not": return not _domainspec_evaluate_expression(expression["term"], environment)
    if operation in ("eq", "lt", "set_equal", "contains"):
        left = _domainspec_value(expression["left"], environment); right = _domainspec_value(expression["right"], environment)
        if operation == "lt": return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left < right
        if operation == "contains": return _domainspec_stable(right) in left if isinstance(left, set) else any(_domainspec_stable(item) == _domainspec_stable(right) for item in left)
        return _domainspec_stable(left) == _domainspec_stable(right)
    if operation in ("exactly_one", "exists", "unique"):
        collection = _domainspec_value(expression["collection"], environment)
        if not isinstance(collection, (list, set, tuple)): raise ValueError("Rule quantifier requires a collection")
        if operation == "unique":
            keys = [_domainspec_stable(_domainspec_value(expression["where"]["left"], {**environment, expression["binding"]: item})) for item in collection]
            return len(set(keys)) == len(keys)
        matches = sum(1 for item in collection if _domainspec_evaluate_expression(expression["where"], {**environment, expression["binding"]: item}))
        return matches == 1 if operation == "exactly_one" else matches > 0
    if operation == "rule_ref": return _domainspec_evaluate(expression["selector"], {argument["parameter"]: _domainspec_value(argument["value"], environment) for argument in expression["arguments"]})
    raise ValueError(f"unsupported Rule operator:{operation}")

def _domainspec_evaluate(selector: str, environment: dict[str, object]) -> bool:
    contract = _DOMAINSPEC_RULE_CONTRACTS.get(selector)
    if contract is None: raise ValueError(f"unresolved Rule reference:{selector}")
    if any(parameter["name"] not in environment for parameter in contract["parameters"]): raise ValueError(f"missing Rule parameter:{selector}")
    return _domainspec_evaluate_expression(contract["expression"], environment)

_DOMAINSPEC_CALCULATION_TYPES = json.loads("{\"inputs\":[{\"name\":\"snapshot\",\"type\":{\"kind\":\"named\",\"selector\":\"capacity-decision:capacity-snapshot\"}}],\"types\":{\"capacity-decision:capacity-decision\":{\"ontology_node\":\"CAPACITY-DECISION\",\"schema_version\":\"domainspec.typed-sum/v1\",\"variants\":[{\"name\":\"Accept\",\"ontology_variant\":\"CAPACITY-DECISION#Accept\",\"payload\":null},{\"name\":\"Reject\",\"ontology_variant\":\"CAPACITY-DECISION#Reject\",\"payload\":null}]},\"capacity-decision:capacity-snapshot\":{\"ontology_node\":\"CAPACITY-SNAPSHOT\",\"properties\":[{\"cardinality\":\"one\",\"identity\":true,\"meaning\":\"Stable identity of the capacity request.\",\"name\":\"request_id\",\"ontology_property\":\"CAPACITY-SNAPSHOT#request_id\",\"type\":{\"kind\":\"scalar\",\"name\":\"String\"}},{\"cardinality\":\"one\",\"identity\":false,\"meaning\":\"Units requested by the operation.\",\"name\":\"requested_units\",\"ontology_property\":\"CAPACITY-SNAPSHOT#requested_units\",\"type\":{\"kind\":\"scalar\",\"name\":\"UInt64\"}},{\"cardinality\":\"one\",\"identity\":false,\"meaning\":\"Units available at the decision boundary.\",\"name\":\"available_units\",\"ontology_property\":\"CAPACITY-SNAPSHOT#available_units\",\"type\":{\"kind\":\"scalar\",\"name\":\"UInt64\"}}],\"schema_version\":\"domainspec.typed-record/v1\"},\"capacity-decision:classify-capacity\":{\"expression\":{\"condition\":{\"arguments\":[{\"parameter\":\"snapshot\",\"value\":{\"op\":\"path\",\"properties\":[],\"root\":\"snapshot\"}}],\"op\":\"rule_ref\",\"selector\":\"capacity-decision:within-capacity\"},\"else\":{\"payload\":null,\"variant\":\"Reject\"},\"op\":\"if\",\"then\":{\"payload\":null,\"variant\":\"Accept\"}},\"inputs\":[{\"name\":\"snapshot\",\"type\":{\"kind\":\"named\",\"selector\":\"capacity-decision:capacity-snapshot\"}}],\"ontology_calculation\":\"CAPACITY-CALC-CLASSIFY\",\"result\":{\"kind\":\"named\",\"selector\":\"capacity-decision:capacity-decision\"},\"schema_version\":\"domainspec.typed-calculation/v2\"},\"capacity-decision:within-capacity\":{\"expression\":{\"left\":{\"op\":\"path\",\"properties\":[\"CAPACITY-SNAPSHOT#requested_units\"],\"root\":\"snapshot\"},\"op\":\"lt\",\"right\":{\"op\":\"path\",\"properties\":[\"CAPACITY-SNAPSHOT#available_units\"],\"root\":\"snapshot\"}},\"ontology_rule\":\"CAPACITY-RULE-WITHIN-AVAILABLE\",\"parameters\":[{\"name\":\"snapshot\",\"type\":{\"kind\":\"named\",\"selector\":\"capacity-decision:capacity-snapshot\"}}],\"schema_version\":\"domainspec.typed-rule/v1\"}}}")
def _domainspec_validate_calculation_value(type_spec: dict[str, object], value: object) -> None:
    kind = type_spec["kind"]
    if kind == "scalar":
        name = type_spec["name"]
        valid = isinstance(value, str) if name == "String" else type(value) is bool if name == "Bool" else type(value) is int and 0 <= value <= 9007199254740991
        if not valid: raise ValueError(f"invalid Calculation scalar:{name}")
        return
    if kind == "optional":
        if value is not None: _domainspec_validate_calculation_value(type_spec["element"], value)
        return
    if kind in ("list", "set"):
        if not isinstance(value, list): raise ValueError("Calculation collection requires a list")
        if kind == "set" and len({_domainspec_stable(child) for child in value}) != len(value): raise ValueError("duplicate Calculation set member")
        for child in value: _domainspec_validate_calculation_value(type_spec["element"], child)
        return
    contract = _DOMAINSPEC_CALCULATION_TYPES["types"].get(type_spec["selector"]) if kind == "named" else type_spec
    if not isinstance(value, dict) or contract is None: raise ValueError("invalid Calculation named value")
    if contract.get("schema_version") == "domainspec.typed-record/v1":
        if sorted(value) != sorted(prop["name"] for prop in contract["properties"]): raise ValueError("Calculation record fields must match the contract")
        for prop in contract["properties"]: _domainspec_validate_calculation_value(prop["type"], value[prop["name"]])
        return
    variant = next((candidate for candidate in contract.get("variants", []) if candidate["name"] == value.get("variant")), None)
    if variant is None or sorted(value) != ["payload", "variant"]: raise ValueError("invalid Calculation variant")
    if variant["payload"] is None:
        if value["payload"] is not None: raise ValueError("unexpected Calculation variant payload")
    else: _domainspec_validate_calculation_value(variant["payload"], value["payload"])

def _domainspec_validate_calculation_inputs(inputs: dict[str, object]) -> None:
    if not isinstance(inputs, dict) or sorted(inputs) != sorted(parameter["name"] for parameter in _DOMAINSPEC_CALCULATION_TYPES["inputs"]): raise ValueError("Calculation inputs must match the contract")
    for parameter in _DOMAINSPEC_CALCULATION_TYPES["inputs"]: _domainspec_validate_calculation_value(parameter["type"], inputs[parameter["name"]])

def classify_capacity(inputs: dict[str, object]) -> dict[str, object]:
    _domainspec_validate_calculation_inputs(inputs)
    expression = json.loads("{\"condition\":{\"arguments\":[{\"parameter\":\"snapshot\",\"value\":{\"op\":\"path\",\"properties\":[],\"root\":\"snapshot\"}}],\"op\":\"rule_ref\",\"selector\":\"capacity-decision:within-capacity\"},\"else\":{\"payload\":null,\"variant\":\"Reject\"},\"op\":\"if\",\"then\":{\"payload\":null,\"variant\":\"Accept\"}}")
    branch = expression["then"] if _domainspec_evaluate_expression(expression["condition"], inputs) else expression["else"]
    return {"variant": branch["variant"], "payload": None}
