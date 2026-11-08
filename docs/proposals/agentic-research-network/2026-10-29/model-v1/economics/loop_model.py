"""Synthetic cash-and-asset loop model. No chain, custody, signing or money I/O."""

from __future__ import annotations

from dataclasses import dataclass, replace


class LoopRefusal(ValueError):
    """A synthetic period cannot honor its cash or asset commitments."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise LoopRefusal(reason)


@dataclass(frozen=True)
class LoopPolicy:
    cash_floor_c: int
    w_cap: int
    u_cap: int
    u_share_bps: int
    w_redemption: str  # burn or recycle
    f_cap_units: int = 0
    f_share_bps: int = 0
    sponsor_unit_price_c: int = 0

    def validate(self) -> None:
        for name in ("cash_floor_c", "w_cap", "u_cap", "u_share_bps",
                     "f_cap_units", "f_share_bps", "sponsor_unit_price_c"):
            value = getattr(self, name)
            require(type(value) is int and value >= 0, f"invalid-policy:{name}")
        require(self.w_cap > 0 and self.u_cap > 0, "invalid-policy:cap")
        require(self.u_share_bps + self.f_share_bps <= 10000,
                "invalid-policy:combined-share")
        require((self.f_cap_units == 0 and self.f_share_bps == 0
                 and self.sponsor_unit_price_c == 0) or
                (self.f_cap_units > 0 and self.f_share_bps > 0
                 and self.sponsor_unit_price_c > 0), "invalid-policy:sponsor-instrument")
        require(self.w_redemption in ("burn", "recycle"), "invalid-policy:w-redemption")


@dataclass(frozen=True)
class LoopState:
    cash_c: int
    research_only_c: int
    service_reserve_c: int
    committed_unpaid_c: int
    w_inventory: int
    w_circulating: int
    w_burned: int
    u_remaining: int
    f_remaining: int = 0

    @property
    def headroom_c(self) -> int:
        return (self.cash_c - self.research_only_c - self.service_reserve_c
                - self.committed_unpaid_c)


@dataclass(frozen=True)
class Period:
    product_net_c: int = 0  # signed, after actual direct Product costs
    distributable_c: int = 0
    sponsor_unrestricted_c: int = 0
    sponsor_research_only_c: int = 0
    sponsor_vested_c: int = 0  # cleared, nonrefundable funding eligible for F
    sponsor_refund_c: int = 0  # return of unspent research-only cash
    operating_c: int = 0  # includes Product development not in product_net_c
    other_loss_c: int = 0
    service_cost_c: int = 0
    service_reserve_add_c: int = 0
    research_c: int = 0
    w_award: int = 0
    w_redeem: int = 0
    u_award: int = 0  # first eligible for payout in the next period
    f_award: int = 0  # first eligible for payout in the next period


@dataclass(frozen=True)
class PeriodResult:
    state: LoopState
    u_payout_c: int
    f_payout_c: int
    research_from_sponsor_c: int


def validate_state(policy: LoopPolicy, state: LoopState) -> None:
    policy.validate()
    for name in state.__dataclass_fields__:
        value = getattr(state, name)
        require(type(value) is int and value >= 0, f"invalid-state:{name}")
    require(state.w_inventory + state.w_circulating + state.w_burned == policy.w_cap,
            "w-conservation")
    require(state.u_remaining <= policy.u_cap, "u-cap")
    require(state.f_remaining <= policy.f_cap_units, "f-cap")
    require(state.headroom_c >= policy.cash_floor_c, "cash-floor")


def step(policy: LoopPolicy, state: LoopState, period: Period) -> PeriodResult:
    """Apply cleared receipts before costs; reject atomically on any failed gate."""
    validate_state(policy, state)
    for name in period.__dataclass_fields__:
        value = getattr(period, name)
        require(type(value) is int, f"invalid-period:{name}")
        if name != "product_net_c":
            require(value >= 0, f"invalid-period:{name}")
    require(period.distributable_c <= max(0, period.product_net_c),
            "distributable-exceeds-product-net")
    require(period.w_award <= state.w_inventory, "w-reward-inventory-exhausted")
    require(period.w_redeem <= state.w_circulating + period.w_award,
            "w-redemption-exceeds-circulation")
    require(period.u_award <= state.u_remaining, "u-allocation-cap-exhausted")
    require(period.f_award <= state.f_remaining, "f-allocation-cap-exhausted")

    service_reserve = state.service_reserve_c + period.service_reserve_add_c
    require(period.service_cost_c <= service_reserve, "service-reserve-insufficient")
    research_only = state.research_only_c + period.sponsor_research_only_c
    research_from_sponsor = min(research_only, period.research_c)
    refundable_research = research_only - research_from_sponsor
    require(period.sponsor_refund_c <= refundable_research,
            "sponsor-refund-exceeds-unspent-restricted")
    require(period.sponsor_vested_c <= (period.sponsor_unrestricted_c
                                        + research_from_sponsor),
            "sponsor-vesting-exceeds-eligible-cleared")
    require(period.f_award * policy.sponsor_unit_price_c
            <= period.sponsor_vested_c, "f-award-exceeds-vested-funding")
    u_issued_at_period_start = policy.u_cap - state.u_remaining
    u_pool = policy.u_share_bps * period.distributable_c // 10000
    # Upper bound on aggregate holder payouts; individual rounding can retain dust.
    u_payout = u_pool * u_issued_at_period_start // policy.u_cap
    f_issued_at_period_start = policy.f_cap_units - state.f_remaining
    f_pool = policy.f_share_bps * period.distributable_c // 10000
    f_payout = (f_pool * f_issued_at_period_start // policy.f_cap_units
                if policy.f_cap_units else 0)

    cash = (state.cash_c + period.product_net_c + period.sponsor_unrestricted_c
            + period.sponsor_research_only_c - u_payout - f_payout
            - period.operating_c - period.service_cost_c - period.research_c
            - period.other_loss_c - period.sponsor_refund_c)
    new_state = LoopState(
        cash_c=cash,
        research_only_c=refundable_research - period.sponsor_refund_c,
        service_reserve_c=service_reserve - period.service_cost_c,
        committed_unpaid_c=state.committed_unpaid_c,
        w_inventory=(state.w_inventory - period.w_award
                     + (period.w_redeem if policy.w_redemption == "recycle" else 0)),
        w_circulating=state.w_circulating + period.w_award - period.w_redeem,
        w_burned=(state.w_burned + period.w_redeem
                  if policy.w_redemption == "burn" else state.w_burned),
        u_remaining=state.u_remaining - period.u_award,
        f_remaining=state.f_remaining - period.f_award,
    )
    validate_state(policy, new_state)
    return PeriodResult(new_state, u_payout, f_payout, research_from_sponsor)


def run(policy: LoopPolicy, initial: LoopState, periods: list[Period]) -> dict:
    """Return the first refusal and last valid state, with no partial period effects."""
    state = initial
    validate_state(policy, state)
    traces = []
    for index, period in enumerate(periods, start=1):
        try:
            result = step(policy, state, period)
        except LoopRefusal as error:
            return {"completed_periods": len(traces), "first_refused_period": index,
                    "reason": str(error), "last_valid_state": state.__dict__,
                    "trace": traces}
        state = result.state
        traces.append({"period": index, "cash_c": state.cash_c,
                       "headroom_c": state.headroom_c,
                       "u_payout_c": result.u_payout_c,
                       "f_payout_c": result.f_payout_c,
                       "sponsor_research_spent_c": result.research_from_sponsor_c,
                       "w_inventory": state.w_inventory,
                       "w_burned": state.w_burned,
                       "u_remaining": state.u_remaining})
        traces[-1]["f_remaining"] = state.f_remaining
    return {"completed_periods": len(traces), "first_refused_period": None,
            "reason": None, "last_valid_state": state.__dict__, "trace": traces}


def max_safe_constant_research(policy: LoopPolicy, initial: LoopState,
                               periods: list[Period], upper_bound_c: int) -> int | None:
    """Largest constant per-period X that survives this finite disclosed path."""
    require(type(upper_bound_c) is int and upper_bound_c >= 0, "invalid-upper-bound")

    def survives(amount: int) -> bool:
        trial = [replace(period, research_c=amount) for period in periods]
        return run(policy, initial, trial)["first_refused_period"] is None

    if not survives(0):
        return None
    low, high = 0, upper_bound_c
    while low < high:
        middle = (low + high + 1) // 2
        if survives(middle):
            low = middle
        else:
            high = middle - 1
    return low
