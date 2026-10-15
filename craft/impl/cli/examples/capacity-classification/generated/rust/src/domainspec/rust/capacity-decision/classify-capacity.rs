// domainspec-meta: {"baseline_digest":"bfbc335d151ab8b29150dc95f246c2bc0954cff179ece5ce51222b2d1455abda","baseline_id":"domainspec-meta-types-current-implemented@10","binding_sha256":"9bb380f5f1825b447477b3f9b0cf9281168e7904f343153b755bfa01d8cd80c2","language":"rust","meta_type_id":"DS-D1.6","meta_type_label":"Calculation","provider_sha256":"33f75aba66ab47675fa13efb86665eac295bedd9d017c1037b4e3a4e76942869","source_sha256":"560fc36e55619c449b0861c833f39ee4cc7d09a99ab889cf4d27e90516854fe8"}
// domainspec-body: {"description":"Classify a supplied snapshot: Accept when requested units are strictly below available units; otherwise Reject. This pure derivation reserves no capacity.","inputs":["snapshot"],"typed_contract":{"expression":{"condition":{"arguments":[{"parameter":"snapshot","value":{"op":"path","properties":[],"root":"snapshot"}}],"op":"rule_ref","selector":"capacity-decision:within-capacity"},"else":{"payload":null,"variant":"Reject"},"op":"if","then":{"payload":null,"variant":"Accept"}},"inputs":[{"name":"snapshot","type":{"kind":"named","selector":"capacity-decision:capacity-snapshot"}}],"ontology_calculation":"CAPACITY-CALC-CLASSIFY","result":{"kind":"named","selector":"capacity-decision:capacity-decision"},"schema_version":"domainspec.typed-calculation/v2"}}
// domainspec-relationships: []
// domainspec-calculation-semantics: "domainspec.typed-calculation/v2"
// domainspec-typed-closure-sha256: "05dbda85a04b79e541da93324fdecd6dc0b8590417b88c805b1ac4116b97a41c"
pub const DOMAINSPEC_TYPED_CLOSURE_SHA256: &str =
    "05dbda85a04b79e541da93324fdecd6dc0b8590417b88c805b1ac4116b97a41c";
#[rustfmt::skip]
pub const DOMAINSPEC_PROPERTY_BINDINGS: &[(&str, &str)] = &[
    ("CAPACITY-SNAPSHOT#available_units", "CapacitySnapshot::available_units"),
    ("CAPACITY-SNAPSHOT#request_id", "CapacitySnapshot::request_id"),
    ("CAPACITY-SNAPSHOT#requested_units", "CapacitySnapshot::requested_units"),
];
#[rustfmt::skip]
pub const DOMAINSPEC_VARIANT_BINDINGS: &[(&str, &str)] = &[
    ("CAPACITY-DECISION#Accept", "CapacityDecision::Accept"),
    ("CAPACITY-DECISION#Reject", "CapacityDecision::Reject"),
];
#[rustfmt::skip]
pub const DOMAINSPEC_RULE_SELECTORS: &[(&str, &str)] = &[
    ("CAPACITY-RULE-WITHIN-AVAILABLE", "capacity-decision:within-capacity"),
];
#[rustfmt::skip]
pub const DOMAINSPEC_RULE_IMPLEMENTATION_BINDINGS: &[(&str, &str, &str)] = &[
    ("CAPACITY-RULE-WITHIN-AVAILABLE", "capacity-decision:within-capacity", "within_capacity"),
];

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum CapacityDecision {
    Accept,
    Reject,
}

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct CapacitySnapshot {
    pub request_id: String,
    pub requested_units: u64,
    pub available_units: u64,
}

#[rustfmt::skip]
pub fn within_capacity(snapshot: &CapacitySnapshot) -> bool {
    snapshot.requested_units < snapshot.available_units
}

pub fn classify_capacity(snapshot: &CapacitySnapshot) -> CapacityDecision {
    if within_capacity(snapshot) {
        CapacityDecision::Accept
    } else {
        CapacityDecision::Reject
    }
}
