"""Synthetic EA task -> finding -> Product decision -> W/U/F/cash path."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "economics"))
from loop_model import LoopPolicy, LoopState, Period, run  # noqa: E402


def case(*, outcome: str, sale_c: int = 1000,
         product_sales_right_retained: bool = True) -> dict:
    """Outcome and sales are declared synthetic inputs, never model judgments."""
    if outcome not in ("controlled-improvement", "decision-closing-negative",
                       "inconclusive"):
        raise ValueError("unknown synthetic outcome")
    if type(sale_c) is not int or sale_c < 0:
        raise ValueError("invalid synthetic Product receipt")

    manifest = json.loads((ROOT / "source-manifest.json").read_text())
    catalog = json.loads((ROOT / "task-catalog.json").read_text())
    task = next(t for t in catalog["tasks"] if t["task_ref"] == "ea-task:e03")
    assert task["experiment_ref"] == "experiment-design:ea:e03"
    assert catalog["source_cut_sha256"] == manifest["source_cut_sha256"]

    # These are stipulated independent decisions inside a fictional scenario.
    # A real reviewer or Product owner has not made them.
    valid_execution = True
    independent_reviewers = ["synthetic-reviewer-1", "synthetic-reviewer-2"]
    controlled_decision_resolution = outcome != "inconclusive"
    hypothetical_owner_acceptance = controlled_decision_resolution
    durable_advance = (valid_execution and len(set(independent_reviewers)) == 2
                       and controlled_decision_resolution
                       and hypothetical_owner_acceptance)
    product_decision = ({"controlled-improvement": "adopt-scorer-variant",
                         "decision-closing-negative": "retain-baseline-scorer",
                         "inconclusive": "hold-scorer-change"})[outcome]
    policy = LoopPolicy(cash_floor_c=500, w_cap=300, u_cap=300,
                        u_share_bps=2000, w_redemption="burn",
                        f_cap_units=1400, f_share_bps=1000,
                        sponsor_unit_price_c=1)
    initial = LoopState(cash_c=1000, research_only_c=0, service_reserve_c=0,
                        committed_unpaid_c=0, w_inventory=300,
                        w_circulating=0, w_burned=0, u_remaining=300,
                        f_remaining=1400)
    # Periods 1-2: two assumed cleared sponsor installments pay for bounded
    # research. W is reserved for valid task execution; U is awarded only at
    # the second period's independently adjudicated decision resolution.
    periods = [
        Period(sponsor_unrestricted_c=700, sponsor_vested_c=700, f_award=700,
               operating_c=200, research_c=400, w_award=100,
               service_reserve_add_c=50),
        Period(sponsor_unrestricted_c=700, sponsor_vested_c=700, f_award=700,
               operating_c=200, research_c=400, w_award=100,
               service_reserve_add_c=50, u_award=100 if durable_advance else 0),
    ]
    # Periods 3-5: assumed Product receipts after the separate Product decision.
    # Two hypothetical 100-W practice-service redemptions consume the 100-C
    # reserve; no later W issue is assumed. Sale net is after direct Product
    # costs, and only the separately declared D enters U/F payout.
    for index in range(3):
        periods.append(Period(product_net_c=sale_c, distributable_c=sale_c,
                              operating_c=200, research_c=400,
                              w_redeem=100 if index < 2 else 0,
                              service_cost_c=50 if index < 2 else 0))
    if sale_c and not product_sales_right_retained:
        economic = run(policy, initial, periods[:2])
        economic["first_refused_period"] = 3
        economic["reason"] = "product-revenue-rights-lost"
    else:
        economic = run(policy, initial, periods)
    return {
        "status": "synthetic-simulation-only", "authority_effect": "none",
        "source_cut_sha256": manifest["source_cut_sha256"],
        "task_ref": task["task_ref"],
        "outcome": outcome,
        "research_chain": [
            {"period": 1, "stage": "source-pinned-object-and-prior",
             "input": "20 authored synthetic answers; baseline scorer and candidate repair",
             "decision": "test-candidate", "w_award_units": 100,
             "u_award_units": 0},
            {"period": 2, "stage": "controlled-run-and-independent-review",
             "input": "matched baseline/variant comparison with two synthetic independent reviewers",
             "decision": outcome,
             "assumed_owner_acceptance": hypothetical_owner_acceptance,
             "decision_scope": "local authored-fixture uncertainty only",
             "w_award_units": 100,
             "u_award_units": 100 if durable_advance else 0},
            {"period": 3, "stage": "separate-product-owner-decision",
             "decision": product_decision, "w_award_units": 0,
             "u_award_units": 0},
        ],
        "product_decision": product_decision,
        "commercial_rights_retained_assumption": product_sales_right_retained,
        "service": "hypothetical 100-W practice service, no participant data",
        "economic_policy": asdict(policy),
        "periods_planned": len(periods),
        "completed_periods": economic["completed_periods"],
        "first_refused_period": economic["first_refused_period"],
        "reason": economic["reason"],
        "last_valid_state": economic["last_valid_state"],
        "u_paid_c": sum(row["u_payout_c"] for row in economic["trace"]),
        "f_paid_c": sum(row["f_payout_c"] for row in economic["trace"]),
        "trace": economic["trace"],
        "claim_ceiling": "Constructed research verdict, Product choice and cash path; no EA run, human response, sale, W/U/F issue or Product authority."}


def report() -> dict:
    return {"schema_version": "arn.ea-integrated-scenarios/v1",
            "status": "synthetic-simulation-only", "authority_effect": "none",
            "cases": {
                "controlled_improvement_sales": case(outcome="controlled-improvement"),
                "decision_closing_negative_sales": case(outcome="decision-closing-negative"),
                "valid_but_inconclusive_sales": case(outcome="inconclusive"),
                "improvement_no_sales": case(outcome="controlled-improvement", sale_c=0),
                "rights_lost_blocks_sales": case(outcome="controlled-improvement",
                                                 product_sales_right_retained=False),
            },
            "claim_ceiling": "No empirical research, market, service, Product-owner or asset effect."}


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
