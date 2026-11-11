<!-- GENERATED summary: decision.json, authorization.json and owner-responses.json are canonical. -->

# Decision 0076: shared definitions and records activation

The owner explicitly accepted five exact Definition candidates, admitted the mixed-version Definition Registry/v2 contract, and authorized canonical internal publication and activation of one shared Lab workflow.

The five independent semantic decisions are recorded in dispositions/. Registry admission is recorded in registry-admission.json. Their source bodies are unchanged; earlier candidate metadata and residues remain authored historical context. Current admission comes from these owner decisions and the selected registry.

The new registry retains all 189 prior exact versions and their original decisions, then adds the five accepted versions: 194 admitted versions and 188 current identities. The five identities had no previously admitted current versions, so no prior Definition was withdrawn or made historical.

authority/definitions/current.json selects the canonical shared Registry/v2 snapshot. authority/definitions/registry.json remains the byte-exact v1 predecessor and native compatibility baseline. Frozen historical native profiles keep their original source pins.

The root Product workspace links the existing native authority Project to host the signed transaction. This does not create another Project workspace or copy a runtime.

The operator signing key is delegated mechanical signing authority for the configured workspace and source cut. It is stored outside the repository; it is not a cryptographic signature by the human owner. authorization.json preserves the actual owner message separately.

## Verification and recovery

    python3 -B docs/decisions/0076-shared-definitions-records-activation/validate.py
    node implementation/lab-runtime/lab.mjs shared status
    node implementation/lab-runtime/lab.mjs catalog --category definition --current

Read receipts/ for native review, signed application, canonical publication, join reconciliation, Define discovery and final regression verification. snapshot-files.json in the admission bundle preserves the complete published material independently of the local database.

The activation is local and internal. It performs no external deployment, release or publication.

The source transition is recorded in receipts/source-transition.json. The canonical Decision changes the native admission inventory. The activation therefore preserves its original signed publication branch and provisions a fresh current data branch under the same runtime, with the same six exact local targets. No frozen source pins or original approvals are rewritten. This is data lineage, not another runtime installation.
