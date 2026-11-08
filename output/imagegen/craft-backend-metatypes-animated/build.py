"""Build editable SMIL SVG plus a matching GIF and still image. No raster inputs."""
from pathlib import Path
from html import escape
import io
import json
import math
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
W, H = 1800, 1140
SCALE = 0.8
FPS, SECONDS_PER_PHASE = 8, 2
COLORS = {'Structural': '#087f82', 'Behavioral': '#5850b5', 'Connective': '#b47710', 'Lifecycle': '#9744ad'}
PALE = {'Structural': '#e1f3f1', 'Behavioral': '#eeecfb', 'Connective': '#fff2d9', 'Lifecycle': '#f4e7f8'}
TYPES = [
    ('Structural', 'Entity', 'Stable identity and typed fields.', 'Identity persists through lifecycle changes.'),
    ('Structural', 'Value Object', 'Immutable, complete value; no identity.', 'Equality is determined by its fields.'),
    ('Structural', 'Enum', 'Closed, finite set of named variants.', 'Unknown values are rejected.'),
    ('Behavioral', 'Operation', 'Changes state; declares reads, writes and effects.', 'Guard before mutation; explicit failure continuation.'),
    ('Behavioral', 'Query', 'Reads entity data with typed inputs and results.', 'No state mutation or side effects.'),
    ('Behavioral', 'Calculation', 'Pure value derived from declared inputs.', 'Formula, rounding and error behavior are explicit.'),
    ('Behavioral', 'Rule', 'Typed Boolean condition: allow or block.', 'Gates whether an Operation may execute.'),
    ('Behavioral', 'Policy', 'Selects behavior from declared strategies.', 'Explicit conditions, default and ambiguity handling.'),
    ('Behavioral', 'Workflow', 'Coordinates ordered Operations in declared scope.', 'Explicit failure and recovery semantics.'),
    ('Connective', 'Interface', 'Versioned callable boundary.', 'Exposes Operation or Query contracts.'),
    ('Connective', 'Event', 'Typed record of a fact that already happened.', 'Carries payload and source context.'),
    ('Connective', 'Mapping', 'Projects source fields into a target shape.', 'Direction, conversions and totality are explicit.'),
    ('Lifecycle', 'State Machine', 'States, initial state and valid transitions.', 'Declares transition guards and effects.'),
]
CATEGORY = {name: cat for cat, name, *_ in TYPES}
PHASES = [
    ('THE TYPE VOCABULARY', 'Identity, values, behavior, boundaries and lifecycle.', set(CATEGORY)),
    ('EXECUTION', 'Rules gate; Calculations derive; Workflows coordinate.', {'Entity', 'Rule', 'Calculation', 'Workflow', 'Operation', 'Event', 'State Machine'}),
    ('BOUNDARIES & DECISIONS', 'Interfaces expose; Policies choose; Mappings project.', {'Interface', 'Operation', 'Query', 'Policy', 'Calculation', 'Mapping', 'Entity', 'Value Object'}),
    ('DATA & IDENTITY', 'Reads, creation, embedded values and event subjects.', {'Entity', 'Value Object', 'Operation', 'Query', 'Event'}),
    ('ACROSS FEATURES', 'Events activate behavior; Operations project to other features.', {'Event', 'Operation', 'Entity'}),
    ('OWNERSHIP & MEMBERSHIP', 'Lifecycle responsibility and assignment carry different meaning.', {'Entity'}),
]
DURATION = len(PHASES) * SECONDS_PER_PHASE


def text(x, y, value, size=16, weight=400, color='#26334c', anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(value)}</text>'


def rect(x, y, width, height, fill='#ffffff', stroke='#d4dce7', radius=12, extra=''):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}" {extra}/>'


def gate(phase):
    times = [0]
    vals = ['1' if phase == 0 else '0']
    for i in range(1, len(PHASES)):
        times.append(i / len(PHASES))
        vals.append('1' if phase == i else '0')
    times.append(1)
    vals.append(vals[0])
    return f'<animate attributeName="opacity" values="{";".join(vals)}" keyTimes="{";".join(str(n) for n in times)}" calcMode="discrete" dur="{DURATION}s" repeatCount="indefinite"/>'


