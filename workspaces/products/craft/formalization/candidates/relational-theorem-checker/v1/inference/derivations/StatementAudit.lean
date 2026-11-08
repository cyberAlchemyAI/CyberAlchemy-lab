import DerivationSoundness

namespace Inference.Audit

-- Exact required type assignment prevents a proof of True being substituted.
theorem required_statement : RequiredDerivationSoundness := audited_derivation_soundness

#print axioms required_statement
#print axioms derivation_checker_iff
#print axioms derivation_certificate_sound
#print axioms chain_sound
#print axioms step_sound
#print axioms resolved_premises_are_previous
#print axioms derivable_in_every_closed_model

end Inference.Audit
