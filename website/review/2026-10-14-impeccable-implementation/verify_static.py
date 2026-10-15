"""Verify exact record preservation, complete payloads and event boundaries."""
from pathlib import Path
import base64
from collections import Counter
import gzip
import hashlib
import json
import re
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'output/playwright/impeccable-implementation-20261014'
SITE = ROOT / 'website/dist'
LAB = SITE / 'governance-lab-series'
sys.path.insert(0, str(ROOT / 'website/source/governance-lab-series'))
from event_status import event_state
from research_pages import hackathon_bindings


def run():
    before = json.loads((OUT / 'baseline-site/governance-lab-series/research/reference-pages.json').read_text())
    after = json.loads((LAB / 'research/reference-pages.json').read_text())
    identities = lambda value: {r['id']: r['body_sha256'] for r in value['records']}
    assert identities(before) == identities(after)
    assert len(identities(after)) == 454
    bodies = {'identities': 454, 'exact_body_fingerprints_preserved': True}
    search_receipt = json.loads((LAB / 'research/site-search-index.json').read_text())
    payloads = []
    values = {}
    for name, variable, receipt in [
        ('site-search-index', 'LabSiteSearchIndex', search_receipt['delivery']),
        ('site-search-quick', 'LabSiteSearchQuick', search_receipt['quick_delivery']),
        ('reference-search-data', 'LabReferenceSearchText', after['search_delivery']),
    ]:
        code = (LAB / 'assets' / (name + '.js')).read_text()
        decoded = gzip.decompress(base64.b64decode(json.loads(re.search(r'atob\(("[^"]+")\)', code)[1])))
        fallback = LAB / 'assets' / receipt['fallback']
        literal = fallback.read_text().split('window.' + variable + '=', 1)[1].split(';\n', 1)[0].encode()
        assert decoded == literal
        assert hashlib.sha256(literal).hexdigest() == receipt['payload_sha256']
        assert hashlib.sha256(fallback.read_bytes()).hexdigest() == receipt['fallback_sha256']
        values[name] = json.loads(decoded)
        payloads.append({'name': name, 'identical_delivery': True, 'payload_bytes': len(decoded), 'script_bytes': len(code.encode())})
    full, quick = values['site-search-index']['entries'], values['site-search-quick']['entries']
    assert len(full) == len(quick)
    assert [(e['id'], e['href'], e['aliases']) for e in full] == [(e['id'], e['href'], e['aliases']) for e in quick]
    assert all(a['text'].startswith(b['text']) for a, b in zip(full, quick))
    cfg = json.loads((ROOT / 'website/hackathon.json').read_text())
    boundaries = [('2026-10-13T17:59:59-03:00', 'before'), ('2026-10-13T18:00:00-03:00', 'building'),
                  ('2026-10-23T23:59:59-03:00', 'building'), ('2026-10-24T00:00:00-03:00', 'submitted'),
                  ('2026-10-24T12:00:00-03:00', 'voting'), ('2026-10-25T18:00:00-03:00', 'review'),
                  ('2026-10-26T00:00:00-03:00', 'ended')]
    event = []
    for at, phase in boundaries:
        result = event_state(cfg, at)
        assert result['phase'] == phase
        assert not any(action['enabled'] for action in result['actions'].values())
        event.append({'at': at, 'phase': phase, 'no_unconfigured_actions': True})
    linked = {**cfg, **{key + '_url': 'https://example.org/' + key for key in ('registration', 'submission', 'gallery', 'voting')}}
    assert event_state(linked, '2026-10-14T12:00:00-03:00')['actions']['registration']['enabled']
    assert not event_state(linked, '2026-10-24T12:00:00-03:00')['actions']['voting']['enabled']
    linked['voting_access_verified'] = True
    assert event_state(linked, '2026-10-24T12:00:00-03:00')['actions']['voting']['enabled']
    assert not event_state(linked, '2026-10-25T18:00:00-03:00')['actions']['voting']['enabled']
    try:
        event_state(cfg, '2026-10-14T12:00:00')
    except ValueError:
        pass
    else:
        raise AssertionError('A timezone is required')
    with tempfile.TemporaryDirectory(prefix='lab-event-check-') as folder:
        target=Path(folder)
        escaped={**cfg, 'organizer_name':'An <example> & team'}
        (target/'hackathon.json').write_text(json.dumps(escaped))
        bindings=hackathon_bindings(target)
        decoded=json.loads(bindings['EVENT_CONFIG'].split('>',1)[1].rsplit('</script>',1)[0])
        assert decoded['organizer_name']==escaped['organizer_name']
        assert '<example>' not in bindings['EVENT_CONFIG']
        assert 'DTSTART:20261013T210000Z' in (target/'downloads/hackathon-dates.ics').read_text()
        for value in ('javascript:alert(1)', 'http://example.org/form', 'https://user:pass@example.org/form'):
            (target/'hackathon.json').write_text(json.dumps({**cfg,'registration_url':value}))
            try:
                hackathon_bindings(target)
            except ValueError:
                pass
            else:
                raise AssertionError('Unsafe form address accepted: '+value)
    manifest = json.loads((SITE / 'release-manifest.json').read_text())
    # Package structure is verified by the integrated builder; inspect all
    # archive bytes independently here, including the manifest itself.
    build = json.loads((ROOT / 'website/artifacts/build.json').read_text())
    archive = ROOT / build['archive']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == build['archive_sha256']
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        members = z.namelist()
        assert len(members) == len(set(members))
        for member in members:
            assert z.read(member) == (SITE / member).read_bytes(), member
        assert not any('/.impeccable/' in p or p.endswith(('PRODUCT.md', 'DESIGN.md')) for p in members)
    result = {'formal_bodies': bodies, 'payloads': payloads, 'same_quick_identities': len(full),
              'event_boundaries': event, 'ballot_readiness_checks': True, 'timezone_rejection': True,
              'json_roundtrip_and_safe_embedding':True, 'unsafe_url_rejections':3, 'utc_calendar':True,
              'archive': build, 'archive_members_match_dist': len(members), 'zip_integrity': True}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'static-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'preserved_bodies': 454, 'search_entries': len(full), 'payloads': len(payloads),
                      'event_boundaries': len(event), 'archive_files': len(members), 'result': 'pass'}))


if __name__ == '__main__':
    run()
