# Shared documentation site

The guide, reference library, expanded essays, guided learning pages and Craft
share local search. The original Craft article stays in the adjacent
`craft-documentation-proposal` directory. Keep the two directories together.

`start-here.html` is the short introduction to the enduring model. Its editable
source is `templates/start-here.html.in`; `start_here.py` binds the shared icons,
reading time and source references. The main renderer rebuilds it with the other
pages. Keep it free of implementation status and test counts. The existing guide
and reference snapshots retain their own dates and scopes.

The guide includes a static Start here sidebar link. Shared `site-search.js`
also supplies that link to the guide, essays/reference and Craft
sidebars, so every enhanced documentation page has the same entry point.

## Rebuild

The product landing page is `index.html`; research, culture and ambition live in
`research.html`; the expanded product introduction is `company-brain.html`.
Edit `templates/lab-landing.html.in`, `templates/research-landing.html.in` and
`templates/company-brain.html.in`. `research_pages.py` supplies their shared
header, footer, reading time and incident values. Their KEP adapter is
`assets/research-site.css`; keep the original KEP tokens, logos and orb unchanged.
All three pages are built by the main renderer, appear in shared search, and are linked
from documentation sidebars. The research and positioning rationale is in
`research/research-landing-editorial.json`.

Keep the homepage centered on the company brain: its purpose, connected records,
agent context and routes into the documentation. The research identity and
longer horizon have their own page. Top navigation makes both reachable.
`assets/research-navigation.js` sends the former homepage's research, culture,
name and alignment bookmarks to their corresponding sections in `research.html`.

The homepage role map is maintained in `templates/company-brain-map.html.in`,
`assets/company-brain-map.css` and `assets/company-brain-map.js`. Its five branches
show people, agents, knowledge, work and decisions around durable project state.
It is an explanatory role map, not a declaration of new ontology edges or an
operational console. Native buttons focus one branch and explain its role; the
whole map remains readable without scripts. `research_pages.py` binds the shared
Work and Agent glyphs and supporting icons. The following knowledge/work/decision
flow is maintained in the homepage template. Keep the same colors and icons in
both visuals. The incident remains a separate walkthrough.

Keep organizational ambition, product design and demonstrated results distinct.
The alignment section expresses research questions; it does not establish model
alignment. Company-brain language refers to persistent project knowledge.
Machine agent sessions remain ephemeral. Keep the incident fictional and bind
its facts to `research/incident-extraction-case.json`.

From this directory, run `python3 render_article.py` after editing the Lab
article templates. It also rebuilds `assets/site-search-index.js`.

To rebuild Craft after editing its Markdown source, run
`python3 ../craft-documentation-proposal/tools/build_article.py`.
It also rebuilds the same search index.

To refresh only the search index, run `python3 build_site_search.py`.
The builder reads the generated public HTML. It includes the guide's topic
headings, the expanded essays and their section headings, exact catalog record
bodies, consolidated governance chapters, Craft sections and subsections, and the source
library. Private source trees and the separate Craft editorial proposal are not
indexed. The two guide filenames point to one canonical search destination.

## Local delivery

The index is a JavaScript asset rather than a fetched JSON file. Search therefore
works when opened through `file://` as well as from a static server. No remote
search service, storage credentials or build server is required. URLs resolve
relative to the index asset and preserve record identities and subsection links.

The header search covers all documentation. The catalog's own search retains its
scope and ranking for browsing records in a selected catalog.

Navigation and search are explanatory interfaces. They do not change the source
records, their acceptance, or Craft's development status.

## Guided reading paths and reference introductions

`incident-walkthrough.html` follows the shared fictional incident. Its definition
anatomy, record connections and session handoff are explanatory visuals. The
later review route is conditional; it does not add completed recovery or closure
to the case. `concept-comparisons.html` distinguishes the core responsibilities,
including Craft's pure Calculation and state-changing Operation.

Edit their content in `templates/incident-walkthrough.html.in` and
`templates/concept-comparisons.html.in`. `learning_docs.py` binds definition
links, shared icons and the documentation shell. Both pages are rebuilt by
`render_article.py` and indexed in shared search. Navigation from the guide, essays, reference and Craft includes both reading paths.

`reference_reading.py` adds source-derived applicability, schema fields and exact
connection patterns to catalog entries. Selected core concepts also have reviewed
incident examples and common mistakes. These introductions do not replace the
unchanged normative statements, schema constraints or ordered pair tables.
After editing the reference renderer, run `python3 render_series.py`, then
`python3 render_article.py`. Do not edit generated reference HTML by hand.

## Governance lives in the guide

Authority, provenance and lifecycle have one canonical explanation each:
`governance-lab-reference.html#governance`, `#evidence` and `#change`. The former
standalone articles are generated redirects and are excluded from search. The
guide sidebar lists each chapter once. Expanded essays keep their separate role
as deeper discussions.

The unique authority-surface, provenance-boundary and lifecycle-continuity
material is maintained in the `templates/governance-*-additions.html.in` and
`templates/governance-lifecycle-continuity.html.in` fragments, with the shared
authority context. Existing incident examples and definition presentations
remain in the guide. The earlier article templates are retained as source
history; the renderer no longer publishes them as separate articles.

`governance_consolidation.py` generates the three legacy redirects. Their known
section identities come from `research/governance-legacy-sections.json`; targets
are checked against the generated guide. Redirects preserve query strings and
map known fragments; unknown fragments fall back to the corresponding chapter.
Without JavaScript, a timed redirect and manual link reach that chapter.

Existing guide subsection IDs were stabilized before inserting content. Keep
those explicit IDs when editing headings so bookmarks and search destinations
remain stable. Rebuilding the article also rebuilds the redirect maps and shared
search.

### Generated company brain medallions

The landing map uses six transparent PNG illustrations in `assets/brain-medallions/`: people, agents, knowledge, work, decisions and the shared state hub. These were generated with the built-in imagegen tool; the subjects and source paths are recorded in `research/brain-medallions-generation.json`. Keep labels as live HTML and preserve the alpha channel. The smaller explanatory flow retains its original line glyphs. Source and interaction behavior remain in the existing map template, stylesheet and script.
