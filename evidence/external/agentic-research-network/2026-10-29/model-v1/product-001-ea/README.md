# Engineer Assessment whole Product candidate for ARN

Status: candidate, unadmitted, source-pinned. This package maps the existing Engineer Assessment Product across experience, case/scoring science, research, software operation, evidence, reward, Product value and governance. It is an ARN **reference model**; it does not change the EA workspace.

Start with [MODEL.md](MODEL.md) for the full layer map and research-to-Product chain, [VALUE-FLOW.md](VALUE-FLOW.md) for actors and cash/evidence boundaries, [LEAD-PLATFORM.md](LEAD-PLATFORM.md) for the proposed engineer marketplace and API/SDK branch, and [VISIBILITY-REDEMPTION.md](VISIBILITY-REDEMPTION.md) for W search placement.

| Artifact | Purpose |
| --- | --- |
| [source-manifest.json](source-manifest.json) | SHA-256 and byte count for 88 selected EA files; source workspace has no Git HEAD |
| [crosswalk.json](crosswalk.json) | EA Product/Project, six Goals, seven Capabilities, ten Inquiries, fifteen Designs, 27 Roles and 124 unapplied relation proposals |
| [task-catalog.json](task-catalog.json) | One candidate miner task family per Design; distinct W execution and U advance tests |
| [VALUE-FLOW.md](VALUE-FLOW.md) | Participant, Product, miner, sponsor and customer value/transaction paths |
| [LEAD-PLATFORM.md](LEAD-PLATFORM.md) and [proposal record](lead-platform-proposal.json) | Optional qualified introductions, engineer E rewards, web/API/SDK operations and buyer access gates |
| [VISIBILITY-REDEMPTION.md](VISIBILITY-REDEMPTION.md) and [service record](visibility-service-proposal.json) | Candidate W redemption for a labeled promoted search slot, with relevance, capacity and cash-cost gates |
| [integrated_scenario.py](integrated_scenario.py) and [result](fixtures/integrated-results.json) | Five synthetic end-to-end research, Product and economics cases |
| [lead_loop.py](lead_loop.py) and [result](fixtures/lead-loop-results.json) | Five synthetic cohorts, W promotion cost and the minimum paid-introduction threshold for recurring commitments |
| [validate.py](validate.py) | Checks source hashes, complete crosswalk/task coverage and exact simulation result |

Run from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 validate.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q test_integrated_scenario.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q test_lead_loop.py
```

`build_model.py` regenerates the manifest, crosswalk and catalog after an intentional EA source-cut review. A changed source does not silently update the stored candidate. The crosswalk retains missing EA relation proposals as visible gaps. The lead branch is a Network proposal and does not change EA's disabled employer access in the MVP. All task offers, lead sales and research findings remain absent.
