# Long-case inputs for native LL/FO investigations

Date: 11 October 2026. Input preparation only. No strategy execution, reader study, game implementation, listening analysis or efficacy result is recorded. CASES.json is the machine-readable bank; SOURCES.json records actual access. Original fiction, reused design seeds, real documentary records and synthetic activity fixtures have separate provenance.

## Frozen literary selection

Criteria were written at 18:40:07 UTC before new comparison retrieval and passage choice. Hold Mary Shelley and original English constant; include a public-domain novel first published in 1818–1833 with a dated primary title page or institutional record; choose the earliest accessible novel after Frankenstein. Take exactly the first 160 whitespace-delimited prose words of main Chapter I, excluding headings/prefaces, normalizing whitespace only. Match position and length, not a favored feature. The targeted search found Valperga; the earliest-eligibility criterion was not verified through an exhaustive bibliography. Keep that limitation.

The author already knew the supplied Frankenstein anchor and cannot be blind. A/B masking cannot remove recognition. No validated canonicity measure, curriculum data or historical readership corpus exists here. “Less canonized” is a curatorial candidate label. Native work can code source features and missingness; it cannot fabricate reader responses or infer endurance causes.

## N01 — The Dry Platform

Newly authored fiction for this bank; no historical originality claim. Applicable inputs: LL01, LL03, LL04, LL05, LL06, LL11, LL12, FO08.

**Disclosed ending:** All twelve people survive dry and uninjured. Four seed cases are lost; the next planting uses two of six planned plots.

Before the river rose, Mara pinned the gate diagram beside the gauge. Twelve people waited above the courtyard. Below them stood six seed cases. Opening the sluice would save the platform and wet the courtyard; moving the cases first required two helpers for eight minutes. Ivo pointed to the cart. Mara pointed to the four people still waiting for blankets. She would not borrow their helpers. At 06:05 she opened the gate. Water took the four low cases. Two on a high shelf stayed dry. By 06:12 all twelve people were wrapped and safe. At 06:20 the flood peaked below their boots. The next day, four germination checks failed. At the next planting Ivo marked out two plots, leaving four stakes without seed. Mara returned the diagram to its hook. Ivo left the empty cart beneath it.

**Fixed event ledger** (authority for both narrators):

- E01 / 06:00: A public gauge predicts the flood peak at 06:20. Twelve evacuees wait on a raised platform; six seed cases lie in the lower courtyard.
- E02 / 06:02: The published gate diagram says opening the sluice keeps the platform dry but floods the courtyard. A two-helper cart move takes eight minutes. Moving helpers delays blankets for four evacuees by four minutes; no extra injury is guaranteed.
- E03 / 06:04: Ivo asks Mara to cart the six cases before opening the sluice. Mara declines because she will not withdraw the two helpers from warming duty.
- E04 / 06:05: Mara opens the sluice. Nobody carts the cases.
- E05 / 06:06: Water reaches four low seed cases. Two cases already on a high shelf stay dry.
- E06 / 06:12: All twelve evacuees are dry and have received blankets. Nobody is injured.
- E07 / 06:20: The flood peaks. The raised platform remains dry.
- E08 / Next day / next planting: The four soaked cases are discarded after failed germination checks; the two dry cases remain viable. The next planting uses two of the six originally planned plots.

**Mara's goal:** Keep all twelve people safe without withdrawing warming helpers during the flood window.

I wanted all twelve people safe without withdrawing their warming helpers. I posted the 06:20 forecast and the diagram: opening the gate protected the platform and flooded the courtyard. I knew six seed cases were below it, and that two helpers could cart them in eight minutes, delaying four people's blankets by four minutes. At 06:04 Ivo asked me to move them first. I declined. At 06:05 I opened the sluice without a cart move. Four low cases soaked; two high cases stayed dry. By 06:12 everybody was dry, wrapped and uninjured; the 06:20 peak left the platform dry. Later four cases failed their germination checks. Two remained viable, so only two of six planned plots were planted. My decision met the immediate goal I chose. That does not make the lost seed disappear.

**Ivo's goal:** Preserve six viable seed cases while accepting the declared temporary blanket delay.

I wanted all six seed cases viable as well as all twelve people safe. I accepted a four-minute blanket delay for four people if two helpers carted the cases during the eight minutes before the 06:20 flood peak. Mara had posted the forecast and the gate diagram: the platform would stay dry and the courtyard would flood. At 06:04 I asked for the cart move. She declined. At 06:05 she opened the sluice; nobody moved the cases. Four low cases soaked, and two high cases stayed dry. By 06:12 everyone was dry, wrapped and uninjured. At 06:20 the platform remained dry. Four cases later failed germination checks. The two viable cases supplied two of six planned plots. Her chosen immediate goal was met. My goal was not. I cannot claim from this record that my proposed delay would have caused no discomfort.

