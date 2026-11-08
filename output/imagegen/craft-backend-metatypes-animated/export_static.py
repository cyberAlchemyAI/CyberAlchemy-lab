"""Export the current graph with every definition and connection fully visible."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image
import build as base
import layout_graph_brand as brand

ROOT=Path(__file__).resolve().parent
STEM='craft-taxonomy-ontology-static'


def main():
    root=ET.fromstring((ROOT/'craft-backend-metatypes-v12.svg').read_text(encoding='utf-8'))
    for element in root.iter():element.tag=element.tag.split('}')[-1]
    root.set('xmlns','http://www.w3.org/2000/svg')
    # Remove phase overlays, leaving each canonical arrow and label exactly once.
    for child in list(root):
        if child.get('data-focus-type'):root.remove(child)
    for parent in list(root.iter()):
        for child in list(parent):
            if child.tag in {'animate','animateMotion','set'}:parent.remove(child)
    root.find('desc').text='Static full-visibility graph of all thirteen backend meta-types, all seventeen canonical relationship signatures and the separate dashed field-typing reference. No animated focus, fading, or bottom legend. Official Lab logo and website Paper & crimson palette.'
    for element in root.iter():
        if element.get('opacity') is not None and element.tag!='circle':element.set('opacity','1')
        if element.get('stroke-opacity') is not None:element.set('stroke-opacity','1')
        if element.get('data-meta-type'):
            element.set('opacity','1')
            name=element.get('data-meta-type')
            frame=next(e for e in element if e.tag=='rect')
            frame.set('fill',brand.SURFACE)
            frame.set('stroke',brand.CATEGORIES[base.CATEGORY[name]])
            frame.set('stroke-width','1.8')
        if element.get('data-label-state')=='context':
            frame=next(e for e in element if e.tag=='rect')
            frame.set('fill',brand.SURFACE)
    nodes=[e for e in root.iter() if e.get('data-meta-type')]
    arrows=[e for e in root.iter() if e.get('data-signature')]
    labels=[e for e in root.iter() if e.get('data-label-state')]
    assert len(nodes)==13 and len(arrows)==22 and len({e.get('data-signature') for e in arrows})==17
    assert len(labels)==23
    assert all(e.get('opacity','1')=='1' for e in root.iter() if e.tag in {'g','path','rect','text'})
    assert not any(e.tag in {'animate','animateMotion','set'} for e in root.iter())
    svg=ET.tostring(root,encoding='unicode')
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    cairosvg.svg2png(bytestring=svg.encode(),write_to=str(ROOT/f'{STEM}.png'),scale=2)
    with Image.open(ROOT/f'{STEM}.png') as im:
        info={'title':root.find('title').text,'static':True,'fading':False,'all_definition_boxes_visible':True,'all_arrow_labels_visible':True,'unique_types':13,'canonical_signatures':17,'canonical_branches':22,'label_capsules':23,'dimensions':list(im.size)}
    (ROOT/f'{STEM}.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__=='__main__':main()
