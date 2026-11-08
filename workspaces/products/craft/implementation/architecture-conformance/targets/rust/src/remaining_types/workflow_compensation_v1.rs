//! First-class Rust Workflow recovery profile for canonical D36, D37, and D40.
use sha2::{Digest, Sha256};
use std::collections::{HashMap, HashSet};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RecoveryFailureContinuation {
    Retry,
    Escalate,
    TerminalFailure,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct RecoveryOperationMapping<'a> {
    pub step_id: &'a str,
    pub operation_id: Option<&'a str>,
    pub depends_on: &'a [&'a str],
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RecoveryPlanEntry {
    pub plan_occurrence_id: String,
    pub step_id: String,
    pub operation_id: String,
    pub depends_on: Vec<String>,
    pub invocation_identity: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RecoveryIntent {
    pub schema_version: &'static str,
    pub intent_id: String,
    pub workflow_id: String,
    pub workflow_execution_id: String,
    pub failure_occurrence_id: String,
    pub failed_step_id: String,
    pub completed_step_journal_digest: String,
    pub plan_digest: String,
    pub semantic_status: &'static str,
    pub plan: Vec<RecoveryPlanEntry>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct WorkflowRecoveryDecision {
    pub schema_version: &'static str,
    pub workflow_evaluation_result: &'static str,
    pub recovery_intent: Option<RecoveryIntent>,
}

#[derive(Clone, Copy)]
pub struct RecoveryOperationBinding<'a> {
    pub workflow_id: &'a str,
    pub operation_id: &'a str,
    pub failure_continuation: RecoveryFailureContinuation,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RecoveryInvocationReport {
    pub schema_version: &'static str,
    pub outcome: &'static str,
    pub executed_plan_occurrence_ids: Vec<String>,
    pub failed_plan_occurrence_id: Option<String>,
    pub failure_continuation: Option<RecoveryFailureContinuation>,
    pub reason: Option<String>,
    pub recovery_intent_semantic_status: &'static str,
    pub durable_terminal_disposition: Option<&'static str>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct WorkflowRecoveryError {
    pub code: &'static str,
    pub detail: String,
}

#[derive(Clone, Copy)]
pub struct PlanningInput<'a> {
    pub workflow_id: &'a str,
    pub workflow_execution_id: &'a str,
    pub failure_occurrence_id: &'a str,
    pub failed_step_id: &'a str,
    pub completed_step_ids: &'a [&'a str],
    pub orchestrated_operation_ids: &'a [&'a str],
    pub mappings: &'a [RecoveryOperationMapping<'a>],
}

fn error(code: &'static str, detail: impl Into<String>) -> WorkflowRecoveryError {
    WorkflowRecoveryError { code, detail: detail.into() }
}

fn valid_identity(value: &str) -> bool {
    let mut parts = value.split('-');
    let Some(first) = parts.next() else { return false };
    let valid_part = |part: &str, first_part: bool| {
        !part.is_empty()
            && part.chars().enumerate().all(|(index, character)| {
                character.is_ascii_lowercase()
                    || character.is_ascii_digit() && (!first_part || index > 0)
            })
            && (!first_part || first.chars().next().is_some_and(|character| character.is_ascii_lowercase()))
    };
    valid_part(first, true) && parts.all(|part| valid_part(part, false))
}

fn require_identity(value: &str, label: &str) -> Result<(), WorkflowRecoveryError> {
    if valid_identity(value) { Ok(()) } else { Err(error("RECOVERY_IDENTITY_INVALID", format!("{label}:{value}"))) }
}

fn sha256(value: &str) -> String {
    format!("{:x}", Sha256::digest(value.as_bytes()))
}

fn journal_material(completed_step_ids: &[&str]) -> String {
    std::iter::once("domainspec.workflow-completed-step-journal/v1")
        .chain(completed_step_ids.iter().copied())
        .collect::<Vec<_>>()
        .join("\n")
}

fn plan_material(entries: &[RecoveryPlanEntry]) -> String {
    std::iter::once("domainspec.workflow-recovery-plan/v1".to_owned())
        .chain(entries.iter().map(|entry| format!(
            "{}|{}|{}|{}",
            entry.plan_occurrence_id,
            entry.step_id,
            entry.operation_id,
            entry.depends_on.join(",")
        )))
        .collect::<Vec<_>>()
        .join("\n")
}

fn invocation_identity(intent_id: &str, plan_digest: &str, operation_id: &str, plan_occurrence_id: &str) -> String {
    sha256(&[
        "domainspec.compensation-invocation-identity/v1",
        intent_id,
        plan_digest,
        operation_id,
        plan_occurrence_id,
    ].join("\n"))
}

