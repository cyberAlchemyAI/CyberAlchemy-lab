use domainspec_architecture_conformance_rust::remaining_types::query_v1::{
    BoundQuery, CompleteSettlementInput, CompleteSettlementReadPort,
    CompleteSettlementView, PayoutRecord, SettlementRecord,
    COMPLETE_SETTLEMENT_QUERY, PAYOUT_BY_SETTLEMENT_TARGET,
    SETTLEMENT_BY_ID_TARGET,
};

#[derive(Default)]
struct OwnerReadFixture {
    trace: Vec<(&'static str, String)>,
}

impl CompleteSettlementReadPort for OwnerReadFixture {
    fn read_settlement_by_id(
        &mut self,
        target_id: &'static str,
        settlement_id: &str,
    ) -> SettlementRecord {
        self.trace.push((target_id, settlement_id.to_owned()));
        SettlementRecord {
            settlement_id: settlement_id.to_owned(),
            settlement_status: "complete".to_owned(),
            gross_amount_minor: 125_000,
        }
    }

    fn read_payout_by_settlement(
        &mut self,
        target_id: &'static str,
        settlement_id: &str,
    ) -> PayoutRecord {
        self.trace.push((target_id, settlement_id.to_owned()));
        PayoutRecord {
            payout_id: "payout-001".to_owned(),
            payout_status: "recorded".to_owned(),
        }
    }
}

fn assert_bound_query(query: BoundQuery) -> BoundQuery {
    query
}

#[test]
fn query_v1_reads_the_exact_owner_targets_in_order_and_returns_the_closed_view() {
    let query = assert_bound_query(COMPLETE_SETTLEMENT_QUERY);
    let mut reads = OwnerReadFixture::default();
    let result = query(
        &CompleteSettlementInput {
            settlement_id: "settlement-001",
        },
        &mut reads,
    );

    assert_eq!(
        reads.trace,
        vec![
            (
                SETTLEMENT_BY_ID_TARGET,
                "settlement-001".to_owned(),
            ),
            (
                PAYOUT_BY_SETTLEMENT_TARGET,
                "settlement-001".to_owned(),
            ),
        ]
    );
    assert_eq!(
        result,
        CompleteSettlementView {
            settlement_id: "settlement-001".to_owned(),
            settlement_status: "complete".to_owned(),
            gross_amount_minor: 125_000,
            payout_id: "payout-001".to_owned(),
            payout_status: "recorded".to_owned(),
        }
    );
}

#[test]
fn query_v1_is_a_copyable_typed_function_item_binding() {
    let first = COMPLETE_SETTLEMENT_QUERY;
    let second = first;
    let mut first_reads = OwnerReadFixture::default();
    let mut second_reads = OwnerReadFixture::default();
    let input = CompleteSettlementInput {
        settlement_id: "settlement-001",
    };

    assert_eq!(first(&input, &mut first_reads), second(&input, &mut second_reads));
    assert_eq!(first_reads.trace, second_reads.trace);
}
