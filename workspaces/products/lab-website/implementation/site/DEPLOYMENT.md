# Deploy the documentation website

[Website source and build instructions](README.md)

## Current cyberalchemize.com deployment

On 15 October 2026, the reviewed Paper & crimson website replaced the Co-Op
portfolio homepage at <https://cyberalchemize.com/>. The apex retains the
reviewed entry redirect into `governance-lab-series/index.html`.

The existing `coop-engine-site` Nginx container serves `/srv/co-op-engine/site`
on the VPS identified by `../domainspec-core/projects/co-op-engine/infra/`.
The deployed release keeps the existing `/craft`, `/bella`,
`/agent-orchestration`, `/agent-orchestration-guide`, and protected
`/domainspec/` routes. The live server configuration is authoritative; the
older full-deployment script must not be run against this combined site.

The deployment added only the reviewed documentation directories and release
manifest, replaced the root `index.html`, and added explicit Nginx locations
for those directories. Compose, credentials, existing security headers and
other containers were preserved. The existing image was reused without a pull.

Latest release ID: `lab-20261015T160928Z-bcb0331e6778`.
Reviewed ZIP SHA-256:
`f73e325c01136d5066d07ff37aa5977ca13b4bd865d3fa879978e42c792307c5`.
The initial Co-Op site and configuration remain in the private release directory
`/srv/co-op-engine/deployments/lab-20261015T042807Z-a9aa3c2652f7/rollback`.
That directory is outside the served tree and must remain private because its
configuration backup includes the existing authentication material.

The exact envelope, deployment helper, public file checks and live browser
evidence are retained in
`../output/deployments/cyberalchemize-20261015/`. Future deployments should stage
against current live state, preserve unrelated paths, validate a complete
rollback, and verify public HTTPS before claiming completion. Do not reuse the
old release helper or its baseline assertions for a new release.

The subsequent live review added the GitHub repository link to the homepage
menu/footer and documentation navigation, corrected announcement spacing, and
kept the narrow-phone menu inside the viewport. Its fresh rollback copy of the
previous Paper & crimson release is retained at
`/srv/co-op-engine/deployments/lab-20261015T044607Z-819f60b5a819/rollback`.
This update preserved the live Nginx configuration byte-for-byte. Its receipt
and verification are in
`../output/deployments/cyberalchemize-github-20261015/`.

The hackathon v1.1 update published the confirmed October/November schedule,
Studio front-end and Open projects categories, per-category prizes/votes,
matching rules downloads, and calendar. Its previous-live-site rollback is at
`/srv/co-op-engine/deployments/lab-20261015T051446Z-7708a94f4cf5/rollback`.
See `../output/deployments/cyberalchemize-hackathon-20261015/` for the exact
release and evidence. Hosting configuration and secondary pages stayed
unchanged; a prior public hashed event stylesheet remains available for old
resource URLs. Real event form URLs still require organizer configuration.

The category-card update adds two original generated paper-and-crimson
illustrations and padded responsive cards to the hackathon challenge section.
All existing text, links, dates, rules, downloads and earlier artwork remain
unchanged. Its previous-live-site rollback is retained at
`/srv/co-op-engine/deployments/lab-20261015T053101Z-5eae124ed3be/rollback`.
The combined live tree retains old hashed asset URLs and secondary pages.
The exact envelope and verification receipt are in
`../output/deployments/cyberalchemize-category-cards-20261015/`.
Hosting configuration, credentials and unrelated containers remain unchanged.

The diagram-readability update fits complete maps and figures to their panels,
adds guided connections and short figure-reading steps for constrained widths,
and compacts the company-brain and homepage role diagrams. The original
SVG assets, map data, captions, record notes, links, rules and downloads remain
intact. Its previous-live-site rollback is retained at
`/srv/co-op-engine/deployments/lab-20261015T063619Z-e3647122213c/rollback`.
The exact envelope and local/live evidence are in
`../output/deployments/cyberalchemize-diagrams-20261015/`.
Hosting configuration, authentication, secondary pages and unrelated containers
remain unchanged.

