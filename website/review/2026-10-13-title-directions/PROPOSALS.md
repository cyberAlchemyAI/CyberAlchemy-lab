# Title and hero proposals

13 October 2026. Four design studies for the homepage. The user selected and authorized applying the centered opening with company brain positioning, Craft and the background orb. That composition is now in the maintained homepage template and the rebuilt website. The other directions remain alternatives.

## What repeats

The homepage's main headline and four main section headings use explicit HTML line breaks. Its four section titles request the same serif stack, weight 400 and approximately 63 px at the observed 1440 px viewport. The repeated treatments combine paired phrases, imperatives and similar framing. The wording changes while the visual hierarchy stays almost identical.

The 1440×1000 browser observation places the main headline at y≈551, the secondary map heading at y≈290 and the primary actions at y≈1090. The opening section is about 1,449 px tall. Centering the copy beside the complete role map gives the secondary heading an earlier position and pushes the entry action below the first viewport. These measurements describe that viewport and edition; they are not reader-study results.

Existing specific titles such as “Start here”, “Agent Instance” and “Choosing better experiments” already identify their subject. Keep them in the appropriate hierarchy.

## Revised compositions

The user identified a structural problem in the first proposals: they all began with content on the left and an image or secondary surface on the right. The revision changes the reading sequence and the use of the page width. The earlier proposal files and observations are retained in `iterations/01-split-layout/`.

| Direction | Proposed opening | Composition | Where it fits |
| --- | --- | --- | --- |
| 1. Centered opening | An open company brain | Company brain positioning, a short Craft explanation and actions share one centered axis. The orb fills the background. A topic band and example follow below. | Selected homepage direction, refined for review |
| 2. Full-width cover | Before the next agent starts | A large editorial title spans the cover. The orb fills its background field. Reading follows below. | Essays and selected research features |
| 3. An incident, unfolding | Why is this export missing 200 records? | Scope and evidence come first. The question and investigation stages follow vertically. | First worked example in the guide |
| 4. Index-led entrance | A shared model for knowledge and work | Large, full-width topic rows form the opening, using the dark KEP palette. No separate image. | Documentation-focused homepage alternative |

The comparison includes a switch to use the current hero headline in all four layouts. It lets the user compare typography and composition without requiring a choice of new wording first.

## Recommendation

The user selected the centered opening and asked to include “open company brain”, Craft and the cover’s orb. Direction 1 now incorporates those choices. The prototype explains Craft as the software-design product within the Lab and uses a full-field orb behind the centered content. The previous centered edition is preserved in `iterations/02-distinct-compositions/`. Direction 2 remains an essay treatment, and direction 3 remains an incident explanation.

In direction 1, the primary action follows the purpose statement. In direction 4, the topic rows are the main actions. The orb contributes identity to the centered opening and editorial cover without occupying a separate column. The detailed role map belongs in the explanation after the opening. Retain the current-status and source entrance when implementing a selected direction.

## A heading system for the whole site

- Homepage: product identity and a short purpose statement. Section titles describe what the reader will find.
- Guide: direct subjects such as “Authority and definitions”, “Project state” and “Agent sessions”. Supporting headings identify scope, steps or questions.
- Practical guides: task titles such as “Prepare an incident assessment”. Inputs, steps, output and review carry the smaller hierarchy.
- Expanded essays: vary the form with the essay. Examples include “Who decides what complete means?”, “Knowledge between sessions” and “What an observation establishes”. Avoid turning every essay into a question.
- Reference: retain exact canonical names such as “Agent Instance”. Type, version and standing have their own metadata.
- Craft: title the actual software responsibility, such as “Capacity decisions and reservations”. Calculation stays pure; Operation changes state.
- Research: a literal entrance, “Research at CyberAlchemy”, followed by titles naming a specific question, method or investigation.
- Robot series: retain concrete existing titles and give them the essay hierarchy. Speculative work stays distinguished from observed results.

Use natural wrapping instead of hard line breaks. Apply the same palette and navigation across families. Set type by its role: restrained sans serif for navigation and guide headings; larger editorial type for chosen features; compact record titles for reference.

## Research and its application

- [Pentagram's editorial practice](https://www.pentagram.com/editorial-design) describes combining a familiar setting with variation across stories. This supports a shared identity with different page compositions. It is design guidance, not measured proof of this proposal's usability.
- [Pentagram's Isomorphic Labs project](https://www.pentagram.com/work/isomorphic-labs) uses an underlying informational grid with typography, imagery and a restrained core palette. This informs the atlas direction and the use of a common structure behind varied expression.
- [Stripe Press](https://press.stripe.com/) presents titles with different shapes, including short topic names, questions and longer subjects. I used this as an editorial reference for essay naming, not as a template to copy.
- [Linear Method](https://linear.app/method) combines an editorial entrance with concrete practice names. The site's different title roles inform the separation between a large opening and useful smaller headings.
- [Conductor's quickstart](https://docs.conductor-oss.org/quickstart/index.html) uses a direct task title and compact supporting headings. This matches the user's existing documentation direction.
- [Anthropic Engineering](https://www.anthropic.com/engineering) names specific methods, investigations and results. This informs research/essay specificity.
- [W3C's heading guidance](https://www.w3.org/WAI/WCAG21/Understanding/headings-and-labels) requires headings to describe topic or purpose. A creative feature title still needs to orient its reader.
- [Shulman, Markowitz and Rogers (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11152133/) examined news headline experiments and found a preference for simpler writing among general readers. The findings support attention to familiar words and readable phrasing. They do not determine the right font, prove documentation comprehension or validate one Lab layout.

## Review boundary

The preview uses repository-owned KEP assets, existing palette values and local font stacks. Browser observations cover the prototype at desktop and compact widths. They are presentation inspections rather than a conformance claim or a usability score. Selection should consider identity, specificity, reading sequence and how each family connects to the Lab model.

The centered homepage implementation updates the maintained template, scoped homepage styles and adopted editorial entries together. It moves the role map into the model explanation, adds a Craft introduction and documentation route, and rebuilds search and sharing metadata. The full build completed successfully. Desktop and compact browser observations are stored under `output/playwright/applied-centered-homepage-20261013/`. The frozen reviewed release, exact reference bodies and Lab authority records remain preserved.
