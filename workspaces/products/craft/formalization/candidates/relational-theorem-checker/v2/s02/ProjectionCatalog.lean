import ContextProjection
namespace Successor.Projection.Catalog
abbrev RequiredProjection : Prop := Successor.Required.ProjectionExact project
abbrev RequiredKinds : Prop := Successor.Required.KindProjectionExact projectKinds
abbrev RequiredUnary : Prop := Successor.Required.ExistentialViewExact project projectUnary
abbrev RequiredSupport : Prop := ∀ g x, x ∈ project g ↔ ∃ s, Supports g x s
abbrev RequiredKindEncoding : Prop := Successor.Required.KindEncodingInjective
end Successor.Projection.Catalog
