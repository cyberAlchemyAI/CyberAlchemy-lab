"""Produce a deterministic synthetic mining and settlement ledger fixture."""

import json
import hashlib
from pathlib import Path

from reference_model import ADVANCE_GATES, REVIEW_GATES, Model, Policy


ROOT = Path(__file__).resolve().parent


def run() -> tuple[dict, list[dict]]:
    m = Model(Policy.load(ROOT / "simulation-policy.json"))
    m.offer_task("task:synthetic-negative", "epoch:synthetic-1", slots=1,
                 base=100, bonus=50, reviewer_fee=5,
                 commit_deadline=10, reveal_deadline=20, challenge_end=30)
    m.assign("task:synthetic-negative", 0, "miner:alice")
    content_hash = hashlib.sha256(b"synthetic-content").hexdigest()
    commitment = m.commitment("task:synthetic-negative", 0, "miner:alice", content_hash, "secret")
    m.commit("task:synthetic-negative", 0, commitment, at=5)
    m.reveal("task:synthetic-negative", 0, content_hash, "secret",
             set(), "negative", at=15)
    for reviewer in ("reviewer:one", "reviewer:two"):
        m.review("task:synthetic-negative", 0, reviewer,
                 {key: "pass" for key in REVIEW_GATES}, True,
                 quality_status="pass")
    work_award = m.finalize_slot("task:synthetic-negative", 0, at=31,
                                  owner_decision=True, appeal_closed=True)
    m.transfer_w("miner:alice", "miner:bob", 30, event_id="transfer:synthetic-1", nonce=0)
    m.redeem_w("miner:bob", 10, service_ref="service:synthetic-public-demo",
               authorized=True, capacity_reserved=True,
               event_id="redemption:synthetic-1", nonce=0)
    m.reserve_milestone("milestone:synthetic-1", 2000)
    units = m.allocate_advance("advance:synthetic-1", "milestone:synthetic-1",
                               {"miner:alice": 6000, "miner:bob": 4000},
                               {key: True for key in ADVANCE_GATES},
                               agreement_signed=True, owner_decision=True,
                               appeal_closed=True)
    m.deposit_revenue("period:synthetic-1", 100000,
                      source_kind="product-receipts",
                      event_id="revenue:synthetic-1", nonce=0)
    settlement = m.settle_revenue("period:synthetic-1", gross=100000,
                                  refunds=5000, taxes=2000, fees=1000,
                                  direct_costs=1000, reserves=1000, exclusions=0,
                                  active_units={"miner:alice": 1200, "miner:bob": 800},
                                  audited=True, agreements_active=True,
                                  payment_finality_confirmed=True)
    m.check_invariants()
    summary = {"schema_version": "arn.synthetic-economic-scenario/v1",
               "status": "simulation-only", "authority_effect": "none",
               "work_award_units": work_award, "participation_awards": units,
               "settlement": settlement, "work_balances": m.w,
               "participation_balances": m.u, "stablecoin_balances": m.c,
               "event_count": len(m.events),
               "ledger_root_digest": m.events[-1]["digest"],
               "claim_ceiling": "Synthetic arithmetic and transitions only; no real work, agreement, revenue, token or payment."}
    transactions = []
    for event in m.events:
        transactions.append({
            "schema_version": "arn.ledger-transaction/v1",
            "record_id": event["event_id"],
            "version": "0.1.0-fixture.1",
            "status": "candidate-unadmitted",
            "authority_effect": "none",
            "subject_ref": event["ref"],
            "owner_ref": "role:arn-simulation-only",
            "source_refs": ["docs/proposals/agentic-research-network/2026-10-29/model-v1/economics/scenario.py"],
            "challenge_route": "role:arn-simulation-only",
            "claim_ceiling": "Synthetic ledger event only; no real transfer or settlement.",
            "data": {
                "event_id": event["event_id"],
                "previous_digest": event["previous_digest"],
                "asset_ref": event["asset"],
                "kind": event["kind"],
                "amount_units": event["amount"],
                "debit_account": event["debit"],
                "credit_account": event["credit"],
                "signer_ref": event["signer"],
                "signer_nonce": event["nonce"],
                "idempotency_key": event["idempotency_key"],
                "decision_ref": event["decision_ref"],
                "event_digest": event["digest"],
                "finality_state": "simulation-only",
            },
        })
    return summary, transactions


if __name__ == "__main__":
    summary, transactions = run()
    output = ROOT / "fixtures"
    (output / "transactions").mkdir(parents=True, exist_ok=True)
    (output / "scenario.json").write_text(json.dumps(summary, indent=2) + "\n")
    for index, event in enumerate(transactions, 1):
        (output / "transactions" / f"{index:02d}.json").write_text(json.dumps(event, indent=2) + "\n")
    print(f"Wrote {len(transactions)} synthetic transactions; ledger root {summary['ledger_root_digest']}")
