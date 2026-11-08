/** Checked C12 Event handoff data. Source, profile, Auth, storage, and relay
 * owners must recheck these closed values before effects. No caller supplies an
 * occurrence or receiver credential.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import type {ValueTypeV1} from '../commerce/commerce-data-v1.js';
import type {GenericKeyedRoleExpressionV1,GenericLogicalEntryV1} from './query-data-v1.js';
import type {GenericRootCommandTupleV1,GenericTransactionApplicationContractV1,GenericTransactionEntryV1,GenericTransactionPlanV1,GenericTransactionSourceSiteV1,GenericTransactionStepV1,GenericStatefulControlV1} from './transaction-data-v1.js';
import type {GenericExternalCheckedBindingV1} from './external-read-data-v1.js';
import type {GenericExternalWriteCheckedBindingV1,GenericExternalWritePreflightStepV1,GenericExternalWriteSelectionV1,GenericExternalEffectTupleV1} from './external-write-data-v1.js';

export interface GenericEventBindingV1 {
 readonly id:string;
 readonly event_selector:string;
 readonly event_version:1;
 readonly producer_service:string;
 readonly producer_operation:string;
 readonly payload_type:ValueTypeV1;
 readonly payload_schema_sha256:string;
 readonly target_service:string;
 readonly target_entry:string;
 readonly target_route:string;
 readonly target_permission:Readonly<{permission:string;resource:string;action:string;scope:string}>;
 readonly consumer_operation:string;
 readonly consumer_mapping:string;
 readonly event_source_site:string;
}

/** The Event receiver's original root identity is service-scoped. V1–V3
 * customer tuples retain their exact existing discriminant and encoding. */
export interface GenericEventServiceRootCommandTupleV2 extends Omit<GenericRootCommandTupleV1,'schema_version'|'principal'> {
 readonly schema_version:'craft.generic-root-command/v2-candidate';
 readonly principal:Readonly<{kind:'service';service:string;subject:string;tenant:null}>;
}
export interface GenericEventOperatorRootCommandTupleV2 extends Omit<GenericRootCommandTupleV1,'schema_version'|'principal'> {
 readonly schema_version:'craft.generic-root-command/v2-candidate';
 readonly principal:Readonly<{kind:'operator';subject:string;tenant:null}>;
}

/** V4 causal identity is a separately tagged domain. V1 customer tuples and
 * their canonical bytes remain exactly as before. */
export interface GenericEventExternalEffectTupleV2 extends Omit<GenericExternalEffectTupleV1,'schema_version'|'parent'> {
 readonly schema_version:'craft.generic-external-effect/v2-candidate';
 readonly parent:GenericEventOperatorRootCommandTupleV2|GenericEventServiceRootCommandTupleV2;
}

export interface GenericEventEmitStepV1 {
 readonly kind:'emit-event';
 readonly binding_ref:string;
 readonly binding_sha256:string;
 readonly event_selector:string;
 readonly event_version:1;
 readonly payload_type:ValueTypeV1;
 readonly payload:GenericKeyedRoleExpressionV1;
 readonly source_site:GenericTransactionSourceSiteV1;
 readonly emission_ordinal:number;
}

export interface GenericEventTransactionPlanV1 extends Omit<GenericTransactionPlanV1,'body'> {
 readonly body:readonly (GenericTransactionStepV1|GenericEventEmitStepV1)[];
}

export interface GenericEventStatefulControlV1 extends Omit<GenericStatefulControlV1,'schema_version'|'semantics_revision'|'preflight'|'transaction'> {
 readonly schema_version:'craft.generic-stateful-control/v4-candidate';
 readonly semantics_revision:'atomic-event-handoff/v1-candidate';
 readonly preflight:readonly GenericExternalWritePreflightStepV1[];
 readonly transaction:GenericEventTransactionPlanV1;
}

export interface GenericEventEntryV1 extends Omit<GenericTransactionEntryV1,'schema_version'|'interaction'|'access'> {
 readonly schema_version:'craft.generic-event-entry/v1-candidate';
 readonly interaction:'event';
 readonly event_selector:string;
 readonly event_version:1;
 readonly payload_type:ValueTypeV1;
 readonly mapping:string;
 readonly access:Readonly<{principal_kind:'service';caller:string;permission:string;resource:string;action:string;scope:string;route:string;context_type:'Craft.Generated.Auth.ServiceContext';context_abi:'craft.generic-auth-service-context/v1-candidate';native_abi:'craft.commerce-auth-ready-bridge/v1-candidate';native_asset:'auth-foundation-ready';current_action:'fresh-ready-before-inbox-replay-and-commit'}>;
}

export interface GenericEventOperatorEntryV1 extends Omit<GenericTransactionEntryV1,'schema_version'|'access'> {
 readonly schema_version:'craft.generic-operator-entry/v1-candidate';
 readonly access:Omit<GenericTransactionEntryV1['access'],'principal_kind'|'caller'>&Readonly<{principal_kind:'operator';caller:'self'}>;
}
export interface GenericEventOperatorQueryEntryV1 extends Omit<GenericLogicalEntryV1,'schema_version'|'access'> {
 readonly schema_version:'craft.generic-operator-query-entry/v1-candidate';
 readonly access:Omit<GenericLogicalEntryV1['access'],'principal_kind'|'caller'>&Readonly<{principal_kind:'operator';caller:'self'}>;
}

export interface GenericEventTransactionApplicationV1 extends Omit<GenericTransactionApplicationContractV1,'schema_version'|'semantics_revision'|'admission_mode'|'stateful_operations'|'entries'> {
 readonly schema_version:'craft.generic-transaction-application/v4-candidate';
 readonly semantics_revision:'atomic-event-handoff/v1-candidate';
 readonly admission_mode:'event-handoff-entry';
 readonly stateful_operations:readonly GenericEventStatefulControlV1[];
 readonly entries:readonly (GenericLogicalEntryV1|GenericTransactionEntryV1|GenericEventOperatorEntryV1|GenericEventOperatorQueryEntryV1|GenericEventEntryV1)[];
 readonly external_bindings:readonly GenericExternalCheckedBindingV1[];
 readonly write_bindings:readonly GenericExternalWriteCheckedBindingV1[];
 readonly identity_limits?:GenericExternalWriteSelectionV1['identity_limits'];
 readonly event_bindings:readonly GenericEventBindingV1[];
 readonly execution_policy:'original-durable-event-handoff';
}