The map-canvas update adds click-to-expand behavior, pan/zoom/fit/focus,
keyboard and touch controls, exact view/lens selection and the existing concept
inspector in a larger canvas. Closing restores inline reading, focus and scroll.
Model data, original SVG assets, content, links, rules and downloads remain
intact. Its previous-live-site rollback is retained at
`/srv/co-op-engine/deployments/lab-20261015T070744Z-1533ea94e251/rollback`.
The exact envelope and local/live verification receipt are in
`../output/deployments/cyberalchemize-map-canvas-20261015/`.
An earlier candidate in that receipt was staged privately but never served.
Hosting configuration, credentials, secondary pages and unrelated containers
remain unchanged.

## Portable static hosting

Build with `python website/build.py` after installing `website/requirements.txt`. Set the hosting output directory to **`website/dist`**, or upload the contents of that directory. The portable archive has the same files at its root.

Preserve the sibling `governance-lab-series`, `craft-documentation-proposal` and `robot-learning-series` directories. Do not configure a single-page application fallback: these are distinct HTML documents, with explicit redirects for retired governance pages. No runtime environment variables, database, API endpoint or search backend are needed.

Use ordinary static-file MIME types for HTML, CSS, JavaScript, JSON, SVG, WebP and font files. Allow the supplied local scripts and inline enhancements used by the existing documentation. Prefer revalidation for HTML and search scripts; their filenames remain stable between editions.

## Prepared GitHub Pages workflow

The repository's Git remote is on GitHub. [`.github/workflows/documentation-site.yml`](../.github/workflows/documentation-site.yml) follows the [GitHub Pages custom workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) model. Action revisions are pinned.

The workflow is **manual only**. Its `deploy` input defaults to `false`:

1. Include the reviewed `website/` sources and workflow in the repository commit and publish that commit to GitHub.
2. Run **Build or deploy documentation website** with deployment disabled to obtain the static artifact.
3. For deployment, enable **Settings → Pages → Source → GitHub Actions** in the repository. Confirm the intended audience and configure the `github-pages` environment's branch and approval settings for that audience.
4. Run the workflow on the intended published revision with **Deploy the generated site to GitHub Pages** enabled.
5. GitHub reports the resulting URL in the deployment environment.

The build job has read access to repository contents. Only the optional deployment job receives Pages and identity-token write permissions. The workflow uploads `website/dist`, rather than the repository or source tree. Uploading a workflow artifact with deployment disabled does not create a public site.

GitHub Pages availability and audience controls depend on the repository and account plan; see [GitHub's Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). The provided workflow has been prepared locally; it has not been dispatched or deployed in this task.

## What the deployment includes

The release manifest identifies each selected file. Published content includes the reviewed documentation, teaching specimens and source excerpts linked by the reference library. Those excerpts are captured documentation evidence. They do not expose the current repository checkout, local runtime stores, credentials, browser traces, build backups, participant responses or the facilitator answer rubric.

The site's source capture date and its deployment date are separate facts. A deployment does not change the standing of a Lab definition, artifact or runtime.

The GitHub header update adds a static icon and Star on GitHub action across
all maintained page headers, with compact labels on narrow home layouts.
It was built in an isolated snapshot matching the previous live release;
unrelated runtime documentation changes remain local. All prior content and
links are preserved. Verification and the private rollback reference are in
`../output/deployments/cyberalchemize-github-header-20261015/RECEIPT.md`.

The follow-up header review improves search sizing, icon/results typography,
Unicode highlighting, 44 px controls, mobile menu dismissal and keyboard order.
The homepage explicitly identifies an open-source company brain and links to
GitHub while preserving existing actions. Independent review, local/live
verification and the private rollback reference are retained in
`../output/deployments/cyberalchemize-header-review-20261015/RECEIPT.md`.
This publication uses the previous reviewed source snapshot and leaves
unrelated runtime-doc3 documentation changes in the shared workspace.

The final whole-site review fixes keyboard access and focus for scrollable
code panes, and native mobile navigation overflow when JavaScript is disabled.
The approved hero, GitHub header, search, reading paths and illustrations are
preserved. Independent review, local/live evidence and the private rollback
reference are retained in
`../output/deployments/cyberalchemize-final-live-20261015/RECEIPT.md`.
This bounded release excludes unrelated runtime-doc3 documentation work.
