#!/usr/bin/env python3
"""A real local transaction and Agent context in a disposable isolated branch."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from lab_runtime.cli import example
from lab_runtime.common import encoded, load, require
from lab_runtime.session import Session
from lab_runtime.store import Store, keygen

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[2]


def run():
    with TemporaryDirectory(prefix="cal-lab-runtime-demo-") as name:
        root = Path(name)
        keygen(root / "operator.pem", root / "operator.pub")
        store = Store(root / "store", REPO)
        before = store.initialize(load(PACKAGE / "profile.json"), "operational-demo", "principal:local-demo-operator", (root / "operator.pub").read_text().strip())
        proposal = example(store, "review-runtime-work")
        review = store.review(proposal)
        approval = store.authorize(proposal, root / "operator.pem")
        applied = store.apply(proposal, approval)
        again = store.apply(proposal, approval)
        verification = subprocess.run([sys.executable, str(PACKAGE / "lab.py"), "--store", str(store.path), "verify"], capture_output=True, text=True)
        require(verification.returncode == 0, verification.stderr)
        session = Session(store, proposal["targets"][0]["version_ref"])
        context = session.context()
        session.note("Working scratch; not durable Project memory.")
        disposition = session.close()
        after = store.status()
        return {"result": "PASS", "source_snapshot_digest": before["freshness"]["snapshot_digest"],
                "repository_baseline": before["repository_admission_as_of"], "before_state": before["current_project_state"]["node_id"],
                "review": review, "proposal_digest": applied["receipt"]["proposal_digest"], "receipt": applied["receipt"],
                "local_after_state": after["current_project_state"]["node_id"], "history_cursors": after["history_cursors"],
                "idempotent_repeat": again["idempotent"], "fresh_process_replay": "PASS",
                "context_records": {"ontology_nodes": len(context["ontology_nodes"]), "ontology_edges": len(context["ontology_edges"]),
                                    "context_view": context["context_view"]["node_id"], "ontology_view": context["ontology_view"]["node_id"]},
                "session_disposition": disposition, "disposable_store_removed_after_run": True,
                "private_key_published": False, "repository_admission_effect": "none", "external_effects": 0}


if __name__ == "__main__":
    print(encoded(run()).decode(), end="")
