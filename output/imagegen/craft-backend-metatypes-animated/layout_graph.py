"""One graph: the thirteen definition boxes ARE the nodes."""
from pathlib import Path
import io
import json
import sys
import math
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw
import build as base
import layout_horizontal as horizontal
import layout_atlas as art

ROOT=Path(__file__).resolve().parent
STEM='craft-backend-metatypes-v4'
W,H,SCALE=2240,1640,0.8
NW,NH=360,190
POSITIONS={
    'Mapping':(600,220),'Query':(1180,220),
    'Calculation':(60,460),'Rule':(600,460),'Interface':(1760,460),
    'Value Object':(60,860),'Entity':(600,860),'Operation':(1180,860),'Event':(1760,860),
    'Enum':(60,1250),'Policy':(600,1250),'Workflow':(1180,1250),'State Machine':(1760,1250),
}

# source, target, canonical verb, animation phase, route, label position.
ARCS=[
 ('Entity','Operation','performs',1,[(960,970),(1180,970)],(1070,960)),
 ('Operation','Event','produces',1,[(1540,955),(1760,955)],(1650,945)),
 ('Operation','Entity','produces-for',4,[(1470,860),(1470,780),(990,780),(990,885),(960,885)],(1345,770)),
 ('Operation','Entity','creates',3,[(1180,920),(960,920)],(1070,910)),
 ('Event','Operation','triggers-cross',4,[(1760,1010),(1540,1010)],(1650,1000)),
 ('Rule','Operation','enforces',1,[(780,650),(780,700),(1250,700),(1250,860)],(1170,690)),
 ('Calculation','Operation','calculates',1,[(240,650),(240,740),(1200,740),(1200,860)],(850,730)),
 ('Event','State Machine','transitions',1,[(1940,1050),(1940,1250)],(1940,1150)),
 ('Interface','Operation','exposes',2,[(1840,650),(1840,740),(1620,740),(1620,900),(1540,900)],(1730,730)),
 ('Interface','Query','exposes',2,[(1760,510),(1660,510),(1660,315),(1540,315)],(1660,420)),
 ('Workflow','Operation','orchestrates',1,[(1360,1250),(1360,1050)],(1360,1150)),
 ('Policy','Operation','applies',2,[(960,1320),(1100,1320),(1100,1040),(1180,1040)],(1100,1190)),
 ('Policy','Calculation','applies',2,[(600,1350),(510,1350),(510,550),(420,550)],(510,1150)),
 ('Mapping','Entity','maps',2,[(960,315),(1040,315),(1040,810),(780,810),(780,860)],(1040,520)),
 ('Mapping','Value Object','maps',2,[(600,350),(470,350),(470,955),(420,955)],(470,720)),
 ('Mapping','Interface','maps',2,[(960,270),(1060,270),(1060,190),(2120,190),(2120,510)],(1880,180)),
 ('Entity','Value Object','contains',3,[(600,955),(420,955)],(510,945)),
 ('Query','Entity','reads',3,[(1180,350),(1100,350),(1100,760),(900,760),(900,860)],(1100,550)),
 ('Operation','Entity','reads',3,[(1180,1020),(960,1020)],(1070,1010)),
 ('Entity','Event','emits',3,[(960,875),(1000,875),(1000,670),(1920,670),(1920,860)],(1520,660)),
 ('Entity','Entity','owns',5,[(650,1050),(650,1145),(750,1145),(750,1050)],(700,1170)),
 ('Entity','Entity','belongs-to',5,[(800,1050),(800,1195),(930,1195),(930,1050)],(865,1220)),
]
SIGNATURES={a[2] for a in ARCS}
assert len(SIGNATURES)==17
assert len(POSITIONS)==13


def path_for(points):return 'M'+' L'.join(f'{x},{y}' for x,y in points)


def check_routes():
    """Catch wires crossing the interior of any definition box."""
    for src,dst,verb,_,points,_ in ARCS:
        for (x1,y1),(x2,y2) in zip(points,points[1:]):
            assert x1==x2 or y1==y2
            for name,(nx,ny) in POSITIONS.items():
                if x1==x2:
                    hit=nx+1<x1<nx+NW-1 and max(min(y1,y2),ny+1)<min(max(y1,y2),ny+NH-1)
                else:
                    hit=ny+1<y1<ny+NH-1 and max(min(x1,x2),nx+1)<min(max(x1,x2),nx+NW-1)
                assert not hit,(src,dst,verb,'crosses',name)


