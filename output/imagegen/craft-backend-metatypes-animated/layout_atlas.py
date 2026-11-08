"""Craft semantic atlas: vector artwork, definitions first, dark animated circuit."""
from pathlib import Path
from html import escape
import io
import json
import sys
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw
import build as base
import layout_horizontal as previous

ROOT=Path(__file__).resolve().parent
W,H,SCALE=2080,1800,0.8
STEM='craft-backend-metatypes-v3'
INK='#edf3ff'
MUTED='#a4b7d0'
COLORS={'Structural':'#5be4c2','Behavioral':'#88adff','Connective':'#ffc16e','Lifecycle':'#e9a1ee'}
TONES={'Structural':'#122e31','Behavioral':'#152842','Connective':'#30291f','Lifecycle':'#2b233a'}
LEADS=['Identity over time.','Meaning through value.','Only these possibilities.','An intentional state change.','Read without mutation.','A value from a formula.','May this proceed?','Which strategy applies?','A coordinated sequence.','The callable boundary.','A fact, already happened.','One shape into another.','The legal next states.']
EXAMPLES=['Order · id: order_id','Money · amount + currency','Status · draft | paid | shipped','PayOrder · guard → commit','GetOrder · id → result','OrderTotal · Σ line amounts','HasStock · available ≥ requested','ShippingPolicy · select carrier','FulfilOrder · pay → pack → ship','OrdersAPI · request → response','OrderPaid · order_id + time','RequestToOrder · field projection','OrderLife · draft → paid']
PANELS=[(770,245,30,1166),(770,495,1050,1166),(1280,495,1560,1166),(770,787,30,1458),(1280,787,540,1458)]
PANEL_BG='#101e32'


def label(x,y,value,size=18,weight=400,color=INK,anchor='start',tracking=None):
    s=base.text(x,y,value,size,weight,color,anchor)
    return s.replace('<text ',f'<text letter-spacing="{tracking}" ',1) if tracking else s


def icon(name,x,y,color,size=49):
    paths={
      'Entity':'<rect x="6" y="5" width="36" height="38" rx="10"/><circle cx="24" cy="18" r="5"/><path d="M15 31h18M18 36h12"/>',
      'Value Object':'<path d="M24 3L46 24 24 45 2 24Z"/><circle cx="16" cy="24" r="2"/><circle cx="24" cy="24" r="2"/><circle cx="32" cy="24" r="2"/>',
      'Enum':'<rect x="4" y="5" width="40" height="9" rx="4"/><rect x="4" y="20" width="40" height="9" rx="4"/><rect x="4" y="35" width="40" height="9" rx="4"/><path d="M11 9h4m-4 15h4m-4 15h4"/>',
      'Operation':'<circle cx="10" cy="25" r="6"/><rect x="34" y="18" width="12" height="14" rx="3"/><path d="M17 25h14m-7-7 7 7-7 7M24 3v7m-4-3 4 4 4-4"/>',
      'Query':'<circle cx="20" cy="20" r="14"/><path d="M30 30l14 14M13 20h14m-10-5-5 5 5 5"/>',
      'Calculation':'<rect x="4" y="4" width="40" height="40" rx="10"/><path d="M12 16h10m-5-5v10m11-5h9M12 29l9 9m0-9-9 9m16-8h9m-9 6h9"/>',
      'Rule':'<path d="M24 3 42 10v15c0 10-18 20-18 20S6 35 6 25V10Z"/><path d="m14 24 7 7 14-15"/>',
      'Policy':'<path d="M24 44V29M24 29 8 14M24 29l16-15M2 14h12V2m20 0v12h12"/><circle cx="24" cy="29" r="4"/>',
      'Workflow':'<rect x="2" y="4" width="13" height="13" rx="3"/><rect x="18" y="18" width="13" height="13" rx="3"/><rect x="34" y="32" width="13" height="13" rx="3"/><path d="M15 11h10v7m6 7h10v7"/>',
      'Interface':'<path d="M14 4H5v40h9M34 4h9v40h-9M11 24h26m-7-7 7 7-7 7"/>',
      'Event':'<circle cx="24" cy="24" r="20"/><path d="M10 25h8l5-13 5 24 4-11h6"/>',
      'Mapping':'<path d="M3 8h10m-10 16h10M3 40h10M35 8h10M35 24h10M35 40h10M14 8l19 32M14 24h19M14 40 33 8"/>',
      'State Machine':'<circle cx="24" cy="8" r="6"/><circle cx="8" cy="38" r="6"/><circle cx="40" cy="38" r="6"/><path d="m20 14-9 17m5 7h16m5-7L28 14m-10 4 2-4 4 2m4 18 4 4-4 4"/>',
    }
    return f'<g transform="translate({x} {y}) scale({size/48})" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{paths[name]}</g>'


