# Work Orchestration context import

Define bounded steps -> route work -> record progress -> replay the recorded path.

The candidate describes multi-step work while keeping domain decisions and external-effect permissions with their owners. It preserves 22 concepts, 24 relationships, 14 declared relation types, eight local terms and 12 obligations. Six unresolved construction items remain recorded; RWO is an unselected implementation proposal.

The initial source validator reported BLOCK because references used an older directory layout and two pinned documents differed from their current versions. All six original evidence selections were recovered with exactly matching fingerprints from `../cya-orquestrator`. The package itself is copied unchanged from `../cyberAlchemy-v2/work-orchestration`; this does not substitute another capability or update its meaning. `plan.json` records the origin and full-file digest of every snapshot. `original-source-validation.json` retains the initial failure.

The unchanged source validator now passes against the recovered evidence, including original selectors, package schemas, relation signatures, source references and construction limits. `source-validation.json` retains that result. Context and Ontology headers also validate against Lab migration-scoped contracts. The isolated store `.local/ontology-context-import-0044/` contains both the package and its evidence documents so these checks can be repeated after restoration.

Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0044-work-orchestration-context-import/verify.py` from the repository root. Checks cover replay, rejected graph mutations, evidence drift, restored source validation and unchanged capability storage.

This imports a source-qualified candidate model. It does not select a scheduler, authorize effects, establish runtime conformance or admit a global ontology. Source repositories and previous migration artifacts remain unchanged.
