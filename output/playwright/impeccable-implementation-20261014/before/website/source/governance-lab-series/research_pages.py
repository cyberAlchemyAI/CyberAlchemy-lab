"""Render the product entrance, research page and introduction using KEP assets."""
from html import escape
from html.parser import HTMLParser
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math
import re
from urllib.parse import urlsplit
from lab_visual_language import ICONS


HEAD = '''<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<link rel="icon" type="image/svg+xml" href="assets/kep/cyberalchemy-lab-logo-light-v2.svg">
<link rel="stylesheet" href="assets/kep/design-system.css">
<link rel="stylesheet" href="assets/site-search.css">
<link rel="stylesheet" href="assets/research-site.css">
<script src="assets/search-engine.js" defer></script>
<script src="assets/site-search.js" defer></script>'''
HEAD += '\n<script src="assets/research-navigation.js" defer></script>'


class WordCount(HTMLParser):
    def __init__(self):
        super().__init__(); self.omit = 0; self.words = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'nav'): self.omit += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav'): self.omit -= 1
    def handle_data(self, data):
        if not self.omit: self.words += len(data.split())


def header(current):
    nav = [('index.html', 'The Lab'), ('research.html#research', 'Research'),
           ('research.html#culture', 'About us'), ('hackathon.html', 'Hackathon'),
           ('start-here.html', 'Documentation')]
    links = []
    for href, text in nav:
        selected = ' aria-current="page"' if href == current or (current=='research.html' and href=='research.html#research') else ''
        extra = ' class="nav-docs"' if text == 'Documentation' else ''
        links.append(f'<a href="{href}"{selected}{extra}>{text}</a>')
    return '''<header class="topbar research-topbar"><div class="topbar-inner">
<a class="research-brand" href="index.html" aria-label="CyberAlchemy Lab home"><img src="assets/kep/cyberalchemy-lab-logo-light-v2.svg" alt="CyberAlchemy Lab" width="470" height="110"></a>
<nav aria-label="Main navigation">''' + ''.join(links) + '</nav></div></header>'


FOOTER = '''<footer class="research-footer"><div class="page-width">
<div><strong>CyberAlchemy Lab</strong><p>An open-source company brain system, built by CyberAlchemy.</p></div>
<nav aria-label="Footer navigation"><a href="index.html">The Lab</a><a href="research.html">Research &amp; culture</a><a href="hackathon.html">Hackathon</a><a href="start-here.html">Documentation</a><a href="lab-reference-library.html#articles-library">Expanded essays</a></nav>
</div></footer>'''


