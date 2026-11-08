"""A planar arrangement of the type graph, with larger readable definitions."""
from pathlib import Path
import io
import json
import sys
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import build as base
import layout_atlas as art
import layout_graph as prior

ROOT=Path(__file__).resolve().parent
STEM='craft-backend-metatypes-v5'
W,H,SCALE=2280,2300,0.72
NW,NH=440,240
BODY=24
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',BODY)
POSITIONS={
    'Value Object':(220,220),'Mapping':(1000,220),'Enum':(1750,220),
    'Entity':(220,770),'Query':(1000,770),'Interface':(1750,770),
    'Rule':(1000,1080),
    'Event':(220,1400),'Operation':(1000,1400),'Calculation':(1750,1400),
    'State Machine':(220,1900),'Workflow':(1000,1900),'Policy':(1750,1900),
}
ARCS=[
 ('Entity','Operation','performs',1,[(660,1000),(740,1000),(740,1560),(1000,1560)],(740,1270)),
 ('Operation','Event','produces',1,[(1000,1595),(660,1595)],(830,1585)),
 ('Operation','Entity','produces-for',4,[(1000,1510),(800,1510),(800,950),(660,950)],(900,1500)),
 ('Operation','Entity','creates',3,[(1000,1410),(920,1410),(920,850),(660,850)],(920,1080)),
 ('Event','Operation','triggers-cross',4,[(660,1625),(1000,1625)],(830,1654)),
 ('Rule','Operation','enforces',1,[(1220,1320),(1220,1400)],(1220,1368)),
 ('Calculation','Operation','calculates',1,[(1750,1550),(1440,1550)],(1595,1540)),
 ('Event','State Machine','transitions',1,[(440,1640),(440,1900)],(440,1770)),
 ('Interface','Operation','exposes',2,[(1750,970),(1660,970),(1660,1460),(1440,1460)],(1660,1200)),
 ('Interface','Query','exposes',2,[(1750,820),(1440,820)],(1595,810)),
 ('Workflow','Operation','orchestrates',1,[(1220,1900),(1220,1640)],(1220,1770)),
 ('Policy','Operation','applies',2,[(1750,2020),(1600,2020),(1600,1600),(1440,1600)],(1600,1770)),
 ('Policy','Calculation','applies',2,[(1970,1900),(1970,1640)],(1970,1770)),
 ('Mapping','Entity','maps',2,[(1000,340),(800,340),(800,790),(660,790)],(800,610)),
 ('Mapping','Value Object','maps',2,[(1000,300),(660,300)],(830,290)),
 ('Mapping','Interface','maps',2,[(1440,340),(1660,340),(1660,790),(1750,790)],(1660,610)),
 ('Entity','Value Object','contains',3,[(440,770),(440,460)],(440,610)),
 ('Query','Entity','reads',3,[(1000,820),(660,820)],(830,839)),
 ('Operation','Entity','reads',3,[(1000,1460),(860,1460),(860,900),(660,900)],(860,1135)),
 ('Entity','Event','emits',3,[(440,1010),(440,1400)],(440,1200)),
 ('Entity','Entity','owns',5,[(220,815),(130,815),(130,880),(220,880)],(130,799)),
 ('Entity','Entity','belongs-to',5,[(220,925),(80,925),(80,1000),(220,1000)],(135,1042)),
]
SIGNATURES={a[2] for a in ARCS}


def crossings(arcs):
    hits=set()
    overlaps=[]
    for i,a in enumerate(arcs):
        for j,b in enumerate(arcs[:i]):
            for p,q in zip(a[4],a[4][1:]):
                for r,s in zip(b[4],b[4][1:]):
                    if p[0]==q[0] and r[1]==s[1]:
                        if min(p[1],q[1])<r[1]<max(p[1],q[1]) and min(r[0],s[0])<p[0]<max(r[0],s[0]):hits.add((p[0],r[1]))
                    elif p[1]==q[1] and r[0]==s[0]:
                        if min(r[1],s[1])<p[1]<max(r[1],s[1]) and min(p[0],q[0])<r[0]<max(p[0],q[0]):hits.add((r[0],p[1]))
                    elif p[0]==q[0]==r[0]==s[0]:
                        if max(min(p[1],q[1]),min(r[1],s[1]))<min(max(p[1],q[1]),max(r[1],s[1])):overlaps.append((i,j))
                    elif p[1]==q[1]==r[1]==s[1]:
                        if max(min(p[0],q[0]),min(r[0],s[0]))<min(max(p[0],q[0]),max(r[0],s[0])):overlaps.append((i,j))
    return sorted(hits),overlaps


