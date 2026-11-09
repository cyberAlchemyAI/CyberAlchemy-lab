"""Deterministic in-memory ARN economics simulation. No signing, chain or money I/O."""

from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path


REVIEW_GATES = frozenset({
    "source_trace", "rights", "reproducibility", "independence",
    "nonduplicate", "bounded_cost",
})
ADVANCE_GATES = frozenset({
    "prior_closure", "novelty_or_new_information", "controlled_evidence",
    "reproducibility", "decision_impact", "rights", "attribution",
    "conflicts_resolved",
})


class Refusal(ValueError):
    """A candidate transition violates a model rule."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Refusal(message)


def integer(value: int, name: str, *, positive: bool = False) -> None:
    require(type(value) is int and value >= (1 if positive else 0), f"{name} must be a nonnegative integer")


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


@dataclass(frozen=True)
class Policy:
    product_ref: str
    work_asset: str
    participation_asset: str
    stablecoin_asset: str
    work_cap_units: int
    epoch_release_cap_units: int
    participation_cap_units: int
    revenue_share_bps: int
    funder_share_bps: int
    minimum_independent_reviews: int

    @classmethod
    def load(cls, path: Path) -> "Policy":
        data = json.loads(path.read_text())
        require(data["status"] == "simulation-only" and data["authority_effect"] == "none", "policy is not simulation-only")
        policy = cls(**{k: data[k] for k in cls.__dataclass_fields__})
        for key in ("work_cap_units", "epoch_release_cap_units", "participation_cap_units"):
            integer(getattr(policy, key), key, positive=True)
        integer(policy.revenue_share_bps, "revenue_share_bps")
        integer(policy.funder_share_bps, "funder_share_bps")
        require(policy.funder_share_bps == 0, "funder revenue branch is disabled in simulation")
        require(policy.revenue_share_bps + policy.funder_share_bps <= 10000, "revenue shares exceed 100%")
        require(policy.minimum_independent_reviews >= 2, "at least two independent reviewers required")
        require(len({policy.work_asset, policy.participation_asset, policy.stablecoin_asset}) == 3, "asset identities must be distinct")
        return policy


@dataclass
class Review:
    gates: dict[str, str]
    decision_resolved: bool
    quality_status: str


@dataclass
class Slot:
    miner: str | None = None
    state: str = "unassigned"
    commit: str | None = None
    content_digest: str | None = None
    collaborators: set[str] = field(default_factory=set)
    reviews: dict[str, Review] = field(default_factory=dict)
    result_sign: str | None = None
    miner_award: int = 0


@dataclass
class Task:
    epoch: str
    base: int
    bonus: int
    reviewer_fee: int
    commit_deadline: int
    reveal_deadline: int
    challenge_end: int
    slots: dict[int, Slot]
    slot_cap: int
    state: str = "offered"


class Model:
    def __init__(self, policy: Policy):
        self.policy = policy
        self.w = {"reserve": policy.work_cap_units, "burn": 0}
        self.c = {"treasury": 0}
        self.u: dict[str, int] = {"unit-reserve": policy.participation_cap_units}
        self.events: list[dict] = []
        self.event_ids: set[str] = set()
        self.nonces: set[tuple[str, int]] = set()
        self.epoch_reserved: dict[str, int] = {}
        self.epoch_spent: dict[str, int] = {}
        self.encumbered_w = 0
        self.tasks: dict[str, Task] = {}
        self.milestones: dict[str, int] = {}
        self.unit_reserved = 0
        self.advances: set[str] = set()
        self.revenue_deposits: dict[str, int] = {}
        self.settled_periods: set[str] = set()

    @staticmethod
    def commitment(task_id: str, slot: int, miner: str, content_digest: str, nonce: str) -> str:
        return digest(["arn-commit/v1", task_id, slot, miner, content_digest, nonce])

    @contextmanager
    def _atomic(self):
        snapshot = deepcopy(self.__dict__)
        try:
            yield
        except Exception:
            self.__dict__.clear()
            self.__dict__.update(snapshot)
            raise

    def _post(self, *, event_id: str, kind: str, asset: str, amount: int,
              debit: str, credit: str, ref: str, signer: str, nonce: int,
              external_deposit: bool = False) -> dict:
        with self._atomic():
            return self._post_impl(event_id=event_id, kind=kind, asset=asset,
                                   amount=amount, debit=debit, credit=credit,
                                   ref=ref, signer=signer, nonce=nonce,
                                   external_deposit=external_deposit)

    def _post_impl(self, *, event_id: str, kind: str, asset: str, amount: int,
                   debit: str, credit: str, ref: str, signer: str, nonce: int,
                   external_deposit: bool = False) -> dict:
        integer(amount, "amount", positive=True)
        integer(nonce, "nonce")
        require(event_id not in self.event_ids, "duplicate event_id")
        require((signer, nonce) not in self.nonces, "replayed signer nonce")
        require(debit != credit and debit and credit, "invalid endpoints")
        require(asset in (self.policy.work_asset, self.policy.participation_asset,
                          self.policy.stablecoin_asset), "unsupported asset")
        balances = (self.w if asset == self.policy.work_asset else
                    self.u if asset == self.policy.participation_asset else self.c)
        if asset == self.policy.participation_asset:
            require(kind == "unit-allocation" and debit == "unit-reserve" and credit != "unit-reserve", "U transfer forbidden")
        if external_deposit:
            require(asset == self.policy.stablecoin_asset and debit == "external:simulation", "invalid external deposit")
        else:
            require(debit not in ("burn", "external:simulation"), "nonspendable source")
            require(balances.get(debit, 0) >= amount, "insufficient balance")
        previous = self.events[-1]["digest"] if self.events else "GENESIS"
        event = {"event_id": event_id, "kind": kind, "asset": asset, "amount": amount,
                 "debit": debit, "credit": credit, "ref": ref, "signer": signer,
                 "nonce": nonce, "idempotency_key": event_id,
                 "decision_ref": "decision:simulation-only",
                 "previous_digest": previous}
        event["digest"] = digest(event)
        if not external_deposit:
            balances[debit] = balances.get(debit, 0) - amount
        balances[credit] = balances.get(credit, 0) + amount
        self.events.append(event)
        self.event_ids.add(event_id)
        self.nonces.add((signer, nonce))
        self.check_invariants()
        return event

    def _next_nonce(self, signer: str) -> int:
        return max((nonce for actor, nonce in self.nonces if actor == signer), default=-1) + 1

    def offer_task(self, task_id: str, epoch: str, *, slots: int, base: int, bonus: int,
                   reviewer_fee: int, commit_deadline: int, reveal_deadline: int,
                   challenge_end: int) -> None:
        require(task_id not in self.tasks, "duplicate task")
        for name, value in (("slots", slots), ("base", base), ("bonus", bonus), ("reviewer_fee", reviewer_fee)):
            integer(value, name, positive=True)
        require(0 < commit_deadline < reveal_deadline < challenge_end, "invalid deadlines")
        cap = base + bonus + self.policy.minimum_independent_reviews * reviewer_fee
        liability = slots * cap
        used = self.epoch_reserved.get(epoch, 0) + self.epoch_spent.get(epoch, 0)
        require(used + liability <= self.policy.epoch_release_cap_units, "epoch cap exceeded")
        require(self.w["reserve"] - self.encumbered_w >= liability, "unissued W reserve exhausted")
        self.epoch_reserved[epoch] = self.epoch_reserved.get(epoch, 0) + liability
        self.encumbered_w += liability
        self.tasks[task_id] = Task(epoch, base, bonus, reviewer_fee,
                                   commit_deadline, reveal_deadline, challenge_end,
                                   {i: Slot() for i in range(slots)}, cap)
        self.check_invariants()

    def assign(self, task_id: str, slot_id: int, miner: str) -> None:
        task = self.tasks[task_id]
        slot = task.slots[slot_id]
        require(task.state == "offered" and slot.state == "unassigned", "slot unavailable")
        require(miner and all(other.miner != miner for other in task.slots.values()), "miner already has a slot")
        slot.miner = miner
        slot.state = "assigned"

    def commit(self, task_id: str, slot_id: int, commitment: str, at: int) -> None:
        task, slot = self.tasks[task_id], self.tasks[task_id].slots[slot_id]
        require(slot.state == "assigned" and at <= task.commit_deadline, "commit not allowed")
        require(len(commitment) == 64, "invalid commitment digest")
        slot.commit = commitment
        slot.state = "committed"

    def reveal(self, task_id: str, slot_id: int, content_digest: str, nonce: str,
               collaborators: set[str], result_sign: str, at: int) -> None:
        task, slot = self.tasks[task_id], self.tasks[task_id].slots[slot_id]
        require(slot.state == "committed" and at <= task.reveal_deadline, "reveal not allowed")
        require(result_sign in ("positive", "negative", "null"), "unknown result sign")
        require(slot.commit == self.commitment(task_id, slot_id, slot.miner or "", content_digest, nonce), "commitment mismatch")
        slot.content_digest = content_digest
        slot.collaborators = set(collaborators)
        slot.result_sign = result_sign
        slot.state = "revealed"

    def review(self, task_id: str, slot_id: int, reviewer: str,
               gates: dict[str, str], decision_resolved: bool,
               quality_status: str) -> None:
        slot = self.tasks[task_id].slots[slot_id]
        require(slot.state in ("revealed", "reviewing"), "review not allowed")
        require(reviewer and reviewer not in ("reserve", "burn", "unit-reserve", "treasury")
                and reviewer != slot.miner and reviewer not in slot.collaborators, "conflicted reviewer")
        require(reviewer not in slot.reviews, "duplicate reviewer")
        require(set(gates) == REVIEW_GATES and all(v in ("pass", "fail", "unknown") for v in gates.values()), "invalid gate set")
        require(type(decision_resolved) is bool, "decision_resolved must be boolean")
        require(quality_status in ("pass", "fail", "unknown"), "invalid review quality status")
        slot.reviews[reviewer] = Review(dict(gates), decision_resolved, quality_status)
        slot.state = "reviewing"

    def finalize_slot(self, task_id: str, slot_id: int, *, at: int,
                      owner_decision: bool, appeal_closed: bool) -> int:
        with self._atomic():
            return self._finalize_slot_impl(task_id, slot_id, at=at,
                                            owner_decision=owner_decision,
                                            appeal_closed=appeal_closed)

    def _finalize_slot_impl(self, task_id: str, slot_id: int, *, at: int,
                            owner_decision: bool, appeal_closed: bool) -> int:
        task, slot = self.tasks[task_id], self.tasks[task_id].slots[slot_id]
        require(slot.state == "reviewing" and at >= task.challenge_end, "challenge window open")
        require(owner_decision and appeal_closed, "owner decision or appeal closure missing")
        require(len(slot.reviews) >= self.policy.minimum_independent_reviews, "insufficient independent reviews")
        selected = list(slot.reviews.items())[:self.policy.minimum_independent_reviews]
        require(all(review.quality_status == "pass" for _, review in selected), "review quality unresolved or failed")
        outcomes = [v for _, review in selected for v in review.gates.values()]
        require("unknown" not in outcomes, "unresolved review gate")
        decisions = {review.decision_resolved for _, review in selected}
        require(len(decisions) == 1, "decision resolution disputed")
        accepted = "fail" not in outcomes
        award = task.base + (task.bonus if accepted and True in decisions else 0) if accepted else 0
        total = award + len(selected) * task.reviewer_fee
        require(total <= task.slot_cap, "slot liability exceeded")
        self.encumbered_w -= task.slot_cap
        self.epoch_reserved[task.epoch] -= task.slot_cap
        self.epoch_spent[task.epoch] = self.epoch_spent.get(task.epoch, 0) + total
        if accepted:
            self._post(event_id=f"award:{task_id}:{slot_id}", kind="work-award",
                       asset=self.policy.work_asset, amount=award, debit="reserve",
                       credit=slot.miner or "", ref=task_id, signer="owner:simulation",
                       nonce=self._next_nonce("owner:simulation"))
        for reviewer, _ in selected:
            self._post(event_id=f"review-fee:{task_id}:{slot_id}:{reviewer}", kind="review-fee",
                       asset=self.policy.work_asset, amount=task.reviewer_fee,
                       debit="reserve", credit=reviewer, ref=task_id,
                       signer="owner:simulation", nonce=self._next_nonce("owner:simulation"))
        slot.miner_award = award
        slot.state = "accepted" if accepted else "rejected"
        self.check_invariants()
        return award

    def expire_slot(self, task_id: str, slot_id: int, *, at: int) -> None:
        task, slot = self.tasks[task_id], self.tasks[task_id].slots[slot_id]
        require(at > task.reveal_deadline and slot.state in ("unassigned", "assigned", "committed"), "slot cannot expire")
        self.encumbered_w -= task.slot_cap
        self.epoch_reserved[task.epoch] -= task.slot_cap
        slot.state = "expired"
        self.check_invariants()

    def transfer_w(self, sender: str, recipient: str, amount: int, *, event_id: str, nonce: int) -> None:
        require(sender not in ("reserve", "burn") and recipient not in ("reserve", "burn"), "restricted W endpoint")
        self._post(event_id=event_id, kind="transfer", asset=self.policy.work_asset,
                   amount=amount, debit=sender, credit=recipient, ref="peer-transfer",
                   signer=sender, nonce=nonce)

    def redeem_w(self, holder: str, amount: int, *, service_ref: str,
                 authorized: bool, capacity_reserved: bool, event_id: str, nonce: int) -> None:
        require(authorized and capacity_reserved and service_ref, "product access not authorized")
        require(holder not in ("reserve", "burn"), "restricted W holder")
        self._post(event_id=event_id, kind="product-redemption", asset=self.policy.work_asset,
                   amount=amount, debit=holder, credit="burn", ref=service_ref,
                   signer=holder, nonce=nonce)

    def reserve_milestone(self, milestone_id: str, max_units: int) -> None:
        integer(max_units, "max_units", positive=True)
        require(milestone_id not in self.milestones, "duplicate milestone")
        require(self.unit_reserved + max_units <= self.u["unit-reserve"], "U cap exceeded")
        self.milestones[milestone_id] = max_units
        self.unit_reserved += max_units

    def allocate_advance(self, advance_id: str, milestone_id: str,
                         shares_bps: dict[str, int], gates: dict[str, bool], *,
                         agreement_signed: bool, owner_decision: bool,
                         appeal_closed: bool) -> dict[str, int]:
        with self._atomic():
            return self._allocate_advance_impl(
                advance_id, milestone_id, shares_bps, gates,
                agreement_signed=agreement_signed, owner_decision=owner_decision,
                appeal_closed=appeal_closed)

    def _allocate_advance_impl(self, advance_id: str, milestone_id: str,
                               shares_bps: dict[str, int], gates: dict[str, bool], *,
                               agreement_signed: bool, owner_decision: bool,
                               appeal_closed: bool) -> dict[str, int]:
        require(advance_id not in self.advances, "duplicate research advance")
        require(milestone_id in self.milestones, "unreserved milestone")
        require(set(gates) == ADVANCE_GATES and all(type(v) is bool and v for v in gates.values()), "research advance gate failed or unknown")
        require(agreement_signed and owner_decision and appeal_closed, "advance rights or decision incomplete")
        require(shares_bps and all(name and name != "unit-reserve" and type(bps) is int
                                   and 0 <= bps <= 10000 for name, bps in shares_bps.items()), "invalid attribution shares")
        require(sum(shares_bps.values()) <= 10000, "attribution exceeds 100%")
        cap = self.milestones.pop(milestone_id)
        self.unit_reserved -= cap
        awards = {name: cap * bps // 10000 for name, bps in shares_bps.items()}
        for name, units in awards.items():
            if units:
                self._post(event_id=f"unit:{advance_id}:{name}", kind="unit-allocation",
                           asset=self.policy.participation_asset, amount=units,
                           debit="unit-reserve", credit=name, ref=advance_id,
                           signer="owner:simulation", nonce=self._next_nonce("owner:simulation"))
        self.advances.add(advance_id)
        self.check_invariants()
        return awards

    def transfer_u(self, *_args, **_kwargs) -> None:
        raise Refusal("U is nontransferable")

    def deposit_revenue(self, period: str, amount: int, *, source_kind: str,
                        event_id: str, nonce: int) -> None:
        require(source_kind in ("product-receipts", "licensed-ip"), "funding and token sales are excluded from revenue")
        self._post(event_id=event_id, kind="eligible-revenue-deposit",
                   asset=self.policy.stablecoin_asset, amount=amount,
                   debit="external:simulation", credit="treasury", ref=period,
                   signer="treasury:simulation", nonce=nonce, external_deposit=True)
        self.revenue_deposits[period] = self.revenue_deposits.get(period, 0) + amount

    def settle_revenue(self, period: str, *, gross: int, refunds: int, taxes: int,
                       fees: int, direct_costs: int, reserves: int, exclusions: int,
                       active_units: dict[str, int], audited: bool, agreements_active: bool,
                       payment_finality_confirmed: bool) -> dict:
        with self._atomic():
            return self._settle_revenue_impl(
                period, gross=gross, refunds=refunds, taxes=taxes, fees=fees,
                direct_costs=direct_costs, reserves=reserves, exclusions=exclusions,
                active_units=active_units,
                audited=audited, agreements_active=agreements_active,
                payment_finality_confirmed=payment_finality_confirmed)

    def _settle_revenue_impl(self, period: str, *, gross: int, refunds: int, taxes: int,
                             fees: int, direct_costs: int, reserves: int, exclusions: int,
                             active_units: dict[str, int], audited: bool,
                             agreements_active: bool,
                             payment_finality_confirmed: bool) -> dict:
        require(period not in self.settled_periods, "period already settled")
        for name, value in (("gross", gross), ("refunds", refunds), ("taxes", taxes),
                            ("fees", fees), ("direct_costs", direct_costs),
                            ("reserves", reserves), ("exclusions", exclusions)):
            integer(value, name)
        require(gross <= self.revenue_deposits.get(period, 0), "gross exceeds eligible receipt deposits")
        require(audited and agreements_active and payment_finality_confirmed, "settlement authorization or finality missing")
        require(all(name != "unit-reserve" and type(units) is int and
                    0 <= units <= self.u.get(name, 0)
                    for name, units in active_units.items()), "invalid active unit snapshot")
        distributable = max(0, gross - refunds - taxes - fees - direct_costs - reserves - exclusions)
        pool = distributable * self.policy.revenue_share_bps // 10000
        payouts = {name: pool * units // self.policy.participation_cap_units
                   for name, units in sorted(active_units.items()) if units > 0}
        paid = sum(payouts.values())
        require(paid <= pool and self.c["treasury"] >= paid, "treasury or pool insufficient")
        for name, amount in payouts.items():
            if amount:
                self._post(event_id=f"settle:{period}:{name}", kind="stablecoin-settlement",
                           asset=self.policy.stablecoin_asset, amount=amount,
                           debit="treasury", credit=name, ref=period,
                           signer="treasury:simulation", nonce=self._next_nonce("treasury:simulation"))
        self.settled_periods.add(period)
        return {"period": period, "distributable": distributable, "pool": pool,
                "payouts": payouts, "unallocated": pool - paid}

    def check_invariants(self) -> None:
        require(all(type(value) is int and value >= 0 for value in self.w.values()), "negative W balance")
        require(all(type(value) is int and value >= 0 for value in self.u.values()), "negative U balance")
        require(all(type(value) is int and value >= 0 for value in self.c.values()), "negative C balance")
        require(sum(self.w.values()) == self.policy.work_cap_units, "W conservation failed")
        require(self.encumbered_w >= 0 and self.encumbered_w <= self.w["reserve"], "W reservation failed")
        require(sum(self.u.values()) == self.policy.participation_cap_units, "U conservation failed")
        require(0 <= self.unit_reserved <= self.u["unit-reserve"], "U reservation failed")
        require(all(self.epoch_spent.get(e, 0) + self.epoch_reserved.get(e, 0) <= self.policy.epoch_release_cap_units
                    for e in set(self.epoch_spent) | set(self.epoch_reserved)), "epoch cap failed")
        previous = "GENESIS"
        for event in self.events:
            require(event["previous_digest"] == previous, "event chain broken")
            body = {k: v for k, v in event.items() if k != "digest"}
            require(event["digest"] == digest(body), "event digest broken")
            previous = event["digest"]


if __name__ == "__main__":
    policy = Policy.load(Path(__file__).with_name("simulation-policy.json"))
    print(f"ARN simulation policy loaded for {policy.product_ref}; no assets or funds created.")