def hackathon_bindings(root):
    """Render honest action states from the organizer's maintained event settings."""
    config_path = root / 'hackathon.json'
    if not config_path.exists():
        config_path = root.parents[1] / 'hackathon.json'
    config = json.loads(config_path.read_text())
    if config['timezone'] != 'America/Sao_Paulo':
        raise ValueError('The hackathon uses the announced Brasília time zone.')
    dates = [date.fromisoformat(config[key]) for key in
             ('registration_opens', 'submissions_close', 'selection_ends')]
    if not dates[0] < dates[1] < dates[2] or any(d.year != config['year'] for d in dates):
        raise ValueError('Hackathon dates must be ordered within the announced year.')
    bindings = {'EVENT_YEAR': str(config['year'])}
    for prefix, value in zip(('REGISTRATION', 'SUBMISSION', 'SELECTION'), dates):
        bindings[prefix + '_DATE'] = value.isoformat()
        bindings[prefix + '_LABEL'] = value.strftime('%B') + ' ' + str(value.day)
        bindings[prefix + '_SHORT'] = value.strftime('%b') + ' ' + str(value.day)
        bindings[prefix + '_MONTH'] = value.strftime('%B')
        bindings[prefix + '_DAY'] = str(value.day)
    timed_keys = [('REGISTRATION', 'registration_opens_at'), ('BUILD', 'build_opens_at'),
                  ('SUBMISSION', 'submissions_close_at'), ('VOTING_OPEN', 'voting_opens_at'),
                  ('VOTING_CLOSE', 'voting_closes_at'), ('RESULTS', 'provisional_results_at'),
                  ('REPORT', 'report_deadline_at'), ('SELECTION', 'selection_ends_at')]
    timed = {}
    for prefix, key in timed_keys:
        value = datetime.fromisoformat(config[key])
        if value.utcoffset() != timedelta(hours=-3):
            raise ValueError(f'{key} must use the announced Brasília offset.')
        timed[key] = value
        bindings[prefix + '_DATETIME'] = value.isoformat()
        bindings[prefix + '_TIME'] = value.strftime('%H:%M')
        bindings[prefix + '_LABEL'] = value.strftime('%B') + ' ' + str(value.day)
        bindings[prefix + '_MONTH'] = value.strftime('%B')
        bindings[prefix + '_DAY'] = str(value.day)
    if [timed[key] for _, key in timed_keys] != sorted(timed[key] for _, key in timed_keys):
        raise ValueError('Hackathon timestamps must follow the event schedule.')
    for day_key, timestamp_key in [('registration_opens', 'registration_opens_at'),
                                   ('submissions_close', 'submissions_close_at'),
                                   ('selection_ends', 'selection_ends_at')]:
        if timed[timestamp_key].date().isoformat() != config[day_key]:
            raise ValueError(f'{day_key} disagrees with its timestamp.')
    bindings['MINIMUM_AGE'] = str(config['minimum_age'])
    bindings['RETENTION_DAYS'] = str(config['data_retention_days'])
    bindings['ORGANIZER_NAME'] = escape(config['organizer_name'])
    for key, label in [('registration', 'Register'), ('submission', 'Submit project'),
                       ('gallery', 'View projects'), ('voting', 'Open ballot')]:
        url = config.get(key + '_url')
        if url:
            parsed = urlsplit(url)
            if (parsed.scheme != 'https' or not parsed.netloc or parsed.username or
                    parsed.password or any(c.isspace() for c in url)):
                raise ValueError(f'{key}_url must be an absolute HTTPS public link.')
            action = f'<a class="text-link" href="{escape(url, quote=True)}">{label} <span aria-hidden="true">↗</span></a>'
        else:
            action = '<span class="hack-coming-soon">Coming soon</span>'
        bindings[key.upper() + '_ACTION'] = action
    url = config.get('registration_url')
    bindings['HERO_ACTION'] = (f'<a class="ds-button" href="{escape(url, quote=True)}">Register <span aria-hidden="true">↗</span></a>'
                              if url else '<a class="ds-button" href="#participate">How to enter <span aria-hidden="true">→</span></a>')
    email = config.get('contact_email')
    if email and not re.fullmatch(r'[^\s@<>?]+@[^\s@<>?]+\.[^\s@<>?]+', email):
        raise ValueError('contact_email must be a plain organizer email address.')
    bindings['CONTACT'] = (f'<p class="hack-contact">Questions? <a href="mailto:{escape(email, quote=True)}">Contact the organizer</a>.</p>'
                           if email else '')
    calendar_revision = datetime.fromisoformat(config['calendar_revision_at'])
    if calendar_revision.utcoffset() is None:
        raise ValueError('calendar_revision_at must include its time-zone offset.')
    calendar_stamp = calendar_revision.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    calendar = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//CyberAlchemy Lab//Hackathon 2026//EN', 'CALSCALE:GREGORIAN']
    calendar_events = [('registration', 'registration_opens_at', 'Registration and building open'),
                       ('submission', 'submissions_close_at', 'Submissions close'),
                       ('voting-open', 'voting_opens_at', 'Participant voting opens'),
                       ('voting-close', 'voting_closes_at', 'Participant voting closes'),
                       ('selection', 'selection_ends_at', 'Selection ends')]
    for key, timestamp_key, label in calendar_events:
        value = timed[timestamp_key].astimezone(timezone.utc)
        calendar += ['BEGIN:VEVENT', f'UID:craft-lab-hackathon-{key}-{value.isoformat()}@cyberalchemy-lab',
                     'DTSTAMP:' + calendar_stamp,
                     'DTSTART:' + value.strftime('%Y%m%dT%H%M%SZ'),
                     'SUMMARY:CyberAlchemy Lab x Craft - ' + label,
                     'DESCRIPTION:Confirmed event time. Brasilia time is UTC-3.',
                     'END:VEVENT']
    calendar.append('END:VCALENDAR')
    downloads = root / 'downloads'
    downloads.mkdir(exist_ok=True)
    (downloads / 'hackathon-dates.ics').write_bytes(('\r\n'.join(calendar) + '\r\n').encode())
    return bindings


