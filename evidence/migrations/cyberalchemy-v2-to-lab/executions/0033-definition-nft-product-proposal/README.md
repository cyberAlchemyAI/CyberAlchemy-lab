# Definition NFT — proposed Product rules

Exact shared definition -> preview card and metadata -> verify wallet and stored bytes -> separate mint confirmation -> recorded outcome.

These are proposed behavior choices for review. They have not been imported or recorded as accepted.

| Choice | Proposed behavior | Why it matters |
| --- | --- | --- |
| Product | Standalone Definition NFT Product attached to a completed KEP share. | Keeps NFT representation separate from knowledge ownership and permissions. |
| One mint | One finalized NFT per exact definition version on this Product's devnet, across all sharing users. Repeated requests return the existing result. | Defines exactly what “one NFT” means; another sharer cannot mint another copy under this rule. |
| Retry | An uncertain result blocks a new attempt until reconciled. A proven failure requires fresh confirmation. No automatic replacement, burn or successor mint. | Prevents a delayed success from producing an unintended duplicate. |
| Representation | Deterministic SVG card plus versioned JSON metadata. Show only the version commitment by default; extra display fields require explicit approval. | Makes the exact output reviewable without publishing private definition content automatically. |
| Storage | Content-addressed local copy for review/export. Mint requires an explicitly configured retrieval location and exact media/metadata readback. No permanent availability promise. | A mint must reference checked bytes; storage lifetime must not be implied. |
| Wallet | Separately authenticate the sharing identity and verify a one-use wallet challenge bound to this exact request and expiry. The verified wallet receives and pays. | Wallet control and Knowledge Identity remain distinct. |
| Confirmation | Show preview, wallet, devnet, fee estimate/ceiling and availability limit. Changed commitments or exceeded fee ceiling require new confirmation. | Generation is not permission to mint or charge a network fee. |

Decline -> no transaction and no mint fee. This does not promise that hosting or representation generation is universally free.

[Exact proposal](proposal.json) includes all 20 missing semantic reference proposals. Proposed Product and Capability shapes validate. These are semantic descriptions, not executable API or wallet contracts; no cryptographic security or operational readiness is claimed.

[Verification](verification.json) records consistency, exact reference coverage and unchanged active storage. Reproduce with `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0033-definition-nft-product-proposal/verify.py`.

## What approval would mean

Approval selects the Product rules above so they can become the candidate import's requirements. It does not authorize an actual mint, payment, publication of private content or deployment. Those effects remain tied to their exact future requests.

These choices require review because the source explicitly left them undecided; the general instruction to finish the migration did not select their behavior.

## Open questions

Accept or revise these rules. After selection, validate the successor candidate against the complete graph and import it. Runtime provider, token-program/metadata adapter, executable schemas and security implementation remain separate work.

Current migration remains **40 imported / 1 blocked / 3 reference examples / 1 excluded**. The active inventory and store remain run 0032.
