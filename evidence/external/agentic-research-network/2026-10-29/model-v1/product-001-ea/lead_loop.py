"""Deterministic, synthetic EA qualified-introduction cohort economics."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Cohort:
    assessed: int = 100
    paid_introductions: int = 30
    price_c: int = 200
    process_revenue_c: int = 0
    assessment_cost_c: int = 20
    introduction_cost_c: int = 10
    engineer_reward_c: int = 60
    locked_reserve_c: int = 10
    research_budget_c: int = 500
    fixed_overhead_c: int = 200
    alpha_bps: int = 2000
    beta_bps: int = 1000
    fulfilled_w_promotions: int = 0
    w_price_per_promotion: int = 20
    available_w_units: int = 100
    promotion_capacity: int = 5
    promotion_cost_c: int = 2


def evaluate(cohort: Cohort) -> dict:
    values = asdict(cohort)
    if any(not isinstance(v, int) or v < 0 for v in values.values()):
        raise ValueError("cohort inputs must be nonnegative integers")
    if cohort.paid_introductions > cohort.assessed:
        raise ValueError("this probe assumes at most one paid introduction per assessed engineer")
    if cohort.alpha_bps + cohort.beta_bps > 10000:
        raise ValueError("U and F shares exceed the distributable base")
    if cohort.fulfilled_w_promotions > min(cohort.promotion_capacity, cohort.assessed):
        raise ValueError("W promotion exceeds campaign capacity or assessed cohort")
    w_burned = cohort.fulfilled_w_promotions * cohort.w_price_per_promotion
    if w_burned > cohort.available_w_units:
        raise ValueError("W promotion exceeds available W")

    gross = cohort.paid_introductions * cohort.price_c + cohort.process_revenue_c
    assessment_cost = cohort.assessed * cohort.assessment_cost_c
    intro_cost = cohort.paid_introductions * cohort.introduction_cost_c
    engineer_rewards = cohort.paid_introductions * cohort.engineer_reward_c
    locked_reserve = cohort.paid_introductions * cohort.locked_reserve_c
    net = gross - assessment_cost - intro_cost - engineer_rewards - locked_reserve
    distributable = max(0, net)
    u_pool = distributable * cohort.alpha_bps // 10000
    f_pool = distributable * cohort.beta_bps // 10000
    promotion_cost = cohort.fulfilled_w_promotions * cohort.promotion_cost_c
    spendable = net - u_pool - f_pool - cohort.research_budget_c - cohort.fixed_overhead_c - promotion_cost
    return {
        "assessed": cohort.assessed,
        "paid_introductions": cohort.paid_introductions,
        "gross_realized_c": gross,
        "assessment_cost_c": assessment_cost,
        "introduction_cost_c": intro_cost,
        "engineer_rewards_c": engineer_rewards,
        "locked_reserve_c": locked_reserve,
        "net_product_contribution_c": net,
        "distributable_c": distributable,
        "u_pool_c": u_pool,
        "f_pool_c": f_pool,
        "research_budget_c": cohort.research_budget_c,
        "fixed_overhead_c": cohort.fixed_overhead_c,
        "w_promotions_fulfilled": cohort.fulfilled_w_promotions,
        "w_units_burned": w_burned,
        "w_promotion_service_cost_c": promotion_cost,
        "spendable_after_commitments_c": spendable,
        "funds_all_commitments": spendable >= 0,
        "funding_gap_c": max(0, -spendable),
    }


def minimum_introductions(cohort: Cohort) -> int | None:
    for count in range(cohort.assessed + 1):
        candidate = Cohort(**{**asdict(cohort), "paid_introductions": count})
        if evaluate(candidate)["funds_all_commitments"]:
            return count
    return None


def report() -> dict:
    base = Cohort()
    cases = {
        "thirty-introductions": base,
        "twenty-five-introductions": Cohort(**{**asdict(base), "paid_introductions": 25}),
        "ten-introductions": Cohort(**{**asdict(base), "paid_introductions": 10}),
        "process-api-only": Cohort(**{**asdict(base), "paid_introductions": 0, "process_revenue_c": 3000}),
        "five-w-promotions": Cohort(**{**asdict(base), "fulfilled_w_promotions": 5}),
    }
    return {
        "schema_version": "arn.ea-lead-loop-result/v1",
        "status": "synthetic-only",
        "authority_effect": "none",
        "assumptions": "One paid introduction at most per engineer; fully funded U/F pools; no actual buyers, engineers, payments or job outcomes.",
        "minimum_introductions_without_process_revenue": minimum_introductions(base),
        "cases": {name: {"inputs": asdict(case), "result": evaluate(case)} for name, case in cases.items()},
    }


if __name__ == "__main__":
    path = Path(__file__).resolve().parent / "fixtures/lead-loop-results.json"
    path.write_text(json.dumps(report(), indent=2, sort_keys=True) + "\n")
