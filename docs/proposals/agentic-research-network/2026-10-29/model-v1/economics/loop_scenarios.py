"""Synthetic Product and sponsor paths for the circular-loop hypothesis."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from loop_model import (LoopPolicy, LoopState, Period, max_safe_constant_research,
                        run)


ROOT = Path(__file__).resolve().parent


def initial(*, cash=1000, u_remaining=0, f_remaining=0) -> LoopState:
    return LoopState(cash_c=cash, research_only_c=0, service_reserve_c=0,
                     committed_unpaid_c=0,
                     w_inventory=300, w_circulating=0, w_burned=0,
                     u_remaining=u_remaining, f_remaining=f_remaining)


def policy(w_redemption="recycle", *, sponsor_participation=False) -> LoopPolicy:
    return LoopPolicy(cash_floor_c=500, w_cap=300, u_cap=300,
                      u_share_bps=2000, w_redemption=w_redemption,
                      f_cap_units=1400 if sponsor_participation else 0,
                      f_share_bps=1000 if sponsor_participation else 0,
                      sponsor_unit_price_c=1 if sponsor_participation else 0)


def recurring_period(**changes) -> Period:
    return replace(Period(product_net_c=1000, distributable_c=1000,
                          operating_c=200, service_cost_c=100,
                          service_reserve_add_c=100, research_c=400,
                          w_award=100, w_redeem=100), **changes)


def cases() -> dict[str, tuple[LoopPolicy, LoopState, list[Period]]]:
    product = recurring_period()
    downturn = recurring_period(product_net_c=600, distributable_c=600)
    no_sales = recurring_period(product_net_c=0, distributable_c=0)
    sponsor = recurring_period(product_net_c=0, distributable_c=0,
                               sponsor_unrestricted_c=700)
    sponsor_lost = replace(sponsor, sponsor_unrestricted_c=0)
    research_only = recurring_period(product_net_c=0, distributable_c=0,
                                     sponsor_research_only_c=700)
    vested_sponsor = recurring_period(product_net_c=0, distributable_c=0,
                                      sponsor_unrestricted_c=700,
                                      sponsor_vested_c=700, f_award=700)
    exited_sponsor_product = recurring_period()
    free_access_product = recurring_period(service_cost_c=250,
                                           service_reserve_add_c=250)
    exited_sponsor_no_product = recurring_period(product_net_c=0,
                                                 distributable_c=0)
    refundable_sponsor = recurring_period(product_net_c=0, distributable_c=0,
                                          sponsor_research_only_c=700,
                                          sponsor_vested_c=400, f_award=400,
                                          sponsor_refund_c=300)
    return {
        "product_recurring": (policy(), initial(), [product] * 5),
        "product_downturn": (policy(), initial(), [downturn] * 5),
        "product_no_sales": (policy(), initial(), [no_sales] * 5),
        "sponsor_recurring": (policy(), initial(u_remaining=300), [sponsor] * 5),
        "sponsor_withdrawal": (policy(), initial(u_remaining=300),
                               [sponsor] * 2 + [sponsor_lost] * 3),
        "sponsor_research_only": (policy(), initial(cash=500, u_remaining=300),
                                  [research_only] * 5),
        "product_w_burn": (policy("burn"), initial(), [product] * 5),
        "product_u_exhaustion": (policy(), initial(u_remaining=300),
                                 [replace(product, u_award=100)] * 5),
        "sponsor_vested_exit_product": (
            policy(sponsor_participation=True), initial(f_remaining=1400),
            [vested_sponsor] * 2 + [exited_sponsor_product] * 3),
        "sponsor_vested_exit_no_product": (
            policy(sponsor_participation=True), initial(f_remaining=1400),
            [vested_sponsor] * 2 + [exited_sponsor_no_product] * 3),
        "sponsor_free_access_cost": (
            policy(sponsor_participation=True), initial(f_remaining=1400),
            [vested_sponsor] * 2 + [free_access_product] * 4),
        "sponsor_pledge_cannot_vest": (
            policy(sponsor_participation=True), initial(f_remaining=1400),
            [replace(exited_sponsor_no_product, f_award=700)]),
        "sponsor_refund_unspent": (
            policy(sponsor_participation=True),
            initial(u_remaining=300, f_remaining=1400),
            [refundable_sponsor]),
    }


def report() -> dict:
    results = {}
    for name, (loop_policy, state, periods) in cases().items():
        result = run(loop_policy, state, periods)
        results[name] = {
            "periods_planned": len(periods),
            "completed_periods": result["completed_periods"],
            "first_refused_period": result["first_refused_period"],
            "reason": result["reason"],
            "end_cash_c": result["last_valid_state"]["cash_c"],
            "end_headroom_c": (result["last_valid_state"]["cash_c"]
                               - result["last_valid_state"]["research_only_c"]
                               - result["last_valid_state"]["service_reserve_c"]
                               - result["last_valid_state"]["committed_unpaid_c"]),
            "end_w_inventory": result["last_valid_state"]["w_inventory"],
            "end_w_burned": result["last_valid_state"]["w_burned"],
            "end_u_remaining": result["last_valid_state"]["u_remaining"],
            "end_f_remaining": result["last_valid_state"]["f_remaining"],
            "f_awarded_units": (state.f_remaining
                                - result["last_valid_state"]["f_remaining"]),
            "f_payout_total_c": sum(row["f_payout_c"] for row in result["trace"]),
            "sponsor_refunded_c": sum(period.sponsor_refund_c
                                      for period in periods[:result["completed_periods"]]),
        }
    product_policy, product_state, downturn = cases()["product_downturn"]
    sponsor_policy, sponsor_state, withdrawal = cases()["sponsor_withdrawal"]
    return {"status": "synthetic-simulation-only", "authority_effect": "none",
            "max_periods_planned": max(len(periods) for _, _, periods in cases().values()),
            "cash_floor_c": 500,
            "cases": results,
            "stress_budget_c_per_period": {
                "product_downturn_five_periods": max_safe_constant_research(
                    product_policy, product_state, downturn, 1000),
                "sponsor_withdrawal_five_periods": max_safe_constant_research(
                    sponsor_policy, sponsor_state, withdrawal, 1000),
            },
            "claim_ceiling": "Arithmetic and bounded-path feasibility only; no observed demand, sponsor commitment, asset value or long-run viability."}


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
