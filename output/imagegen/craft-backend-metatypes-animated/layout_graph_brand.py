"""Apply the maintained Lab logo and website-owned Paper & crimson color roles."""
from pathlib import Path
import hashlib
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw
import build as base
import layout_atlas as art
import layout_graph_clear as graph

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
ASSETS=REPO/'website/source/governance-lab-series/assets/paper-crimson'
STEM='craft-backend-metatypes-v6'
CSS=(ASSETS/'appearance.css').read_text()


def token(name):
    match=re.search(r'--paper-'+re.escape(name)+r':(#[0-9a-fA-F]{3,8})[;}]',CSS)
    if not match:raise ValueError('Missing website token: '+name)
    return match.group(1)


PAPER=token('paper');SURFACE=token('surface');SOFT=token('soft')
INK=token('ink');MUTED=token('muted');LINE=token('line');CONTROL=token('control')
ACCENT=token('accent');HOVER=token('hover')
CATEGORIES={'Structural':token('success'),'Behavioral':ACCENT,'Connective':token('warning'),'Lifecycle':MUTED}
COLORS={**{art.COLORS[k]:v for k,v in CATEGORIES.items()},
 '#07111f':PAPER,'#101d35':PAPER,'#152a41':SURFACE,'#0d1a2b':SURFACE,
 '#647ca2':LINE,'#86a6cd':MUTED,'#7695bb':MUTED,'#b9ffea':ACCENT,
 '#7d93af':CONTROL,'#91a6c1':MUTED,'#133433':SOFT,'#0b1728':PAPER,
 '#bcd1ed':MUTED,'#8df2d5':ACCENT,'#e0e9f6':INK,'#edf3ff':INK,
 '#a4b7d0':MUTED,'#142840':SOFT,'#bfd1e9':INK}


def build(current=0,animated=False):
    root=ET.fromstring(graph.build(current=current,animated=animated))
    for element in root.iter():
        element.tag=element.tag.split('}')[-1]
        for attribute in ['fill','stroke','stop-color']:
            original=element.get(attribute)
            if original in COLORS:element.set(attribute,COLORS[original])
        if element.tag=='rect':
            if float(element.get('width','0'))>0:element.set('rx','3')
        if element.tag=='text' and element.get('y')=='2275' and element.get('x')=='60':
            element.set('fill',ACCENT)
    root.find('title').text='Craft backend meta-types · CyberAlchemy Lab'
    root.find('desc').text+=' Branded with the official CyberAlchemy Lab vector logo and exact website Paper & crimson palette tokens.'
    # Motion outside type boxes uses the website action accent. Type-box emphasis retains category meaning.
    def motion_colors(element,in_type=False):
        in_type=in_type or bool(element.get('data-meta-type'))
        if element.tag=='g' and element.get('class')=='motion' and not in_type:
            for child in element.iter():
                if child.tag=='path' and child.get('stroke'):child.set('stroke',ACCENT)
                if child.tag=='circle':child.set('fill',ACCENT)
        for child in element:motion_colors(child,in_type)
    motion_colors(root)
    for element in root.iter():
        if element.tag=='marker' and element.get('id')=='activeArrow':
            for child in element:child.set('fill',ACCENT)
    # Recompose the masthead to give the original wordmark ample clear space.
    for child in list(root):
        if child.tag=='text' and (child.get('x'),child.get('y')) in {('40','42'),('38','100'),('40','140')}:
            root.remove(child)
    logo=ET.fromstring((ASSETS/'logo.svg').read_bytes())
    for element in logo.iter():element.tag=element.tag.split('}')[-1]
    logo.set('x','40');logo.set('y','18');logo.set('width','470');logo.set('height','110')
    logo.set('data-brand-asset','cyberalchemy-lab-official-logo')
    root.append(logo)
    for value in [art.label(560,61,'CRAFT / BACKEND META-TYPES',31,700,INK),
                  art.label(560,103,'Meaning, connected.',32,700,ACCENT),
                  art.label(560,138,'13 meta-types · 17 relationship signatures',20,400,MUTED)]:
        root.append(ET.fromstring(value))
    return ET.tostring(root,encoding='unicode')


