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

Release ID: `lab-20261015T042807Z-a9aa3c2652f7`.
Reviewed ZIP SHA-256:
`3c67bc377be92144e8ce9daf3ce4b919f14ebd286eedee364131aeec4ebd0cbc`.
The original site and configuration remain in the private release directory
`/srv/co-op-engine/deployments/lab-20261015T042807Z-a9aa3c2652f7/rollback`.
That directory is outside the served tree and must remain private because its
configuration backup includes the existing authentication material.

The exact envelope, deployment helper, public file checks and live browser
evidence are retained in
`../output/deployments/cyberalchemize-20261015/`. Future deployments should stage
against current live state, preserve unrelated paths, validate a complete
rollback, and verify public HTTPS before claiming completion. Do not reuse the
old release helper or its baseline assertions for a new release.

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
