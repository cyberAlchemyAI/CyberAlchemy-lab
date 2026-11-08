# Independent UI confirmation

Two reproducible issues from the actual live site were reported to parent and repaired at the narrow component level:

1. Homepage hackathon announcement had no inner horizontal padding after migration. Its paragraph and CTA touched the page-frame border. The Paper homepage now supplies retained announcement flex layout,20px mobile/24px desktop inset,16px block spacing and a44px CTA target.
2. At320px, the homepage header wraps navigation to another row. More's right-anchored230px menu began at x=-38.75 and clipped navigation labels. The<=370px rule now positions More's dropdown against the header, keeping the existing appearance. At320 it fits x65..295; at360 x105..335.

The parent added the requested GitHub repository link to homepage More/footer and documentation sidebar, including the static no-script fallback.

Focused local verification:12 homepage/documentation states across320/390/1440 and both themes;32 checks, initially30passed and2existing320menu-bound failures. All banner inset/CTA, GitHub target/count/visibility, menu Escape/focus, docs sidebar, search results bounds/keyboard/Escape checks passed. Both390px no-script home/docs GitHub checks passed. Zero document overflow and runtime errors in these12 states.

After the final menu repair and final normal build, reran only the affected cases using actual delivered CSS:320/360 in light/dark plus no-script320/360,6/6 passed with no overflow, visible GitHub and dropdown fully within viewport. No source edits by this reviewer. Initial broad live review was interrupted for the confirmed finding; no aggregate broad matrix success is claimed. Screenshots inspected for home, Start, Actor, company-brain and event. The approved Paper & crimson identity and content are retained.

Evidence: confirm.json and raw output (the2initial failures remain honestly recorded), menu-edge-final.json (6final passes), initial and repaired screenshots. Hotpatch results are diagnostic only; final six cases use rebuilt artifact without injected styling. Parent owns preservation/integrity checks and live release verification.