def highlight(x, y, width, height, phase, current, animated, color='#4f70cd', radius=12):
    if not animated and phase != current:
        return ''
    anim = gate(phase) if animated else ''
    return f'<g class="motion" opacity="{1 if phase == 0 or not animated else 0}">{anim}' + rect(x, y, width, height, 'none', color, radius, 'stroke-width="3"') + '</g>'


def node(x, y, label, width=123, height=32):
    base = label.replace(' A', '').replace(' B', '')
    cat = CATEGORY.get(base, 'Structural')
    return rect(x, y, width, height, PALE[cat], COLORS[cat], 8) + text(x + width/2, y+height/2+5, label, 14, 700, COLORS[cat], 'middle')


EDGES = []


def edge(points, label, lx, ly, phase, animated, current):
    path = 'M' + ' L'.join(f'{x},{y}' for x, y in points)
    idx = len(EDGES)
    EDGES.append((phase, points))
    active = phase == current and current != 0
    color = '#1b9ba1' if active and not animated else '#75849a'
    parts = [f'<path id="edge-{idx}" d="{path}" fill="none" stroke="{color}" stroke-width="{2.8 if active and not animated else 1.7}" marker-end="url(#arrow)"/>']
    tw = len(label) * 7.4 + 14
    parts += [rect(lx-tw/2, ly-14, tw, 19, '#ffffff', 'none', 4), text(lx, ly, label, 13, 600, '#35455e', 'middle')]
    if animated:
        parts += [f'<g class="motion" opacity="0">{gate(phase)}<circle r="4.5" fill="#0d9da4"><animateMotion dur="{SECONDS_PER_PHASE}s" repeatCount="indefinite" path="{path}"/></circle></g>']
    return ''.join(parts)


def panel(x, y, width, height, letter, title, phase, current, animated):
    return rect(x, y, width, height) + highlight(x, y, width, height, phase, current, animated) + text(x+18, y+30, letter, 15, 800, '#087f82') + text(x+45, y+30, title, 20, 700)


