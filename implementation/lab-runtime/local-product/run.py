#!/usr/bin/env python3
"""Run a complete, disposable local Work journey on the admitted v1 runtime."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNTIME = HERE.parent / "v1"
sys.dont_write_bytecode = True
sys.path.insert(0, str(RUNTIME))

from lab_runtime.cli import example  # noqa: E402
from lab_runtime.common import RuntimeFault, load, require  # noqa: E402
from lab_runtime.session import Session  # noqa: E402
from lab_runtime.store import Store, keygen  # noqa: E402


def run() -> dict:
    with TemporaryDirectory(prefix="cal-local-product-") as directory:
        owned_root = Path(directory)
        private_key = owned_root / "owner.pem"
        public_key = owned_root / "owner.pub"
        keygen(private_key, public_key)

        store = Store(owned_root / "store", REPO)
        before = store.initialize(
            load(RUNTIME / "profile.json"),
            "local-product-fixture",
            "principal:local-product-fixture-owner",
            public_key.read_text().strip(),
        )
        proposal = example(store, "local-work-journey")
        review = store.review(proposal)
        require(review["target_count"] == 1 and review["approval_required"], "Work review did not select one target")
        approval = store.authorize(proposal, private_key)

        # The signed approval must bind the exact proposal. Check before the
        # real effect so this cannot become a stale-HEAD refusal instead.
        altered = copy.deepcopy(proposal)
        altered["proposal_id"] = "local-work-journey-altered"
        try:
            store.apply(altered, approval)
        except RuntimeFault as error:
            require(
                str(error) == "approval does not bind exact proposal, authority, scope and HEAD",
                "unexpected refusal: " + str(error),
            )
        else:
            raise RuntimeFault("changed proposal was accepted under the original approval")
        after_refusal = store.status()
        require(
            after_refusal["head"] == before["head"]
            and after_refusal["sequence"] == before["sequence"]
            and not after_refusal["recovery_required"],
            "refused request changed durable state",
        )

        applied = store.apply(proposal, approval)
        repeated = store.apply(proposal, approval)
        require(not applied["idempotent"] and repeated["idempotent"], "exact retry was not idempotent")
        require(repeated["transaction_digest"] == applied["transaction_digest"], "exact retry changed transaction")

        verify = subprocess.run(
            [sys.executable, "-B", str(RUNTIME / "lab.py"), "--store", str(store.path), "verify"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        require(verify.returncode == 0, "fresh-process replay failed: " + verify.stderr[-2000:])

        session = Session(store, proposal["targets"][0]["version_ref"])
        context = session.context()
        session.note("Disposable working note; never a durable project record.")
        disposition = session.close()
        require(
            disposition["termination_state"] == "closed"
            and disposition["short_memory_erased"]
            and not session.memory,
            "Session did not close and erase its short memory",
        )
        after = store.status()
        require(after["sequence"] == before["sequence"] + 1, "transaction sequence did not advance once")
        require(not after["recovery_required"], "unexpected recovery residue")

        result = {
            "result": "PASS",
            "runtime": "admitted Lab Operational Runtime v1",
            "profile": {
                "path": str((RUNTIME / "profile.json").relative_to(REPO)),
                "sha256": hashlib.sha256((RUNTIME / "profile.json").read_bytes()).hexdigest(),
            },
            "repository_baseline": before["repository_admission_as_of"],
            "source_snapshot_digest": before["freshness"]["snapshot_digest"],
            "work_version": proposal["targets"][0]["version_ref"],
            "reviewed_targets": review["target_count"],
            "review": {
                "proposal_digest": review["proposal_digest"],
                "target_count": review["target_count"],
                "planned_consequences": review["planned_consequences"],
            },
            "refusal": {"case": "altered signed proposal", "result": "rejected", "head_unchanged": True},
            "receipt": applied["receipt"],
            "local_sequence": after["sequence"],
            "local_project_state": after["current_project_state"]["node_id"],
            "exact_retry_idempotent": True,
            "fresh_process_replay": "PASS",
            "context": {
                "view": context["context_view"]["node_id"],
                "ontology_view": context["ontology_view"]["node_id"],
            },
            "session_closed": disposition["termination_state"] == "closed",
            "short_memory_erased": disposition["short_memory_erased"],
            "repository_admission_effect": "none",
            "external_effects": 0,
        }

    require(not owned_root.exists(), "disposable root remains after cleanup")
    result["disposable_root_removed"] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the complete machine-readable receipt")
    arguments = parser.parse_args()
    try:
        outcome = run()
    except (RuntimeFault, OSError, subprocess.TimeoutExpired, ValueError) as error:
        print(f"Local Work journey failed: {error}", file=sys.stderr)
        return 1
    if arguments.json:
        print(json.dumps(outcome, indent=2, sort_keys=True))
    else:
        print("CyberAlchemy Lab — local Work journey: PASS")
        print(f"Runtime: {outcome['runtime']}; frozen repository baseline: {outcome['repository_baseline']}")
        print(f"Profile SHA-256: {outcome['profile']['sha256']}")
        print(f"Work: {outcome['work_version']}")
        print(f"Proposal review: {outcome['reviewed_targets']} target; approval required")
        print("Altered signed proposal: rejected; local HEAD unchanged")
        print(f"Committed local sequence: {outcome['local_sequence']}")
        print(f"Local Project State: {outcome['local_project_state']}")
        print("Exact retry: idempotent; fresh-process replay: PASS")
        print("Agent context: prepared; Session closed and short memory erased")
        print("Disposable store and fixture key: removed")
        print("Repository admission effect: none; external effects: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
