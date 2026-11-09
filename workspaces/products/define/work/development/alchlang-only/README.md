# Define AlchLang migration record

The current migration is complete for local candidate behavior. Read STATUS.md, VERIFICATION.json and COVERAGE.json. DEFINITIONS.json reuses exact existing semantic sources; ARTIFACTS.json and models/{business,bridge,system}.json record the construction chain. Technical refinements have matching business, bridge and system projections. MODEL-INDEX.json in the maintained implementation indexes all authored source selections.

BASELINE.json is an immutable pre-migration hash audit, not executable source. REVIEW.json retains the preimplementation review and links the completion review. RETIREMENT.json names removed predecessors; DEPENDENCY-AUDIT.json checks current dependencies. Latest per-surface evidence is retained once here, while compiler outputs and temporary test directories remain ignored caches. No new canonical admission or production owner outcome is inferred.