def check():
    registry=ROOT.parents[2]/'craft/authority/definitions/relationships/relationships.yml'
    raw=json.loads(registry.read_text(encoding='utf-8-sig'))['signatures']
    canonical={}
    for row in raw:
        sources=row.get('source_types',[row.get('source_type')]);targets=row.get('target_types',[row.get('target_type')])
        if set(sources).issubset(POSITIONS) and set(targets).issubset(POSITIONS):canonical[row['id']]=(sources,targets)
    assert len(POSITIONS)==13 and SIGNATURES==set(canonical) and len(SIGNATURES)==17
    for source,target,verb,_,points,_ in ARCS:
        assert source in canonical[verb][0] and target in canonical[verb][1]
        for (x1,y1),(x2,y2) in zip(points,points[1:]):
            assert x1==x2 or y1==y2
            for name,(nx,ny) in POSITIONS.items():
                hit=(nx+1<x1<nx+NW-1 and max(min(y1,y2),ny+1)<min(max(y1,y2),ny+NH-1)) if x1==x2 else (ny+1<y1<ny+NH-1 and max(min(x1,x2),nx+1)<min(max(x1,x2),nx+NW-1))
                assert not hit,(source,verb,target,'crosses node',name)
    hits,overlaps=crossings(ARCS)
    assert not hits,('crossings',hits)
    assert not overlaps,('overlaps',overlaps)
    for i,(_,_,verb,_,_,(lx,ly)) in enumerate(ARCS):
        width=len(verb)*9.5+20
        left,right,top,bottom=lx-width/2,lx+width/2,ly-21,ly+8
        for j,arc in enumerate(ARCS):
            if i==j:continue
            for (x1,y1),(x2,y2) in zip(arc[4],arc[4][1:]):
                if x1==x2:hit=left<x1<right and max(min(y1,y2),top)<min(max(y1,y2),bottom)
                else:hit=top<y1<bottom and max(min(x1,x2),left)<min(max(x1,x2),right)
                assert not hit,('label hides another arrow',verb,arc[2],(lx,ly))
        for name,(nx,ny) in POSITIONS.items():
            assert not(max(left,nx)<min(right,nx+NW) and max(top,ny)<min(bottom,ny+NH)),('label overlaps node',verb,name)
    return len(crossings(prior.ARCS)[0])


def wrap(value):
    lines=[];line=''
    for word in value.split():
        candidate=(line+' '+word).strip()
        if FONT.getlength(candidate)>NW-48 and line:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    assert len(lines)<=4,(value,lines)
    return lines


def backplate(x,y,value,color='#bcd1ed',active=False):
    # Small labels on parallel tracks are staggered vertically to keep generous clearance.
    width=len(value)*9.5+20
    return base.rect(x-width/2,y-21,width,29,'#133433' if active else '#0b1728','none',6)+art.label(x,y,value,17,700 if active else 600,color,'middle')


