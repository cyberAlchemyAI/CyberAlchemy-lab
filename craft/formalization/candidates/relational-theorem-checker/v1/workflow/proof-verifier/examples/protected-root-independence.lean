import SemanticLogic
theorem submitted : ∀ (g : Relational.Graph) (roots : List Relational.AdmissionRoot) (e : Relational.Assertion), Relational.InstanceValid (Relational.Logic.withAdmissionRoots g roots) e ↔ Relational.InstanceValid g e := Relational.Logic.admission_roots_do_not_change_instance_meaning
