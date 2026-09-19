# Capability imported without a Team instance

Complete Capability + Product reference -> validated candidate import -> operational admission later.

The isolated store `.local/capability-candidate-import-0004/import.json` now contains the People and Teams Capability and its Product as two candidate records. No Team instance was required or created. [results.json](results.json) preserves the normalized records and their original source records; [verification.json](verification.json) binds the store and implementation.

Three corrections made this possible:

- The earlier sample required admitted Definitions even for candidate storage. This successor permits exact, verified candidate Definitions for candidate import while retaining them as blockers to operational use. It does not admit or activate those Definitions.
- The lifecycle status now has an explicit migration binding to the source schema's `candidate` vocabulary. Source bytes remain unchanged.
- The source's `CA2-CAP-BIND-PEOPLE-AND-TEAMS-UNSELECTED` reference has no matching binding. The imported companion metadata records no realization selected and preserves that unresolved reference as source residue. It does not invent an implementation.

Product, consumer, participant-concept, input, output, policy and outcome references resolve to the source nodes. The linked obligations supply acceptance conditions, not evidence that the conditions are satisfied. The full source Capability passes its source schema; the normalized Product and Capability pass the registered record contracts and graph reference checks together.

Seven checks passed: deterministic import without Teams, preservation of the candidate Definition blocker, rejection of missing consumers, dangling inputs, unknown lifecycle status and unknown realization references, and explicit vocabulary/realization handling.

## Remaining limits

This is a candidate import. The Capability Definition is still unadmitted; operational use is not authorized. There is no realized implementation, conformance or actual Team claim. The earlier Thesis staging result is unchanged. The next operational step must resolve the exact Definition dependency and any selected realization through their own recorded evidence; neither is required merely to preserve this complete candidate.