def build(current=0,animated=False):
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
      '<title id="title">Craft backend meta-types: a readable connected definition graph</title>',
      '<desc id="desc">Thirteen unique definition nodes, twenty-two branches representing seventeen canonical signatures, with no arrow crossings or overlapping segments. Definitions use 24-point text. Dashed Enum reference is field typing rather than a canonical signature.</desc>',
      '<defs><linearGradient id="canvas" x2="1" y2="1"><stop stop-color="#07111f"/><stop offset="1" stop-color="#101d35"/></linearGradient><linearGradient id="card" x2="1" y2="1"><stop stop-color="#152a41"/><stop offset="1" stop-color="#0d1a2b"/></linearGradient><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#647ca2" opacity=".12"/></pattern><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 7 3.5 0 7Z" fill="#86a6cd"/></marker><marker id="activeArrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 7 3.5 0 7Z" fill="#5be4c2"/></marker></defs>',
      '<style>text{font-family:DejaVu Sans,Arial,sans-serif}@media(prefers-reduced-motion:reduce){.motion{display:none}}</style>',base.rect(0,0,W,H,'url(#canvas)','none',0),base.rect(0,0,W,H,'url(#grid)','none',0),
      art.label(40,42,'CRAFT / BACKEND SEMANTIC GRAPH',17,700,'#5be4c2',tracking=2.2),art.label(38,100,'Meaning, connected.',50,800),
      art.label(40,140,'13 meta-types · 17 relationship signatures · definitions inside the nodes',22,400,art.MUTED)]
    for i,(cat,color) in enumerate(art.COLORS.items()):
        x=1540+(i%2)*310;y=65+(i//2)*38
        s += [f'<circle cx="{x}" cy="{y-6}" r="5" fill="{color}"/>',art.label(x+16,y,cat,17,600,color)]
    # Each canonical branch has a dedicated, non-crossing track.
    for i,(_,_,verb,phase,points,_) in enumerate(ARCS):
        path=prior.path_for(points);active=phase==current and current!=0
        s += [f'<path id="edge-{i}" data-signature="{verb}" d="{path}" fill="none" stroke="{"#5be4c2" if active else "#7695bb"}" stroke-width="{3 if active else 2}" marker-end="url(#{"activeArrow" if active else "arrow"})" opacity="{1 if active else .8}"/>']
        if animated:s.append(f'<g class="motion" opacity="0">{base.gate(phase)}<path d="{path}" stroke="#5be4c2" stroke-width="3" fill="none" marker-end="url(#activeArrow)"/><circle r="5" fill="#b9ffea"><animateMotion dur="2s" repeatCount="indefinite" path="{path}"/></circle></g>')
    s += ['<path d="M440 220V180H1970V220" stroke="#7d93af" stroke-width="1.7" stroke-dasharray="6 8" fill="none" marker-end="url(#arrow)"/>',backplate(1670,181,'typed field reference','#91a6c1')]
    for _,_,verb,phase,_,(x,y) in ARCS:
        active=phase==current and current!=0
        s.append(backplate(x,y,verb,'#8df2d5' if active else '#bcd1ed',active))
        if animated:s += [f'<g class="motion" opacity="0">{base.gate(phase)}',backplate(x,y,verb,'#8df2d5',True),'</g>']
    for cat,name,a,b in base.TYPES:
        x,y=POSITIONS[name];color=art.COLORS[cat]
        s += [f'<g id="type-{name.lower().replace(" ","-")}" data-meta-type="{name}">',base.rect(x,y,NW,NH,'url(#card)',color,17,'stroke-opacity=".85" stroke-width="1.8"'),
          f'<path d="M{x+20} {y+1}h80" stroke="{color}" stroke-width="3.5" stroke-linecap="round"/>',art.label(x+24,y+31,cat.upper(),13,700,color,tracking=1.4),art.label(x+24,y+76,name,34,800),art.icon(name,x+NW-69,y+24,color,44)]
        for j,line in enumerate(wrap(a+' '+b)):
            s.append(art.label(x+24,y+117+j*30,line,BODY,400,'#e0e9f6'))
        if animated:
            for phase,(_,_,members) in enumerate(base.PHASES):
                if phase and name in members:s.append(base.highlight(x,y,NW,NH,phase,current,True,color,17))
        elif current and name in base.PHASES[current][2]:s.append(base.rect(x,y,NW,NH,'none',color,17,'stroke-width="3.5"'))
        s.append('</g>')
    s += [art.label(44,2191,'Solid arrows: canonical signatures. Dashed arrow: field typing. Entity loops relate Entity instances.',18,400,art.MUTED),
          art.label(44,2222,'Saga is represented by Workflow. Animation guides reading; it does not prescribe an execution order.',18,400,art.MUTED),base.rect(40,2243,W-80,47,'#142840','none',12)]
    for phase,(name,detail,_) in enumerate(base.PHASES):
        if not animated and phase!=current:continue
        s += [f'<g class="motion" opacity="{1 if not animated or phase==0 else 0}">',base.gate(phase) if animated else '',art.label(60,2275,f'{phase+1:02d} / {name}',16,700,'#5be4c2'),art.label(565,2275,detail,17,400,'#bfd1e9'),'</g>']
    s.append('</svg>')
    return ''.join(s)


def main():
    old_crossings=check()
    svg=build(animated=True);root=ET.fromstring(svg)
    assert len([e for e in root.iter() if e.get('data-meta-type')])==13
    assert len({e.get('data-signature') for e in root.iter() if e.get('data-signature')})==17
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    cairosvg.svg2png(bytestring=build().encode(),write_to=str(ROOT/f'{STEM}.png'))
    if '--still' in sys.argv:
        print(json.dumps({'previous_crossings':old_crossings,'new_crossings':0,'overlapping_segments':0,'definition_font':BODY,'box_dimensions':[NW,NH]}));return
    # Use a shared palette from the six phases; quantize frames as they are built.
    backgrounds=[]
    for phase in range(6):
        png=cairosvg.svg2png(bytestring=build(current=phase).encode(),output_width=round(W*SCALE),output_height=round(H*SCALE))
        backgrounds.append(Image.open(io.BytesIO(png)).convert('RGB'))
    sample=Image.new('RGB',(backgrounds[0].width,backgrounds[0].height*6))
    for i,bg in enumerate(backgrounds):sample.paste(bg,(0,i*bg.height))
    palette=sample.quantize(colors=240);del sample
    frames=[]
    for phase,bg in enumerate(backgrounds):
        for f in range(16):
            frame=bg.copy();d=ImageDraw.Draw(frame)
            for _,_,_,p,points,_ in ARCS:
                if p!=phase:continue
                for offset,r,color in [(.045,5,'#368c83'),(0,3.6,'#b9ffea')]:
                    t=(f+.5)/16-offset
                    if t<0:continue
                    x,y=base.at_distance(points,t);x*=SCALE;y*=SCALE
                    d.ellipse((x-r,y-r,x+r,y+r),fill=color)
            frames.append(frame.quantize(palette=palette,dither=Image.Dither.NONE))
    frames[0].save(ROOT/f'{STEM}.gif',save_all=True,append_images=frames[1:],duration=[120,130]*48,loop=0,optimize=True,disposal=1)
    with Image.open(ROOT/f'{STEM}.gif') as gif:
        duration=0
        for i in range(gif.n_frames):gif.seek(i);duration+=gif.info['duration']
        assert duration==12000 and gif.info['loop']==0
        info={'design':'planar-definition-graph','unique_types':13,'canonical_signatures':17,'branches':22,'previous_crossings':old_crossings,'crossings':0,'overlapping_segments':0,'node_interior_crossings':0,'definition_font_size':24,'previous_definition_font_size':17,'box_dimensions':[NW,NH],'svg_dimensions':[W,H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'loop_seconds':12}
    (ROOT/f'{STEM}.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__=='__main__':main()
