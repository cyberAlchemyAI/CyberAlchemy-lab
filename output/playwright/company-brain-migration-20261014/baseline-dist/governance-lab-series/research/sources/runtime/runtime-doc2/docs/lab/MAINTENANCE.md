# Maintaining the repository documentation

[Documentation home](README.md)

## Edit the appropriate surface

The root documentation index and the guide, essay and reference indexes are maintained directly as Markdown. The remaining pages are imported from the reviewed documentation edition by [the importer](../../tooling/docs/import_site_docs.py).

For a change to an imported explanation, update its maintained source and rerun the import. Keep exact governing statements, the examples’ candidate standing, model boundaries and source capture dates intact. A prose edit supplies no reason to change an authority record.

The full website's maintained source and build now live in [website/](../../website/README.md). After a reviewed build, its generated pages are at `website/dist/governance-lab-series`. The Markdown import remains a separate operation; the website build does not replace these Markdown pages.

The adopted explanatory wording lives in `website/editorial-copy.json`. Edit the relevant passage there, rebuild the site, then import the final pages. The prose edition uses the natural editorial voice selected on 12 October 2026. Exact formal bodies keep their captured wording.

## Refresh an imported edition

From repository root, run:

```bash
python3 tooling/docs/import_site_docs.py --site website/dist/governance-lab-series
```

The argument is the reviewed documentation folder containing its generated HTML, catalog, templates and assets. Craft and the linked robot-learning series are read from their sibling documentation folders. Readers need neither those folders nor this command after the Markdown edition has been added to the repository.

The importer uses only the Python standard library. It reads source HTML without running scripts, rewrites links to repository Markdown or source records, copies referenced illustrations, creates standalone SVG diagrams and includes diagram labels as text. It writes an import manifest with hashes, capture scope and unresolved references. Review any unresolved references before presenting the edition as self-contained.

The command replaces imported pages and refreshes their manifest. It does not write canonical authority records, run the Lab, grant permissions, authorize deployment, commit or publish.

## Visual assets

The illustrations and diagrams in `assets/` accompany the explanation. Diagram geometry and labels come from the reviewed website; embedded styles allow SVGs to be displayed as ordinary repository images. The original KEP design vocabulary supplies their colors and visual presentation. Styles are explanatory presentation, not Lab definitions or governing contracts.

Each diagram also carries its labels in the Markdown text. The company-brain overview uses Mermaid plus an ordinary responsibilities table, so the explanation survives viewers without Mermaid support.

## Standing and freshness

The reference selection is dated in [the catalog](reference/catalog-snapshot.json). Current source links may evolve after import. Check the import manifest and repository authority selection before relying on a captured version as the current governing one.

Operational descriptions keep the selected runtime's source profile and evidence scope. Research ambitions, plans, candidate implementations and admitted implementations retain distinct standing.
