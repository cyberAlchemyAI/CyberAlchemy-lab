# Required theorem statements

The specification fixes these targets before checker implementation. All variables quantify over arbitrary finite typed inputs; there is no graph-size bound.

```lean
instance_check_sound (g : Graph) (e : Assertion) :
  checkInstance g e = true → InstanceValid g e
graph_check_sound (g : Graph) :
  checkGraph g = true → Inv g
addition_preserves (g : Graph) (e : Assertion) :
  checkAddition g e = true → Inv (applyAddition g e)
```

The final theorem uses full rechecking, so no unnecessary premise `Inv g` is required. Additional completeness targets (`checkGraph g = true ↔ Inv g`, similarly for instances) establish that this checker decides precisely the scoped invariant rather than simply rejecting everything. Addition must preserve admission roots by equality. `Nonempty`/existential witnesses must include all three relation kinds, an accepted addition, conformance without admission, and valid coexistence with independent admission provenance.

The statement audit checks Lean elaborated types against these targets in a separate module using named target definitions and `example` assignments. It checks transitive axioms of those assignments and concrete witness theorems. Proof acceptance requires fresh pinned-toolchain replay, source identity, exact statements, accepted and rejected controls, and recorded semantic review. Renaming, checking a different theorem, proving `True`, relying only on examples, assuming the intended conclusion, or introducing a custom axiom fails the audit.

Typed constructors account for missing/extra qualifier fields. A representable kind/qualifier mismatch must reject. Accepted fixtures are synthetic input ledgers, not live source/evidence claims. Kernel validity does not establish the accuracy of the English/source interpretation, JSON decoding, hash authentication or compiled-runtime behavior.
