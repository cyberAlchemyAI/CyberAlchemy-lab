#!/usr/bin/env python3
"""Author the candidate relational theorem-checker interface package; no server or prover."""
import argparse
import copy
import hashlib
import html
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[5]
PLAN = ROOT / "docs/plans/relational-theorem-checker"
DIALECT = "https://json-schema.org/draft/2020-12/schema"
NS = "https://cyberalchemy.local/schemas/relational-checker/v1/"
FILES, CATALOG, EXAMPLES = {}, [], {}
BT = chr(96)
def data(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
def sha(value):
    return hashlib.sha256(value).hexdigest()
def emit(path, value):
    FILES[path] = value.encode() if isinstance(value, str) else data(value)
def text():
    return {"type":"string","minLength":1}
def enum(*values):
    return {"enum":list(values)}
def const(value):
    return {"const":value}
def obj(properties, required=None):
    return {"type":"object","additionalProperties":False,"properties":properties,
            "required":list(properties) if required is None else required}
def arr(items, minimum=0, unique=False):
    return {"type":"array","items":items,"minItems":minimum,**({"uniqueItems":True} if unique else {})}
def ref(name):
    return {"$ref":NS+name+".schema.json"}
def common(name):
    return {"$ref":NS+"common.schema.json#/$defs/"+name}
def nullable(schema):
    return {"anyOf":[schema,{"type":"null"}]}
def version(name):
    return "relational-checker."+name+"/v1-candidate"
def add(name, layer, purpose, properties=None, required=None, extra=None, body=None):
    schema = {"$schema":DIALECT,"$id":NS+name+".schema.json","title":name.replace("-"," ").title(),
        "description":purpose,"x-layer":layer,"x-status":"candidate-interface"}
    if body is None:
        fields={"schema_version":const(version(name)),**(properties or {})}
        schema.update(obj(fields, ["schema_version"] + (list(properties or {}) if required is None else required)))
    else:
        schema.update(body)
    schema.update(extra or {})
    emit("schemas/"+name+".schema.json",schema)
    CATALOG.append({"name":name,"layer":layer,"purpose":purpose,"path":"schemas/"+name+".schema.json",
        "required":schema.get("required",[]),"refs":[]})
    return schema
def example(name, **fields):
    value={"schema_version":version(name),**fields}
    emit("examples/"+name+".json",value)
    EXAMPLES[name]=value
    return value
def exact(label="artifact"):
    return {"artifact_id":"example:"+label,"sha256":"a"*64,"size_bytes":1,"media_type":"application/json"}
def source_binding(path):
    raw=(ROOT/path).read_bytes()
    return {"repo_path":path,"sha256":sha(raw),"size_bytes":len(raw)}
def artifact(path):
    raw=FILES[path]
    return {"artifact_id":"package:"+path,"sha256":sha(raw),"size_bytes":len(raw),
            "media_type":"application/json" if path.endswith(".json") else "text/plain"}
def point(name="capability", kind="capability-instance"):
    return {"node_id":"example:"+name,"version":"candidate.1","kind":kind,"source_ref":exact(name)}
def declarations():
    add("common","shared","Reusable exact identities, typed endpoints, statuses and diagnostics.",body={
        "$defs":{
            "text":text(),"digest":{"type":"string","pattern":"^[a-f0-9]{64}$"},
            "exact-ref":obj({"artifact_id":text(),"sha256":{"type":"string","pattern":"^[a-f0-9]{64}$"},
                "size_bytes":{"type":"integer","minimum":1},
                "media_type":enum("application/json","text/plain","application/octet-stream")}),
            "source-binding":obj({"repo_path":{"type":"string","pattern":r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$)).+$"},
                "sha256":{"type":"string","pattern":"^[a-f0-9]{64}$"},"size_bytes":{"type":"integer","minimum":1}}),
            "node-ref":obj({"node_id":text(),"version":text(),"kind":text(),"source_ref":common("exact-ref")}),
            "pair":obj({"source_kind":text(),"target_kind":text()}),
            "diagnostic":obj({"code":text(),"message":text(),"location":text(),"obligation_id":nullable(text()),
                "artifact_ref":nullable(common("exact-ref")),"next_action":text()}),
            "verdict":enum("satisfied","violated","unknown","unsupported","not-run"),
            "execution":enum("completed","timeout","unavailable","provider-error"),
            "currentness":enum("current","stale","unresolved"),
            "evidence-method":enum("verified-checker","kernel-proof","checked-model-witness","bounded-search","none"),
            "ground-atom":obj({"predicate":text(),"arguments":arr(text())}),
            "term":{"oneOf":[obj({"variable":text()}),obj({"constant":text()})]},
            "atom":obj({"predicate":text(),"arguments":arr(common("term"))}),
            "protected-key":obj({"target_version_ref":common("exact-ref"),"effect":text(),"scope":text(),"epoch":text()})
        }})
    add("baseline-snapshot","L0","Exact source snapshot with explicit source/effective-state overlay; no claim of perpetual freshness.",{
        "snapshot_id":text(),"registry_source":common("source-binding"),
        "source_bindings":arr(common("source-binding"),1,True),
        "effective_state_bindings":arr(obj({"kind_id":text(),"source_lifecycle":text(),
            "effective_lifecycle":text(),"admission_decision_id":text(),"registry_evidence":common("source-binding")}),1),
        "captured_at":{"type":"string","format":"date-time"},"authority_effect":const("none")})
    add("relation-kind","L1","Normalized declaration retaining ordered pairs, original qualifier schema and forbidden justifications.",{
        "kind_id":text(),"version":text(),"source_ref":common("exact-ref"),"source_binding":common("source-binding"),
        "axis_id":text(),"allowed_endpoint_pairs":arr(common("pair"),1,True),
        "qualifier_schema":{"type":"object","description":"A Draft 2020-12 schema; validate against the meta-schema separately."},
        "forbidden_inferences":arr(text(),0,True),"source_lifecycle":text(),"effective_lifecycle":text(),
        "semantic_state":enum("imported","defined","proved","unsupported"),"prose_semantics":text()})
    add("registry-snapshot","L1","A finite registry declaration import; counts and hash bindings are recomputed by the consumer.",{
        "registry_id":text(),"baseline_ref":common("exact-ref"),"kinds":arr(ref("relation-kind"),1),
        "kind_count":{"type":"integer","minimum":1},"relation_specific_pair_count":{"type":"integer","minimum":1}})
    add("semantic-profile","L0","Explicit candidate semantic input profile with reviewed meaning required before semantic readiness.",{
        "profile_id":text(),"baseline_ref":common("exact-ref"),"registry_ref":common("exact-ref"),
        "carrier":enum("candidate-companion","explicit-successor"),"supported_kind_ids":arr(text(),1,True),
        "invariant_statement_refs":arr(common("exact-ref"),1,True),
        "normative_review":obj({"state":enum("draft","reviewed"),"review_ref":nullable(common("exact-ref"))}),
        "rule_profile_ref":nullable(common("exact-ref")),"trusted_boundaries":arr(enum(
            "source-interpretation","json-decoder","hash-function","compiled-runtime","proof-kernel"),1,True),
        "authority_effect":const("none")},extra={"allOf":[{
            "if":{"properties":{"normative_review":{"properties":{"state":const("reviewed")}}}},
            "then":{"properties":{"normative_review":{"properties":{"review_ref":common("exact-ref")}}}}}]})
    add("relation-assertion","L0","Identified relation assertion. Dynamic qualifier validity is checked against the selected kind declaration.",{
        "assertion_id":text(),"relation_kind_id":text(),"relation_kind_version":text(),"definition_ref":common("exact-ref"),
        "source":common("node-ref"),"target":common("node-ref"),
        "qualifiers":{"type":"object","description":"Intentional dynamic map; the selected kind's closed qualifier schema applies."}})
    add("graph","L0","Finite identified graph. Identity uniqueness and endpoint referential integrity are contract obligations.",{
        "graph_id":text(),"nodes":arr(common("node-ref"),1),"assertions":arr(ref("relation-assertion"))})
    add("normalization-report","L0","Field-preservation projection, exact dependencies and remaining parser trust boundary.",{
        "input_ref":common("exact-ref"),"profile_ref":common("exact-ref"),"normal_form_ref":common("exact-ref"),
        "source_mappings":arr(obj({"source_pointer":text(),"target_pointer":text(),"source_ref":common("exact-ref")}),1),
        "diagnostics":arr(common("diagnostic")),"parser_proof_status":enum("trusted","proved","unsupported")})
    add("reference-assessment","L1","Resolution assessment does not upgrade an arbitrary qualifier string into authenticated authority.",{
        "assertion_ref":common("exact-ref"),"qualifier_name":text(),"raw_value":text(),
        "expected_kind":text(),"expected_version":text(),"scope":text(),"resolved_ref":nullable(common("exact-ref")),
        "verdict":common("verdict"),"diagnostics":arr(common("diagnostic"))})
    add("coverage-ledger","L1","Keep declaration import, structural checks, defined semantics, proofs and unsupported obligations distinct.",{
        "registry_ref":common("exact-ref"),"profile_ref":common("exact-ref"),
        "rows":arr(obj({"kind_id":text(),"declaration_imported":{"type":"boolean"},
            "structural_verdict":common("verdict"),"semantics_state":enum("defined","unresolved","unsupported"),
            "required_obligation_ids":arr(text(),0,True),"proved_obligation_ids":arr(text(),0,True),
            "unresolved_obligation_ids":arr(text(),0,True),"evidence_refs":arr(common("exact-ref"),0,True)}),1)})
    add("change-proposal","L2","Exact baseline and proposed graph/registry/rules identities; author labels are checked against an independent diff.",{
        "proposal_id":text(),"baseline_ref":common("exact-ref"),"base_graph_ref":common("exact-ref"),
        "proposed_graph_ref":common("exact-ref"),"base_registry_ref":common("exact-ref"),
        "proposed_registry_ref":common("exact-ref"),"base_rules_ref":nullable(common("exact-ref")),
        "proposed_rules_ref":nullable(common("exact-ref")),"author_change_labels":arr(enum(
            "instance-addition","kind-addition","endpoint-pair-change","qualifier-change","rule-change",
            "identity-mapping-change"),1,True),
        "requested_claims":arr(enum("selected-data-compatibility","invariant-preservation","model-conservativity",
            "protected-lineage","non-entailment"),1,True),"authority_effect":const("none")})
    add("semantic-diff","L2","Normalized exact changes computed by the consumer, not accepted from author labels.",{
        "proposal_ref":common("exact-ref"),"base_ref":common("exact-ref"),"proposed_ref":common("exact-ref"),
        "changes":arr(obj({"change_id":text(),"classification":text(),"location":text(),
            "before_ref":nullable(common("exact-ref")),"after_ref":nullable(common("exact-ref"))}),1),
        "unsupported_changes":arr(text(),0,True)})
    add("obligation","L2","An independently required statement with exact premises, scope and permitted evidence methods.",{
        "obligation_id":text(),"layer":enum("L0","L1","L2","L3","L4"),"family":enum(
            "signature-validity","qualifier-validity","reference-validity","graph-invariant","checker-soundness",
            "projection-fidelity","obligation-coverage","selected-data-compatibility","invariant-preservation",
            "inhabitation","model-conservativity","derivation-soundness","closure-adequacy",
            "protected-lineage","non-entailment","proof-submission-audit","freshness"),
        "hard":{"type":"boolean"},"required_statement_ref":common("exact-ref"),
        "required_dependency_refs":arr(common("exact-ref"),1,True),"scope_ref":common("exact-ref"),
        "generated_by_policy_ref":common("exact-ref"),
        "permitted_evidence_methods":arr(enum("verified-checker","kernel-proof","checked-model-witness"),1,True),
        "requirement_source_ref":common("exact-ref")})
    add("obligation-set","L2","Complete required set generated from actual diff and selected policy; client-submitted subsets are not authoritative.",{
        "set_id":text(),"proposal_ref":common("exact-ref"),"diff_ref":common("exact-ref"),
        "policy_ref":common("exact-ref"),"obligations":arr(ref("obligation"),1),
        "coverage_statement_ref":common("exact-ref")})
    add("rule-profile","L3","Finite positive function-free range-restricted profile with explicitly defined protected roots.",{
        "profile_id":text(),"language":const("finite-positive-function-free-range-restricted"),
        "ground_universe":arr(text(),1,True),"protected_predicates":arr(obj({
            "predicate":text(),"argument_roles":const(["targetVersion","effect","scope","epoch"])}),1),
        "root_adapter_policy_ref":common("exact-ref"),"semantics_statement_ref":common("exact-ref"),
        "new_identity_generation":const(False),"external_fact_lookup":const(False)})
    add("rule-set","L3","Rule declarations use variable/constant terms; head variables must occur in the body.",{
        "rule_set_id":text(),"profile_ref":common("exact-ref"),"rules":arr(obj({
            "rule_id":text(),"version":text(),"head":common("atom"),"body":arr(common("atom"),1)}),1)})
    add("base-facts","L3","Finite ground facts and separately attested protected roots; root legitimacy needs a trusted adapter check.",{
        "profile_ref":common("exact-ref"),"facts":arr(obj({
            "fact_id":text(),"atom":common("ground-atom"),"origin_ref":common("exact-ref")}),1),
        "protected_roots":arr(obj({"root_id":text(),"key":common("protected-key"),
            "fact_id":text(),"evidence_refs":arr(common("exact-ref"),1,True),
            "trusted_adapter_attestation_ref":common("exact-ref")}))})
    step={"oneOf":[obj({"step_id":text(),"kind":const("base"),"base_fact_id":text(),"conclusion":common("ground-atom")}),
        obj({"step_id":text(),"kind":const("rule"),"rule_id":text(),"rule_version":text(),
            "substitution":{"type":"object","additionalProperties":text()},
            "premise_step_ids":arr(text(),1,True),"conclusion":common("ground-atom")})]}
    add("derivation-certificate","L3","Finite acyclic proof DAG with exact rule versions, ground substitutions and earlier premises.",{
        "certificate_id":text(),"rule_set_ref":common("exact-ref"),"base_facts_ref":common("exact-ref"),
        "steps":arr(step,1),"conclusion_step_id":text()})
    add("closure-certificate","L3","Claimed least fixed point; all initial facts, every rule consequence and no unexplained facts must be checked.",{
        "certificate_id":text(),"profile_ref":common("exact-ref"),"rule_set_ref":common("exact-ref"),
        "base_facts_ref":common("exact-ref"),"ground_universe":arr(text(),1,True),
        "closure":arr(common("ground-atom"),1,True),"derivation_refs":arr(common("exact-ref"),1,True),
        "adequacy_statement_ref":common("exact-ref")})
    add("model-witness","L2","Finite inhabited interpretation or countermodel, checked against every theory axiom and the claimed target.",{
        "witness_id":text(),"purpose":enum("inhabitation","countermodel"),"theory_ref":common("exact-ref"),
        "domain":arr(text(),1,True),"interpretations":arr(obj({"predicate":text(),
            "arity":{"type":"integer","minimum":0},"tuples":arr(arr(text()),0,True)}),1),
        "target_statement_ref":common("exact-ref"),"negated_statement_ref":nullable(common("exact-ref")),
        "search_bounds":nullable(obj({"domain_size":{"type":"integer","minimum":1},
            "description":text()}))},extra={"allOf":[{"if":{"properties":{"purpose":const("countermodel")}},
            "then":{"properties":{"negated_statement_ref":common("exact-ref")}}}]})
    add("proof-policy","L4","Pin toolchain, isolate untrusted submissions and audit exact statements, dependencies and transitive axioms.",{
        "policy_id":text(),"toolchain_ref":common("exact-ref"),"allowed_axioms":arr(text(),0,True),
        "required_dependency_refs":arr(common("exact-ref"),1,True),"allow_sorry":const(False),
        "network_during_replay":const(False),"isolation":const("submission-isolated"),
        "statement_equivalence":const("exact-bound-required-statement")})
    add("proof-submission","L4","Untrusted proof submission; matching metadata does not itself prove its required statement.",{
        "submission_id":text(),"obligation_ref":common("exact-ref"),"required_statement_ref":common("exact-ref"),
        "proof_artifact_ref":common("exact-ref"),"dependency_refs":arr(common("exact-ref"),1,True),
        "toolchain_ref":common("exact-ref"),"policy_ref":common("exact-ref")})
    add("proof-audit","L4","Verifier-produced exact-statement, dependency, replay and axiom audit, bound to a proof submission.",{
        "submission_ref":common("exact-ref"),"policy_ref":common("exact-ref"),
        "required_statement_ref":common("exact-ref"),"checked_statement_ref":common("exact-ref"),
        "state":enum("checked","rejected","unresolved"),"transitive_axioms":arr(text(),0,True),
        "dependency_refs":arr(common("exact-ref"),1,True),"replay_execution":common("execution"),
        "diagnostics":arr(common("diagnostic"))},extra={"allOf":[{
            "if":{"properties":{"state":const("checked")}},
            "then":{"properties":{"replay_execution":const("completed"),"diagnostics":{"maxItems":0}}}}]})
    add("provider-result","L4","Raw provider execution separated from normalized verdict; exhausted bounded search is not theorem evidence.",{
        "provider_id":text(),"obligation_ref":common("exact-ref"),"execution":common("execution"),
        "evidence_method":common("evidence-method"),"raw_output_ref":nullable(common("exact-ref")),
        "search_bounds":nullable(obj({"domain_size":{"type":"integer","minimum":1},"description":text()})),
        "diagnostics":arr(common("diagnostic"))},extra={"allOf":[{
            "if":{"properties":{"evidence_method":const("bounded-search")}},
            "then":{"properties":{"search_bounds":{"type":"object"}}}}]})
    result_fields={"obligation_id":text(),"required_statement_ref":common("exact-ref"),
        "execution":common("execution"),"currentness":common("currentness"),"evidence_method":common("evidence-method"),
        "verdict":common("verdict"),"evidence_refs":arr(common("exact-ref"),0,True),
        "assumption_refs":arr(common("exact-ref"),0,True),"diagnostics":arr(common("diagnostic"))}
    satisfied={"if":{"properties":{"verdict":const("satisfied")}},
        "then":{"properties":{"execution":const("completed"),"currentness":const("current"),
            "evidence_method":enum("verified-checker","kernel-proof","checked-model-witness"),
            "evidence_refs":{"minItems":1}}}}
    add("obligation-result","L4","Scoped verifier conclusion with independent execution, freshness and evidence-method dimensions.",
        result_fields,extra={"allOf":[satisfied]})
    dimension=obj({"verdict":enum("satisfied","violated","unknown","unsupported","not-required"),
        "scope_ref":common("exact-ref"),"evidence_refs":arr(common("exact-ref"),0,True)})
    add("compatibility-report","L2","Selected-data compatibility, invariant preservation and model conservativity are independent claims.",{
        "proposal_ref":common("exact-ref"),"selected_data":dimension,"invariant_preservation":dimension,
        "model_conservativity":dimension,"rule_obligations_pending":arr(text(),0,True),
        "diagnostics":arr(common("diagnostic"))})
    add("invalidation-report","L1","Changed dependency identities invalidate exactly scoped evidence; currentness is assessed by the verifier.",{
        "old_baseline_ref":common("exact-ref"),"new_baseline_ref":common("exact-ref"),
        "changed_dependencies":arr(obj({"before_ref":common("exact-ref"),"after_ref":nullable(common("exact-ref"))}),0,True),
        "invalidated_evidence_refs":arr(common("exact-ref"),0,True),"recheck_obligation_ids":arr(text(),0,True)})
    add("evidence-bundle","L4","Replayable untrusted submission with exact scope and dependencies; does not carry client readiness flags.",{
        "bundle_id":text(),"snapshot_ref":common("exact-ref"),"profile_ref":common("exact-ref"),
        "graph_ref":common("exact-ref"),"proposal_ref":common("exact-ref"),
        "obligation_set_ref":common("exact-ref"),"proof_policy_ref":common("exact-ref"),
        "evidence_refs":arr(common("exact-ref"),1,True),"dependency_refs":arr(common("exact-ref"),1,True),
        "provider_result_refs":arr(common("exact-ref"),0,True),"compatibility_ref":common("exact-ref"),
        "authority_effect":const("none")})
    add("review-report","L4","Verifier-produced aggregate over independently derived hard obligations, not a client-owned all-passed flag.",{
        "review_id":text(),"bundle_ref":common("exact-ref"),"derived_obligation_set_ref":common("exact-ref"),
        "execution":common("execution"),"currentness":common("currentness"),
        "aggregate_readiness":enum("ready-for-review","blocked","unresolved"),
        "results":arr(ref("obligation-result"),1),"missing_hard_obligation_ids":arr(text(),0,True),
        "diagnostics":arr(common("diagnostic")),"human_meaning_review":enum("pending","reviewed"),
        "authority_effect":const("none")},extra={"allOf":[{
            "if":{"properties":{"aggregate_readiness":const("ready-for-review")}},
            "then":{"properties":{"execution":const("completed"),"currentness":const("current"),
                "missing_hard_obligation_ids":{"maxItems":0},
                "results":{"items":{"properties":{"verdict":const("satisfied")}}}}}}]})
    add("check-receipt","L0","Scoped checker outcome bound to exact inputs, invariant statement and explicit trust assumptions.",{
        "receipt_id":text(),"snapshot_ref":common("exact-ref"),"profile_ref":common("exact-ref"),
        "graph_ref":common("exact-ref"),"proposal_ref":common("exact-ref"),
        "execution":common("execution"),"currentness":common("currentness"),
        "check_scope":enum("structural","supported-semantics"),
        "result":enum("valid","invalid","unknown","unsupported"),
        "soundness_statement_ref":nullable(common("exact-ref")),"soundness_evidence_ref":nullable(common("exact-ref")),
        "trusted_boundaries":arr(text(),1,True),"diagnostics":arr(common("diagnostic")),
        "authority_effect":const("none")},extra={"allOf":[
            {"if":{"properties":{"result":const("valid")}},
             "then":{"properties":{"execution":const("completed"),"currentness":const("current")}}},
            {"if":{"properties":{"check_scope":const("supported-semantics"),"result":const("valid")}},
             "then":{"properties":{"soundness_statement_ref":common("exact-ref"),"soundness_evidence_ref":common("exact-ref")}}}]})
    add("application-recheck","L4","Candidate-only baseline recapture at simulated application; readiness is not governance authority.",{
        "review_ref":common("exact-ref"),"reviewed_baseline_ref":common("exact-ref"),
        "observed_baseline_ref":common("exact-ref"),"invalidation_ref":common("exact-ref"),
        "mode":const("simulate"),"result":enum("ready-for-human-decision","recheck-required","unresolved"),
        "fresh_review_ref":nullable(common("exact-ref")),"authority_effect":const("none")},
        extra={"allOf":[{"if":{"properties":{"result":const("ready-for-human-decision")}},
            "then":{"properties":{"fresh_review_ref":common("exact-ref")}}}]})
    add("job","L4","Asynchronous execution lifecycle; accepted HTTP request is not semantic acceptance.",{
        "job_id":text(),"operation_id":text(),"request_ref":common("exact-ref"),
        "state":enum("queued","running","completed","timeout","unavailable","failed","cancelled"),
        "result_refs":arr(common("exact-ref"),0,True),"diagnostics":arr(common("diagnostic"))},
        extra={"allOf":[{"if":{"properties":{"state":const("completed")}},
            "then":{"properties":{"result_refs":{"minItems":1}}}},
            {"if":{"properties":{"state":enum("queued","running","cancelled")}},
             "then":{"properties":{"result_refs":{"maxItems":0}}}}]})
    add("api-problem","L4","Transport or service failure with an actionable code; semantic violations are result documents.",{
        "type":text(),"title":text(),"status":{"type":"integer","minimum":400,"maximum":599},
        "code":text(),"detail":text(),"request_id":text(),"diagnostics":arr(common("diagnostic"))})
    add("capabilities","L4","Explicit supported profiles and actually available execution engines; this package starts no engine.",{
        "package_version":const("v1-candidate"),"schema_dialect":const(DIALECT),
        "profiles":arr(obj({"profile_id":text(),"profile_ref":common("exact-ref"),
            "state":enum("contract-only","available","unsupported")}),1),
        "engines":arr(obj({"engine_id":text(),"availability":enum("not-implemented","available","unavailable")}),1),
        "authority_effect":const("none")})