def recolor(element):
    mapping={**{base.COLORS[k]:v for k,v in COLORS.items()},**{base.PALE[k]:v for k,v in TONES.items()},
      '#ffffff':PANEL_BG,'#d4dce7':'#2a3d57','#26334c':INK,'#35455e':'#bbcee7','#75849a':'#5c7699',
      '#4f70cd':'#5be4c2','#1b9ba1':'#5be4c2','#087f82':'#5be4c2','#0d9da4':'#5be4c2','#c5d0df':'#3b516d'}
    for e in element.iter():
        e.tag=e.tag.split('}')[-1]
        for key in ['fill','stroke']:
            if e.get(key) in mapping:
                e.set(key,mapping[e.get(key)])
    return element


def build(current=0,animated=False):
    old=recolor(ET.fromstring(base.build(current=current,animated=animated)))
    items=list(old)
    starts=[next(i for i,e in enumerate(items) if e.tag=='rect' and e.get('x')==str(ox) and e.get('y')==str(oy)) for ox,oy,_,_ in PANELS]
    end=next(i for i,e in enumerate(items) if e.tag=='text' and e.get('x')=='771' and e.get('y')=='1023')
    paths=[]
    for phase,pts in base.EDGES:
        ox,oy,nx,ny=PANELS[phase-1]
        paths.append((phase,[(x+nx-ox,y+ny-oy) for x,y in pts]))
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
      '<title id="title">Craft: the backend semantic atlas</title>',
      '<desc id="desc">Thirteen large illustrated definition cards above seventeen directed relationship signatures. Pulses highlight connected definitions and relationships in a twelve-second reading loop.</desc>',
      '<defs><linearGradient id="canvas" x2="1" y2="1"><stop stop-color="#07111f"/><stop offset="1" stop-color="#101d35"/></linearGradient><radialGradient id="halo"><stop stop-color="#1b6170" stop-opacity=".3"/><stop offset="1" stop-color="#07111f" stop-opacity="0"/></radialGradient><linearGradient id="card" x2="1" y2="1"><stop stop-color="#14233a"/><stop offset="1" stop-color="#0e1a2d"/></linearGradient><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#647ca2" opacity=".12"/></pattern></defs>',
      ET.tostring(old.find('defs'),encoding='unicode'),
      '<style>text{font-family:DejaVu Sans,Arial,sans-serif}.mono{font-family:DejaVu Sans Mono,monospace}@media(prefers-reduced-motion:reduce){.motion{display:none}}</style>',
      base.rect(0,0,W,H,'url(#canvas)','none',0),base.rect(0,0,W,H,'url(#grid)','none',0),
      '<ellipse cx="1730" cy="135" rx="450" ry="270" fill="url(#halo)"/>',
      label(32,39,'CRAFT  /  SEMANTIC ATLAS',15,700,'#5be4c2',tracking=3),
      label(30,116,'The grammar of a backend.',61,800),
      label(33,159,'13 meta-types. Each carries meaning. Every connection has a direction.',22,400,MUTED),
      label(2050,41,'BACKEND ONLY',13,700,MUTED,'end',2)]
    # Small abstract semantic constellation in the masthead, made of the same icon vocabulary.
    for i,name in enumerate(['Entity','Operation','Event','State Machine']):
        x=1640+i*108
        color=COLORS[base.CATEGORY[name]]
        if i<3:s.append(f'<path d="M{x+49},112h54" stroke="#345470" stroke-width="1.4"/>')
        s += [icon(name,x,88,color,42),f'<circle cx="{x+22}" cy="156" r="2" fill="{color}"/>']
    s += [label(32,224,'01',16,800,'#5be4c2'),label(79,224,'THE DEFINITIONS',20,700,INK,tracking=2),label(2050,224,'WHAT EACH TYPE MEANS',13,600,MUTED,'end',2)]
    for i,(cat,name,a,b) in enumerate(base.TYPES):
        row,col=divmod(i,5)
        x=30+col*408+(408 if row==2 else 0)
        y=247+row*267
        color=COLORS[cat]
        s += [base.rect(x,y,388,247,'url(#card)','#2a3a52',16),
          f'<path d="M{x+18},{y+1}h76" stroke="{color}" stroke-width="3" stroke-linecap="round"/>',
          label(x+21,y+28,f'{i+1:02d}  /  {cat.upper()}',11,700,color,tracking=1.3),
          label(x+21,y+68,name,27,800),icon(name,x+319,y+22,color,45),
          label(x+21,y+108,LEADS[i],21,600,color)]
        for j,line in enumerate(previous.wrap(a+' '+b,344)):
            s.append(label(x+21,y+140+j*23,line,18,400,'#c1cde0'))
        s += [f'<path d="M{x+21},{y+213}h346" stroke="#283a53"/>',label(x+21,y+234,EXAMPLES[i],13.4,400,'#8fa9c9')]
        if animated:
            for phase,(_,_,members) in enumerate(base.PHASES):
                if name in members:
                    s.append(base.highlight(x,y,388,247,phase,current,True,color,16))
        elif current and name in base.PHASES[current][2]:
            s.append(base.rect(x,y,388,247,'none',color,16,'stroke-width="3"'))
    # Editorial side notes occupy the two spaces left by the final three cards.
    s += [label(34,843,'A TYPE IS',12,700,'#7290b3',tracking=3),label(32,885,'A promise',32,700),label(32,924,'of meaning.',32,700),label(34,965,'Identity. Value. Behavior.',17,400,MUTED),label(34,991,'Boundary. Change.',17,400,MUTED),
          label(1686,843,'AN EDGE IS',12,700,'#7290b3',tracking=3),label(1684,885,'A precise',32,700),label(1684,924,'relationship.',32,700),label(1686,965,'Source → verb → target.',17,400,MUTED),label(1686,991,'Direction is part of meaning.',17,400,MUTED),
          label(32,1067,'Saga is represented by Workflow; it is not a separate active type.',14,400,'#8199b8'),
          '<path d="M30 1092H2050" stroke="#30415a"/>',
          label(32,1136,'02',16,800,'#5be4c2'),label(79,1136,'THE CONNECTIONS',20,700,INK,tracking=2),
          label(2050,1136,'17 DIRECTED SIGNATURES',13,600,MUTED,'end',2)]
    for p,(ox,oy,nx,ny) in enumerate(PANELS):
        stop=starts[p+1] if p+1<len(starts) else end
        s.append(f'<g transform="translate({nx-ox} {ny-oy})">')
        s += [ET.tostring(e,encoding='unicode') for e in items[starts[p]:stop]]
        s.append('</g>')
    # A semantic spotlight replaces the previous large notes box.
    s += [base.rect(1050,1458,1000,209,'#101e32','#2a3d57',12),label(1074,1492,'FOLLOW THE MEANING',12,700,'#5be4c2',tracking=2)]
    spotlight=[('13 types. One shared vocabulary.','Start with the definitions; follow their directed relationships.'),('Rule → enforces → Operation','A permission condition is evaluated before state mutation.'),('Mapping → maps → Entity / Value Object / Interface','Shape projection does not construct, persist or invoke.'),('Entity → contains → Value Object','Identity-bearing things can embed complete, identity-free values.'),('Event → triggers-cross → Operation','The event and its reacting behavior belong to different features.'),('owns ≠ belongs-to','Lifecycle responsibility and membership carry different meaning.')]
    for phase,(headline,detail) in enumerate(spotlight):
        if not animated and phase!=current:continue
        s += [f'<g class="motion" opacity="{1 if not animated or phase==0 else 0}">',base.gate(phase) if animated else '',label(1074,1537,headline,23,700),label(1074,1573,detail,17,400,MUTED),'</g>']
    s += [label(1074,1612,'Enum supplies typed field/state references; it has no dedicated backend edge.',14,400,'#8199b8'),label(1074,1642,'Highlights guide reading. They do not prescribe a runtime execution order.',14,400,'#8199b8'),base.rect(30,1710,2020,60,'#152640','none',12)]
    for phase,(name,detail,_) in enumerate(base.PHASES):
        if not animated and phase!=current:continue
        s += [f'<g class="motion" opacity="{1 if not animated or phase==0 else 0}">',base.gate(phase) if animated else '',label(52,1748,f'{phase+1:02d} / {name}',16,700,'#5be4c2'),label(555,1748,detail,17,400,'#b6c9e4'),'</g>']
    s.append('</svg>')
    return ''.join(s),paths


