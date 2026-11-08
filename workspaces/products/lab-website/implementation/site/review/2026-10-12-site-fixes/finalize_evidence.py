"""Bind the completed local review to its release and retain human residues."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'website/output/playwright/ux-validator/20261012-site-fixes'
MEASURE = OUT / 'measurements'
BUILD_ROOT = Path(os.environ.get('LAB_SITE_VERIFIED_ROOT', str(ROOT / 'website')))

def read(path): return json.loads(path.read_text())
def write(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
def digest(path): return sha256(path.read_bytes()).hexdigest()

build = read(BUILD_ROOT / 'artifacts/build.json')
static = read(MEASURE / 'static.json')
repro = read(MEASURE / 'release-complete-reproducibility.json')
assert build['archive_sha256'] == static['archive']['archive_sha256'] == repro['archiveAfter']
assert repro['sameArchive'] and not repro['inputsChanged'] and not repro['changedEntries']
assert not static['missing_resources'] and not static['manifest_digest_mismatches']
assert not static['selected_binding_mismatches']
assert static['exact_reference_preservation'] == {'count': 454, 'matches': True}
assert all(r['dynamic_candidate'] and r['target'].endswith('/craft-model.html') for r in static['unresolved_fragments'])
http = read(MEASURE / 'http-resources.json')
assert all(r.get('status') == 200 and r.get('digest_matches') for r in http)

matrix_files = sorted(MEASURE.glob('*-final-release.json'))
repeat_files = sorted(MEASURE.glob('*-post-map-layout.json')) + sorted(MEASURE.glob('*-final-hackathon.json')) + sorted(MEASURE.glob('*-latest-hackathon.json')) + sorted(MEASURE.glob('*-current-hackathon.json')) + sorted(MEASURE.glob('*-snapshot-hackathon.json'))
states, latest, events = [], {}, []
for file in matrix_files + repeat_files:
    data = read(file)
    for row in data['states']:
        assert 'error' not in row and row['status'] in (200, 304)
        assert not row['measurements']['pageHorizontalOverflow']
        states.append(row)
        latest[(data['engine'], row['width'], row['path'])] = row
    events += [{'source': str(file.relative_to(OUT)), 'event': e} for e in data.get('events', [])]
assert len(latest) == 480 and len(states) >= 504 and not events

axe_files, incomplete, violation_count = [], [], 0
for (engine, width, _), row in latest.items():
    if engine == 'chromium' and width == 1440:
        file = OUT / 'accessibility' / ('chromium-' + row['key'] + '.json')
        axe = read(file); axe_files.append(file)
        violation_count += len(axe['violations'])
        for rule in axe['incomplete']:
            for node in rule['nodes']:
                incomplete.append({'source': str(file.relative_to(OUT)), 'page': axe['url'], 'rule': rule['id'], 'node': node, 'status': 'manual-review-retained'})
assert len(axe_files) == 60 and violation_count == 0
write(OUT / 'accessibility/incomplete-node-register.json', incomplete)

for name in ['snapshot-interactions', 'snapshot-journeys', 'snapshot-delivery', 'release-complete-performance', 'release-complete-zoom', 'final-map-nodes', 'snapshot-home-geometry', 'final-static-figures-firefox', 'final-release-mobile-performance']:
    data = read(MEASURE / (name + '.json'))
    assert not any('error' in r for r in data['rows']), name
    assert not data.get('events'), name
interactions = read(MEASURE / 'snapshot-interactions.json')
assert all(r['result']['pass'] for r in interactions['rows'] if r['name'].startswith('skip-'))
map_fit = next(r['result'] for r in interactions['rows'] if r['name'] == 'map-all-layouts')
assert len(map_fit) == 10 and all(r['fitPass'] and r['zoomPass'] and not r['missing'] for r in map_fit)
map_nodes = read(MEASURE / 'final-map-nodes.json')['rows'][0]['result']
assert len(map_nodes['layouts']) == 10
assert sum(len(r['nodes']) for r in map_nodes['layouts']) == 87
assert all(not r['missingTextEdges'] for r in map_nodes['layouts'])
assert all(n['expected'] == n['observed'] for r in map_nodes['layouts'] for n in r['nodes'])
assert all(not r['overlaps'] for r in read(MEASURE / 'snapshot-home-geometry.json')['rows'])
assert all(not r.get('nodeOverflow') and not r.get('clipped') for r in read(MEASURE / 'final-static-figures-firefox.json')['rows'])
zoom = read(MEASURE / 'release-complete-zoom.json')['rows'][0]['result']
assert len(zoom) == 10 and all(r['measurements']['scrollWidth'] <= r['measurements']['innerWidth'] + 1 for r in zoom)
search = read(MEASURE / 'search-ranking.json')
scores = {k: {'pass': sum(r['pass'] for r in v), 'total': len(v), 'zero_results': sum(not r['results'] for r in v)} for k, v in search['evaluated'].items()}
assert scores['curated']['pass'] == scores['curated']['total'] == 39
assert all(not r['results'] for r in search['negativeResults'])
payloads = read(MEASURE / 'payload-integrity.json')
assert all(r['samePayload'] for r in payloads)
assert [r['entries'] for r in payloads] == [707, 454]
performance = read(MEASURE / 'release-complete-performance.json')
cls = defaultdict(list)
for row in performance['rows']:
    cls[row['path']].append(sum(e['value'] for e in row['metrics']['cls'] if not e['recentInput']))
mobile = read(MEASURE / 'final-release-mobile-performance.json')
mobile_ranges = {key: [min(r[key] for r in mobile['rows']), max(r[key] for r in mobile['rows'])] for key in ['globalMs', 'catalogMs']}

changes = [
    ('F01', 'Six vector role illustrations; stable dimensions and an uncrowded responsive role map.', ['payload-integrity.json', 'snapshot-home-geometry.json']),
    ('F02', 'Reserved shell space, route preparation, bounded startup fallback and readable no-JavaScript content.', ['release-complete-performance.json', 'snapshot-delivery.json']),
    ('F03', 'Frozen exact destinations separated from explicit vocabulary; corrected capacity and authority/provenance bindings.', ['search-ranking.json']),
    ('F04', 'Question parsing, lexical weighting, inflections, bounded typo recovery and unknown-query rejection; separate answer adjudication and unrun reader prompts.', ['search-ranking.json']),
    ('F05', 'All robot essays join site navigation, shared search and the research route.', ['snapshot-delivery.json', 'snapshot-interactions.json']),
    ('F06', 'Skip links preserve the active topic, focus its visible content and continue Tab inside main.', ['snapshot-interactions.json']),
    ('F07', 'Fit and zoom work in all ten map layouts, with matching relationship text and 87 selectable nodes.', ['snapshot-interactions.json', 'final-map-nodes.json']),
    ('F08', 'Repaired headings, subject-specific table names, landmarks and keyboard access to record code.', ['snapshot-journeys.json']),
    ('F09', 'Larger diagram text, recalculated wrapping/captions and corrected measured label bounds.', ['final-static-figures-firefox.json', 'snapshot-interactions.json']),
    ('F10', 'Source/status entrance, practical next steps and the exact user-selected repository link.', ['static.json']),
    ('F11', 'Compact catalogs, 454 exact static record pages, complete deferred search, compressed local delivery and plaintext fallback.', ['static.json', 'payload-integrity.json', 'snapshot-delivery.json']),
    ('F12', 'Predictable homepage and research links across page families.', ['snapshot-delivery.json', 'snapshot-journeys.json']),
    ('F13', 'Query/hash-preserving guide redirect and portable canonical/share metadata.', ['snapshot-delivery.json', 'static.json']),
    ('F14', 'Explicitly separate the later hypothetical lesson from the fixed S1 incident; extended reader tasks are ready.', ['static.json']),
    ('F15', 'Robot series reuses the existing favicon, with no favicon request failure in the current matrix.', ['snapshot-interactions.json']),
]
original = {r['id']: r for r in read(HERE.parent / '2026-10-12-site-review/FINDINGS.json')['findings']}
findings = [{'id': fid, 'title': original[fid]['title'], 'priority': original[fid]['priority'], 'status': 'local-fix-verified', 'change': change, 'evidence': ['measurements/' + e for e in evidence], 'source_cards': original[fid]['source_cards'], 'residue': 'Newcomer comprehension awaits the arranged reader study.' if fid in ['F04', 'F14'] else 'Automated and expert local evidence; no universal usability or conformance claim.'} for fid, change, evidence in changes]
next(row for row in findings if row['id'] == 'F11')['source_cards'].append('compression-api')
stamp = datetime.now(timezone.utc).isoformat()
build['verified_root'] = str(BUILD_ROOT.relative_to(ROOT))
build['output'] = str((BUILD_ROOT/'dist').relative_to(ROOT))
build['archive'] = 'website/artifacts/reviewed-20261013-website.zip'
build['reviewed_archive'] = 'website/artifacts/reviewed-20261013-website.zip'
build['reviewed_receipt'] = 'website/artifacts/reviewed-20261013-build.json'
summary = {'schema_version': 'site-fixes-completion/v1', 'recorded_at': stamp, 'status': 'local-work-complete', 'goal': 'create better icons and apply all fixes', 'scope': 'All 15 findings and the complete website.', 'artifact': build, 'release_manifest_sha256': digest(BUILD_ROOT / 'dist/release-manifest.json'), 'matrix': {'observations': len(states), 'distinct_current_states': len(latest), 'base_matrix': 480, 'affected_repeats': len(states)-480, 'axe_visible_states': 60, 'axe_violations': violation_count, 'incomplete_nodes_retained': len(incomplete), 'incomplete_rules': dict(Counter(n['rule'] for n in incomplete))}, 'search': scores, 'search_adjudications': read(HERE / 'search-adjudications.json'), 'payloads': payloads, 'static': {'html_pages': len(static['html_pages']), 'local_references': len(static['link_checks']), 'files_served_and_hashed': len(http), 'missing_resources': 0, 'static_dynamic_fragments': len(static['unresolved_fragments']), 'reference_bodies_preserved': 454, 'captured_repository_drift': static['captured_sources']}, 'desktop_cls_ranges': {k: [min(v), max(v)] for k, v in cls.items()}, 'mobile_timing_ranges_ms': mobile_ranges, 'reproducible_archive': True, 'findings': findings, 'authority_effect': 'none', 'deployment_performed': False, 'deferred': ['Arranged newcomer reader responses and comprehension analysis.', 'Actual screen-reader, Safari and physical-phone sessions.', 'Manual disposition of every retained axe incomplete node.', 'Hosted field performance after publication and a chosen public URL.']}
write(HERE / 'COMPLETION-AUDIT.json', summary)
write(OUT / 'completion-audit.json', summary)
write(HERE / 'FINDINGS.json', {'date': stamp, 'authority_effect': 'none', 'findings': findings})
write(OUT / 'findings.json', {'date': stamp, 'authority_effect': 'none', 'findings': findings})
write(OUT / 'console-network.json', {'current_matrix_events': events, 'current_chromium_interaction_events': interactions['events'], 'earlier_webkit_navigation_cancellations': read(MEASURE / 'final-release-webkit-interactions.json')['events'], 'disposition': 'The two earlier WebKit cancellations happened during deliberate navigation. Files are present and the current matrix and delivery runs have no failures. Retain the events; do not reclassify missing resources as harmless.'})
metadata = {'mode': 'validate-interface and report', 'status': 'local-work-complete', 'recorded_at': stamp, 'goal': summary['goal'], 'scope': summary['scope'], 'artifact': build, 'release_manifest_sha256': summary['release_manifest_sha256'], 'matrix_base_artifact': read(MEASURE / 'matrix-build.json'), 'coverage': summary['matrix'], 'browsers': ['Chromium 155.0.8059.12', 'Firefox 156.0', 'Playwright WebKit 26.6, not actual Safari'], 'environment': 'WSL localhost; independent owned browser sessions; desktop widths 1440/1024 and compact widths 390/320, with Firefox/WebKit at 1440/390.', 'performance_profiles': [performance['environment'], mobile['profile']], 'source_cards': 'website/review/2026-10-12-site-fixes/source-cards.json', 'residues': summary['deferred'], 'authority_effect': 'none'}
write(OUT / 'run-metadata.json', metadata)
table = '\n'.join('| ' + row['id'] + ' | ' + row['change'] + ' | Verified locally |' for row in findings)
checks = read(BUILD_ROOT / '.build/logs/documentation-checks.log')['checks']
report = f'''# Website fixes and verification

13 October 2026. Local implementation of all 15 findings is complete. The scope covers the whole website: homepage, company story, research, guide, eight expanded essays, reference catalogs and records, practical guides, Craft, robot essays, event page and reader form.

The exact selected source repository is [CyberAlchemy-lab](https://github.com/cyberAlchemyAI/CyberAlchemy-lab). The site links to this address. Its public website address is still unset, so canonical metadata stays portable. This work did not publish the site, change GitHub visibility or admit any Lab records.

## Changes

| Finding | Applied change | Status |
| --- | --- | --- |
{table}

The six editable vector illustrations total 5,060 bytes, replacing about 10.7 MB of deployed bitmap medallions. Original bitmaps remain in source. Larger reading text and icon labels fit in intrinsic rows on compact screens. Measured role/label boxes do not overlap at 1440, 1024, 640, 390 or 320 px. The desktop map retains its visual connections. These illustrations depict responsibilities rather than declaring new ontology relations.

## What was checked

- {checks:,} integrated structural checks pass. The release contains {len(static['html_pages'])} HTML files and {build['files']:,} packaged files, including its manifest.
- {len(states)} browser observations cover 480 distinct route/viewport/engine states. Chromium uses 1440, 1024, 390 and 320 px; Firefox and Playwright WebKit use 1440 and 390 px. The 480-state matrix was followed by {len(states)-480} checks of affected pages after spacing and event-page edits. Their latest observations replace the earlier states. No page overflow, failed load or runtime event was recorded in these current checks.
- All ten system-map layouts Fit and zoom. All 87 selected nodes show the expected inspector heading, and the relationship lists match the diagrams. Keyboard selection, topic-preserving skip links, search keyboard movement, Escape, browser history, local response downloads and catalog recovery were exercised.
- Fourteen static figures have no measured text outside their nodes or SVG bounds in Firefox. The earlier Chromium figure pass also recorded zero such issues. Visible labels and relationship text remain available separately from diagrams.
- Five page families reflow at actual 200% and 400% Chromium browser zoom. No page-level horizontal overflow was measured. Wide technical figures still have their labeled scrolling/panning regions.
- Root hosting, a project directory, file origins and no-JavaScript reading pass 47 delivery scenarios: 21 redirects, 15 searches, two complete plaintext fallbacks and nine no-JavaScript routes. Redirects preserve the specified query/hash behavior. The reader form cannot accidentally submit answers without its script.
- All {len(http):,} manifest-listed deployed resources returned HTTP 200 with matching hashes. {len(static['link_checks']):,} local references have no missing or out-of-site dependency. The 479 statically unresolved fragments all target Craft's dynamically created overview; actual route checks and the readable no-JavaScript article are recorded. They are not missing files.
- All 454 reference-body fingerprints match the preserved baseline in identity order. The Markdown import reports 493 pages, 63 assets, zero unresolved links and zero changed captured-source bytes. Comparing the retained capture to current repository files finds one existing README drift among 484 compared files. The capture was preserved rather than silently refreshed.

## Search and loading

Search contains 707 entries in 13 groups. Its fixed curated judgments pass 39/39. The original broader questions retain a literal score of 21/24 and the later expert set 15/16. Each set has zero empty results. Three original misses return valid alternate destinations, and the later miss directly answers the question in the first result while its frozen target ranks fourth. These decisions are recorded in `search-adjudications.json`; they do not replace the literal scores. Four unrelated negative queries return no result.

The evaluated expert sets have been examined during development. They are not untouched holdouts or reader measurements. Eight unrun prompts in `reader-search-reserve.json` support a later reader review, with query wording and answer judgments kept out of index vocabulary.

The catalog is about 485 KB instead of 3.02 MB, with roughly 5,600 DOM nodes instead of 27,900. Exact bodies live on static record pages, and their old links resolve to those identities. Complete-record text loads when needed. Global search loads on first use.

Current complete search payloads are {payloads[0]['bytes']:,} bytes and {payloads[1]['bytes']:,} bytes. Their compressed local scripts are {payloads[0]['compressedScriptBytes']:,} and {payloads[1]['compressedScriptBytes']:,} bytes. Decoded bytes, plaintext fallback and recorded digests match. Native decompression uses [DecompressionStream](https://developer.mozilla.org/en-US/docs/Web/API/DecompressionStream); tested plaintext fallback supplies the same full content when this API is absent. File-origin delivery needs no external service or fetch request.

Forty desktop samples record zero short-window startup CLS for home, company, research, start and robot routes. Guide/library are approximately 0.0046–0.0047 and Craft about 0.000073. These are local observations over 600 ms after fonts become ready.

The latest five simulated-phone samples use 390×844 CSS pixels, 4× CPU slowdown, 100 ms latency and 1.6 Mbit/s download. First global search takes {mobile_ranges['globalMs'][0]/1000:.2f}–{mobile_ranges['globalMs'][1]/1000:.2f} seconds; complete catalog filtering takes {mobile_ranges['catalogMs'][0]/1000:.2f}–{mobile_ranges['catalogMs'][1]/1000:.2f} seconds. An earlier plain-payload run took roughly 10.9–14 seconds for first global search. These separate local runs, some alongside other browser checks, do not establish physical-device performance, hosted percentiles or INP.

## Accessibility and reader follow-ups

The 60 current visible desktop states have zero axe violations under WCAG tags and best-practice checks. Every incomplete node is retained in `accessibility/incomplete-node-register.json` ({len(incomplete)} nodes). An incomplete result is not a pass. Dynamic search controls were also exercised with the popup open, and skip navigation was checked with the keyboard.

Remaining manual work covers symbolic/illustrated content, obscured or overlapping backgrounds, dynamic popup reference interpretation and actual assistive-technology operation. Automated results do not establish full WCAG conformance. The maintained [accessibility disposition](ACCESSIBILITY-RESIDUES.md) explains these limits.

The user is arranging newcomer readers and explicitly requested continued preparation while responses take time. Their comprehension, including the distinction between a hypothetical lesson and the established incident, is deferred. Screen-reader sessions, actual Safari/physical-phone checks and hosted field performance also remain follow-ups. The site supplies a twelve-task local response form. Its synthetic download check is labeled NOT A PARTICIPANT RESPONSE.

The research guidance remains the original review's [WCAG 2.2 reference](https://www.w3.org/WAI/WCAG22/quickref/), [task-scenario guidance](https://www.nngroup.com/articles/task-scenarios-usability-testing/), [Diátaxis](https://diataxis.fr/) and [Web Vitals guidance](https://web.dev/articles/vitals). Standards checks, expert editorial judgment and actual reader evidence are reported separately.

## Release and evidence

The repeated build uses identical maintained inputs and produces the same archive, with zero differing entries and a successful ZIP integrity check. A fixed `calendar_revision_at` replaces wall-clock calendar generation. Existing concurrent event edits were preserved and checked again.

Archive SHA-256: `{build['archive_sha256']}`. The verified archive is `website/artifacts/reviewed-20261013-website.zip`, with its separate `reviewed-20261013-build.json` receipt. Its exact package is saved under the ignored review output's `verified-source/website/dist/`. The working `website/dist` remains available for ongoing edits and must not be assumed to share this snapshot's hash. Future source edits require rebuilding and renewed checks of affected surfaces.

Maintained evidence: `COMPLETION-AUDIT.json`, `FINDINGS.json`, the collectors and the independent search judgments/adjudications in this folder. Local raw evidence: `website/output/playwright/ux-validator/20261012-site-fixes/`, including screenshots, ARIA snapshots, traces, accessibility findings, measurements, console/network dispositions, hashes and residues. Generated raw evidence stays out of the deployment archive and Git.

Earlier failures remain development evidence. The missed skip selector, record heading/scroll accessibility, robot compact overflow, figure wrapping and central-label collision were repaired and checked again. A collector's missing screenshot helper and mistaken session-button expectation were collector errors; corrected probes passed. Two earlier WebKit navigation cancellations remain recorded separately from the failure-free current matrix/delivery checks. The earlier overwritten ignored search diagnostic is disclosed in `PROGRESS.md` rather than reconstructed as original evidence.
'''
HERE.joinpath('REPORT.md').write_text(report)
OUT.joinpath('summary.md').write_text(report)
audit = f'''# Completion audit

Goal: create better icons and apply all fixes.

Local implementation and verification are complete for all 15 original findings. This audit covers the entire site rather than a reduced documentation or icon scope. The per-finding changes and evidence are in [REPORT.md](REPORT.md), [FINDINGS.json](FINDINGS.json) and [COMPLETION-AUDIT.json](COMPLETION-AUDIT.json).

| Requirement | Result |
| --- | --- |
| F01–F15 implemented and reviewed | 15 local fixes verified; newcomer comprehension is explicitly deferred |
| Whole website, shared search and old links | {len(states)} observations; 480 current route/viewport/engine states; 47 delivery scenarios |
| Model and formal record preservation | All 454 exact bodies match their identity-ordered baseline |
| Search evaluation independence | Frozen targets and vocabulary separate; original scores retained; new unrun reader prompts |
| Accessibility evidence | 60 visible-state scans, zero violations, all incomplete nodes retained for manual review |
| Performance evidence | Desktop and declared phone diagnostics; complete payload parity; no field or INP claim |
| Portable release | {build['files']:,} files; repeated archive digest and ZIP integrity verified |
| Reader preparation | Twelve-task form and facilitator rubric, local download mechanics checked |
| User-selected source URL | Exact CyberAlchemy-lab GitHub URL applied |
| Scope and authority | No deployment, Git publication or Lab admission; unrelated work preserved |

Readers, actual assistive-technology/device sessions and hosted field measurements remain separate follow-ups authorized to take longer. The local fixes do not claim those outcomes. A public website base address must be selected before emitting absolute hosted metadata.

Verified release SHA-256: `{build['archive_sha256']}`.
'''
HERE.joinpath('COMPLETION-AUDIT.md').write_text(audit)
OUT.joinpath('residue-ledger.yml').write_text('''status: local-work-complete
authority_effect: none
human_study:
  - Arranged newcomer readers; responses and comprehension analysis pending.
  - Hypothetical learning branch must be distinguished from established cause.
manual_accessibility:
  - Every axe incomplete node remains listed in accessibility/incomplete-node-register.json.
  - Actual screen-reader interaction, dynamic ARIA interpretation, symbols and illustrated backgrounds.
manual_environment:
  - Actual Safari and physical-phone sessions.
field_performance:
  - Hosted Core Web Vitals and real-user interaction distributions after publication.
publication:
  - Public base address unset; no publication occurred in this goal.
local_verification:
  - No required local implementation or verification work remains for this goal snapshot.
''')
evidence = []
for folder in ['measurements', 'accessibility', 'aria', 'screenshots', 'traces']:
    for file in sorted((OUT / folder).glob('*')):
        if file.is_file(): evidence.append({'path': str(file.relative_to(OUT)), 'sha256': digest(file), 'bytes': file.stat().st_size})
write(OUT / 'evidence-index.json', evidence)
print(json.dumps({'status': summary['status'], 'matrix': summary['matrix'], 'search': scores, 'archive': build['archive_sha256'], 'findings': len(findings)}))
