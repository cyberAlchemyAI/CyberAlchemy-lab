#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
DEFAULT_SOURCE=HERE.parents[1]/"domainspec-source/cal-ontology-runtime-export-cutover-epoch-002/authored-source.json"
def canonical(v): return (json.dumps(v,indent=2,sort_keys=True)+"\n").encode()
def digest_bytes(v): return hashlib.sha256(v).hexdigest()
def validate_source(s):
    if s.get("schema_version")!="domainspec.authored-source/v2": raise ValueError("SOURCE_SCHEMA_MISMATCH")
    if {x.get("ref") for x in s.get("contexts",[])}!={"cal.context.governance/v2","cal.context.ontology-lifecycle/v2"}: raise ValueError("CONTEXT_ENDPOINT_MISMATCH")
    m=s.get("context_map",{})
    if m.get("ref")!="cal.context-map.governance-ontology-lifecycle/v2" or m.get("direction")!="source-to-target": raise ValueError("CONTEXT_MAP_MISMATCH")
    if {x.get("aggregate_id") for x in s.get("aggregates",[])}!={"OntologyNode","OntologyRelation"}: raise ValueError("AGGREGATE_MODEL_INCOMPLETE")
    if len({x.get("event_type") for x in s.get("events",[])})!=5: raise ValueError("EVENT_MODEL_INCOMPLETE")
    if {x.get("projection_id") for x in s.get("projections",[])}!={"LatestNodeSnapshot","LatestRelationSnapshot","GovernedContextProjectionV2"}: raise ValueError("PROJECTION_MODEL_INCOMPLETE")
    if any(x.get("canonical_replay_source") is not False for x in s.get("projections",[])): raise ValueError("DERIVATIVE_MARKED_CANONICAL")
def compile_model(source_path, output_dir):
    raw=source_path.read_bytes(); source=json.loads(raw); validate_source(source)
    nodes=[]
    for group,kind,key in ((source["aggregates"],"aggregate","aggregate_id"),(source["commands"],"command","command_id"),(source["events"],"event","event_type"),(source["projections"],"projection","projection_id"),(source["invariants"],"invariant","invariant_id")):
        nodes += [{"id":x[key],"kind":kind,"source":x} for x in group]
    nodes += [{"id":x["ref"],"kind":"context","source":x} for x in source["contexts"]]
    nodes += [{"id":source["context_map"]["ref"],"kind":"context-map","source":source["context_map"]}]
    nodes=sorted(nodes,key=lambda x:(x["kind"],x["id"]))
    edges=[]
    event_ids={x["event_type"] for x in source["events"]}
    for event in source["events"]:
        edges.append({"source":event["event_type"],"predicate":"records-state-for","target":event["aggregate"]})
    for projection in source["projections"]:
        for event in projection["source_events"]:
            if event not in event_ids: raise ValueError("PROJECTION_EVENT_UNRESOLVED")
            edges.append({"source":projection["projection_id"],"predicate":"calculated-from","target":event})
    edges.append({"source":"cal.context.governance/v2","predicate":"publishes-evidence-to","target":"cal.context.ontology-lifecycle/v2"})
    edges.append({"source":"cal.context-map.governance-ontology-lifecycle/v2","predicate":"binds","target":"cal.context.governance/v2"})
    edges.append({"source":"cal.context-map.governance-ontology-lifecycle/v2","predicate":"binds","target":"cal.context.ontology-lifecycle/v2"})
    graph={"schema_version":"domainspec.compiled-graph/v2","project_id":source["project_id"],"source_sha256":hashlib.sha256(raw).hexdigest(),"nodes":nodes,"edges":sorted(edges,key=lambda x:(x["source"],x["predicate"],x["target"])),"canonical_replay_source":False,"authority_effect":"none"}
    system={"schema_version":"cal.system-ontology/v2","ontology_id":"cal.ontology-runtime-export-cutover.system.epoch-002","source_project_id":source["project_id"],"context_bindings":source["contexts"],"context_map_binding":source["context_map"],"aggregate_types":source["aggregates"],"event_types":source["events"],"projection_types":source["projections"],"invariants":source["invariants"],"typed_failures":source["typed_failures"],"adapter_contract":source["public_adapter_contract"],"canonical_replay_source":False,"product_approval":"not-requested","authority_effect":"none"}
    manifest={"schema_version":"domainspec.source-manifest/v2","source_path":str(source_path),"source_sha256":hashlib.sha256(raw).hexdigest(),"compiler_path":str(Path(__file__).resolve()),"compiler_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output_dir.mkdir(parents=True,exist_ok=True)
    artifacts={"graph.json":canonical(graph),"system-ontology.json":canonical(system),"source-manifest.json":canonical(manifest)}
    for name,data in artifacts.items(): (output_dir/name).write_bytes(data)
    receipt={"schema_version":"domainspec.compile-receipt/v2","stage_id":"D65-S5","source_sha256":manifest["source_sha256"],"compiler_sha256":manifest["compiler_sha256"],"outputs":{name:digest_bytes(data) for name,data in sorted(artifacts.items())},"result":"PASS","deterministic_contract":"same source bytes plus same compiler bytes produce byte-identical outputs","product_approval":"not-requested","authority_effect":"none"}
    (output_dir/"compile-receipt.json").write_bytes(canonical(receipt))
def main():
    p=argparse.ArgumentParser(); p.add_argument("--source",type=Path,default=DEFAULT_SOURCE); p.add_argument("--output-dir",type=Path,default=HERE/"generated"); a=p.parse_args()
    try: compile_model(a.source.resolve(),a.output_dir.resolve())
    except (ValueError,KeyError,json.JSONDecodeError) as e: print(f"COMPILE=BLOCK:{e}"); return 1
    print("COMPILE=PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