Both accounts preserve every ledger event. Perspective changes evaluation, not available action. Ivo's alternative was not performed; its declared blanket delay does not prove its injury outcome.

Keep the ledger, ending and chosen narrator identical while changing only the evaluative phrase:

- Literal: A mixed outcome: twelve people dry, four seed cases ruined, two of six plots planted.
- Ironic: A perfect victory: twelve people dry, four seed cases ruined, two of six plots planted.

Each overlay has 15 words and identical factual information. Irony recognition and comprehension are unknown. The bank's disclosed ending prevents an unspoiled first encounter for anyone who reads it. A later disclosure comparison requires separately frozen introductions and fresh exposure.

## G01 — Arrival controls consequence

Reuses the supplied Creature's Errand and four GF paper instances. This is exposure to existing seed material, not independent discovery; no output count is added. Source: LG02 in literature-longevity WORKED-EXAMPLES.md and GF01–GF04 in field-opening WORKED-FAMILY.md. Applicable inputs: LL02, LL05, LL06, LL07, LL08, LL09, LL12, FO01, FO02, FO03, FO04, FO05, FO06, FO07, FO08.

Envelope: choose one hero from three; three boss stages; mid-run items; separate manual and authored-autoplay conditions; at most six ordered rules, first true predicate selecting one legal action per tick.

**Frozen local rules:**

1. One courier carries exactly one charge. Its arrival at a dock consumes that charge and commits one public consequence exactly once. Courier death destroys the charge and is not arrival.
2. On each integer tick: apply the hero's legal action; apply damage/death; recompute the courier's shortest unblocked route; move the courier one cardinal cell; commit arrival; update public cooldowns. A killed courier cannot also arrive. No retroactive outcome changes.
3. Use a 9 by 5 unit grid, coordinates x=0..8, y=0..4. Courier starts (4,2), red dock (0,2), blue dock (8,2), hero (4,4). All cells are initially open. Distance is shortest cardinal path length. Choose the nearest reachable accepting dock; equal distance favors red. Among equal routes use left, up, right, down priority.
4. Red arrival spawns exactly two contact attackers; blue arrival supplies one defensive charge. These are declared consequences, not evidence of balanced value. Neither dock changes acceptance secretly.
5. Before tick 1 allow up to two walls, each costing one shared construction token. Walls cannot occupy a dock, courier or hero cell and cannot block both docks. Wall placement is irreversible during the stage.
6. Knockback moves the living courier two cells in a chosen cardinal direction, stopping before a blocked cell or grid edge; range is Manhattan distance at most three from the hero. It costs one finite charge, with a four-tick cooldown. Hero movement is one open cardinal cell per action.
7. The courier has two hit points; a hero strike within distance three removes one hit point and costs that tick's action. Reflect affects ordinary contact attackers and does not redirect the courier. Every hero must have a public legal route to strike or redirect; no courier immunity.
8. Public observation exposes positions, walls, route lengths/reachability, charge status, dock acceptance/state, hero resources and cooldown. Autoplay cannot use an unexposed shortest-path oracle.
9. Full boss/contact combat, hero-specific abilities, starting health/charges and item schedules are not supplied as an implementation. Freeze them equally across compared conditions before any survival/performance claim. The local rules define the courier micro-system only.

**Allowed axes and ablations:**

- Destination (GF01): red reinforcements versus blue defensive resource; ablate to identical dock consequences.
- Time (GF02): one dock; disclose an accepting boss-phase window before play. Arrival within it grants one defensive charge; outside it spawns two attackers. Specify window and finite delay budget; no indefinite free stall.
- Capacity (GF03): one-slot dock, two couriers, disclosed discharge schedule. Second arrival before discharge overloads into two attackers. Specify simultaneous-arrival order by courier ID; unlimited capacity is the ablation.
- Authorization (GF04): an earlier public action supplies one expiring token. Arrival consumes it once to reduce a declared boss shield amount; no token adds that amount. Specify token lifetime and shield amounts before use. No hidden authority.
- Vary one axis at a time for interpretation; presentation can vary without changing legal actions, observation, costs or rewards. Multiple axes require an explicit combined event order.

Competent ordinary equivalents are payload/escort routing, timed delivery, finite-buffer queues and keyed delivery with a deadline. These may explain the whole contribution. No balance, survival or enjoyment result exists.