def build(current=0, animated=False):
    EDGES.clear()
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title description">',
         '<title id="title">Craft backend meta-types: semantic contracts and relationships</title>',
         '<desc id="description">Thirteen backend types in four categories, connected by seventeen canonical relationship signatures. Highlighting follows six explanatory phases. Animation indicates relationships, not a prescribed runtime execution order.</desc>',
         '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse"><path d="M0,0 L7,3.5 L0,7 Z" fill="#75849a"/></marker></defs>',
         '<style>text{font-family:DejaVu Sans,Arial,sans-serif}@media(prefers-reduced-motion:reduce){.motion{display:none}}</style>',
         rect(0, 0, W, H, '#f5f8fc', 'none', 0),
         text(30, 61, 'CRAFT / BACKEND META-TYPES', 39, 800, '#17243e'),
         text(32, 96, '13 active types • 4 categories • 17 canonical relationship signatures', 21),
         text(32, 136, 'Taxonomy names each kind of concept. Ontology connects the concepts with directed meaning.', 17)]
    for i, (cat, color) in enumerate(COLORS.items()):
        x = 32 + i*195
        s += [f'<circle cx="{x+7}" cy="169" r="6" fill="{color}"/>', text(x+22, 175, cat, 16, 600, color)]
    s += [text(31, 222, 'WHAT EACH TYPE CARRIES', 23, 800), text(770, 222, 'HOW THE TYPES CONNECT', 23, 800)]
    y, last = 245, None
    for cat, name, a, b in TYPES:
        if cat != last:
            s += [text(33, y+20, cat.upper(), 14, 800, COLORS[cat])]
            y += 31
            last = cat
        s += [rect(30, y, 710, 44, '#ffffff', '#e0e6ee', 8)]
        if animated:
            for p, (_, _, members) in enumerate(PHASES):
                if name in members:
                    s += [highlight(30, y, 710, 44, p, current, True, COLORS[cat], 8)]
        elif name in PHASES[current][2]:
            s += [rect(30, y, 710, 44, PALE[cat], COLORS[cat], 8)]
        s += [text(43, y+28, name, 17 if len(name)<12 else 15.5, 700, COLORS[cat]), text(205, y+18, a, 13.4), text(205, y+36, b, 13.4)]
        y += 50

    # A: six signatures, with Operation as the hub.
    s += [panel(770,245,1000,231,'A','Execution',1,current,animated)]
    left = [('Entity',294),('Rule',337),('Calculation',380),('Workflow',423)]
    for label, yy in left:
        s += [node(790,yy,label,130)]
    s += [node(1135,355,'Operation',130),node(1375,355,'Event',120),node(1590,355,'State Machine',155)]
    for (label, yy), verb in zip(left,['performs','enforces','calculates','orchestrates']):
        s += [edge([(920,yy+16),(1068,yy+16),(1124,371),(1135,371)],verb,995,yy+11,1,animated,current)]
    s += [edge([(1265,371),(1375,371)],'produces',1320,361,1,animated,current),edge([(1495,371),(1590,371)],'transitions',1543,361,1,animated,current)]
    s += [text(1134,435,'Arrows express semantic relationships.',14),text(1134,456,'They do not prescribe an execution schedule.',14)]

    # B: three branching signatures (alternatives retain one canonical verb).
    s += [panel(770,495,490,272,'B','Boundaries & decisions',2,current,animated)]
    for yy, src, verb, targets in [(550,'Interface','exposes',['Operation','Query']),(620,'Policy','applies',['Operation','Calculation']),(700,'Mapping','maps',['Entity','Value Object','Interface'])]:
        s += [node(786,yy,src,120)]
        offs = [-15,15] if len(targets)==2 else [-24,5,34]
        for off, target in zip(offs,targets):
            s += [node(1112,yy+off,target,130,26)]
            # Verb is printed once while each branch has its own arrowhead.
            path = [(906,yy+16),(1080,yy+16),(1080,yy+off+13),(1112,yy+off+13)]
            if off == offs[0]:
                s += [edge(path,verb,990,yy+10,2,animated,current)]
            else:
                d='M'+' L'.join(f'{x},{z}' for x,z in path[1:])
                s += [f'<path d="{d}" fill="none" stroke="#75849a" stroke-width="1.7" marker-end="url(#arrow)"/>']

    # C: four signatures; reads admits Query or Operation sources.
    s += [panel(1280,495,490,272,'C','Data & identity',3,current,animated)]
    for yy, source, verb, target in [(548,'Entity','contains','Value Object'),(600,'Query / Operation','reads','Entity'),(652,'Operation','creates','Entity'),(704,'Entity','emits','Event')]:
        if '/' in source:
            s += [rect(1296,yy,153,32,PALE['Behavioral'],COLORS['Behavioral'],8),text(1372,yy+21,source,12.5,700,COLORS['Behavioral'],'middle')]
        else:
            s += [node(1296,yy,source,153)]
        s += [node(1611,yy,target,142),edge([(1449,yy+16),(1611,yy+16)],verb,1530,yy+10,3,animated,current)]

    # D: two cross-feature signatures.
    s += [panel(770,787,490,209,'D','Across features',4,current,animated),text(858,852,'Feature A',14,600,anchor='middle'),text(1177,852,'Feature B',14,600,anchor='middle'),'<path d="M1020,838 L1020,980" stroke="#c5d0df" stroke-dasharray="5 5"/>']
    for yy, src, verb, target in [(870,'Event','triggers-cross','Operation'),(934,'Operation','produces-for','Entity')]:
        s += [node(786,yy,src,130),node(1112,yy,target,130),edge([(916,yy+16),(1112,yy+16)],verb,1010,yy+10,4,animated,current)]

    # E: two different Entity-to-Entity meanings.
    s += [panel(1280,787,490,209,'E','Ownership & membership',5,current,animated)]
    for yy, verb in [(850,'owns'),(902,'belongs-to')]:
        s += [node(1296,yy,'Entity A',130),node(1623,yy,'Entity B',130),edge([(1426,yy+16),(1623,yy+16)],verb,1525,yy+10,5,animated,current)]
    s += [text(1296,960,'owns: lifecycle or custody responsibility',13),text(1296,981,'belongs-to: membership or assignment',13)]
    s += [text(771,1023,'Enum supplies typed field/state references; it has no dedicated backend edge.',14),text(771,1047,'Mapping projects shape; it does not construct, persist or invoke.',14),text(31,1047,'Saga is represented by Workflow; it is not a separate active type.',13.5)]

    # Animated reading guide, always outside the semantic graph.
    s += [rect(30,1070,1740,53,'#e7edf8','none',10)]
    for p,(label,detail,_) in enumerate(PHASES):
        if not animated and p != current:
            continue
        s += [f'<g class="motion" opacity="{1 if not animated or p==0 else 0}">',gate(p) if animated else '',text(48,1102,f'{p+1:02d} / {label}',16,800,'#25427a'),text(450,1102,detail,15),'</g>']
    s += ['</svg>']
    return ''.join(s)


