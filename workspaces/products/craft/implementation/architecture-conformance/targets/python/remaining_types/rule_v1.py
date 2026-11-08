from __future__ import annotations

from fixtures.can_settle_payout import can_settle_payout


RULE_V1_DELEGATE = {
    "rule_id": "can-settle-payout",
    "realization_id": "rule.python.function-v1",
    "provider_id": "python-rule-v1",
    "authority_effect": "none",
}


def evaluate_rule_v1(input_data: dict[str, str | int | None]) -> bool:
    return can_settle_payout(input_data)
