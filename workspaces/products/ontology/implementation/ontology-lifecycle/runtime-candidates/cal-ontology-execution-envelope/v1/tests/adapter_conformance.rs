use cal_ontology_execution_envelope::{
    EventCut, ExecutionEngine, ExecutionFailure, ExecutionStepId, ExecutionTargetAdapter,
    InMemoryTarget, PrototypeTargetBinding, TargetSnapshot,
};

struct WrappedPrototypeAdapter {
    inner: InMemoryTarget,
    binding: PrototypeTargetBinding,
}

impl WrappedPrototypeAdapter {
    fn conforming() -> Self {
        Self {
            inner: InMemoryTarget::new(),
            binding: PrototypeTargetBinding::exact(),
        }
    }
}

impl ExecutionTargetAdapter for WrappedPrototypeAdapter {
    type Snapshot = TargetSnapshot;

    fn binding(&self) -> PrototypeTargetBinding {
        self.binding.clone()
    }

    fn capture_preimage(&self) -> Self::Snapshot {
        self.inner.capture_preimage()
    }

    fn verify_preimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.inner.verify_preimage(expected)
    }

    fn stage(&mut self, candidate: &EventCut) -> Result<(), ExecutionFailure> {
        self.inner.stage(candidate)
    }

    fn activate(&mut self) -> Result<(), ExecutionFailure> {
        self.inner.activate()
    }

    fn migrate(&mut self) -> Result<(), ExecutionFailure> {
        self.inner.migrate()
    }

    fn verify_target(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.inner.verify_target(expected)
    }

    fn cutover(&mut self) -> Result<(), ExecutionFailure> {
        self.inner.cutover()
    }

    fn verify_postimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.inner.verify_postimage(expected)
    }

    fn restore(&mut self, preimage: &Self::Snapshot) -> Result<(), ExecutionFailure> {
        self.inner.restore(preimage)
    }

    fn verify_rollback(&self, preimage: &Self::Snapshot) -> Result<(), ExecutionFailure> {
        self.inner.verify_rollback(preimage)
    }

    fn emergency_restore(&mut self, preimage: &Self::Snapshot) {
        self.inner.emergency_restore(preimage);
    }
}

#[test]
fn public_adapter_contract_accepts_an_external_conforming_type() {
    let envelope = cal_ontology_execution_envelope::ExecutionEnvelope::exact_prototype();
    let mut target = WrappedPrototypeAdapter::conforming();
    let preimage = target.capture_preimage();
    let receipt = ExecutionEngine.execute(&envelope, &mut target).unwrap();
    assert_eq!(receipt.trace.len(), 10);
    assert_eq!(receipt.target_adapter_kind, "in-memory-disposable-target");
    assert_eq!(target.capture_preimage(), preimage);
}

#[test]
fn adapter_binding_mismatch_fails_before_mutation() {
    let envelope = cal_ontology_execution_envelope::ExecutionEnvelope::exact_prototype();
    let mut target = WrappedPrototypeAdapter::conforming();
    target.binding.identity = "unreviewed-adapter".to_owned();
    let preimage = target.capture_preimage();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "PROTOTYPE_TARGET_BOUNDARY_VIOLATION");
    assert_eq!(target.capture_preimage(), preimage);
}

#[test]
fn rollback_failure_forces_emergency_preimage_restore() {
    let envelope = cal_ontology_execution_envelope::ExecutionEnvelope::exact_prototype();
    let mut target = InMemoryTarget::with_fault(ExecutionStepId::Rollback);
    let preimage = target.snapshot();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "INJECTED_PROTOTYPE_FAILURE");
    assert_eq!(target.snapshot(), preimage);
}

#[test]
fn rollback_verification_failure_forces_emergency_preimage_restore() {
    let envelope = cal_ontology_execution_envelope::ExecutionEnvelope::exact_prototype();
    let mut target = InMemoryTarget::with_fault(ExecutionStepId::VerifyRollback);
    let preimage = target.snapshot();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "INJECTED_PROTOTYPE_FAILURE");
    assert_eq!(target.snapshot(), preimage);
}
