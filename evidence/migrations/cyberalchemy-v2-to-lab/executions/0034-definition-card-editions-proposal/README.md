# Definition NFT — collectible card editions

Definition version -> approved base image -> named visual variants -> numbered copies -> separately confirmed mint -> card transfer or trade.

The user clarified that “drop” means collectible versions of the same image, like cards. The revised Product proposal supports configurable variant names and edition sizes. It supersedes the earlier one-NFT-per-definition restriction.

A variant is a visual treatment of the base image. An edition is the permitted copies of that variant. A copy is identified by collection, variant and serial number. Retrying a mint keeps that copy identity; minting another configured copy is an intentional edition, not a duplicate retry.

## Next configuration

Choose the base image, define the visual variants and set each edition size. Preview these before minting. The proposed v1 rule freezes the collection manifest before the first mint, so later changes become a clearly identified new collection. The user has selected configurability and collectible variants, but has not selected particular artwork, numbers or the freeze rule.

Cards can be transferred or traded. Receiving the NFT does not grant definition ownership, copyright, licenses or KEP decryption access. Marketplace, pricing, royalty and exchange mechanics remain separate choices, not silently selected defaults.

[Revised proposal](proposal.json) includes updated required behavior and all 20 semantic reference proposals. No actual mint, trade, media publication or runtime work was performed. Initial minting still targets the sharing user's verified wallet; later transfers belong to the NFT holder's separate authorization.

[Verification](verification.json) checks consistency and unchanged active storage. Current inventory remains **40 imported / 1 blocked / 3 examples / 1 excluded**.

## Open questions

Collection freeze policy, exact art/variants/edition sizes and trading mechanics remain explicit proposed or unselected choices. Complete the Product-rule selection before treating this as an imported, settled capability. No artwork or edition size is inferred from the discussion.
