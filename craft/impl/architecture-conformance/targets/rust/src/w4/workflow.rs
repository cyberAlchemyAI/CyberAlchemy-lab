pub struct WorkflowStep<'a> { pub step_id: &'static str, pub run: &'a mut dyn FnMut() -> Result<(), &'static str>, pub compensation_id: Option<&'static str>, pub compensate: Option<&'a mut dyn FnMut() -> Result<(), &'static str>> }
#[derive(Debug, PartialEq, Eq)]
pub struct WorkflowResult { pub outcome: &'static str, pub trace: Vec<&'static str>, pub failed_step_id: Option<&'static str>, pub compensations: Vec<String> }

pub fn run_settlement_workflow(steps: &mut [WorkflowStep<'_>]) -> Result<WorkflowResult, &'static str> {
    const ORDER: [&str; 4] = ["validate", "decide", "persist", "publish"];
    for step_id in ORDER {
        if !steps.iter().any(|step| step.step_id == step_id) { return Err("ARCH_WORKFLOW_STEP_MISSING"); }
    }
    if steps.len() != ORDER.len()
        || steps.iter().any(|step| !ORDER.contains(&step.step_id))
        || ORDER.iter().any(|step_id| steps.iter().filter(|step| step.step_id == *step_id).count() != 1)
    {
        return Err("ARCH_WORKFLOW_STEP_SET_INVALID");
    }
    for step in steps.iter() {
        let compensation_valid = if step.step_id == "persist" {
            step.compensation_id == Some("rollback-settlement") && step.compensate.is_some()
        } else {
            step.compensation_id.is_none() && step.compensate.is_none()
        };
        if !compensation_valid { return Err("ARCH_WORKFLOW_COMPENSATION_CONTRACT_INVALID"); }
    }
    let mut trace = Vec::new();
    let mut completed_indices = Vec::new();
    for step_id in ORDER {
        let Some(index) = steps.iter().position(|step| step.step_id == step_id) else { return Err("ARCH_WORKFLOW_STEP_MISSING"); };
        if (steps[index].run)().is_err() {
            let mut compensations = Vec::new();
            for completed_index in completed_indices.into_iter().rev() {
                let completed: &mut WorkflowStep<'_> = &mut steps[completed_index];
                if let Some(compensate) = completed.compensate.as_mut() {
                    let compensation_id = completed.compensation_id.ok_or("ARCH_WORKFLOW_COMPENSATION_ID_MISSING")?;
                    compensate()?;
                    compensations.push(compensation_id.to_string());
                }
            }
            return Ok(WorkflowResult {outcome: "settlement-failed", trace, failed_step_id: Some(step_id), compensations});
        }
        trace.push(step_id);
        completed_indices.push(index);
    }
    Ok(WorkflowResult {outcome: "settlement-completed", trace, failed_step_id: None, compensations: Vec::new()})
}
