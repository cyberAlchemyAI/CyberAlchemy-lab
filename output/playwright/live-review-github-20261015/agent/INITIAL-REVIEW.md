# Independent live UI review

Used Impeccable polish guidance and approved DESIGN.md to inspect current live site without changing the identity.

Confirmed P2: homepage hackathon announcement lacks horizontal inset. At390px the paragraph and CTA start at x10 against page-frame x10, unlike the20px inner spacing elsewhere. The retained announcement `.page-width` has no structural rule in Paper homepage; old `hackathon.css` is excluded by homepage dependency selection. Narrow cause: `.paper-home .hack-home-announcement .page-width` needs explicit layout/inset in `home.css`, and the banner link needs an inline-flex touch target. Preserve actual event copy/status.

Evidence: index.html-light-390.png. Start-here, Actor and company-brain screenshots show existing inset working. Initial live batch covered home, Start, two reading paths, company-brain, system map/evidence, catalog, Actor, runtime overview/CLI, event, research, incident, Craft and Robot families at320 and390light; bounded interruption after finding means no aggregate matrix result is claimed. Initial test-only stall on unhydrated hidden chapter img placeholders was corrected; placeholders without src are intentional, not broken images.

Parent owns source fix, GitHub addition, build and publishing. Agent will perform one focused local confirmation round after changes.

Focused final confirmation exposed a second existing mobile defect: at320px the header wraps More to its second row; its230px right-anchored dropdown begins at x=-38.75 and clips the leading text of every destination, including the new GitHub link. At390/1440 it fits. Evidence home-menu-320-final.png and diagnostic. Recommended component fix scopes dropdown positioning to header at<=370px, preserving current desktop/mobile composition. Parent notified before publishing.