def registry_assets():
    registry_path="authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json"
    baseline_plan=json.loads((PLAN/"PLAN-SOURCE.json").read_bytes())
    for binding in baseline_plan["source_bindings"]:
        if sha((ROOT/binding["path"]).read_bytes()) != binding["sha256"]:
            raise ValueError("Design source drift: "+binding["path"])
    registry=json.loads((ROOT/registry_path).read_bytes())
    kinds, source_bindings, overlays, assertion_conditions=[],[source_binding(registry_path)],[],[]
    for entry in registry["entries"]:
        path=entry["instance_path"]
        raw=(ROOT/path).read_bytes()
        if sha(raw) != entry["instance_sha256"]:
            raise ValueError("Registry record drift: "+path)
        record=json.loads(raw); p=record["payload"]
        binding=source_binding(path); source_bindings.append(binding)
        qualifiers=obj(p["qualifier_contract"]["properties"],p["qualifier_contract"]["required_axes"])
        kind={"schema_version":version("relation-kind"),"kind_id":p["relation_kind_id"],
            "version":"sha256:"+sha(raw),"source_ref":{"artifact_id":record["node_id"],"sha256":sha(raw),
                "size_bytes":len(raw),"media_type":"application/json"},"source_binding":binding,
            "axis_id":p["axis_id"],"allowed_endpoint_pairs":p["allowed_endpoint_pairs"],
            "qualifier_schema":qualifiers,"forbidden_inferences":p["forbidden_inferences"],
            "source_lifecycle":record["lifecycle_state"],"effective_lifecycle":entry["lifecycle_state"],
            "semantic_state":"imported","prose_semantics":p["operational_effect"]}
        kinds.append(kind)
        overlays.append({"kind_id":kind["kind_id"],"source_lifecycle":kind["source_lifecycle"],
            "effective_lifecycle":kind["effective_lifecycle"],"admission_decision_id":entry["admission_decision_ref"],
            "registry_evidence":source_binding(registry_path)})
        assertion_conditions.append({"if":{"properties":{"relation_kind_id":const(kind["kind_id"])}},
            "then":{"properties":{"relation_kind_version":const(kind["version"]),
                "definition_ref":{"properties":{"sha256":const(kind["source_ref"]["sha256"]),
                    "size_bytes":const(kind["source_ref"]["size_bytes"])}},"qualifiers":qualifiers},
                "anyOf":[{"properties":dict(
                    source={"properties":dict(kind=const(pair["source_kind"]))},
                    target={"properties":dict(kind=const(pair["target_kind"]))})}
                    for pair in kind["allowed_endpoint_pairs"]]}})
    snapshot=example("baseline-snapshot",snapshot_id="candidate:relational-baseline-2026-10-07",
        registry_source=source_binding(registry_path),source_bindings=source_bindings,
        effective_state_bindings=overlays,captured_at="2026-10-07T00:00:00Z",authority_effect="none")
    # Date denotes logical design capture, not a live freshness assertion.
    emit("profiles/baseline-snapshot.json",snapshot)
    registry_example=example("registry-snapshot",registry_id="candidate:relation-kind-registry",
        baseline_ref=artifact("profiles/baseline-snapshot.json"),kinds=kinds,kind_count=len(kinds),
        relation_specific_pair_count=sum(len(k["allowed_endpoint_pairs"]) for k in kinds))
    emit("profiles/registry-snapshot.json",registry_example)
    add("registry-assertion","L1","Generated companion structural carrier for the captured registry. Enforces 41 kind versions, exact pairs and original closed qualifiers.",
        body={"allOf":[ref("relation-assertion"),
            {"properties":{"relation_kind_id":enum(*(k["kind_id"] for k in kinds))}},
            *assertion_conditions]})
    slice_ids=["relation.conforms-to","relation.declares-effect-on","relation.materializes-consequence"]
    add("l0-assertion","L0","Three-kind companion structural input. It covers the selected materialization kind without changing frozen Typed Relation/v2.",
        body={"allOf":[ref("registry-assertion"),{"properties":{"relation_kind_id":enum(*slice_ids)}}]})
    add("l0-graph","L0","The companion finite graph with all assertions restricted to the selected three-kind structural carrier.",
        body={"allOf":[ref("graph"),{"properties":{"assertions":{"items":ref("l0-assertion")}}}]})
    statements="Independent validity predicates and invariants must be authored and reviewed in P01/P03. This contract artifact is not a Lean theorem.\n"
    emit("profiles/required-semantics.txt",statements)
    profile=example("semantic-profile",profile_id="candidate:l0-three-kind",
        baseline_ref=artifact("profiles/baseline-snapshot.json"),registry_ref=artifact("profiles/registry-snapshot.json"),
        carrier="candidate-companion",supported_kind_ids=slice_ids,
        invariant_statement_refs=[artifact("profiles/required-semantics.txt")],
        normative_review={"state":"draft","review_ref":None},rule_profile_ref=None,
        trusted_boundaries=["source-interpretation","json-decoder","hash-function","compiled-runtime","proof-kernel"],
        authority_effect="none")
    emit("profiles/l0-semantic-profile.json",profile)
    conform=next(k for k in kinds if k["kind_id"]=="relation.conforms-to")
    assertion=example("relation-assertion",assertion_id="example:conformance-1",
        relation_kind_id=conform["kind_id"],relation_kind_version=conform["version"],definition_ref=conform["source_ref"],
        source=point(),target=point("contract","contract"),
        qualifiers={"conformance_scope":"example:static","exact_version_ref":"example:contract@candidate.1",
            "conformance_evidence_refs":"example:evidence-1"})
    emit("examples/l0-assertion.json",assertion)
    emit("examples/registry-assertion.json",assertion)
    graph=example("graph",graph_id="example:graph",nodes=[assertion["source"],assertion["target"]],assertions=[assertion])
    emit("examples/l0-graph.json",graph)
    return kinds, baseline_plan

