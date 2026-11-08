"""Deterministic candidate sponsor ledger; no contracts, custody or token effects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


class Refusal(ValueError):
    """A synthetic period cannot meet a declared entitlement or cash gate."""


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise Refusal(reason)


@dataclass(frozen=True)
class SponsorTerms:
    sponsor_id: str
    f_limit: int
    c_per_f: int
    access_cap: int = 0
    c_per_access: int = 0
    access_cost_c: int = 0
    license_kind: str = "none"  # none, nonexclusive, exclusive-field, assignment
    rights_cleared: bool = False
    product_sales_retained: bool = True


@dataclass(frozen=True)
class Policy:
    floor_c: int
    f_cap: int
    u_share_bps: int
    f_share_bps: int


@dataclass(frozen=True)
class Account:
    pending_refundable_c: int = 0
    vested_c: int = 0
    f_units: int = 0
    access_entitled: int = 0
    access_used: int = 0


@dataclass(frozen=True)
class State:
    cash_c: int
    accounts: Mapping[str, Account]


@dataclass(frozen=True)
class Period:
    product_net_c: int = 0
    distributable_c: int = 0
    deposits_c: Mapping[str, int] | None = None
    vest_c: Mapping[str, int] | None = None
    refunds_c: Mapping[str, int] | None = None
    access_use: Mapping[str, int] | None = None
    operating_c: int = 200
    research_c: int = 400
    w_service_c: int = 100


def validate(policy: Policy, terms: tuple[SponsorTerms, ...], state: State) -> None:
    require(policy.floor_c >= 0 and policy.f_cap > 0, "invalid-policy-cap")
    require(0 <= policy.u_share_bps <= 10000 and 0 <= policy.f_share_bps <= 10000
            and policy.u_share_bps + policy.f_share_bps <= 10000,
            "invalid-combined-share")
    ids = [term.sponsor_id for term in terms]
    require(len(ids) == len(set(ids)) and set(ids) == set(state.accounts),
            "sponsor-identity-mismatch")
    require(sum(term.f_limit for term in terms) <= policy.f_cap,
            "f-reservation-exceeds-cap")
    for term in terms:
        require(term.f_limit >= 0 and term.c_per_f > 0 and term.access_cap >= 0
                and term.access_cost_c >= 0, "invalid-sponsor-terms")
        require((term.access_cap == 0 and term.c_per_access == 0)
                or (term.access_cap > 0 and term.c_per_access > 0),
                "invalid-access-terms")
        require(term.license_kind in ("none", "nonexclusive", "exclusive-field",
                                      "assignment"), "invalid-license-kind")
        account = state.accounts[term.sponsor_id]
        require(all(type(value) is int and value >= 0
                    for value in account.__dict__.values()), "invalid-account")
        require(account.f_units <= term.f_limit and
                account.f_units <= account.vested_c // term.c_per_f,
                "unbacked-f-units")
        expected_access = (min(term.access_cap,
                               account.vested_c // term.c_per_access)
                           if term.access_cap else 0)
        require(account.access_entitled == expected_access and
                account.access_used <= account.access_entitled,
                "unbacked-access")
    require(state.cash_c >= 0 and headroom(state, terms) >= policy.floor_c,
            "cash-floor")


def headroom(state: State, terms: tuple[SponsorTerms, ...]) -> int:
    by_id = {term.sponsor_id: term for term in terms}
    pending = sum(account.pending_refundable_c for account in state.accounts.values())
    access_reserve = sum((account.access_entitled - account.access_used)
                         * by_id[sid].access_cost_c
                         for sid, account in state.accounts.items())
    return state.cash_c - pending - access_reserve


def step(policy: Policy, terms: tuple[SponsorTerms, ...], state: State,
         period: Period) -> tuple[State, dict]:
    validate(policy, terms, state)
    require(type(period.product_net_c) is int and
            0 <= period.distributable_c <= max(0, period.product_net_c),
            "invalid-product-receipt")
    require(all(type(v) is int and v >= 0 for v in
                (period.operating_c, period.research_c, period.w_service_c)),
            "invalid-period-cost")
    term_by_id = {term.sponsor_id: term for term in terms}
    transfers = (period.deposits_c or {}, period.vest_c or {},
                 period.refunds_c or {}, period.access_use or {})
    for transfer in transfers:
        require(set(transfer) <= set(term_by_id) and
                all(type(value) is int and value >= 0 for value in transfer.values()),
                "invalid-sponsor-event")

    # The opening snapshot receives Product distributions. Current vesting earns
    # units for the next period; unissued units receive nothing.
    u_payout = policy.u_share_bps * period.distributable_c // 10000
    f_pool = policy.f_share_bps * period.distributable_c // 10000
    payouts = {sid: f_pool * account.f_units // policy.f_cap
               for sid, account in state.accounts.items()}
    aggregate_entitled = (f_pool * sum(a.f_units for a in state.accounts.values())
                          // policy.f_cap)
    dust = aggregate_entitled - sum(payouts.values())
    require(dust >= 0, "invalid-rounding")

    accounts = dict(state.accounts)
    for term in terms:
        sid = term.sponsor_id
        old = accounts[sid]
        pending = old.pending_refundable_c + (period.deposits_c or {}).get(sid, 0)
        vest = (period.vest_c or {}).get(sid, 0)
        refund = (period.refunds_c or {}).get(sid, 0)
        require(vest + refund <= pending, "vest-or-refund-exceeds-cleared")
        require(vest == 0 or term.license_kind == "none" or term.rights_cleared,
                "ip-rights-not-cleared")
        vested = old.vested_c + vest
        issued = min(term.f_limit, vested // term.c_per_f)
        access = (min(term.access_cap, vested // term.c_per_access)
                  if term.access_cap else 0)
        use = (period.access_use or {}).get(sid, 0)
        require(old.access_used + use <= access, "access-quota-exceeded")
        accounts[sid] = Account(pending - vest - refund, vested, issued,
                                access, old.access_used + use)

    if period.product_net_c:
        require(all(term.product_sales_retained or
                    accounts[term.sponsor_id].vested_c == 0
                    for term in terms), "product-revenue-rights-lost")
    access_cost = sum((period.access_use or {}).get(term.sponsor_id, 0)
                      * term.access_cost_c for term in terms)
    cash = (state.cash_c + period.product_net_c
            + sum((period.deposits_c or {}).values())
            - sum((period.refunds_c or {}).values())
            - u_payout - sum(payouts.values()) - period.operating_c
            - period.research_c - period.w_service_c - access_cost)
    next_state = State(cash, accounts)
    validate(policy, terms, next_state)
    return next_state, {"cash_c": cash, "headroom_c": headroom(next_state, terms),
                        "u_payout_c": u_payout, "f_payouts_c": payouts,
                        "f_rounding_dust_c": dust,
                        "access_cost_c": access_cost,
                        "f_units": {sid: account.f_units
                                    for sid, account in accounts.items()},
                        "access_remaining": {
                            sid: account.access_entitled - account.access_used
                            for sid, account in accounts.items()}}


def run(policy: Policy, terms: tuple[SponsorTerms, ...], initial: State,
        periods: list[Period]) -> dict:
    validate(policy, terms, initial)
    state, trace = initial, []
    for index, period in enumerate(periods, 1):
        try:
            state, row = step(policy, terms, state, period)
        except Refusal as error:
            return {"completed_periods": len(trace), "first_refused_period": index,
                    "reason": str(error), "cash_c": state.cash_c,
                    "headroom_c": headroom(state, terms), "trace": trace}
        trace.append({"period": index, **row})
    return {"completed_periods": len(trace), "first_refused_period": None,
            "reason": None, "cash_c": state.cash_c,
            "headroom_c": headroom(state, terms), "trace": trace}