pub fn plan_workflow_recovery(input: PlanningInput<'_>) -> Result<WorkflowRecoveryDecision, WorkflowRecoveryError> {
    for (label, value) in [
        ("workflow_id", input.workflow_id),
        ("workflow_execution_id", input.workflow_execution_id),
        ("failure_occurrence_id", input.failure_occurrence_id),
        ("failed_step_id", input.failed_step_id),
    ] {
        require_identity(value, label)?;
    }
    let completed: HashSet<_> = input.completed_step_ids.iter().copied().collect();
    if completed.len() != input.completed_step_ids.len() {
        return Err(error("RECOVERY_COMPLETED_STEP_DUPLICATE", "completed step IDs must be unique"));
    }

    let mut orchestrated = HashSet::new();
    for operation_id in input.orchestrated_operation_ids {
        require_identity(operation_id, "orchestrated_operation_id")?;
        if !orchestrated.insert(*operation_id) {
            return Err(error("RECOVERY_ORCHESTRATION_DUPLICATE", *operation_id));
        }
    }

    let mut mappings = HashMap::new();
    for mapping in input.mappings {
        require_identity(mapping.step_id, "mapping.step_id")?;
        if mappings.insert(mapping.step_id, mapping).is_some() {
            return Err(error("RECOVERY_MAPPING_DUPLICATE", mapping.step_id));
        }
        if let Some(operation_id) = mapping.operation_id {
            require_identity(operation_id, "mapping.operation_id")?;
        }
        let dependencies: HashSet<_> = mapping.depends_on.iter().copied().collect();
        if dependencies.len() != mapping.depends_on.len() {
            return Err(error("RECOVERY_DEPENDENCY_DUPLICATE", mapping.step_id));
        }
        for dependency in mapping.depends_on {
            require_identity(dependency, "mapping.depends_on")?;
        }
    }

    let mut selected = Vec::new();
    for (completion_index, step_id) in input.completed_step_ids.iter().enumerate() {
        require_identity(step_id, "completed_step_id")?;
        let Some(mapping) = mappings.get(step_id) else { continue };
        let Some(operation_id) = mapping.operation_id else { continue };
        if !orchestrated.contains(operation_id) {
            return Err(error("RECOVERY_OPERATION_NOT_ORCHESTRATED", format!("{}:{operation_id}", input.workflow_id)));
        }
        selected.push(RecoveryPlanEntry {
            plan_occurrence_id: format!("{step_id}-{operation_id}-{}", completion_index + 1),
            step_id: (*step_id).to_owned(),
            operation_id: operation_id.to_owned(),
            depends_on: mapping.depends_on.iter().map(|value| (*value).to_owned()).collect(),
            invocation_identity: String::new(),
        });
    }
    selected.reverse();
    if selected.is_empty() {
        return Ok(WorkflowRecoveryDecision {
            schema_version: "domainspec.workflow-recovery-decision/v1",
            workflow_evaluation_result: "not-required",
            recovery_intent: None,
        });
    }

    let mut occurrences_by_operation: HashMap<String, Vec<String>> = HashMap::new();
    for entry in &selected {
        occurrences_by_operation.entry(entry.operation_id.clone()).or_default().push(entry.plan_occurrence_id.clone());
    }
    for entry in &mut selected {
        let mut dependencies = Vec::new();
        for dependency in &entry.depends_on {
            let occurrences = occurrences_by_operation.get(dependency).cloned().unwrap_or_default();
            if dependency == &entry.operation_id || occurrences.len() != 1 {
                let code = if occurrences.len() > 1 { "RECOVERY_DEPENDENCY_AMBIGUOUS" } else { "RECOVERY_DEPENDENCY_INVALID" };
                return Err(error(code, format!("{}:depends-on:{dependency}", entry.operation_id)));
            }
            dependencies.push(occurrences[0].clone());
        }
        entry.depends_on = dependencies;
    }

    let mut ordered = Vec::new();
    let mut emitted = HashSet::new();
    while !selected.is_empty() {
        let Some(index) = selected.iter().position(|entry| entry.depends_on.iter().all(|dependency| emitted.contains(dependency))) else {
            return Err(error("RECOVERY_DEPENDENCY_CYCLE", "recovery Operation dependency graph is cyclic"));
        };
        let entry = selected.remove(index);
        emitted.insert(entry.plan_occurrence_id.clone());
        ordered.push(entry);
    }

    let completed_step_journal_digest = sha256(&journal_material(input.completed_step_ids));
    let plan_digest = sha256(&plan_material(&ordered));
    let intent_id = sha256(&[
        "domainspec.workflow-recovery-intent/v2",
        input.workflow_execution_id,
        input.failure_occurrence_id,
        input.failed_step_id,
        &completed_step_journal_digest,
        &plan_digest,
    ].join("\n"));
    for entry in &mut ordered {
        entry.invocation_identity = invocation_identity(&intent_id, &plan_digest, &entry.operation_id, &entry.plan_occurrence_id);
    }
    Ok(WorkflowRecoveryDecision {
        schema_version: "domainspec.workflow-recovery-decision/v1",
        workflow_evaluation_result: "recovery-required",
        recovery_intent: Some(RecoveryIntent {
            schema_version: "domainspec.workflow-recovery-intent/v2",
            intent_id,
            workflow_id: input.workflow_id.to_owned(),
            workflow_execution_id: input.workflow_execution_id.to_owned(),
            failure_occurrence_id: input.failure_occurrence_id.to_owned(),
            failed_step_id: input.failed_step_id.to_owned(),
            completed_step_journal_digest,
            plan_digest,
            semantic_status: "required",
            plan: ordered,
        }),
    })
}