def api_and_contracts(plan):
    operations=[
        ("captureSnapshot","/v1/snapshots","L0","snapshot-request",{"registry_source":common("source-binding")},"baseline-snapshot",["B00","C01"]),
        ("normalizeGraph","/v1/normalizations","L0","normalization-request",{"snapshot_ref":common("exact-ref"),"profile_ref":common("exact-ref"),"graph_ref":common("exact-ref")},"normalization-report",["P01","P02","P03","C03"]),
        ("checkAddition","/v1/checks","L0","check-request",{"snapshot_ref":common("exact-ref"),"profile_ref":common("exact-ref"),"graph_ref":common("exact-ref"),"proposal_ref":common("exact-ref"),"check_scope":enum("structural","supported-semantics")},"check-receipt",["P04","P05","P06","G0"]),
        ("deriveObligations","/v1/obligations","L2","obligation-request",{"snapshot_ref":common("exact-ref"),"profile_ref":common("exact-ref"),"proposal_ref":common("exact-ref"),"policy_ref":common("exact-ref")},"obligation-set",["E01","E02"]),
        ("checkDerivation","/v1/derivations/check","L3","derivation-request",{"profile_ref":common("exact-ref"),"rule_set_ref":common("exact-ref"),"base_facts_ref":common("exact-ref"),"certificate_ref":common("exact-ref")},"obligation-result",["I01","I02"]),
        ("checkClosure","/v1/closures/check","L3","closure-request",{"profile_ref":common("exact-ref"),"rule_set_ref":common("exact-ref"),"base_facts_ref":common("exact-ref"),"certificate_ref":common("exact-ref")},"obligation-result",["I03"]),
        ("checkModel","/v1/models/check","L2","model-request",{"profile_ref":common("exact-ref"),"witness_ref":common("exact-ref"),"obligation_ref":common("exact-ref")},"obligation-result",["E04","I05"]),
        ("verifyProof","/v1/proofs/verify","L4","proof-request",{"submission_ref":common("exact-ref"),"obligation_ref":common("exact-ref"),"policy_ref":common("exact-ref")},"proof-audit",["R02"]),
        ("reviewBundle","/v1/reviews","L4","review-request",{"bundle_ref":common("exact-ref"),"snapshot_ref":common("exact-ref"),"policy_ref":common("exact-ref")},"review-report",["C02","C04","C05","G1","E03","E05","G2","I04","I06","G3","R01","R03","R04","R06","G4"]),
        ("replayBundle","/v1/replays","L4","replay-request",{"bundle_ref":common("exact-ref"),"observed_snapshot_ref":common("exact-ref"),"policy_ref":common("exact-ref")},"review-report",["C06"]),
        ("recheckApplication","/v1/application-rechecks","L4","application-request",{"review_ref":common("exact-ref"),"observed_snapshot_ref":common("exact-ref"),"policy_ref":common("exact-ref"),"mode":const("simulate")},"application-recheck",["R05"])
    ]
    add("cancel-request","L4","Cancellation requests terminate execution without producing readiness.",{"reason":text()})
    api={"openapi":"3.1.1","jsonSchemaDialect":DIALECT,
        "info":{"title":"Relational Theorem Checker Candidate API","version":"1.0.0-candidate",
            "description":"Interface definition only. No running server, verified checker or theorem proof is provided. All authority effects are none."},
        "servers":[{"url":"http://localhost:8787","description":"Proposed loopback development endpoint; not started by this package."}],
        "paths":{},"components":{"securitySchemes":{"bearerAuth":{"type":"http","scheme":"bearer"}}},
        "security":[{"bearerAuth":[]}],"x-status":"contract-only"}
    def sr(name):
        return {"$ref":"../schemas/"+name+".schema.json"}
    def response(name, description):
        return {"description":description,"content":{"application/json":{"schema":sr(name)}}}
    problems={str(code):response("api-problem",label) for code,label in [
        (400,"Malformed request"),(401,"Authentication required"),(403,"Artifact access denied"),
        (404,"Bound artifact or job not found"),(409,"Identity, idempotency or execution-state conflict"),
        (413,"Configured resource limit exceeded"),(422,"Unsupported schema/profile or rejected input shape"),
        (429,"Capacity limit"),(503,"Required execution engine unavailable")]}
    contracts=[]
    behavior={
        "captureSnapshot":("Hash every source and resolve effective state through exact registry evidence.","A selected immutable snapshot with explicit capture evidence; no perpetual currentness claim.","Missing overlays, source drift or ambiguous baseline."),
        "normalizeGraph":("Reject unknown kinds, identity collisions and malformed input; retain exact ordered pairs and original qualifier shapes.","A deterministic projection with preservation mappings and explicit parser trust.","Pair widening, reordered identity bindings, omitted fields or unknown-kind escape."),
        "checkAddition":("Fully recheck the resulting graph against independently defined validity; structural scope stays separate.","A scoped result; semantic-valid requires checked general soundness for the selected profile.","Invalid pair/qualifier/reference/invariant or unsupported semantic definition."),
        "deriveObligations":("Compute the exact semantic diff and derive every required hard obligation using server-selected policy.","Complete obligation set with coverage statement, including L3 obligations for rule changes.","Author relabeling, omitted hard obligations or unsupported change profiles."),
        "checkDerivation":("Resolve every base leaf, exact rule and substitution; validate each premise and typed conclusion in a finite DAG.","Sound supported conclusion only with generic derivation soundness evidence.","Cycle, missing premise, forged root, new identity or unbound external fact."),
        "checkClosure":("Check initial facts, closure under all ground rule instances and justified membership.","Negative non-derivability only with least-fixed-point adequacy or an independent general theorem.","Incomplete saturation, invented member, wrong universe or timeout."),
        "checkModel":("Verify a nonempty interpretation against every bound axiom; countermodel also negates the target statement.","Checked witness with exact finite scope; a fully checked countermodel may refute a universal implication.","Empty domain, wrong arity, missing axiom, wrong target or exhausted search."),
        "verifyProof":("Isolate replay, pin the exact required statement and dependency closure, and audit transitive axioms.","Audit of the actual theorem statement and policy; assumption and kernel boundaries remain explicit.","Weakened theorem, circular assumption, sorry, forbidden axiom or changed dependency."),
        "reviewBundle":("Recompute all digests and required obligations independently; draft normative profiles cannot become semantically ready.","Readiness only after every hard obligation has allowed, current, completed evidence; human meaning review remains explicit.","Missing hard result, stale dependencies, bounded-search upgrade or incomplete rule evidence."),
        "replayBundle":("Compare the complete bound dependency closure with the observed snapshot and rerun affected obligations.","Currentness and invalidation are verifier-produced, not trusted client flags.","Changed registry, graph, profile, rule, evidence or proof dependency."),
        "recheckApplication":("Recapture a trusted observed baseline and recheck at simulated application time.","Candidate recommendation requiring separate human authority; authority effect remains none.","Review/application drift, reused stale receipt or request for actual admission.")
    }
    for op,path,layer,request,fields,result,tasks in operations:
        add(request,layer,"Request contract for "+op+"; exact references must resolve through the local artifact store.",{
            "request_id":text(),**fields})
        api["paths"][path]={"post":{"operationId":op,"tags":[layer],"summary":op,
            "description":behavior[op][0]+" "+behavior[op][1],
            "parameters":[{"name":"Idempotency-Key","in":"header","required":True,"schema":text(),
                "description":"Same principal, route and key with identical raw request bytes returns the same job; different bytes return 409."}],
            "requestBody":{"required":True,"content":{"application/json":{"schema":sr(request)}}},
            "responses":{"202":response("job","Accepted for execution; not semantic acceptance."),**copy.deepcopy(problems)},
            "x-result-schema":sr(result)}}
        contracts.append({"contract_id":"C-"+op,"layer":layer,"task_ids":tasks,
            "input_schema":request,"output_schema":result,"preconditions":[
                "Caller is authenticated and authorized to read every referenced artifact.",
                "Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths."],
            "rules":[behavior[op][0]],"postconditions":[behavior[op][1]],
            "failure_controls":[behavior[op][2]],"trust_boundary":[
                "JSON shape validation is not semantic proof.","Submitted metadata and outputs remain untrusted until independently verified."],
            "authority_effect":"none"})
    parameter_digest={"name":"sha256","in":"path","required":True,"schema":common("digest")}
    parameter_job={"name":"job_id","in":"path","required":True,"schema":text()}
    artifact_names=[c["name"] for c in CATALOG if c["name"] not in ("common","registry-assertion","l0-assertion","l0-graph")]
    # Assertion/graph uploads select either the generic future-profile schema or a stricter companion profile explicitly.
    artifact_names += ["registry-assertion","l0-assertion","l0-graph"]
    api["paths"]["/v1/artifacts"]={"post":{"operationId":"putArtifact","summary":"Validate and store exact untrusted artifact bytes",
        "parameters":[{"name":"X-Artifact-Schema","in":"header","required":True,
            "schema":enum(*artifact_names,"raw-artifact"),
            "description":"Named interface envelope schema, or raw-artifact for untrusted proof source, required statement, provider output or pinned dependency bytes."},
            {"name":"X-Artifact-Media-Type","in":"header","required":True,
             "schema":enum("application/json","text/plain","application/octet-stream"),
             "description":"The original artifact media type. Named envelope schemas require application/json; raw bytes cannot bypass operation-specific role and schema checks."}],
        "requestBody":{"required":True,
            "description":"Exact original bytes. Named envelope schemas require UTF-8 JSON with duplicate-key rejection. Raw proof, statement, provider-output and dependency bytes remain untrusted until their operation-specific verifier accepts them.",
            "content":{"application/octet-stream":{"schema":{"type":"string","format":"binary"}}}},
        "responses":{"201":{"description":"Immutable artifact stored; reference describes original bytes.",
            "content":{"application/json":{"schema":common("exact-ref")}}},
            "200":{"description":"Identical immutable artifact already exists.",
                "content":{"application/json":{"schema":common("exact-ref")}}},**copy.deepcopy(problems)}}}
    api["paths"]["/v1/artifacts/{sha256}"]={"get":{"operationId":"getArtifact","parameters":[parameter_digest],
        "responses":{"200":{"description":"The exact stored bytes, with authorization required even for a known hash.",
            "content":{"application/octet-stream":{"schema":{"type":"string","format":"binary"}}}},**copy.deepcopy(problems)}}}
    api["paths"]["/v1/jobs/{job_id}"]={"get":{"operationId":"getJob","parameters":[parameter_job],
        "responses":{"200":response("job","Execution state and bound result references."),**copy.deepcopy(problems)}}}
    api["paths"]["/v1/jobs/{job_id}/cancel"]={"post":{"operationId":"cancelJob","parameters":[parameter_job],
        "requestBody":{"required":True,"content":{"application/json":{"schema":sr("cancel-request")}}},
        "responses":{"200":response("job","Cancellation acknowledged; terminal results are immutable."),
            **copy.deepcopy(problems)}}}
    api["paths"]["/v1/capabilities"]={"get":{"operationId":"getCapabilities",
        "responses":{"200":response("capabilities","Profiles and actual engine availability."),**copy.deepcopy(problems)}}}
    for op,rule,post,failure in [
        ("artifactTransport","For named JSON envelopes reject invalid UTF-8, duplicate keys, schema mismatch and unsupported documents. Store raw proof, statement, provider and dependency bytes as untrusted artifacts. Resolve each operation's expected role/schema independently of upload labels; hash original bytes without reserialization.",
            "Artifact identifiers never grant read permission; access remains principal-scoped.",
            "Client-supplied digest, size or currentness is never trusted."),
        ("jobLifecycle","Queued -> running -> completed/timeout/unavailable/failed; queued/running may cancel. Terminal states are immutable.",
            "HTTP 202 and completed job state say execution happened, not that an obligation was satisfied.",
            "Completion is refused if its operation-specific result type or scope is wrong."),
        ("layerEvidenceGates","F0 starts with P01 relational semantics, P03 independent formal predicates, P04 Lean reference checker and P05 general soundness review. B00 baseline refresh and P02 schema/API/decoder alignment follow that accepted evidence. Every later task requires current predecessor evidence; G2 closes supported non-rule scope while I06 closes rule obligations.",
            "Contract authoring does not complete any implementation/proof gate in the DAG.",
            "Plan/fixture receipts cannot substitute for execution acceptance."),
        ("protectedLineage","Match targetVersion, effect, scope and epoch against legitimate roots across all indirect rule paths.",
            "Conformance may coexist with independently justified admission; conformance cannot justify admission.",
            "Qualifier strings, axis names and untrusted adapter attestations cannot create authority roots."),
        ("compatibilityClaims","Check selected data, generic invariant preservation and model conservativity separately.",
            "A conservative-extension claim covers every base model via an expansion with unchanged old reduct.",
            "Pair widening is not unchanged old semantics; finite search exhaustion is not proof.")
    ]:
        contracts.append({"contract_id":"C-"+op,"layer":"shared","task_ids":[],
            "input_schema":"evidence-bundle" if op!="artifactTransport" else "common",
            "output_schema":"review-report" if op!="artifactTransport" else "common",
            "preconditions":["Use the selected versioned profile and exact source identities."],
            "rules":[rule],"postconditions":[post],"failure_controls":[failure],
            "trust_boundary":["Implementing this declared rule still requires the corresponding DAG evidence."],
            "authority_effect":"none"})
    contract_row=obj({"contract_id":text(),"layer":text(),"task_ids":arr(text(),0,True),
        "input_schema":text(),"output_schema":text(),"preconditions":arr(text(),1),
        "rules":arr(text(),1),"postconditions":arr(text(),1),"failure_controls":arr(text(),1),
        "trust_boundary":arr(text(),1),"authority_effect":const("none")})
    add("contract-set","shared","Machine-readable preconditions, postconditions, failure rules and DAG traceability.",{
        "status":const("candidate"),"contracts":arr(contract_row,1)})
    example("contract-set",status="candidate",contracts=contracts)
    emit("contracts/contract-set.json",EXAMPLES["contract-set"])
    emit("api/openapi.json",api)
    emit("api/cli-contract.json",{
        "status":"contract-only","program":"relcheck","commands":[
            {"command":"snapshot","operation":"captureSnapshot"},{"command":"normalize","operation":"normalizeGraph"},
            {"command":"check","operation":"checkAddition"},{"command":"obligations","operation":"deriveObligations"},
            {"command":"derive-check","operation":"checkDerivation"},{"command":"closure-check","operation":"checkClosure"},
            {"command":"model-check","operation":"checkModel"},{"command":"proof-verify","operation":"verifyProof"},
            {"command":"review","operation":"reviewBundle"},{"command":"replay","operation":"replayBundle"},
            {"command":"application-recheck --simulate","operation":"recheckApplication"}],
        "review_exit_codes":{"0":"Completed, current and ready-for-review under the selected profile.",
            "1":"A required obligation was violated.","2":"Unknown, unsupported, not-run or missing mandatory evidence.",
            "3":"Provider error, unavailable execution engine or timeout.","4":"Stale baseline or evidence."},
        "other_commands":"Zero means the requested operation completed; inspect its scoped result. It does not imply aggregate review readiness.",
        "flags":["--request <path>","--output <path>","--format json|text"],
        "authority_effect":"none"})
    return operations,contracts,api

