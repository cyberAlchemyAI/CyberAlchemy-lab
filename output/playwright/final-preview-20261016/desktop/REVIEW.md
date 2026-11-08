# Independent desktop and tablet review

Scope: isolated preview on localhost:8780. Read-only; no build, source edit, deployment, commit or push.

Examined 39 unique valid regular views (all 27 recomposed pages, six reading paths, retained library/catalogue, hackathon, robot series, concept comparisons and exact Actor reference), at 1440 and 1024 in light and dark: 156 layout states. Metrics in layout.json; all39 full-page screenshot captures visually reviewed via contact sheets. No horizontal overflow or loaded-image failure in these normal page states. Initial dataset-only theme metrics are layout evidence, not logo evidence.

Separately opened ten retained article disclosures and inspected their figure geometry and up to three figure viewport captures each. Two runtime routes and reader-study were included in route geometry. Full 52kpx Craft capture timed out and was discarded; viewport captures and decoded SVG figures are the authority.

Confirmed issues reported to parent:

1. P2 company-brain retained .brain-knowledge-cycle .cycle-icon svg: 765px black filled icons, diagram2835px high at1440. Missing scoped original company-brain-map styles. company-cycle-before.png.
2. P2 company-brain .company-brain-map: missing node/connection styling, giant filled SVG branches and poorly arranged narrative. retained-1-figure-0.png. .incident-strip dt/dd also concatenate (Declared input10,000).
3. P2 research retained .research-loop and .brain-overview: concatenated stages and labels; action links touch. retained-7-figure-0/1.png.
4. P2 search head: Clear search and positioned Close touch with mismatched vertical alignment; label/select have no gap. search-light.png. Search itself returns9 results and Escape dismisses and restores input focus.
5. P2 retained Craft/model diagram-reading controls stay hidden; figure says use guided reading while generated page omits diagram-reading.js. Existing Open diagram SVG links render correctly. Reuse compatible existing script to restore guided reading.

Headers separately reviewed at both desktop/tablet widths and themes using real StorageEvent theme sync; correct theme logos and unchanged approved design. At1024 Menu opens and Escape closes. Craft first3 SVGs decoded and inspected; earlier blank lazy captures are not asset failures (craft-figure-*-loaded.png supersede).

Awaiting focused post-fix confirmation only.

## Focused confirmation after fix batch

1440/1024, light/dark: company role-map and cycle, research brain layout, search. Confirmed restored map nodes/outline connections; cycle icons29px instead of765px and total figure381px desktop. Search Clear/Close align at same Y,44px tall,12px gap; scope label gets its own row. Theme logos synchronized; no script errors. Research overview stages/labels/actions now separated.

Guided-reading interaction is data-diagram-mode="guide" (not "guided"): at both widths, first1/3, Next2/3, Whole restores full SVG. Company-map People selected aria-pressed=true, second click resets false. These behaviors pass; final-guided-raw.txt.

Two final small refinements reported: top-align cycle parts so Work does not sit16px below peers;14px/margin-top16px for research figcaption. Parent also received exact .retained-reading section.lab-section#lab source for panel-edge flush content (padding64px0, inner wrappers0padding). Awaiting tiny final CSS confirmation only.

## Final desktop/tablet verdict

Confirmed final tiny CSS in browser at1440/1024. Desktop cycle content starts share identical Y432px; tablet follows intentional vertical sequence,29px outline icons. Research tinted section preserves original surface with24px inner insets; caption14px and16px separation. Both screenshots visually inspected; no horizontal overflow. All five actionable findings are resolved, guided reading and role-map selection work, search spacing is consistent. No remaining blocking desktop/tablet issue found in reviewed scope. Read-only reviewer made no source/live changes.