**Future independent-creator assignment:** give only the CASES.json creator_payload, with GF01–GF03 examples and shared obligations. Reserve GF04 authorization for the evaluator. A fresh creator must not read this bank, WORKED-FAMILY, parent history or the evaluator holdout. The author and exposed agents cannot claim withheld generalization. This assignment is prepared, not executed; assigned creation is not cultural uptake.

## M01 — Future Classics documentary pack

Actual documentary evidence for FO08–FO10 and LL01/LL11. Include all supplied FS01–FS09, not only successes. This predates the bank and remains a convenience sample, not a music-lineage corpus. Freeze role codes for a later native audit: catalog identity/credits; attributed testimony; editorial claim; unknown. Promotional copy and current tags can be retrospective.

- D01 / 2006-09-10 / FS06, FS07: Liquid Soul, Synthetic Vibes. Label catalog describes progressive trance; artist catalog gives the same release date and progressive-trance/psytrance tags. Related earlier work; tag/copy creation dates and exact sonic relation to the narrower proposed branch are unknown.
- D02 / 2015-04-15 / FS01: Iboga's authorized Beatspace Bandcamp catalog lists Vini Vici, Future Classics, nine tracks and this release date. Current promotional catalog; no audio listened to.
- D03 / 2015-04-13 / FS02: Supplied Beatport record identifies Future Classics / Iboga / IBOGACD93 with this release date. Retain April 13 and April 15 as an unresolved metadata discrepancy. Direct browser reopen failed here; April 13 is inherited from the inspected local source package, not freshly confirmed.
- D04 / null / FS03: Tomorrowland Academy biography describes old-school sound paired with progressive ideas and attributes a 2015 breakthrough and wider exposure. Public biography read; membership video not watched. Reported rankings not independently audited; its publication date is not resolved.
- D05 / 2017-04-16 / FS04: Supplied artist interview describes exploring new ideas through Vini Vici after Sesto Sento and bridging audiences. Browser direct reopen failed; indexed introduction confirms article identity/date, while detailed answers remain inherited package evidence. Do not relabel the album a Sesto Sento release.
- D06 / 2017-12-22 (modified 2020-11-18) / FS08: TRILLVO editorial introduction says the album created a subgenre. Artist answers separately describe scene growth, new-country exposure and Dreamstate as a bridge. Current page displays original and modification dates; exact date of introduction wording is unknown. The invention assertion belongs to the introduction, not an artist answer.
- D07 / 2018 / FS09: Supplied Nocturnal Times interview attributes mixing psytrance with other electronic music and a perceived opening amid repetitive big-room sounds. Direct browser reopen failed; current bank inherits this account from FS09. No audience or market-share effect is measured.
- D08 / 2020-12 / FS05: Trancentral artist answers describe a professional shift from Sesto Sento and a Life is a Remix project involving favored artists, including Liquid Soul and other established acts. Direct HTML passages read. The 2020 remix project does not prove every collaborator descends from the 2015 album; artists also describe their own earlier influences.

