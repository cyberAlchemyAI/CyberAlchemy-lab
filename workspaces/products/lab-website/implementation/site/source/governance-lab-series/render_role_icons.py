"""Render homepage roles from the vendored, pinned Lucide icon set."""
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)
ROLES = {
    'people': ('#8e5942', 'People', 'users'),
    'agents': ('#5c55b8', 'Agents', 'bot'),
    'knowledge': ('#245fbd', 'Knowledge', 'book-open'),
    'work': ('#b94812', 'Work', 'briefcase-business'),
    'decisions': ('#246440', 'Decisions', 'split'),
    'core': ('#aa4b43', 'Shared project state', 'database'),
}


def render():
    destination = ROOT / 'assets/role-icons'
    destination.mkdir(parents=True, exist_ok=True)
    for key, (color, title, icon) in ROLES.items():
        svg = ET.parse(ROOT / 'assets/lucide' / f'{icon}.svg').getroot()
        # Keep the official geometry and its common 24-unit coordinate system.
        # Every role uses the same outline weight, including shared state.
        svg.attrib.update({
            'width': '192', 'height': '192', 'stroke-width': '1.5',
            'role': 'img', 'aria-labelledby': 'title',
            'style': f'color:{color}', 'data-icon-library': 'lucide',
            'data-icon': icon,
        })
        heading = ET.Element(f'{{{SVG}}}title', {'id': 'title'})
        heading.text = title
        svg.insert(0, heading)
        notice = '<!-- Lucide Icons and Contributors. See ../lucide/LICENSE.txt and source.json. -->\n'
        (destination / f'{key}.svg').write_text(
            notice + ET.tostring(svg, encoding='unicode') + '\n', encoding='utf-8')


if __name__ == '__main__':
    render()