def main():
    svg,_=build(animated=True)
    root=ET.fromstring(svg)
    assert len([e for e in root.iter() if e.get('id','').startswith('edge-')])==17
    assert not any(word in svg.lower() for word in ['profile','typescript','python','rust'])
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    still,_=build()
    cairosvg.svg2png(bytestring=still.encode(),write_to=str(ROOT/f'{STEM}.png'))
    if '--still' in sys.argv:
        print('Still preview rendered.')
        return
    frames=[]
    for phase in range(len(base.PHASES)):
        content,all_paths=build(current=phase)
        bg=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=content.encode(),output_width=round(W*SCALE),output_height=round(H*SCALE)))).convert('RGB')
        for f in range(base.FPS*base.SECONDS_PER_PHASE):
            frame=bg.copy()
            d=ImageDraw.Draw(frame)
            for p,pts in all_paths:
                if p!=phase:continue
                for trail,r,color in [(0.07,6,'#2a6b77'),(0.035,4.5,'#339998'),(0,3.5,'#9effe7')]:
                    t=(f+0.5)/(base.FPS*base.SECONDS_PER_PHASE)-trail
                    if t<0:continue
                    x,y=base.at_distance(pts,t)
                    x,y=x*SCALE,y*SCALE
                    d.ellipse((x-r,y-r,x+r,y+r),fill=color)
            # Moving reading progress line, synchronized to SVG's 12-second loop.
            progress=(phase*base.FPS*base.SECONDS_PER_PHASE+f+1)/(len(base.PHASES)*base.FPS*base.SECONDS_PER_PHASE)
            d.line([(30*SCALE,1785*SCALE),((30+2020*progress)*SCALE,1785*SCALE)],fill='#5be4c2',width=2)
            frames.append(frame)
    # Progress is part of the vector animation too; a static viewer still gets the entire map.
    progress='<path class="motion" d="M30 1785H2050" fill="none" stroke="#5be4c2" stroke-width="2" stroke-dasharray="2020" stroke-dashoffset="2020"><animate attributeName="stroke-dashoffset" from="2020" to="0" dur="12s" repeatCount="indefinite"/></path>'
    (ROOT/f'{STEM}.svg').write_text(svg.replace('</svg>',progress+'</svg>'),encoding='utf-8')
    sample=Image.new('RGB',(frames[0].width,frames[0].height*len(base.PHASES)))
    for i in range(len(base.PHASES)):sample.paste(frames[i*base.FPS*base.SECONDS_PER_PHASE],(0,i*frames[0].height))
    palette=sample.quantize(colors=240)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    frames[0].save(ROOT/f'{STEM}.gif',save_all=True,append_images=frames[1:],duration=[120,130]*(len(frames)//2),loop=0,optimize=True,disposal=1)
    with Image.open(ROOT/f'{STEM}.gif') as gif:
        duration=0
        for i in range(gif.n_frames):gif.seek(i);duration+=gif.info['duration']
        assert duration==12000
        assert gif.info['loop']==0
        info={'design':'semantic-atlas','definition_cards':13,'custom_type_symbols':13,'relationship_signatures':17,'svg_dimensions':[W,H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'loop_seconds':duration/1000}
    (ROOT/f'{STEM}.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__=='__main__':main()
