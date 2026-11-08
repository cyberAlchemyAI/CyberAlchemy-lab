# Craft game shared-control design

Date: 2026-10-29. Status: offline shared runtime implemented and locally checked. Both complete 25-lesson mission paths pass. The inactive official SDK stdio adapter is checked against the real app/PIP logic in a Node harness; live user-tab attachment remains deferred. See the consolidated [functional report](/home/vlad_/projects/cyberAlchemy-v2/goals/plans/craft-game-shared-mcp-2026-10-29/VALIDATION.json).

- [Revised design](DESIGN.md): intended experience, authority, actual model reuse and limits.
- [Distill result](/home/vlad_/projects/cyberAlchemy-v2/goals/plans/craft-game-shared-mcp-2026-10-29/distill/RECONCILIATION.md): two real Proposer/Balancer rounds, findings and decisions.
- [Detailed implementation DAG](IMPLEMENTATION-DAG.md): 19 offline tasks and 5 explicitly deferred live tasks, dependencies and subagent work boundaries.
- [Shared contracts](CONTRACTS.md) and [emitted API schemas](API.json): closed DTOs, semantic validators, actor/operation requirements and current nine-tool schemas.
- [Machine-readable task graph](DAG.json) and [Current check results](/home/vlad_/projects/cyberAlchemy-v2/goals/plans/craft-game-shared-mcp-2026-10-29/VALIDATION.json).
- [Implemented runtime and contracts](/home/vlad_/projects/cyberAlchemy-v2/release-candidates/craft-alchlang-current/public-source-repository/examples/engineering-game/lab/contracts/README.md): public example source and usage. 

The implementation supports preview, proposal/edit/accept, scoped execution, actual PIP work, partial outcomes, retry recovery and immediate player takeover. All eleven actions and sixteen controls are available through the same offline runtime. The offline milestone covers all 25 lessons; it cannot prove actual-tab MCP integration. Local hosting/listeners, live pairing/registration, TDE, EVF and publication remain deferred.

[Historical M02 implementation and limits](/home/vlad_/projects/cyberAlchemy-v2/release-candidates/craft-alchlang-current/public-source-repository/examples/engineering-game/lab/contracts/M02.md).

The [player guide](/home/vlad_/projects/cyberAlchemy-v2/release-candidates/craft-alchlang-current/public-source-repository/examples/engineering-game/lab/contracts/SHARED-GUIDE.md) explains modes, permissions and stopping work. The [adapter guide](/home/vlad_/projects/cyberAlchemy-v2/release-candidates/craft-alchlang-current/public-source-repository/examples/engineering-game/game-mcp/README.md) records the qualified reference tuple and disconnected default. Browser details are in the owned-context QA report (result record excluded).

## Listener-free read-only experiment

The owner has authorized a narrow existing-tab probe using [Site tools](https://learn.chatgpt.com/docs/webmcp). The current game now registers only `craft_connection_probe`, which echoes a challenge and reads live identity/revisions. It does not attach an actor, grant access or expose PIP commands. Source/fake-host and ordinary-browser fallback checks pass. The actual existing tab must load the update and expose the native Site tool before a round trip can be claimed. Current outcome: probe report (result record excluded). The Office document-control connector is unrelated to Site tool discovery. Full live PIP control, listeners, hosting, TDE, EVF and publication remain deferred.

## Open questions

Owned by [DESIGN.md](DESIGN.md#completion-and-open-questions).
