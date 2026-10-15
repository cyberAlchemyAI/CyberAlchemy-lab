import FulfillmentSemantics
set_option maxRecDepth 2048
open RelationalExtensions.Fulfillment
namespace FulfillmentInstance
def source : Source := ⟨⟨"request", "v1"⟩, ⟨"requirement", "v1"⟩, ⟨⟨"ctx", "v1"⟩, "review", 5⟩, true, [⟨"criterion1", "v1"⟩, ⟨"criterion2", "v1"⟩], [⟨⟨"action", "v1"⟩, ⟨"request", "v1"⟩, ⟨"requirement", "v1"⟩, ⟨⟨"ctx", "v1"⟩, "review", 5⟩, [⟨"output", "v1"⟩], true⟩], [⟨⟨"output", "v1"⟩, ⟨"action", "v1"⟩, true⟩], [⟨⟨"evaluation1", "v1"⟩, ⟨"criterion1", "v1"⟩, ⟨"request", "v1"⟩, ⟨"requirement", "v1"⟩, ⟨"action", "v1"⟩, ⟨"output", "v1"⟩, ⟨⟨"ctx", "v1"⟩, "review", 5⟩, .yes⟩, ⟨⟨"evaluation2", "v1"⟩, ⟨"criterion2", "v1"⟩, ⟨"request", "v1"⟩, ⟨"requirement", "v1"⟩, ⟨"action", "v1"⟩, ⟨"output", "v1"⟩, ⟨⟨"ctx", "v1"⟩, "review", 5⟩, .yes⟩]⟩
theorem complete_fulfillment : fulfilled source = true := by decide
theorem complete_verdict : verdict source = .yes := by decide
theorem independent_meaning : fulfilled source = true ↔ Meaning source := fulfillment_exact source
theorem criterion_0 : criterionTruth source ⟨"criterion1", "v1"⟩ = .yes := by decide
#print axioms criterion_0
theorem criterion_1 : criterionTruth source ⟨"criterion2", "v1"⟩ = .yes := by decide
#print axioms criterion_1
#print axioms complete_fulfillment
#print axioms complete_verdict
#print axioms independent_meaning
end FulfillmentInstance
