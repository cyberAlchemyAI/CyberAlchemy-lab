# Deploy the documentation website

[Website source and build instructions](README.md)

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