def at_distance(points, t):
    segments=[math.dist(a,b) for a,b in zip(points,points[1:])]
    distance=t*sum(segments)
    for a,b,length in zip(points,points[1:],segments):
        if distance <= length:
            q=distance/length if length else 0
            return a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q
        distance-=length
    return points[-1]


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    svg=build(animated=True)
    ET.fromstring(svg)
    (ROOT/'craft-backend-metatypes.svg').write_text(svg,encoding='utf-8')
    static=build(current=0)
    cairosvg.svg2png(bytestring=static.encode(),write_to=str(ROOT/'craft-backend-metatypes.png'))
    frames=[]
    for phase in range(len(PHASES)):
        content=build(current=phase)
        paths=[pts for p,pts in EDGES if p==phase]
        base=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=content.encode(),output_width=round(W*SCALE),output_height=round(H*SCALE)))).convert('RGB')
        for f in range(FPS*SECONDS_PER_PHASE):
            frame=base.copy()
            draw=ImageDraw.Draw(frame)
            if phase:
                for pts in paths:
                    x,y=at_distance(pts,(f+0.5)/(FPS*SECONDS_PER_PHASE))
                    x,y=x*SCALE,y*SCALE
                    draw.ellipse((x-6,y-6,x+6,y+6),fill='#a5eeee')
                    draw.ellipse((x-3.5,y-3.5,x+3.5,y+3.5),fill='#087f82')
            frames.append(frame)
    # Shared palette avoids frame-to-frame text color jitter.
    sample=Image.new('RGB',(frames[0].width,frames[0].height*len(PHASES)))
    for i in range(len(PHASES)):
        sample.paste(frames[i*FPS*SECONDS_PER_PHASE],(0,i*frames[0].height))
    palette=sample.quantize(colors=240)
    frames=[frame.quantize(palette=palette,dither=Image.Dither.NONE) for frame in frames]
    frames[0].save(ROOT/'craft-backend-metatypes.gif',save_all=True,append_images=frames[1:],duration=[120,130]*(len(frames)//2),loop=0,optimize=True,disposal=1)
    with Image.open(ROOT/'craft-backend-metatypes.gif') as gif:
        assert gif.n_frames > 60, gif.n_frames
        assert gif.info['loop']==0
        total_duration=0
        for i in range(gif.n_frames):
            gif.seek(i)
            total_duration+=gif.info['duration']
        assert total_duration==12000,total_duration
        info={'svg_dimensions':[W,H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'loop_seconds':12,'backend_types':len(TYPES),'relationship_signatures':17,'source':'craft/authority/definitions/relationships/relationships.yml'}
    (ROOT/'metadata.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__ == '__main__':
    main()