def make_examples():
    schema_map={json.loads(v)["$id"]:json.loads(v) for p,v in FILES.items() if p.startswith("schemas/")}
    def synth(schema):
        if "$ref" in schema:
            uri,sep,fragment=schema["$ref"].partition("#")
            node=schema_map[uri]
            if sep:
                for part in fragment.strip("/").split("/"):
                    node=node[part.replace("~1","/").replace("~0","~")]
            return synth(node)
        if "const" in schema: return copy.deepcopy(schema["const"])
        if "enum" in schema: return copy.deepcopy(schema["enum"][0])
        if "oneOf" in schema: return synth(schema["oneOf"][0])
        if "anyOf" in schema: return synth(schema["anyOf"][0])
        kind=schema.get("type")
        if kind=="object":
            return {k:synth(schema["properties"][k]) for k in schema.get("required",[])}
        if kind=="array":
            return [synth(schema["items"]) for _ in range(schema.get("minItems",0))]
        if kind=="integer": return schema.get("minimum",1)
        if kind=="boolean": return False
        if kind=="null": return None
        if kind=="string":
            if schema.get("pattern")=="^[a-f0-9]{64}$": return "a"*64
            if schema.get("format")=="date-time": return "2026-10-07T00:00:00Z"
            return "example:value"
        raise ValueError("No fixture synthesizer for "+str(schema))
    for row in CATALOG:
        name=row["name"]
        if name in EXAMPLES or name in ("common","registry-assertion","l0-assertion","l0-graph"):
            continue
        schema=json.loads(FILES[row["path"]])
        value=synth(schema)
        if name=="obligation-result":
            value.update(verdict="unknown",currentness="unresolved",evidence_method="none",evidence_refs=[])
        if name=="review-report":
            value.update(aggregate_readiness="unresolved",currentness="unresolved",
                results=[copy.deepcopy(EXAMPLES["obligation-result"])],human_meaning_review="pending")
        if name=="proof-audit": value["state"]="unresolved"
        if name=="check-receipt":
            value.update(result="unsupported",check_scope="supported-semantics",
                soundness_statement_ref=None,soundness_evidence_ref=None)
        if name=="application-recheck":
            value.update(result="unresolved",fresh_review_ref=None)
        if name=="capabilities":
            value["engines"][0]["availability"]="not-implemented"
        emit("examples/"+name+".json",value); EXAMPLES[name]=value
    # Coherent finite structural rule inputs, without claiming actual derivation/proof verification.
    EXAMPLES["rule-profile"].update(profile_id="example:positive-profile",ground_universe=["example:capability"],
        protected_predicates=[{"predicate":"Admitted","argument_roles":["targetVersion","effect","scope","epoch"]}])
    emit("examples/rule-profile.json",EXAMPLES["rule-profile"])
    EXAMPLES["rule-set"].update(rule_set_id="example:rules",profile_ref=artifact("examples/rule-profile.json"),
        rules=[{"rule_id":"example:rule-1","version":"candidate.1",
            "head":{"predicate":"P","arguments":[{"variable":"X"}]},
            "body":[{"predicate":"Q","arguments":[{"variable":"X"}]}]}])
    emit("examples/rule-set.json",EXAMPLES["rule-set"])
    EXAMPLES["base-facts"].update(profile_ref=artifact("examples/rule-profile.json"),
        facts=[{"fact_id":"example:fact-1","atom":{"predicate":"Q","arguments":["example:capability"]},
            "origin_ref":exact("fact-source")}],protected_roots=[])
    emit("examples/base-facts.json",EXAMPLES["base-facts"])
    EXAMPLES["derivation-certificate"].update(certificate_id="example:derivation",
        rule_set_ref=artifact("examples/rule-set.json"),base_facts_ref=artifact("examples/base-facts.json"),
        steps=[{"step_id":"s0","kind":"base","base_fact_id":"example:fact-1",
                "conclusion":{"predicate":"Q","arguments":["example:capability"]}},
            {"step_id":"s1","kind":"rule","rule_id":"example:rule-1","rule_version":"candidate.1",
                "substitution":{"X":"example:capability"},"premise_step_ids":["s0"],
                "conclusion":{"predicate":"P","arguments":["example:capability"]}}],conclusion_step_id="s1")
    emit("examples/derivation-certificate.json",EXAMPLES["derivation-certificate"])
    EXAMPLES["closure-certificate"].update(profile_ref=artifact("examples/rule-profile.json"),
        rule_set_ref=artifact("examples/rule-set.json"),base_facts_ref=artifact("examples/base-facts.json"),
        ground_universe=["example:capability"],
        closure=[{"predicate":"Q","arguments":["example:capability"]},{"predicate":"P","arguments":["example:capability"]}],
        derivation_refs=[artifact("examples/derivation-certificate.json")])
    emit("examples/closure-certificate.json",EXAMPLES["closure-certificate"])
    base_graph=copy.deepcopy(EXAMPLES["graph"]); base_graph.update(graph_id="example:base-graph",assertions=[])
    emit("examples/graph-base.json",base_graph)
    EXAMPLES["change-proposal"].update(proposal_id="example:add-conformance",
        baseline_ref=artifact("profiles/baseline-snapshot.json"),base_graph_ref=artifact("examples/graph-base.json"),
        proposed_graph_ref=artifact("examples/graph.json"),base_registry_ref=artifact("profiles/registry-snapshot.json"),
        proposed_registry_ref=artifact("profiles/registry-snapshot.json"),
        base_rules_ref=None,proposed_rules_ref=None,author_change_labels=["instance-addition"],
        requested_claims=["selected-data-compatibility","invariant-preservation"])
    emit("examples/change-proposal.json",EXAMPLES["change-proposal"])
    EXAMPLES["check-request"].update(request_id="example:check-addition",
        snapshot_ref=artifact("profiles/baseline-snapshot.json"),profile_ref=artifact("profiles/l0-semantic-profile.json"),
        graph_ref=artifact("examples/graph-base.json"),proposal_ref=artifact("examples/change-proposal.json"),
        check_scope="structural")
    emit("examples/check-request.json",EXAMPLES["check-request"])
    # Negative fixtures target schema boundaries. Deeper contract controls are exercised by the package validator.
    negatives=[]
    def bad(name,schema,original,mutate):
        value=copy.deepcopy(original); mutate(value)
        path="fixtures/invalid/"+name+".json";emit(path,value)
        negatives.append({"name":name,"schema":schema,"path":path,"expected":"reject"})
    bad("unknown-kind","l0-assertion",EXAMPLES["relation-assertion"],lambda v:v.update(relation_kind_id="relation.unknown"))
    bad("pair-reversal","l0-assertion",EXAMPLES["relation-assertion"],lambda v:v.update(source=v["target"],target=v["source"]))
    bad("plural-reference-is-not-array","l0-assertion",EXAMPLES["relation-assertion"],
        lambda v:v["qualifiers"].update(conformance_evidence_refs=["example:evidence"]))
    bad("extra-qualifier","l0-assertion",EXAMPLES["relation-assertion"],lambda v:v["qualifiers"].update(authority=True))
    bad("missing-qualifier","l0-assertion",EXAMPLES["relation-assertion"],lambda v:v["qualifiers"].pop("exact_version_ref"))
    bad("wrong-kind-version","l0-assertion",EXAMPLES["relation-assertion"],lambda v:v.update(relation_kind_version="wrong"))
    bad("client-all-passed-flag","evidence-bundle",EXAMPLES["evidence-bundle"],lambda v:v.update(all_passed=True))
    bad("empty-model-domain","model-witness",EXAMPLES["model-witness"],lambda v:v.update(domain=[]))
    bad("countermodel-without-negation","model-witness",EXAMPLES["model-witness"],lambda v:v.update(purpose="countermodel",negated_statement_ref=None))
    bad("sorry-permitted","proof-policy",EXAMPLES["proof-policy"],lambda v:v.update(allow_sorry=True))
    bad("unreviewed-profile-labeled-reviewed","semantic-profile",EXAMPLES["semantic-profile"],
        lambda v:v.update(normative_review={"state":"reviewed","review_ref":None}))
    result=copy.deepcopy(EXAMPLES["obligation-result"])
    result.update(verdict="satisfied",execution="completed",currentness="current",evidence_method="bounded-search",evidence_refs=[exact()])
    bad("bounded-search-as-proof","obligation-result",result,lambda v:None)
    result.update(evidence_method="kernel-proof",currentness="stale")
    bad("stale-satisfaction","obligation-result",result,lambda v:None)
    result.update(currentness="current",execution="timeout")
    bad("timeout-satisfaction","obligation-result",result,lambda v:None)
    result.update(execution="completed",evidence_refs=[])
    bad("satisfaction-without-evidence","obligation-result",result,lambda v:None)
    bad("ready-with-unknown-result","review-report",EXAMPLES["review-report"],
        lambda v:v.update(aggregate_readiness="ready-for-review",currentness="current"))
    bad("actual-admission-request","application-request",EXAMPLES["application-request"],lambda v:v.update(mode="admit"))
    bad("completed-job-without-result","job",EXAMPLES["job"],lambda v:v.update(state="completed",result_refs=[]))
    bad("bad-digest","proof-submission",EXAMPLES["proof-submission"],
        lambda v:v["proof_artifact_ref"].update(sha256="not-a-digest"))
    bad("source-traversal","baseline-snapshot",EXAMPLES["baseline-snapshot"],
        lambda v:v["registry_source"].update(repo_path="../keys"))
    emit("fixtures/schema-controls.json",{"schema_negatives":negatives,
        "positive_examples":[{"schema":r["name"],"path":"examples/"+r["name"]+".json"}
            for r in CATALOG if r["name"]!="common"]+[
                {"schema":"graph","path":"examples/graph-base.json"},
                {"schema":"baseline-snapshot","path":"profiles/baseline-snapshot.json"},
                {"schema":"registry-snapshot","path":"profiles/registry-snapshot.json"},
                {"schema":"semantic-profile","path":"profiles/l0-semantic-profile.json"},
                {"schema":"contract-set","path":"contracts/contract-set.json"}]})

