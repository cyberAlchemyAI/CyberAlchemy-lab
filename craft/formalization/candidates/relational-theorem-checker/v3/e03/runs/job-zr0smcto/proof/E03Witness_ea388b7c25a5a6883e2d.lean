import FulfillmentSemantics
set_option maxRecDepth 2048
open RelationalExtensions.Fulfillment
namespace FulfillmentInstance
def source : Source := ⟨⟨"request", "v1"⟩, ⟨"requirement", "v1"⟩, ⟨⟨"ctx", "v1"⟩, "review", 5⟩, true, [⟨"criterion1", "v1"⟩, ⟨"criterion2", "v1"⟩], [], [], []⟩
theorem complete_fulfillment : fulfilled source = false := by decide
theorem complete_verdict : verdict source = .unknown := by decide
theorem independent_meaning : fulfilled source = true ↔ Meaning source := fulfillment_exact source
theorem criterion_0 : criterionTruth source ⟨"criterion1", "v1"⟩ = .unknown := by decide
#print axioms criterion_0
theorem criterion_1 : criterionTruth source ⟨"criterion2", "v1"⟩ = .unknown := by decide
#print axioms criterion_1
#print axioms complete_fulfillment
#print axioms complete_verdict
#print axioms independent_meaning
end FulfillmentInstance