def main():
    old_crossings=graph.check()
    svg=build(animated=True);root=ET.fromstring(svg)
    nodes=[element for element in root.iter() if element.get('data-meta-type')]
    assert len(nodes)==13
    assert len({element.get('data-signature') for element in root.iter() if element.get('data-signature')})==17
    embedded=next(e for e in root.iter() if e.get('data-brand-asset'))
    original=ET.fromstring((ASSETS/'logo.svg').read_bytes())
    # Compare the actual source paths, transforms and fills; the logo artwork is not re-created or recolored.
    def geometry(e):
        return [(n.tag.split('}')[-1],dict(n.attrib),n.text) for child in e for n in child.iter()]
    assert geometry(embedded)==geometry(original),'Logo artwork changed'
    assert graph.crossings(graph.ARCS)==([],[])
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    cairosvg.svg2png(bytestring=build().encode(),write_to=str(ROOT/f'{STEM}.png'))
    if '--still' in sys.argv:
        print(json.dumps({'logo':'official source vector, unchanged','canvas':PAPER,'surface':SURFACE,'ink':INK,'accent':ACCENT,'crossings':0}));return
    backgrounds=[]
    for phase in range(6):
        png=cairosvg.svg2png(bytestring=build(current=phase).encode(),output_width=round(graph.W*graph.SCALE),output_height=round(graph.H*graph.SCALE))
        backgrounds.append(Image.open(io.BytesIO(png)).convert('RGB'))
    sample=Image.new('RGB',(backgrounds[0].width,backgrounds[0].height*6))
    for i,bg in enumerate(backgrounds):sample.paste(bg,(0,i*bg.height))
    palette=sample.quantize(colors=240);del sample
    frames=[]
    for phase,bg in enumerate(backgrounds):
        for f in range(16):
            frame=bg.copy();d=ImageDraw.Draw(frame)
            for _,_,_,p,points,_ in graph.ARCS:
                if p!=phase:continue
                for offset,r,color in [(.045,5,SOFT),(0,3.6,ACCENT)]:
                    t=(f+.5)/16-offset
                    if t<0:continue
                    x,y=base.at_distance(points,t);x*=graph.SCALE;y*=graph.SCALE
                    d.ellipse((x-r,y-r,x+r,y+r),fill=color)
            frames.append(frame.quantize(palette=palette,dither=Image.Dither.NONE))
    frames[0].save(ROOT/f'{STEM}.gif',save_all=True,append_images=frames[1:],duration=[120,130]*48,loop=0,optimize=True,disposal=1)
    with Image.open(ROOT/f'{STEM}.gif') as gif:
        duration=0
        for i in range(gif.n_frames):gif.seek(i);duration+=gif.info['duration']
        assert duration==12000 and gif.info['loop']==0
        info={'design':'lab-branded-planar-definition-graph','unique_types':13,'canonical_signatures':17,'branches':22,'crossings':0,'overlapping_segments':0,'definition_font_size':24,'box_dimensions':[graph.NW,graph.NH],'svg_dimensions':[graph.W,graph.H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'loop_seconds':12,
          'brand':{'logo_source':str((ASSETS/'logo.svg').relative_to(REPO)),'logo_sha256':hashlib.sha256((ASSETS/'logo.svg').read_bytes()).hexdigest(),'palette_source':str((ASSETS/'appearance.css').relative_to(REPO)),'palette_name':'Paper & crimson','colors':{'canvas':PAPER,'surface':SURFACE,'ink':INK,'muted':MUTED,'border':LINE,'control':CONTROL,'accent':ACCENT,'subtle':SOFT},'category_colors':CATEGORIES}}
    (ROOT/f'{STEM}.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__=='__main__':main()
