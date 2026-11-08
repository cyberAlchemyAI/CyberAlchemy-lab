"""Counterfactual Product 001 sponsor schedules and deterministic stress paths."""

from __future__ import annotations

import json
from dataclasses import replace

from multi_sponsor_model import (Account, Period, Policy, SponsorTerms, State,
                                 run)


def setup(*, access=True, lost_sales_right=False):
    policy = Policy(floor_c=500, f_cap=1400, u_share_bps=2000,
                    f_share_bps=1000)
    sponsors = (
        SponsorTerms("sponsor-A", f_limit=900, c_per_f=1),
        SponsorTerms("sponsor-B", f_limit=500, c_per_f=1,
                     access_cap=5 if access else 0,
                     c_per_access=100 if access else 0,
                     access_cost_c=30 if access else 0,
                     license_kind="assignment" if lost_sales_right else "none",
                     rights_cleared=lost_sales_right,
                     product_sales_retained=not lost_sales_right),
    )
    state = State(1000, {term.sponsor_id: Account() for term in sponsors})
    return policy, sponsors, state


def funding_periods():
    return [Period(deposits_c={"sponsor-A": 900}, vest_c={"sponsor-A": 900}),
            Period(deposits_c={"sponsor-B": 500}, vest_c={"sponsor-B": 500})]


def cases():
    base = funding_periods()
    product = Period(product_net_c=1000, distributable_c=1000)
    return {
        "staggered_exit_with_access": (*setup(), base +
                                        [replace(product, access_use={"sponsor-B": 1})] * 3),
        "staggered_exit_no_access": (*setup(access=False), base + [product] * 3),
        "exit_no_product": (*setup(), base + [Period()] * 2),
        "product_downturn": (*setup(), base +
                             [Period(product_net_c=600, distributable_c=600,
                                     access_use={"sponsor-B": 1})] * 3),
        "sales_right_lost": (*setup(lost_sales_right=True), base + [product]),
        "refund_before_vesting": (*setup(),
                                  [Period(deposits_c={"sponsor-A": 900},
                                          vest_c={"sponsor-A": 500},
                                          refunds_c={"sponsor-A": 400})]),
        "unpaid_pledge": (*setup(),
                          [Period(vest_c={"sponsor-A": 900})]),
        "access_abuse": (*setup(), base +
                         [replace(product, access_use={"sponsor-B": 6})]),
    }


def report():
    results = {}
    for name, (policy, sponsors, initial, periods) in cases().items():
        result = run(policy, sponsors, initial, periods)
        last = result["trace"][-1] if result["trace"] else None
        results[name] = {
            "periods_planned": len(periods),
            "completed_periods": result["completed_periods"],
            "first_refused_period": result["first_refused_period"],
            "reason": result["reason"],
            "end_cash_c": result["cash_c"],
            "end_headroom_c": result["headroom_c"],
            "end_f_units": last["f_units"] if last else
                           {term.sponsor_id: 0 for term in sponsors},
            "end_access_remaining": last["access_remaining"] if last else
                                    {term.sponsor_id: 0 for term in sponsors},
            "f_paid_c": {term.sponsor_id:
                         sum(row["f_payouts_c"][term.sponsor_id]
                             for row in result["trace"])
                         for term in sponsors},
            "u_paid_c": sum(row["u_payout_c"] for row in result["trace"]),
            "f_rounding_dust_c": sum(row["f_rounding_dust_c"]
                                     for row in result["trace"]),
            "access_cost_c": sum(row["access_cost_c"]
                                 for row in result["trace"]),
        }
    return {"status": "synthetic-simulation-only", "authority_effect": "none",
            "product": "Engineer Assessment reference only; no product owner approval",
            "currency": "arbitrary C units, not observed stablecoin receipts",
            "cases": results,
            "claim_ceiling": "Period-boundary arithmetic for two assumed contracts; no demand, IP title, issued F, cash movement or operating authorization."}


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
