import Lean

-- Metadata traversal for the replay inventory, not a proof or native evaluator.
partial def gatherImports (root : String) (pending seen : List String) : IO (List String) := do
  match pending with
  | [] => pure seen
  | name :: rest =>
    if seen.contains name then
      gatherImports root rest seen
    else
      let file := System.FilePath.mk (root ++ "/" ++ name.replace "." "/" ++ ".olean")
      let (data, _) ← Lean.readModuleData file
      let imports := data.imports.toList.map (fun i => i.module.toString)
      gatherImports root (imports ++ rest) (name :: seen)

def main (args : List String) : IO Unit := do
  match args with
  | root :: modules =>
    for name in ← gatherImports root modules [] do
      IO.println name
  | [] => throw (IO.userError "usage: DependencyAudit <library-root> <module>...")
