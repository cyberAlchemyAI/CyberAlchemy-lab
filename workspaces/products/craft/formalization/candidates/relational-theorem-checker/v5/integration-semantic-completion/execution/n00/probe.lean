import Lean
open Lean Elab Command in
run_cmd do
  let env ← getEnv
  for (n, _) in env.constants do
    let s := n.toString
    if (s.startsWith "List." && ((s.splitOn "Chain").length > 1 || (s.splitOn "chain").length > 1 || (s.splitOn "pairwise").length > 1)) || (s.startsWith "String." && ((s.splitOn "lt_trans").length > 1 || (s.splitOn "lt_irrefl").length > 1)) then
      logInfo m!"{n}"
