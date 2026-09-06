def complete_settlement_operation(input_data, ports):
    if "s1_residue" in input_data:
        observed = input_data["s1_residue"]
        scenario = observed["scenario"]
        code = None
        coherent = False
        transaction_present = (
            observed["transaction_id"] is not None
            and observed["transaction_id"] != ""
        )
        occurrence_present = (
            observed["occurrence_id"] is not None
            and observed["occurrence_id"] != ""
        )

        if scenario == "normal":
            coherent = (
                transaction_present
                and occurrence_present
                and observed["state_write_attempted"]
                and observed["outbox_append_attempted"]
                and observed["outbox_checkpoint_observed"]
                and not observed["transaction_aborted"]
                and observed["state_durable"]
                and observed["outbox_occurrence_durable"]
                and observed["commit_observed"]
                and not observed["rollback_requested"]
                and not observed["history_erased"]
                and not observed["forward_recovery_required"]
                and not observed["closed_rejection"]
            )
        elif scenario == "before-state-write-failure":
            code = "RMT_S1_BEFORE_STATE_WRITE_FAILURE"
            coherent = (
                transaction_present
                and not occurrence_present
                and observed["state_write_attempted"]
                and not observed["outbox_append_attempted"]
                and not observed["outbox_checkpoint_observed"]
                and observed["transaction_aborted"]
                and not observed["state_durable"]
                and not observed["outbox_occurrence_durable"]
                and not observed["commit_observed"]
                and not observed["history_erased"]
                and observed["closed_rejection"]
            )
        elif scenario == "between-state-and-outbox-failure":
            code = "RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH"
            coherent = (
                transaction_present
                and occurrence_present
                and observed["state_write_attempted"]
                and not observed["outbox_append_attempted"]
                and not observed["outbox_checkpoint_observed"]
                and observed["transaction_aborted"]
                and not observed["state_durable"]
                and not observed["outbox_occurrence_durable"]
                and not observed["commit_observed"]
                and not observed["history_erased"]
                and observed["closed_rejection"]
            )
        elif scenario == "missing-member":
            code = "RMT_S1_MISSING_MEMBER"
            coherent = (
                (not transaction_present or not occurrence_present)
                and not observed["state_write_attempted"]
                and not observed["outbox_append_attempted"]
                and not observed["outbox_checkpoint_observed"]
                and observed["transaction_aborted"]
                and not observed["state_durable"]
                and not observed["outbox_occurrence_durable"]
                and not observed["commit_observed"]
                and observed["closed_rejection"]
            )
        elif scenario == "mixed-commit":
            code = "RMT_S1_MIXED_COMMIT"
            coherent = (
                observed["state_durable"]
                != observed["outbox_occurrence_durable"]
                and observed["state_write_attempted"]
                and observed["outbox_append_attempted"]
                and not observed["outbox_checkpoint_observed"]
                and not observed["history_erased"]
                and observed["closed_rejection"]
            )
        elif scenario == "rollback-after-commit":
            code = "RMT_S1_ROLLBACK_AFTER_COMMIT"
            coherent = (
                observed["commit_observed"]
                and observed["state_durable"]
                and observed["outbox_occurrence_durable"]
                and observed["rollback_requested"]
                and observed["state_write_attempted"]
                and observed["outbox_append_attempted"]
                and observed["outbox_checkpoint_observed"]
                and not observed["history_erased"]
                and observed["forward_recovery_required"]
                and observed["closed_rejection"]
            )

        if not coherent:
            code = "RMT_OP_S1_RESIDUE_INCOHERENT"
        return {
            "kind": "failure" if code is not None else "success",
            "value": None,
            "failure_code": code,
            "exactly_once_distributed_delivery_claimed": False,
        }

    guard = ports["guard"]("rule.can-settle-payout", input_data)
    if not guard["allowed"]:
        ports["close"](
            "return-await-cancel-close-dispose-finalizer-quiescence",
            "guard-rejected",
        )
        return {
            "kind": "failure",
            "value": None,
            "failure_code": "guard-rejected",
            "exactly_once_distributed_delivery_claimed": False,
        }

    try:
        settlement = ports["read"](
            "settlement.read.settlement-by-id",
            input_data["settlement_id"],
        )
        payout_account = ports["read"](
            "settlement.read.payout-account",
            input_data["settlement_id"],
        )
    except Exception:
        ports["close"](
            "return-await-cancel-close-dispose-finalizer-quiescence",
            "read-failed",
        )
        return {
            "kind": "failure",
            "value": None,
            "failure_code": "read-failed",
            "exactly_once_distributed_delivery_claimed": False,
        }

    transaction = ports["begin_atomic"]()
    payout_id = (
        f'{payout_account["account_id"]}:{settlement["settlement_id"]}'
    )
    try:
        transaction["write"](
            "settlement.write.payout-record",
            {
                "settlement_id": input_data["settlement_id"],
                "payout_id": payout_id,
            },
        )
        transaction["write"](
            "settlement.write.settlement-status",
            {
                "settlement_id": input_data["settlement_id"],
                "status": "committed",
            },
        )
        transaction["commit"]("all-or-nothing")
    except Exception:
        transaction["rollback"]()
        ports["close"](
            "return-await-cancel-close-dispose-finalizer-quiescence",
            "write-failed",
        )
        return {
            "kind": "failure",
            "value": None,
            "failure_code": "write-failed",
            "exactly_once_distributed_delivery_claimed": False,
        }

    try:
        ports["external_effect"](
            "event-store.append.PayoutCreated",
            {
                "event_type": "PayoutCreated",
                "settlement_id": input_data["settlement_id"],
                "payout_id": payout_id,
            },
        )
    except Exception:
        ports["close"](
            "return-await-cancel-close-dispose-finalizer-quiescence",
            "effect-failed",
        )
        return {
            "kind": "failure",
            "value": None,
            "failure_code": "effect-failed",
            "exactly_once_distributed_delivery_claimed": False,
        }

    ports["close"](
        "return-await-cancel-close-dispose-finalizer-quiescence",
        None,
    )
    return {
        "kind": "success",
        "value": {
            "settlement_id": input_data["settlement_id"],
            "payout_id": payout_id,
            "status": "committed",
        },
        "failure_code": None,
        "exactly_once_distributed_delivery_claimed": False,
    }