def render(root):
    hackathon_css = (root/'assets/hackathon.css').read_bytes()
    stylesheet = 'hackathon-' + hashlib.sha256(hackathon_css).hexdigest()[:12] + '.css'
    (root/'assets'/stylesheet).write_bytes(hackathon_css)
    carousel_js = (root/'assets/hackathon-carousel.js').read_bytes()
    carousel_script = 'hackathon-carousel-' + hashlib.sha256(carousel_js).hexdigest()[:12] + '.js'
    (root/'assets'/carousel_script).write_bytes(carousel_js)
    case = json.loads((root/'research/incident-extraction-case.json').read_text())['export']
    fields = {'REQUIRED_COUNT': f"{case['required_count']:,}",
              'OUTPUT_COUNT': f"{case['output_row_count']:,}",
              'MISSING_COUNT': f"{case['missing_required_count']:,}",
              'ACCOUNT': case['account'], 'FILTERS': case['filters'],
              'SNAPSHOT': case['snapshot'], 'OUTPUT': case['output'], 'RUN': case['run']}
    pages = {}
    for name, source in [('index.html', 'lab-landing'), ('research.html', 'research-landing'), ('company-brain.html', 'company-brain'), ('source-and-status.html', 'source-and-status'), ('hackathon.html', 'hackathon')]:
        content = (root/f'templates/{source}.html.in').read_text()
        page_head = HEAD + f'\n<link rel="stylesheet" href="assets/{stylesheet}">'
        if name == 'hackathon.html':
            page_head += f'\n<script src="assets/{carousel_script}" defer></script>'
        if name == 'index.html':
            page_head += '\n<link rel="stylesheet" href="assets/company-brain-map.css">\n<script src="assets/company-brain-map.js" defer></script>'
        count = WordCount(); count.feed(content)
        bindings = {'HEAD': page_head, 'HEADER': header(name), 'FOOTER': FOOTER,
                    'COMPANY_BRAIN_MAP': (root/'templates/company-brain-map.html.in').read_text(),
                    'READING_TIME': str(math.ceil(count.words / 220))}
        glyphs = {
            'PEOPLE': '<circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M17 4a3 3 0 0 1 0 6m1 5a5 5 0 0 1 3 4v2"/>',
            'AGENTS': ICONS['robot'],
            'KNOWLEDGE': '<path d="M12 5C8 2 4 3 2 4v16c3-2 7-2 10 0 3-2 7-2 10 0V4c-2-1-6-2-10 1Zm0 0v15M5 8h4M5 12h4m6-4h4m-4 4h4"/>',
            'WORK': ICONS['hammer'],
            'DECISIONS': '<path d="M8 5H4v17h16V5h-4"/><rect x="8" y="2" width="8" height="5" rx="2"/><path d="m8 14 3 3 6-7"/>'
        }
        bindings.update({f'BRAIN_{key}_ICON': f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{geometry}</svg>' for key,geometry in glyphs.items()})
        bindings.update({key: escape(str(value)) for key, value in fields.items()})
        if name in ('index.html', 'hackathon.html'):
            bindings.update(hackathon_bindings(root))
        for key, value in bindings.items(): content = content.replace('{{'+key+'}}', value)
        assert '{{' not in content, name
        pages[name] = content
    return pages