def documents(operations,contracts,api,plan):
    def refs(node):
        found=[]
        if isinstance(node,dict):
            if "$ref" in node: found.append(node["$ref"])
            for value in node.values():found+=refs(value)
        elif isinstance(node,list):
            for value in node:found+=refs(value)
        return sorted(set(found))
    for row in CATALOG:
        row["refs"]=refs(json.loads(FILES[row["path"]]))
    emit("catalog.json",{"status":"candidate-interface","schemas":CATALOG,
        "contracts":contracts,"api_operations":[{"operation_id":item["operationId"],"method":method.upper(),
            "path":path,"layer":(item.get("tags") or ["shared"])[0],"definition":item}
            for path,methods in api["paths"].items() for method,item in methods.items()]})
    def relative(path):
        import os
        return os.path.relpath(ROOT/path,BASE)
    plan_link=relative("docs/plans/relational-theorem-checker/dag-plan/PLAN.md")
    def markdown(path,lines):
        emit(path,"\n".join(lines)+"\n")
    markdown("README.md",["# Relational theorem checker interfaces", "",
        "**Status: candidate definitions.** This package authors schemas, behavioral contracts and API specifications across L0-L4. It includes structural conformance tooling and synthetic examples. F0 now has a [pure Lean reference checker and general soundness proof](../formal/RESULT.md), with candidate acceptance and author self-review. The JSON decoder, HTTP service and CLI remain unimplemented; no layer evidence gate is marked complete.", "",
        "## Inspect", "",
        "- [Interactive schema and API explorer](index.html)",
        "- [Schema catalog](SCHEMAS.md) and [behavioral contracts](CONTRACTS.md)",
        "- [OpenAPI specification](api/openapi.json) and [API flows](API.md)",
        "- [CLI contract](api/cli-contract.json)",
        "- [DAG traceability](TRACEABILITY.md) and [original plan]("+plan_link+")",
        "- [Validation report](receipts/interface-validation.json)", "",
        "## Profile policy", "",
        "The generated companion carrier preserves all 41 selected relation kinds and 550 relation-specific ordered-pair entries, including materializes-consequence. It imports original qualifier shapes: conformance_evidence_refs remains a string. Generic graph/proposal contracts can represent a future changed registry; its actual qualifier and endpoint semantics must be validated against that proposed registry, not silently against the frozen companion.",
        "The L0 profile is explicitly draft. Formalization is the first plan phase: P01 semantics, P03 formal predicates, P04 Lean reference checker and P05 soundness review precede B00/P02 execution capture and interface/decoder alignment. Existing schemas/APIs are draft projections to align with that accepted formal model. The required-semantics text is not a formal theorem; imported forbidden-inference text is preserved, not proved.",
        "Normalized kind versions use sha256:<source digest> because the selected source records do not supply a uniform version field. This content identity is an explicit projection convention, not a newly admitted semantic version.", "",
        "## Validation", "",BT*3+"bash",
        "python3 -B craft/formalization/candidates/relational-theorem-checker/v1/interfaces/validate_interfaces.py",
        BT*3, "",
        "Validation checks all schema meta-definitions and local references, positive/negative fixtures, generated registry fidelity, OpenAPI structure, contract/DAG coverage and declared structural cross-record boundaries. It does not execute Lean, solve model obligations, authenticate protected roots or certify semantic correctness.",
        "Examples containing synthetic identities are shape fixtures, not deployable requests or accepted evidence. The bound package example sources and registry digests are real; semantic status remains imported/draft.",
        "", "## Version and identity policy", "",
        "Every instance envelope declares a candidate schema version. Objects are closed except intentional qualifier/substitution maps. Hash SHA-256 over exact UTF-8 bytes; reject duplicate JSON keys, invalid UTF-8 and untrusted digest claims before interpreting a document. Hash references do not grant artifact access. No network fetch or arbitrary filesystem path evaluation is part of reference resolution.",
        "The schema namespace is a logical identifier and is resolved locally; no publication at cyberalchemy.local is claimed.",
        "", "## Standards", "",
        "The definitions use [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core) and [OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html)."])
    markdown("SCHEMAS.md",["# Schema catalog", "",
        "All definitions are candidate interfaces. Required fields below exclude the version envelope; cross-record conditions belong to the behavioral contracts.", "",
        "| Layer | Schema | Purpose | Required fields |","|---|---|---|---|"]+[
        f'| {r["layer"]} | [{r["name"]}]({r["path"]}) | {r["purpose"]} | '+", ".join(k for k in r["required"] if k!="schema_version")+" |"
        for r in CATALOG]+["", "## Dynamic and generated boundaries", "",
        "The generic assertion schema intentionally leaves the qualifier map dynamic. The companion registry assertion schema supplies the selected declarations' closed qualifier contracts and exact pair checks. Shape validity never proves reference legitimacy, graph invariants or inference safety.",
        "Schema uniqueness on object arrays does not establish identity uniqueness; consumers must reject duplicate node, assertion, rule, obligation and certificate-step identifiers even when their contents differ."])
    lines=["# Behavioral contracts", "",
        "Each contract binds inputs, ordering, outputs, failures and retained trust boundaries. Fields reported by an untrusted submitter are assertions until independently verified.", ""]
    for c in contracts:
        lines += ["## "+c["contract_id"],"",f'Layer: {c["layer"]}. DAG tasks: '+(", ".join(c["task_ids"]) or "cross-cutting")+".",
            f'Input: [{c["input_schema"]}](schemas/{c["input_schema"]}.schema.json). Output: [{c["output_schema"]}](schemas/{c["output_schema"]}.schema.json).',
            "", "**Preconditions**", ""]+["- "+v for v in c["preconditions"]]+[
            "", "**Rules**", ""]+["- "+v for v in c["rules"]]+["", "**Postconditions**",""]+[
            "- "+v for v in c["postconditions"]]+["","**Failure controls**",""]+[
            "- "+v for v in c["failure_controls"]]+["","**Trust boundary**",""]+[
            "- "+v for v in c["trust_boundary"]]+[""]
    lines += ["## Review outcome rules", "",
        "Execution, currentness, evidence method, obligation verdict and aggregate readiness stay independent. Satisfied obligations require completed, current allowed evidence. A bounded-search provider output must become a checked witness before it can discharge a witness-eligible obligation.",
        "The verifier derives the complete hard obligation set from the actual diff/policy and matches exact statements and scope. Schema validation cannot enforce that cross-document completeness or prove a submitted proof term.",
        "Ready-for-review is a candidate review state, not admission. Human normative meaning review is separately recorded. G2 readiness excludes rule changes until I06/L3 discharge them."]
    markdown("CONTRACTS.md",lines)
    apidoc=["# API contract and flows", "",
        "The proposed service exposes 16 operations. No endpoint is started by this package. Requests are untrusted; asynchronous 202 responses only acknowledge execution scheduling.", "",
        "| Method | Path | Operation |","|---|---|---|"]
    apidoc += [f'| {method.upper()} | {path} | {item["operationId"]} |' for path,methods in api["paths"].items() for method,item in methods.items()]
    apidoc += ["", "## Artifact transport", "",
        "Upload exact original bytes to POST /v1/artifacts with X-Artifact-Schema and X-Artifact-Media-Type. Named envelope schemas require UTF-8 JSON and duplicate-key rejection. Use raw-artifact for proof source, required statements, raw provider output and pinned dependencies. A raw upload remains untrusted and cannot bypass the expected role/schema checks of its consuming operation. SHA-256 and byte size describe original bytes without reserialization.",
        "A controlled source adapter may register captured immutable authority source bytes and aliases in the artifact store. Caller-submitted repo paths are not executed or fetched directly. Every read, including raw proof/dependency content and known digests, still requires principal-scoped authorization.",
        "Idempotency-Key is required for asynchronous operations. Same principal/route/key with identical raw request bytes returns the original job; different bytes produce 409. Idempotency records and jobs must remain principal scoped.",
        "", "## Add a relation", "",
        "1. Capture and upload a selected source snapshot and reviewed semantic profile.",
        "2. Upload the base graph, resulting graph and exact change proposal.",
        "3. Normalize inputs and request complete obligations derived from the actual diff.",
        "4. Request the checker and attach proof/model evidence for applicable obligations.",
        "5. Submit the evidence bundle for independent review aggregation.",
        "6. Poll the job; read its result documents and their scope/currentness dimensions.",
        "7. Simulate application recheck against a fresh trusted baseline; actual admission is separate.",
        "", "## Example check request", "",
        "[Complete request](examples/check-request.json) binds the captured snapshot, draft profile, base graph and addition proposal. Its requested scope is structural. A supported-semantics request cannot become ready with this draft profile or without independent semantics and soundness evidence.",
        "", "## Rule changes", "",
        "Upload the positive finite rule profile, rules, base facts and derivation/closure certificates. Certificates carry exact rule versions and ground substitutions. Only an independently verified least fixed point or general theorem supports negative non-derivability claims. The checker must preserve protected root lineage across all intermediate rules.",
        "", "## Errors and resource policy", "",
        "Malformed data is 400; unknown or unsupported input schema/profile is 422; identity/idempotency/terminal-state conflicts are 409. Authentication and authorization use 401/403. Configured request size, graph size, rule-grounding, proof time and concurrency limits produce 413/429 or explicit timeout/unavailability job states. No throughput limit is invented here.",
        "A syntactically valid job may finish with violated, unknown or unsupported semantic obligations. That is represented in the result, not converted into a transport success claim.",
        "", "## Lifecycle", "",
        "Queued -> running -> completed / timeout / unavailable / failed. Queued or running work can cancel. Completed jobs require operation-compatible result references; terminal artifacts are immutable. Cancellation never creates readiness."]
    markdown("API.md",apidoc)
    mapping={t["id"]:[] for t in plan["tasks"]}
    for c in contracts:
        for task in c["task_ids"]:mapping[task].append(c["contract_id"])
    markdown("TRACEABILITY.md",["# DAG-to-interface traceability", "",
        "Every DAG task has a declared interface contract. This records interface coverage, not implementation completion.", "",
        "| Task | Layer | Contract | Status |","|---|---|---|"]+[
        f'| {t["id"]} — {t["title"]} | {t["layer"]} | {", ".join(mapping[t["id"]])} | interface candidate; task not started |'
        for t in plan["tasks"]])
    for layer in ("L0","L1","L2","L3","L4"):
        selected=[r for r in CATALOG if r["layer"]==layer]
        selected_contracts=[c for c in contracts if c["layer"] in (layer,"shared")]
        markdown("contracts/"+layer+".md",["# "+layer+" interface boundary", "",
            "## Definitions", ""]+[f'- [{r["name"]}](../{r["path"]}) — {r["purpose"]}' for r in selected]+[
            "", "## Behaviors", ""]+[f'- **{c["contract_id"]}**: '+ " ".join(c["rules"]+c["postconditions"]) for c in selected_contracts]+[
            "", "## Acceptance boundary", "",
            "These interface definitions are authored. Their executable semantic behavior and proof obligations remain the corresponding DAG tasks."])
    lanes={"status":"candidate","mode":"artifact","target":"Relational checker L0-L4 interface definitions",
        "user_intent":"Browse the complete schema, contract and API package.",
        "handles":{"surface.summary":"README.md","properties.catalog":"catalog.json","components.map":"SCHEMAS.md",
            "dependencies.internal":"catalog.json#/schemas/refs","dependencies.external":"package-manifest.json#/sources",
            "flow.graph":"API.md","lifecycle.timeline":"API.md#lifecycle","risk.questions":"CONTRACTS.md",
            "visual.model":"index.html"},
        "selected_lanes":["surface","properties","components","internal_dependencies","external_dependencies","flow","lifecycle","risk_questions","visual_composition"],
        "omitted_lanes":{},"renderer":"L0 semantic HTML and inline SVG with optional local selection controls",
        "interaction":["isolate","trace"],"visual_library":{"patterns":["pattern.dependency-boundary","pattern.lifecycle-stack"],
            "components":["shape.layer-panel","shape.node","shape.boundary","connector.arrow"]},
        "evidence_boundary":"Registry shapes and pairs are source-backed. All APIs, semantic interfaces and proposed behaviors are candidate design. No running proof/check service or theorem correctness claim.",
        "open_decisions":plan["decisions"],"skill":"/mnt/c/Users/vlad_/.codex/skills/x-ray/SKILL.md"}
    emit("xray-lanes.json",lanes)
    # A self-contained explorer; data is escaped and inserted only through textContent.
    template=(BASE/"explorer.template.html").read_text()
    catalog=json.loads(FILES["catalog.json"])
    inspector={"schemas":[{**r,"definition":json.loads(FILES[r["path"]]),
        "example":json.loads(FILES["examples/"+r["name"]+".json"]) if "examples/"+r["name"]+".json" in FILES else None} for r in CATALOG],
        "contracts":contracts,"apis":catalog["api_operations"],"lanes":lanes}
    payload=json.dumps(inspector,ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    emit("index.html",template.replace("__DATA__",payload))
    sources=[{"path":"docs/plans/relational-theorem-checker/"+name,
        "sha256":sha((PLAN/name).read_bytes())} for name in ("PLAN-SOURCE.json","ANALYSIS.md","SOURCE-BASELINE.json")]
    emit("package-manifest.json",{"schema_version":"relational-checker.interface-package/v1-candidate",
        "status":"candidate-interface","scope":"L0-L4 contract definitions only","authority_effect":"none",
        "created_on":"2026-10-07","schema_dialect":DIALECT,"api_version":"3.1.1",
        "counts":{"schemas":len(CATALOG),"behavior_contracts":len(contracts),"api_operations":len(catalog["api_operations"]),
            "dag_tasks_covered":sum(bool(v) for v in mapping.values())},
        "sources":sources,"fixture_claim_ceiling":"Shape and structural consistency examples; no accepted semantic/proof evidence.",
        "generator_sha256":sha(Path(__file__).read_bytes()),
        "artifacts":[{"path":p,"sha256":sha(v),"bytes":len(v)} for p,v in sorted(FILES.items())]})

def build():
    declarations()
    kinds,plan=registry_assets()
    operations,contracts,api=api_and_contracts(plan)
    make_examples()
    documents(operations,contracts,api,plan)
    return FILES

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=["build","check"])
    args=parser.parse_args()
    files=build()
    if args.mode=="build":
        if (BASE/"package-manifest.json").exists():
            raise SystemExit("Refusing to overwrite existing interface package; review a successor version.")
        for p,v in files.items():
            target=BASE/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(v)
    else:
        for p,v in files.items():
            if (BASE/p).read_bytes()!=v:raise SystemExit("Generated artifact drift: "+p)
    manifest=json.loads(files["package-manifest.json"])
    print(json.dumps({"mode":args.mode,"result":"pass","counts":manifest["counts"]},indent=2))

if __name__=="__main__":
    main()