fn verify_intent(intent: &RecoveryIntent) -> Result<(), WorkflowRecoveryError> {
    let mut emitted = HashSet::new();
    for entry in &intent.plan {
        if !entry.depends_on.iter().all(|dependency| emitted.contains(dependency)) {
            return Err(error("RECOVERY_PLAN_ORDER_INVALID", &entry.plan_occurrence_id));
        }
        if !emitted.insert(entry.plan_occurrence_id.clone()) {
            return Err(error("RECOVERY_PLAN_OCCURRENCE_DUPLICATE", &entry.plan_occurrence_id));
        }
    }
    if sha256(&plan_material(&intent.plan)) != intent.plan_digest {
        return Err(error("RECOVERY_PLAN_DIGEST_MISMATCH", &intent.plan_digest));
    }
    let observed_intent_id = sha256(&[
        "domainspec.workflow-recovery-intent/v2",
        &intent.workflow_execution_id,
        &intent.failure_occurrence_id,
        &intent.failed_step_id,
        &intent.completed_step_journal_digest,
        &intent.plan_digest,
    ].join("\n"));
    if observed_intent_id != intent.intent_id {
        return Err(error("RECOVERY_INTENT_ID_MISMATCH", observed_intent_id));
    }
    for entry in &intent.plan {
        if invocation_identity(&intent.intent_id, &intent.plan_digest, &entry.operation_id, &entry.plan_occurrence_id) != entry.invocation_identity {
            return Err(error("RECOVERY_INVOCATION_IDENTITY_MISMATCH", &entry.plan_occurrence_id));
        }
    }
    Ok(())
}

pub fn execute_workflow_recovery(
    intent: &RecoveryIntent,
    bindings: &[RecoveryOperationBinding<'_>],
    mut invoke: impl FnMut(&str, &str) -> Result<(), String>,
) -> Result<RecoveryInvocationReport, WorkflowRecoveryError> {
    verify_intent(intent)?;
    let required: HashSet<_> = intent.plan.iter().map(|entry| entry.operation_id.as_str()).collect();
    let mut registry = HashMap::new();
    for binding in bindings {
        if binding.workflow_id != intent.workflow_id {
            return Err(error("RECOVERY_BINDING_WORKFLOW_MISMATCH", format!("{}:{}", binding.workflow_id, binding.operation_id)));
        }
        if !required.contains(binding.operation_id) {
            return Err(error("RECOVERY_BINDING_UNDECLARED", binding.operation_id));
        }
        if registry.insert(binding.operation_id, binding).is_some() {
            return Err(error("RECOVERY_BINDING_DUPLICATE", binding.operation_id));
        }
    }
    for operation_id in required {
        if !registry.contains_key(operation_id) {
            return Err(error("RECOVERY_BINDING_MISSING", operation_id));
        }
    }

    let mut executed = Vec::new();
    for entry in &intent.plan {
        let binding = registry.get(entry.operation_id.as_str()).ok_or_else(|| error("RECOVERY_BINDING_MISSING", &entry.operation_id))?;
        if let Err(reason) = invoke(&entry.operation_id, &entry.invocation_identity) {
            return Ok(RecoveryInvocationReport {
                schema_version: "domainspec.workflow-recovery-in-process-report/v1",
                outcome: "failed",
                executed_plan_occurrence_ids: executed,
                failed_plan_occurrence_id: Some(entry.plan_occurrence_id.clone()),
                failure_continuation: Some(binding.failure_continuation),
                reason: Some(reason),
                recovery_intent_semantic_status: "required",
                durable_terminal_disposition: None,
            });
        }
        executed.push(entry.plan_occurrence_id.clone());
    }
    Ok(RecoveryInvocationReport {
        schema_version: "domainspec.workflow-recovery-in-process-report/v1",
        outcome: "succeeded",
        executed_plan_occurrence_ids: executed,
        failed_plan_occurrence_id: None,
        failure_continuation: None,
        reason: None,
        recovery_intent_semantic_status: "required",
        durable_terminal_disposition: None,
    })
}
