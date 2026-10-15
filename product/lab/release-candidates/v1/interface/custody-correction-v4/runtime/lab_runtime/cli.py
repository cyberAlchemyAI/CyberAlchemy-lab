from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from .common import RuntimeFault, atomic, digest, encoded, load, require, sealed
from .graph import build, posture, query
from .session import Session
from .sources import capture, resolve
from .store import Store, keygen

PACKAGE = Path(__file__).resolve().parents[1]
DEFAULT_REPO = PACKAGE.parents[6]


def read_data(repo, store):
    if store.path.exists():
        return store.replay()
    source = capture(repo, load(PACKAGE / "profile.json"))
    return {"baseline": source, "projection": Store.initial_projection(source), "freshness": {"status": "current", "changed": [], "checked_count": len(source["materials"]), "snapshot_digest": source["snapshot_digest"]},
            "head": {"transaction_digest": source["snapshot_digest"], "sequence": 0}, "transactions": [],
            "config": {"store_id": "repository-inspection", "source_snapshot_digest": source["snapshot_digest"]}}


def example(store, proposal_id):
    require(proposal_id and all(c.isalnum() or c == "-" for c in proposal_id), "invalid proposal identity")
    data = store.replay(require_current=True)
    cfg = data["config"]
    record = copy.deepcopy(data["projection"]["documents"]["authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/work.json"])
    record.update(node_id="work:lab-runtime:" + proposal_id, name="Candidate local Lab work", scope_ref=cfg["scope_ref"],
                  owner_ref=cfg["owner_ref"], evidence_refs=["runtime-source-snapshot:" + cfg["source_snapshot_digest"]],
                  claim_ceiling="Candidate work record for exact local review; no work completion or execution is asserted.")
    record["payload"]["project_ref"] = data["projection"]["state"]["payload"]["project_ref"]
    record["payload"].update(completion_state="planned", goal_refs=["goal:lab-runtime-local-work"],
                              input_refs=[data["projection"]["state"]["node_id"]],
                              output_refs=["candidate:local-work-output"],
                              work_statement="Prepare a bounded local work proposal for owner review.")
    version = record["node_id"] + "@candidate.1"
    return {"schema_version": "lab-runtime-proposal/v1", "proposal_id": proposal_id,
            "expected_head": data["head"]["transaction_digest"], "source_snapshot_digest": cfg["source_snapshot_digest"],
            "scope_ref": cfg["scope_ref"], "policy_ref": cfg["policy_ref"], "challenge_route": cfg["challenge_route"], "schemas": {},
            "targets": [{"category": "artifact-instance", "operation": "admit", "version_ref": version,
                         "carrier_ref": "cal.artifact-type.work/v1", "record": record, "predecessor_ref": None,
                         "decision_ref": "decision:local:" + proposal_id, "contract": None}]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Candidate CyberAlchemy Lab operational runtime: source inspection, governed local transactions and ephemeral Agent context.")
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--store", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("verify")
    rebuild = sub.add_parser("rebuild")
    rebuild.add_argument("--out", type=Path, required=True, help="Write a disposable source-bound graph snapshot.")
    init = sub.add_parser("init")
    init.add_argument("--id", required=True)
    init.add_argument("--owner", required=True)
    init.add_argument("--public-key", type=Path, required=True)
    keys = sub.add_parser("keygen")
    keys.add_argument("--private", type=Path, required=True)
    keys.add_argument("--public", type=Path, required=True)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("subject")
    inspect.add_argument("--record", action="store_true")
    catalog = sub.add_parser("catalog")
    catalog.add_argument("--category", choices=["definition", "artifact-type", "relation-kind", "artifact-instance", "typed-relation"])
    catalog.add_argument("--current", action="store_true")
    q = sub.add_parser("query")
    q.add_argument("root", nargs="?", default="Lifecycle")
    q.add_argument("--direction", choices=["both", "incoming", "outgoing"], default="both")
    q.add_argument("--depth", type=int, default=4)
    q.add_argument("--max-nodes", type=int, default=100)
    q.add_argument("--max-edges", type=int, default=200)
    q.add_argument("--predicate", action="append")
    ex = sub.add_parser("example")
    ex.add_argument("--id", required=True)
    ex.add_argument("--out", type=Path, required=True)
    review = sub.add_parser("review")
    review.add_argument("proposal", type=Path)
    approve = sub.add_parser("authorize")
    approve.add_argument("proposal", type=Path)
    approve.add_argument("--private-key", type=Path, required=True)
    approve.add_argument("--out", type=Path, required=True)
    apply = sub.add_parser("apply")
    apply.add_argument("proposal", type=Path)
    apply.add_argument("approval", type=Path)
    recover = sub.add_parser("recover")
    recover.add_argument("--expected-head", required=True)
    session = sub.add_parser("session")
    session.add_argument("subject")
    session.add_argument("--ttl", type=int, default=900)
    session.add_argument("--context-only", action="store_true", help="Emit the derived context packet and immediately close the ephemeral session.")
    args = parser.parse_args(argv)
    try:
        repo = args.repo.resolve()
        store = Store(args.store or repo / ".local/lab-runtime/custody-correction-v4/store", repo)
        if args.command == "keygen":
            require(not args.private.resolve().is_relative_to(repo), "private key must remain outside repository")
            result = keygen(args.private, args.public)
        elif args.command == "init":
            result = store.initialize(load(PACKAGE / "profile.json"), args.id, args.owner, args.public_key.read_text().strip())
        elif args.command in ("status", "verify", "inspect", "catalog", "query", "rebuild"):
            data = read_data(repo, store)
            if args.command == "status":
                if store.path.exists():
                    result = store.status()
                else:
                    result = {"store_initialized": False, "current_project_state": data["projection"]["state"],
                              "repository_admission_as_of": data["baseline"]["admission_as_of"], "freshness": data["freshness"],
                              "subject_count": len(data["projection"]["subjects"]), "authority_effect": "none"}
            elif args.command == "verify":
                require(data["freshness"]["status"] == "current", "stale repository sources")
                result = {"result": "PASS", "source_snapshot_digest": data["baseline"]["snapshot_digest"], "head": data["head"]["transaction_digest"],
                          "verified_source_count": len(data["baseline"]["materials"]), "subject_count": len(data["projection"]["subjects"]),
                          "transactions_replayed": len(data["transactions"]), "authority_effect": "none"}
            elif args.command == "rebuild":
                require(data["freshness"]["status"] == "current", "stale sources cannot produce a current graph")
                graph = build(data)
                result = {"schema_version": "lab-runtime-derived-graph/v1", "source_snapshot_digest": data["baseline"]["snapshot_digest"],
                          "head": data["head"]["transaction_digest"], "freshness": data["freshness"], "graph": graph, "authority_effect": "none", "replay_source": False}
                out = args.out.resolve()
                require(not out.is_relative_to(repo) or out.is_relative_to(repo / ".local"), "derived output inside repository must live under .local/")
                require(not out.is_relative_to(store.path) or out.is_relative_to(store.path / "derived"), "derived output cannot replace canonical store material")
                atomic(args.out, encoded(result))
                result = {"output": str(args.out), "graph_digest": graph["graph_digest"], "nodes": len(graph["nodes"]), "edges": len(graph["edges"]), "authority_effect": "none"}
            elif args.command == "inspect":
                entry = resolve(data["projection"]["subjects"], args.subject)
                result = {**posture(entry), "freshness": data["freshness"], "authority_effect": "none"}
                if args.record:
                    result["record"] = entry["record"]
            elif args.command == "catalog":
                values = [posture(v) for _, v in sorted(data["projection"]["subjects"].items()) if
                          (not args.category or v["category"] == args.category) and
                          (not args.current or v["effective_state"] in ("admitted-current", "local-admitted-current"))]
                result = {"count": len(values), "subjects": values, "freshness": data["freshness"], "authority_effect": "none"}
            else:
                result = query(data, args.root, args.direction, args.depth, args.max_nodes, args.max_edges, args.predicate)
        elif args.command == "example":
            result = example(store, args.id)
            require(not args.out.exists(), "proposal output already exists")
            atomic(args.out, encoded(result))
            result = {"candidate_proposal": str(args.out), "proposal_digest": digest(result), "authority_effect": "none"}
        elif args.command == "review":
            result = store.review(load(args.proposal))
        elif args.command == "authorize":
            result = store.authorize(load(args.proposal), args.private_key)
            require(not args.out.exists(), "approval output already exists")
            atomic(args.out, encoded(result))
            result = {"approval_path": str(args.out), "approval_digest": digest(result), "outcome": result["outcome"], "applied": False}
        elif args.command == "apply":
            result = store.apply(load(args.proposal), load(args.approval))
        elif args.command == "recover":
            result = store.recover(args.expected_head)
        elif args.command == "session":
            s = Session(store, args.subject, args.ttl)
            try:
                if args.context_only:
                    result = {"context_packet": s.context(), "session_disposition": "closed-after-export"}
                else:
                    print(encoded({"session_id": s.session_id, "state": "active", "commands": ["context", "note TEXT", "memory", "close"]}).decode(), flush=True)
                    for line in sys.stdin:
                        line = line.strip()
                        if line == "close":
                            break
                        if line == "context":
                            output = s.context()
                        elif line.startswith("note "):
                            output = s.note(line[5:])
                        elif line == "memory":
                            s.context()
                            output = {"session_memory": list(s.memory), "persisted": False}
                        else:
                            raise RuntimeFault("unknown session command")
                        print(encoded(output).decode(), flush=True)
                    result = s.close()
            finally:
                s.close()
        print(encoded(result).decode(), end="")
        return 0
    except (RuntimeFault, OSError) as exc:
        print(json.dumps({"error": str(exc), "result": "BLOCKED", "authority_effect": "none"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
