#!/usr/bin/env python3
"""Validate interface definitions and structural contract controls; no theorem claims."""
import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote
import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[5]
REPORT=BASE/"receipts/interface-validation.json"
def require(condition,message):
    if not condition:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def unique_pairs(pairs):
    found={}
    for k,v in pairs:
        require(k not in found,"Duplicate JSON key: "+k)
        found[k]=v
    return found
def read(path):
    return json.loads(Path(path).read_bytes(),object_pairs_hook=unique_pairs)
def errors(validator,value):
    return list(validator.iter_errors(value))
def main():
    schemas={p.name.removesuffix(".schema.json"):read(p) for p in (BASE/"schemas").glob("*.schema.json")}
    resources=Registry().with_resources((s["$id"],Resource.from_contents(s,default_specification=DRAFT202012)) for s in schemas.values())
    validators={n:jsonschema.Draft202012Validator(s,registry=resources,format_checker=jsonschema.FormatChecker()) for n,s in schemas.items()}
    for n,s in schemas.items():jsonschema.Draft202012Validator.check_schema(s)
    manifest=read(BASE/"package-manifest.json")
    for binding in manifest["sources"]:
        require(sha((ROOT/binding["path"]).read_bytes())==binding["sha256"],"Design source drift: "+binding["path"])
    require(sha((BASE/"build_interfaces.py").read_bytes())==manifest["generator_sha256"],"Generator drift")
    for artifact in manifest["artifacts"]:
        raw=(BASE/artifact["path"]).read_bytes()
        require(len(raw)==artifact["bytes"] and sha(raw)==artifact["sha256"],"Artifact drift: "+artifact["path"])
    # Resolve schema references without network access, including JSON Pointer targets.
    reference_count=0
    def walk_refs(node,base_uri):
        nonlocal reference_count
        if isinstance(node,dict):
            uri=node.get("$id",base_uri)
            if "$ref" in node:
                resources.resolver(uri).lookup(node["$ref"])
                reference_count+=1
            for v in node.values():walk_refs(v,uri)
        elif isinstance(node,list):
            for v in node:walk_refs(v,base_uri)
    for s in schemas.values():walk_refs(s,s["$id"])
    controls=read(BASE/"fixtures/schema-controls.json")
    positives=[]
    for control in controls["positive_examples"]:
        found=errors(validators[control["schema"]],read(BASE/control["path"]))
        require(not found,"Invalid positive fixture "+control["path"]+": "+("; ".join(e.message for e in found[:2])))
        positives.append({"path":control["path"],"schema":control["schema"],"result":"accepted-shape"})
    negatives=[]
    for control in controls["schema_negatives"]:
        found=errors(validators[control["schema"]],read(BASE/control["path"]))
        require(found,"Negative fixture accepted: "+control["name"])
        negatives.append({"name":control["name"],"result":"rejected","error_keywords":sorted({e.validator for e in found})})
    # Selected source import fidelity and exhaustive finite structural pair coverage.
    baseline=read(BASE/"profiles/baseline-snapshot.json")
    registry=read(BASE/"profiles/registry-snapshot.json")
    origin=read(ROOT/baseline["registry_source"]["repo_path"])
    imported={k["kind_id"]:k for k in registry["kinds"]}
    require(len(imported)==registry["kind_count"]==len(origin["entries"]),"Kind count mismatch")
    pair_count=0;pair_controls=0;cross_product_rejections=0
    def field_value(spec):
        if "const" in spec:return spec["const"]
        if "enum" in spec:return spec["enum"][0]
        kind=spec.get("type","string")
        if kind=="string":return "example:value"
        if kind=="boolean":return False
        if kind=="integer":return spec.get("minimum",1)
        if kind=="number":return spec.get("minimum",1)
        if kind=="array":return [field_value(spec.get("items",{"type":"string"})) for _ in range(spec.get("minItems",0))]
        if kind=="object":return {k:field_value(spec["properties"][k]) for k in spec.get("required",[])}
        raise ValueError("Unsupported qualifier fixture type: "+str(spec))
    seed=read(BASE/"examples/relation-assertion.json")
    for entry in origin["entries"]:
        raw=(ROOT/entry["instance_path"]).read_bytes()
        require(sha(raw)==entry["instance_sha256"],"Registry source changed")
        p=read(ROOT/entry["instance_path"])["payload"]; k=imported[entry["relation_kind_id"]]
        require(k["allowed_endpoint_pairs"]==p["allowed_endpoint_pairs"],"Ordered pairs changed")
        expected={"type":"object","additionalProperties":False,"properties":p["qualifier_contract"]["properties"],
            "required":p["qualifier_contract"]["required_axes"]}
        require(k["qualifier_schema"]==expected,"Qualifier shape changed")
        jsonschema.Draft202012Validator.check_schema(k["qualifier_schema"])
        require(k["forbidden_inferences"]==p["forbidden_inferences"],"Forbidden inference text changed")
        require(k["source_ref"]["sha256"]==sha(raw),"Source binding changed")
        allowed={(x["source_kind"],x["target_kind"]) for x in k["allowed_endpoint_pairs"]}
        pair_count+=len(k["allowed_endpoint_pairs"])
        template=copy.deepcopy(seed)
        template.update(relation_kind_id=k["kind_id"],relation_kind_version=k["version"],definition_ref=k["source_ref"])
        template["qualifiers"]={key:field_value(spec) for key,spec in expected["properties"].items() if key in expected["required"]}
        for source_kind,target_kind in allowed:
            fixture=copy.deepcopy(template);fixture["source"]["kind"]=source_kind;fixture["target"]["kind"]=target_kind
            found=errors(validators["registry-assertion"],fixture)
            require(not found,"Declared pair rejected: "+k["kind_id"]+" "+str((source_kind,target_kind)))
            pair_controls+=1
        for source_kind in {a for a,b in allowed}:
            for target_kind in {b for a,b in allowed}:
                if (source_kind,target_kind) not in allowed:
                    fixture=copy.deepcopy(template);fixture["source"]["kind"]=source_kind;fixture["target"]["kind"]=target_kind
                    require(errors(validators["registry-assertion"],fixture),"Cartesian-product pair accepted")
                    cross_product_rejections+=1
    require(pair_count==registry["relation_specific_pair_count"],"Pair count mismatch")
    # Materialization now has an explicit companion shape, with original string qualifiers.
    material=imported["relation.materializes-consequence"]
    sample=copy.deepcopy(seed)
    sample.update(relation_kind_id=material["kind_id"],relation_kind_version=material["version"],definition_ref=material["source_ref"])
    sample["source"]["kind"]="admission-transaction";sample["target"]["kind"]="generated-output"
    sample["qualifiers"]={"application_receipt_ref":"example:receipt","consequence_role":"example:output","output_digest":"example:opaque-original-string"}
    require(not errors(validators["l0-assertion"],sample),"Materialization companion shape rejected")
    # Cross-record structural guards. These deliberately do not establish truth of any theorem.
    structural=[]
    def rejected(name,fn):
        try:fn()
        except (ValueError,KeyError):structural.append({"name":name,"result":"rejected"})
        else:raise ValueError("Structural negative control accepted: "+name)
    def unique_ids(rows,key):
        ids=[r[key] for r in rows];require(len(ids)==len(set(ids)),"duplicate identity")
    def graph_guard(g):
        unique_ids(g["nodes"],"node_id");unique_ids(g["assertions"],"assertion_id")
        nodes={n["node_id"]:n for n in g["nodes"]}
        for a in g["assertions"]:
            for endpoint in ("source","target"):
                require(a[endpoint]["node_id"] in nodes,"dangling endpoint")
                require(a[endpoint]==nodes[a[endpoint]["node_id"]],"endpoint identity/version mismatch")
    graph=read(BASE/"examples/graph.json");graph_guard(graph)
    duplicate=copy.deepcopy(graph);duplicate["nodes"].append({**duplicate["nodes"][0],"version":"different"})
    rejected("duplicate-node-identity",lambda:graph_guard(duplicate))
    dangling=copy.deepcopy(graph);dangling["assertions"][0]["target"]["node_id"]="example:missing"
    rejected("dangling-endpoint",lambda:graph_guard(dangling))
    mismatch=copy.deepcopy(graph);mismatch["assertions"][0]["target"]["version"]="different"
    rejected("endpoint-version-mismatch",lambda:graph_guard(mismatch))
    def rule_guard(rules):
        unique_ids(rules["rules"],"rule_id")
        for rule in rules["rules"]:
            body_vars={a["variable"] for atom in rule["body"] for a in atom["arguments"] if "variable" in a}
            head_vars={a["variable"] for a in rule["head"]["arguments"] if "variable" in a}
            require(head_vars<=body_vars,"head variable is not range restricted")
    rules=read(BASE/"examples/rule-set.json");rule_guard(rules)
    not_restricted=copy.deepcopy(rules);not_restricted["rules"][0]["head"]["arguments"]=[{"variable":"NEW"}]
    rejected("non-range-restricted-rule",lambda:rule_guard(not_restricted))
    def derivation_guard(certificate):
        unique_ids(certificate["steps"],"step_id");seen=set()
        for step in certificate["steps"]:
            if step["kind"]=="rule":require(set(step["premise_step_ids"])<=seen,"unresolved or cyclic premise")
            seen.add(step["step_id"])
        require(certificate["conclusion_step_id"] in seen,"missing conclusion")
    certificate=read(BASE/"examples/derivation-certificate.json");derivation_guard(certificate)
    cycle=copy.deepcopy(certificate);cycle["steps"][1]["premise_step_ids"]=["s1"]
    rejected("cyclic-certificate",lambda:derivation_guard(cycle))
    missing=copy.deepcopy(certificate);missing["conclusion_step_id"]="missing"
    rejected("missing-certificate-conclusion",lambda:derivation_guard(missing))
    def model_guard(witness):
        require(witness["domain"],"empty domain");domain=set(witness["domain"])
        for predicate in witness["interpretations"]:
            for row in predicate["tuples"]:
                require(len(row)==predicate["arity"],"model arity mismatch")
                require(set(row)<=domain,"model member outside domain")
    witness=read(BASE/"examples/model-witness.json");model_guard(witness)
    wrong_arity=copy.deepcopy(witness);wrong_arity["interpretations"][0].update(arity=1,tuples=[[]])
    rejected("model-tuple-arity",lambda:model_guard(wrong_arity))
    wrong_member=copy.deepcopy(witness);wrong_member["interpretations"][0].update(arity=1,tuples=[["outside"]])
    rejected("model-member-outside-domain",lambda:model_guard(wrong_member))
    def complete_hard_results(obligations,results):
        unique_ids(obligations,"obligation_id");unique_ids(results,"obligation_id")
        got={r["obligation_id"]:r for r in results}
        for o in obligations:
            if o["hard"]:
                require(o["obligation_id"] in got,"missing hard obligation")
                r=got[o["obligation_id"]]
                require(r["required_statement_ref"]==o["required_statement_ref"],"required statement substitution")
                require(r["verdict"]=="satisfied" and r["execution"]=="completed" and r["currentness"]=="current","hard evidence incomplete")
                require(r["evidence_method"] in o["permitted_evidence_methods"] and r["evidence_refs"],"wrong evidence method")
    obligation=read(BASE/"examples/obligation.json");obligation.update(hard=True)
    rejected("omitted-hard-obligation",lambda:complete_hard_results([obligation],[]))
    changed=read(BASE/"examples/obligation-result.json")
    changed.update(obligation_id=obligation["obligation_id"],verdict="satisfied",execution="completed",
        currentness="current",evidence_method="kernel-proof",evidence_refs=[copy.deepcopy(obligation["required_statement_ref"])])
    changed["required_statement_ref"]["sha256"]="b"*64
    rejected("substituted-required-statement",lambda:complete_hard_results([obligation],[changed]))
    bounded=copy.deepcopy(changed);bounded["required_statement_ref"]=copy.deepcopy(obligation["required_statement_ref"]);bounded["evidence_method"]="bounded-search"
    rejected("wrong-hard-evidence-method",lambda:complete_hard_results([obligation],[bounded]))
    # OpenAPI meta-validation against the unmodified official document when supplied.
    api=read(BASE/"api/openapi.json")
    official=BASE/"validation/openapi31-official.schema.json"
    downloaded=Path("/tmp/relational-openapi-schema.json")
    if not official.exists() and downloaded.exists():
        official.parent.mkdir(parents=True,exist_ok=True);official.write_bytes(downloaded.read_bytes())
    require(official.exists(),"Official OpenAPI validation schema is unavailable")
    official_schema=read(official)
    jsonschema.Draft202012Validator(official_schema,format_checker=jsonschema.FormatChecker()).validate(api)
    api_ref_count=0;operation_ids=[]
    def local_api_refs(node):
        nonlocal api_ref_count
        if isinstance(node,dict):
            if "$ref" in node:
                reference=node["$ref"];api_ref_count+=1
                if reference.startswith("https://cyberalchemy.local/"):
                    resources.resolver().lookup(reference)
                elif reference.startswith("#/"):
                    pointer=api
                    for token in reference[2:].split("/"):pointer=pointer[unquote(token)]
                else:
                    target=(BASE/"api"/reference.split("#")[0]).resolve()
                    require(target.is_relative_to(BASE) and target.is_file(),"OpenAPI reference escape or missing target")
            for v in node.values():local_api_refs(v)
        elif isinstance(node,list):
            for v in node:local_api_refs(v)
    local_api_refs(api)
    for path,methods in api["paths"].items():
        for method,op in methods.items():
            operation_ids.append(op["operationId"])
            require(op["responses"],"missing operation response")
            expected=set(re.findall(r"\{([^}]+)\}",path))
            actual={p["name"] for p in op.get("parameters",[]) if p["in"]=="path" and p["required"]}
            require(expected==actual,"path parameter mismatch")
            if "202" in op["responses"]:
                require("x-result-schema" in op,"asynchronous result contract missing")
                require(any(p["name"]=="Idempotency-Key" and p["required"] for p in op.get("parameters",[])),"missing idempotency contract")
    require(len(operation_ids)==len(set(operation_ids))==manifest["counts"]["api_operations"],"operation uniqueness/count mismatch")
    # Every planned task is covered once or more, without claiming its execution.
    plan=read(ROOT/"docs/plans/relational-theorem-checker/PLAN-SOURCE.json")
    contracts=read(BASE/"contracts/contract-set.json")["contracts"]
    ids={t["id"] for t in plan["tasks"]}
    covered={i for c in contracts for i in c["task_ids"]}
    require(covered==ids,"DAG contract coverage mismatch")
    require(len({c["contract_id"] for c in contracts})==len(contracts),"duplicate contract")
    for c in contracts:require(c["input_schema"] in schemas and c["output_schema"] in schemas,"unknown contract schema")
    # Local links and self-contained explorer structure.
    links=0
    for p in BASE.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)",p.read_text()):
            if "://" in target or target.startswith("#"):continue
            resolved=(p.parent/target.split("#")[0]).resolve()
            require(resolved.is_file() or resolved==REPORT,"missing Markdown link: "+str(p)+": "+target)
            links+=1
    class ExplorerParser(HTMLParser):
        def __init__(self):super().__init__();self.ids=set();self.script_external=[];self.lanes=set();self.in_data=False;self.data=""
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if "id" in a:
                require(a["id"] not in self.ids,"duplicate HTML ID");self.ids.add(a["id"])
            if "data-lane" in a:self.lanes.add(a["data-lane"])
            if tag=="script" and "src" in a:self.script_external.append(a["src"])
            if tag=="script" and a.get("id")=="package-data":self.in_data=True
        def handle_endtag(self,tag):
            if tag=="script":self.in_data=False
        def handle_data(self,value):
            if self.in_data:self.data+=value
    page=(BASE/"index.html").read_text();parser=ExplorerParser();parser.feed(page)
    require(not parser.script_external,"explorer requires external JavaScript")
    parsed=json.loads(parser.data)
    require(len(parsed["schemas"])==len(schemas),"explorer catalog mismatch")
    require({"surface","flow","components","properties","internal_dependencies","external_dependencies","risk_questions","lifecycle"}<=parser.lanes,"missing visual lane")
    require({"category","layer","search","list","definition","example"}<=parser.ids,"missing explorer controls")
    report={"schema_version":"relational-checker.interface-validation/v1-candidate","result":"pass",
        "claim_ceiling":"Schema and API definition validation, selected registry structural fidelity and declared cross-record shape controls only. No Lean proof, semantic theorem, model satisfaction or running API validation.",
        "counts":{"schemas":len(schemas),"schema_references":reference_count,"positive_fixtures":len(positives),
            "schema_negative_controls":len(negatives),"cross_record_negative_controls":len(structural),
            "kind_count":len(imported),"declared_pairs_exercised":pair_controls,
            "cartesian_product_pairs_rejected":cross_product_rejections,"api_operations":len(operation_ids),
            "api_references":api_ref_count,"dag_tasks_covered":len(covered),"markdown_links":links},
        "official_openapi_schema":{"url":"https://spec.openapis.org/oas/3.1/schema/2022-10-07",
            "sha256":sha(official.read_bytes()),"result":"pass"},
        "schema_positives":positives,"schema_negatives":negatives,"structural_negatives":structural,
        "materialization_companion_control":"accepted structural shape; no authority/evidence legitimacy claim",
        "explorer":{"structure":"pass","interaction":"not-yet-browser-tested"},
        "validator_sha256":sha(Path(__file__).read_bytes()),"package_manifest_sha256":sha((BASE/"package-manifest.json").read_bytes()),
        "authority_effect":"none","execution_tasks":"F0 accepted; interface/decoder implementation and other tasks not-started"}
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"result":"pass","counts":report["counts"],"official_openapi_schema":"pass",
        "claim_ceiling":report["claim_ceiling"]},indent=2))
if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,OSError,jsonschema.ValidationError,jsonschema.SchemaError) as error:
        raise SystemExit("Interface validation failed: "+str(error))
