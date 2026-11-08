import RelationalSemantics

namespace Relational

-- Constructive finite decision procedures for the independently stated clauses.
-- No parser, host validator, external lookup or proof axiom is used here.
def checkInstance (g : Graph) (e : Assertion) : Bool :=
  decide (e.id ≠ "") && decide (EndpointValid g e) &&
    decide (QualifierValid e) && decide (VersionScopeValid g e)

def checkGraph (g : Graph) : Bool :=
  decide (InventoryValid g) && g.assertions.all (checkInstance g) &&
    decide ((g.assertions.map Assertion.id).Nodup)

def checkAddition (g : Graph) (e : Assertion) : Bool :=
  checkGraph (applyAddition g e)

end Relational