Primary links: [Future Classics label catalog](https://iboga-beatspace.bandcamp.com/album/vini-vici-future-classics-iboga-records), [Beatport](https://www.beatport.com/release/future-classics/1486451), [2006 label catalog](https://iboga-beatspace.bandcamp.com/album/liquid-soul-synthetic-vibes-iboga-records), [2006 artist catalog](https://liquidsoul.bandcamp.com/album/synthetic-vibes), [TRILLVO editorial and artist answers](https://trillvo.wordpress.com/2017/12/22/viniviciinterview/), [Trancentral artist answers](https://trancentral.tv/2020/12/vini-vici-life-is-a-remix-interview/), [Tomorrowland biography](https://academy.tomorrowland.com/artist-advice/q-a-with-vini-vici-2). Exact URLs/access for failed reopens are in SOURCES.json.

**Observed relations:** the 2015 track list credits Liquid Soul, Zyce and Solar Kid on Come In Peace (Vini Vici remix). The 2020 artist interview describes a collaborative remix project. Credits support reworking or collaboration; they do not identify descendants, prove original-track chronology, or make earlier artists offspring of the 2015 album.

**Frozen documentary classification:** code roles and date certainty in bins before April 2015, April 2015, and after April 2015 through December 2020. Keep sonic branch membership and invention/uptake claims unknown unless inspected evidence supports them. Missing: exact branch definition; systematic predecessors; independent descendant testimony; rival branches; dropouts; consistent audience denominator; multi-year market share; audio annotations. Missing is not zero. Historical invention, access and wider recognition require separate timelines; current chronology alone does not establish causal influence.

**Truthful framing input:** “A 2015 psytrance album by Vini Vici on Iboga Records” versus “The creators titled their 2015 psytrance album Future Classics.” Future status is an interpretation to investigate, not verified acclaim. These descriptions may differ in information and length; do not call them a matched causal framing stimulus without further preparation.

Synthetic lineage graphs can only be separately tagged audit fixtures. Never insert generated descendants into observed_relations or call them observed musical lineage. Actual dropout, market-share or persistence conclusions remain unsupported.

## L01 — Same-author opening-window comparison

Frankenstein (1818 edition) and Valperga (1823, volume I). Valperga is a curatorial less-canonized candidate, not a measured canon group. The earliest-accessible-novel criterion was searched through a targeted Gutenberg/UPenn discovery, not an exhaustive bibliography; earliest eligibility is not certified. Same author, original English, five-year first-publication gap, main Chapter I opening, 160 words each. Gothic/scientific fiction versus historical fiction is a genre mismatch; narrator person and subject also differ. Neither historical reach nor present familiarity is controlled.

Frankenstein uses the explicit PG41445 1818 transcription, not the unresolved supplied PG84. Its transcribed title page and transcriber note identify 1818. Valperga's volume-I title page identifies London, G. and W. B. Whittaker, 1823. Digital availability is observed now; historical availability, missing novels, edition history and readership were not audited.

**Window A — Frankenstein; Or, The Modern Prometheus (1818)**, 160 words. Volume I, Chapter I, opening three paragraphs, prose words 1–160; begins 'I am by birth' and ends 'poverty and oblivion in'. [Primary text](https://www.gutenberg.org/files/41445/41445-h/41445-h.htm).

> I am by birth a Genevese; and my family is one of the most distinguished of that republic. My ancestors had been for many years counsellors and syndics; and my father had filled several public situations with honour and reputation. He was respected by all who knew him for his integrity and indefatigable attention to public business. He passed his younger days perpetually occupied by the affairs of his country; and it was not until the decline of life that he thought of marrying, and bestowing on the state sons who might carry his virtues and his name down to posterity. As the circumstances of his marriage illustrate his character, I cannot refrain from relating them. One of his most intimate friends was a merchant, who, from a flourishing state, fell, through numerous mischances, into poverty. This man, whose name was Beaufort, was of a proud and unbending disposition, and could not bear to live in poverty and oblivion in

**Window B — Valperga: or, The Life and Adventures of Castruccio, Prince of Lucca (1823)**, 160 words. Volume I, Chapter I, opening three paragraphs, prose words 1–160; begins 'The other nations' and ends 'the Guelphs and the Ghibelines were'. [Primary text](https://www.gutenberg.org/cache/epub/63337/pg63337-images.html).

> The other nations of Europe were yet immersed in barbarism, when Italy, where the light of civilization had never been wholly eclipsed, began to emerge from the darkness of the ruin of the Western Empire, and to catch from the East the returning rays of literature and science. At the beginning of the fourteenth century Dante had already given a permanent form to the language which was the offspring of this revolution; he was personally engaged in those political struggles, in which the elements of the good and evil that have since assumed a more permanent form were contending; his disappointment and exile gave him leisure to meditate, and produced his Divina Comedia. Lombardy and Tuscany, the most civilized districts of Italy, exhibited astonishing specimens of human genius; but at the same time they were torn to pieces by domestic faction, and almost destroyed by the fury of civil wars. The antient quarrels of the Guelphs and the Ghibelines were

The 160-word windows may end mid-sentence by the frozen rule. Native coding may identify perspective, evaluation, causal connection, contrast and attributed claim, citing exact words and retaining disagreement. Compare the same features against a classics-only inventory. If a suspected feature is absent, do not replace the opening to improve the finding. No reader ratings, familiarity, voluntary return, canon score, feature discrimination across a population or historical causality may be invented. Metadata masking is possible for a fresh coder, but the author is unblinded and the text can be recognized.

## F01 — Completion and return classification fixtures

Explicitly synthetic inputs for LL01/LL12; seven-day window. They are fictional records, not observed players.

- S1: Completed three bosses on day 1; reports satisfaction; had access all seven days; no return by day 7; recalls the cost decision.
- S2: Stops at stage 1 on day 1 and reports frustration; access unavailable on days 2–7; no observed return.
- S3: Completes on day 1; returns voluntarily on day 2 with a changed routing plan and the same rewards; no further observation after day 3.
- S4: Still playing an unfinished run at the day-7 cutoff; no satisfaction or reason-for-stopping report.

Native agents can audit event definitions and incomplete observation. These fixtures supply no measured retention, causal discovery effect or population prevalence.

**Source access:** targeted browser retrieval was performed for the primary literary windows and existing music documentation. Some direct reopens failed; SOURCES.json separates current access from inherited package evidence. No listening, human reading, game playing or strategy comparison was performed to create these inputs.