def check_canonical_signatures():
    registry=ROOT.parents[2]/'craft/authority/definitions/relationships/relationships.yml'
    signatures=json.loads(registry.read_text(encoding='utf-8-sig'))['signatures']
    backend={}
    for signature in signatures:
        sources=signature.get('source_types',[signature.get('source_type')])
        targets=signature.get('target_types',[signature.get('target_type')])
        if set(sources).issubset(POSITIONS) and set(targets).issubset(POSITIONS):
            backend[signature['id']]=(sources,targets)
    assert set(backend)==SIGNATURES,(set(backend),SIGNATURES)
    for src,dst,verb,*_ in ARCS:
        sources,targets=backend[verb]
        assert src in sources and dst in targets,(src,verb,dst)


def build(current=0,animated=False):
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
       '<title id="title">Craft backend meta-types: a connected definition graph</title>',
       '<desc id="desc">Exactly one definition box per backend meta-type. Directed labeled arrows connect those same boxes, with seventeen canonical signatures and a dashed field-type reference to Enum. Entity self-loops describe relationships between Entity instances, not a claim that an instance owns itself.</desc>',
       '<defs><linearGradient id="canvas" x2="1" y2="1"><stop stop-color="#07111f"/><stop offset="1" stop-color="#101d35"/></linearGradient><linearGradient id="card" x2="1" y2="1"><stop stop-color="#14283e"/><stop offset="1" stop-color="#0d1a2b"/></linearGradient><pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#647ca2" opacity=".12"/></pattern><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 8 4 0 8Z" fill="#7193bb"/></marker><marker id="activeArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 8 4 0 8Z" fill="#5be4c2"/></marker></defs>',
       '<style>text{font-family:DejaVu Sans,Arial,sans-serif}@media(prefers-reduced-motion:reduce){.motion{display:none}}</style>',
       base.rect(0,0,W,H,'url(#canvas)','none',0),base.rect(0,0,W,H,'url(#grid)','none',0),
       art.label(40,40,'CRAFT  /  BACKEND SEMANTIC GRAPH',15,700,'#5be4c2',tracking=2.4),
       art.label(38,96,'The definitions are the graph.',47,800),
       art.label(40,133,'13 meta-types · 17 directed relationship signatures · one connected map',20,400,art.MUTED)]
    for i,(cat,color) in enumerate(art.COLORS.items()):
        x=1500+(i%2)*300;y=54+(i//2)*35
        s += [f'<circle cx="{x}" cy="{y-5}" r="4" fill="{color}"/>',art.label(x+14,y,cat,14,600,color)]
    # Faint wires are permanent; an animated overlay follows one relationship group at a time.
    for i,(src,dst,verb,phase,points,(lx,ly)) in enumerate(ARCS):
        path=path_for(points)
        active=current==phase and current!=0
        color='#5be4c2' if active and not animated else '#597a9e'
        s += [f'<path id="edge-{i}" data-signature="{verb}" d="{path}" stroke="{color}" stroke-width="{2.4 if active else 1.6}" fill="none" marker-end="url(#{"activeArrow" if active else "arrow"})" opacity="{1 if active else .66}"/>']
        if animated:
            s += [f'<g class="motion" opacity="0">{base.gate(phase)}<path d="{path}" stroke="#5be4c2" stroke-width="2.5" fill="none" marker-end="url(#activeArrow)"/><circle r="4.7" fill="#b9ffea"><animateMotion dur="2s" repeatCount="indefinite" path="{path}"/></circle></g>']
    # Enum references a field type, not a new canonical relationship verb.
    ref='M240 1050V1250'
    s += [f'<path d="{ref}" fill="none" stroke="#8a9fbb" stroke-width="1.5" stroke-dasharray="5 7" marker-end="url(#arrow)"/>',base.rect(155,1147,170,23,'#0a1525','none',5),art.label(240,1163,'typed field reference',13,400,'#99aec9','middle')]
    # Labels sit on small opaque backplates so line crossings never obscure their text.
    for _,_,verb,phase,_,(lx,ly) in ARCS:
        width=len(verb)*8.3+19
        s += [base.rect(lx-width/2,ly-17,width,25,'#0b1728','none',5),art.label(lx,ly+1,verb,15,600,'#a9c5e5','middle')]
        if animated:
            s += [f'<g class="motion" opacity="0">{base.gate(phase)}',base.rect(lx-width/2,ly-17,width,25,'#143334','none',5),art.label(lx,ly+1,verb,15,700,'#8df2d5','middle'),'</g>']
    # Definition boxes mask any routing behind them. Every type occurs exactly once.
    for cat,name,a,b in base.TYPES:
        x,y=POSITIONS[name]
        color=art.COLORS[cat]
        s += [f'<g id="type-{name.lower().replace(" ","-")}" data-meta-type="{name}">',
              base.rect(x,y,NW,NH,'url(#card)',color,15,'stroke-opacity=".7" stroke-width="1.6"'),
              f'<path d="M{x+18} {y+1}h63" stroke="{color}" stroke-width="3" stroke-linecap="round"/>',
              art.label(x+20,y+25,cat.upper(),10.5,700,color,tracking=1.3),
              art.label(x+20,y+58,name,26,800),art.icon(name,x+303,y+19,color,36)]
        for j,line in enumerate(horizontal.wrap(a+' '+b,316)):
            s.append(art.label(x+20,y+94+j*23,line,17,400,'#c1cfe2'))
        if animated:
            for phase,(_,_,members) in enumerate(base.PHASES):
                if phase and name in members:
                    s.append(base.highlight(x,y,NW,NH,phase,current,True,color,15))
        elif current and name in base.PHASES[current][2]:
            s.append(base.rect(x,y,NW,NH,'none',color,15,'stroke-width="3.5"'))
        s.append('</g>')
    s += [art.label(44,1490,'Solid arrows: canonical signatures. Dashed arrow: field typing. Crossed wires do not imply a connection.',15,400,art.MUTED),
          art.label(44,1518,'Entity loops mean Entity → Entity between instances. Saga is represented by Workflow.',15,400,art.MUTED),
          base.rect(40,1550,2160,59,'#142840','none',12)]
    for phase,(name,detail,_) in enumerate(base.PHASES):
        if not animated and phase!=current:continue
        s += [f'<g class="motion" opacity="{1 if not animated or phase==0 else 0}">',base.gate(phase) if animated else '',art.label(60,1587,f'{phase+1:02d} / {name}',16,700,'#5be4c2'),art.label(560,1587,detail,17,400,'#bfd1e9'),'</g>']
    if animated:s.append('<path class="motion" d="M40 1622H2200" stroke="#5be4c2" stroke-width="2" stroke-dasharray="2160" stroke-dashoffset="2160"><animate attributeName="stroke-dashoffset" from="2160" to="0" dur="12s" repeatCount="indefinite"/></path>')
    s.append('</svg>')
    return ''.join(s)


def main():
    check_routes()
    check_canonical_signatures()
    svg=build(animated=True)
    root=ET.fromstring(svg)
    nodes=[e for e in root.iter() if e.get('data-meta-type')]
    assert len(nodes)==13 and len({e.get('data-meta-type') for e in nodes})==13
    assert len({e.get('data-signature') for e in root.iter() if e.get('data-signature')})==17
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    cairosvg.svg2png(bytestring=build().encode(),write_to=str(ROOT/f'{STEM}.png'))
    if '--still' in sys.argv:
        print('Single-graph preview rendered; all routes clear of definition interiors.')
        return
    frames=[]
    for phase in range(len(base.PHASES)):
        bg=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=build(current=phase).encode(),output_width=round(W*SCALE),output_height=round(H*SCALE)))).convert('RGB')
        for f in range(16):
            frame=bg.copy();draw=ImageDraw.Draw(frame)
            for _,_,_,p,points,_ in ARCS:
                if p!=phase:continue
                for offset,r,color in [(.045,5,'#368c83'),(0,3.6,'#b9ffea')]:
                    t=(f+.5)/16-offset
                    if t<0:continue
                    x,y=base.at_distance(points,t);x*=SCALE;y*=SCALE
                    draw.ellipse((x-r,y-r,x+r,y+r),fill=color)
            progress=(phase*16+f+1)/96
            draw.line([(40*SCALE,1622*SCALE),((40+2160*progress)*SCALE,1622*SCALE)],fill='#5be4c2',width=2)
            frames.append(frame)
    sample=Image.new('RGB',(frames[0].width,frames[0].height*6))
    for i in range(6):sample.paste(frames[i*16],(0,i*frames[0].height))
    palette=sample.quantize(colors=240)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    frames[0].save(ROOT/f'{STEM}.gif',save_all=True,append_images=frames[1:],duration=[120,130]*48,loop=0,optimize=True,disposal=1)
    with Image.open(ROOT/f'{STEM}.gif') as gif:
        total=0
        for i in range(gif.n_frames):gif.seek(i);total+=gif.info['duration']
        assert total==12000 and gif.info['loop']==0
        metadata={'design':'definition-boxes-as-graph-nodes','unique_type_nodes':13,'canonical_signatures':17,'directed_branches':22,'additional_field_type_reference':1,'svg_dimensions':[W,H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'seconds':total/1000,'routes_clear_of_node_interiors':True}
    (ROOT/f'{STEM}.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(metadata))


if __name__=='__main__':main()
