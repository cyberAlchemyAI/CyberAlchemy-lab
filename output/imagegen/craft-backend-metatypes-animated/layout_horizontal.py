"""Definition-first horizontal revision. Reuses the checked relationship drawings."""
from pathlib import Path
import io
import json
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image, ImageDraw, ImageFont

import build as base

ROOT = Path(__file__).resolve().parent
W, H, SCALE = 2080, 1480, 0.8
STEM = 'craft-backend-metatypes-v2'
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
PANELS = [
    (770,245,30,850),
    (770,495,1050,850),
    (1280,495,1560,850),
    (770,787,30,1142),
    (1280,787,540,1142),
]


def wrap(value, max_width=344):
    lines, line = [], ''
    for word in value.split():
        candidate = (line + ' ' + word).strip()
        if FONT.getlength(candidate) > max_width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    assert len(lines) <= 4, (value, lines)
    return lines


def build(current=0, animated=False):
    old = ET.fromstring(base.build(current=current, animated=animated))
    for element in old.iter():
        element.tag = element.tag.split('}')[-1]
    items = list(old)
    starts=[]
    for ox,oy,_,_ in PANELS:
        starts.append(next(i for i,e in enumerate(items) if e.tag=='rect' and e.get('x')==str(ox) and e.get('y')==str(oy)))
    end=next(i for i,e in enumerate(items) if e.tag=='text' and e.get('x')=='771' and e.get('y')=='1023')
    translated=[]
    for phase, points in base.EDGES:
        ox,oy,nx,ny=PANELS[phase-1]
        translated.append((phase,[(x+nx-ox,y+ny-oy) for x,y in points]))

    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title description">',
       '<title id="title">Craft backend meta-types: definitions above, relationships below</title>',
       '<desc id="description">Thirteen large definition cards occupy the top section. Five relationship diagrams below contain seventeen canonical signatures. A twelve-second reading animation highlights related definition cards and diagrams.</desc>',
       ET.tostring(old.find('defs'),encoding='unicode'),
       ET.tostring(old.find('style'),encoding='unicode'),
       base.rect(0,0,W,H,'#f5f8fc','none',0),
       base.text(30,60,'CRAFT / BACKEND META-TYPES',40,800,'#17243e'),
       base.text(32,97,'13 semantic types • what they mean • how they connect',23),
       base.text(32,148,'01',20,800,'#087f82'),base.text(83,148,'DEFINITIONS',27,800),
       base.text(2050,148,'The meaning carried by each type',18,400,anchor='end')]
    for i,(cat,name,a,b) in enumerate(base.TYPES):
        row,col=divmod(i,5)
        x=30+col*408+(408 if row==2 else 0)
        y=176+row*192
        color,pale=base.COLORS[cat],base.PALE[cat]
        s += [base.rect(x,y,388,176,'#ffffff','#d4dce7',14),
              base.rect(x,y,388,55,pale,'none',14),
              base.rect(x,y+38,388,17,pale,'none',0),
              base.text(x+20,y+22,cat.upper(),12,800,color),
              base.text(x+20,y+48,name,26,800,color)]
        for j,line in enumerate(wrap(a+' '+b)):
            s.append(base.text(x+20,y+86+j*25,line,18,400,'#26334c'))
        if animated:
            for phase,(_,_,members) in enumerate(base.PHASES):
                if name in members:
                    s.append(base.highlight(x,y,388,176,phase,current,True,color,14))
        elif name in base.PHASES[current][2]:
            s.append(base.rect(x,y,388,176,'none',color,14,'stroke-width="3"'))

    s += [base.text(30,772,'Saga is represented by Workflow; it is not a separate active type.',15),
          '<path d="M30,794 H2050" stroke="#ccd7e6" stroke-width="2"/>',
          base.text(32,830,'02',20,800,'#087f82'),base.text(83,830,'RELATIONSHIPS',27,800),
          base.text(2050,830,'17 canonical signatures • arrows carry directed meaning',18,400,anchor='end')]
    for p,(ox,oy,nx,ny) in enumerate(PANELS):
        stop=starts[p+1] if p+1<len(starts) else end
        s.append(f'<g transform="translate({nx-ox} {ny-oy})">')
        s += [ET.tostring(e,encoding='unicode') for e in items[starts[p]:stop]]
        s.append('</g>')
    s += [base.rect(1050,1142,1000,209,'#eaf0f8','none',12),
          base.text(1074,1177,'READING THE MAP',18,800,'#25427a'),
          base.text(1074,1212,'Enum appears in typed fields and state values; it has no dedicated backend edge.',17),
          base.text(1074,1245,'Mapping projects shape; it does not construct, persist or invoke.',17),
          base.text(1074,1278,'Branching targets are alternatives within one relationship signature.',17),
          base.text(1074,1311,'The animation guides reading; it does not prescribe runtime execution order.',17),
          base.rect(30,1380,2020,63,'#e0e9f6','none',12)]
    for phase,(label,detail,_) in enumerate(base.PHASES):
        if not animated and phase!=current:
            continue
        s += [f'<g class="motion" opacity="{1 if not animated or phase==0 else 0}">',base.gate(phase) if animated else '',
              base.text(52,1420,f'{phase+1:02d} / {label}',18,800,'#25427a'),base.text(570,1420,detail,18),'</g>']
    s.append('</svg>')
    return ''.join(s),translated


def main():
    svg,_=build(animated=True)
    ET.fromstring(svg)
    assert not any(word in svg.lower() for word in ['profile','typescript','python','rust'])
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    still,_=build()
    cairosvg.svg2png(bytestring=still.encode(),write_to=str(ROOT/f'{STEM}.png'))
    frames=[]
    for phase in range(len(base.PHASES)):
        content,all_paths=build(current=phase)
        assert len(all_paths)==17
        paths=[pts for p,pts in all_paths if p==phase]
        bg=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=content.encode(),output_width=round(W*SCALE),output_height=round(H*SCALE)))).convert('RGB')
        for f in range(base.FPS*base.SECONDS_PER_PHASE):
            frame=bg.copy()
            draw=ImageDraw.Draw(frame)
            for pts in paths:
                x,y=base.at_distance(pts,(f+0.5)/(base.FPS*base.SECONDS_PER_PHASE))
                x,y=x*SCALE,y*SCALE
                draw.ellipse((x-6,y-6,x+6,y+6),fill='#a5eeee')
                draw.ellipse((x-3.5,y-3.5,x+3.5,y+3.5),fill='#087f82')
            frames.append(frame)
    sample=Image.new('RGB',(frames[0].width,frames[0].height*len(base.PHASES)))
    for i in range(len(base.PHASES)):
        sample.paste(frames[i*base.FPS*base.SECONDS_PER_PHASE],(0,i*frames[0].height))
    palette=sample.quantize(colors=240)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    frames[0].save(ROOT/f'{STEM}.gif',save_all=True,append_images=frames[1:],duration=[120,130]*(len(frames)//2),loop=0,optimize=True,disposal=1)
    with Image.open(ROOT/f'{STEM}.gif') as gif:
        total=0
        for i in range(gif.n_frames):
            gif.seek(i)
            total+=gif.info['duration']
        assert total==12000
        assert gif.info['loop']==0
        info={'layout':'definitions-top-relationships-bottom','definition_cards':13,'definition_font_size':18,'relationship_signatures':17,'svg_dimensions':[W,H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'loop_seconds':total/1000}
    (ROOT/f'{STEM}.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__=='__main__':
    main()
