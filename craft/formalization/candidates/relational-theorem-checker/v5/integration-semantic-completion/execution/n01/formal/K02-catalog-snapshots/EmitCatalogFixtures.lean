import CatalogRuntimeControls
set_option autoImplicit false
open RelationalSuccessor.CandidateCatalogSnapshots.RuntimeEncoding
open RelationalSuccessor.CandidateCatalogSnapshots.RuntimeControls

def main : IO Unit := do
  IO.FS.writeFile "/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/formal/K02-catalog-snapshots/fixtures/metadata.json" (render metadataAst)
  IO.FS.writeFile "/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/formal/K02-catalog-snapshots/fixtures/payload.json" (render payloadAst)
  IO.FS.writeFile "/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/formal/K02-catalog-snapshots/fixtures/owned.json" (render ownedAst)
