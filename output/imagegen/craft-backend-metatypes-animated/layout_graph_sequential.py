"""A single highlighted connection at a time; stream the GIF to bound memory."""
from pathlib import Path
import io
import json
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw, ImageChops, GifImagePlugin
import build as base
import layout_atlas as art
import layout_graph_clear as graph
import layout_graph_brand as brand

ROOT=Path(__file__).resolve().parent
STEM='craft-backend-metatypes-v7'
ORDER=[
 ('Rule','enforces','Operation'),('Entity','performs','Operation'),
 ('Operation','creates','Entity'),('Operation','reads','Entity'),
 ('Calculation','calculates','Operation'),('Policy','applies','Calculation'),
 ('Policy','applies','Operation'),('Workflow','orchestrates','Operation'),
 ('Operation','produces','Event'),('Entity','emits','Event'),
 ('Event','transitions','State Machine'),('Event','triggers-cross','Operation'),
 ('Operation','produces-for','Entity'),('Interface','exposes','Operation'),
 ('Interface','exposes','Query'),('Query','reads','Entity'),
 ('Mapping','maps','Entity'),('Mapping','maps','Value Object'),
 ('Mapping','maps','Interface'),('Entity','contains','Value Object'),
 ('Entity','owns','Entity'),('Entity','belongs-to','Entity'),
]
LOOKUP={(a[0],a[2],a[1]):a for a in graph.ARCS}
assert len(ORDER)==len(LOOKUP)==22 and set(ORDER)==set(LOOKUP)
STEPS=[LOOKUP[key] for key in ORDER]+[
 ('Value Object','Enum','typed field reference',None,[(440,220),(440,180),(1970,180),(1970,220)],(1670,181))]
SECONDS=2
DURATION=len(STEPS)*SECONDS
SVG_NS='http://www.w3.org/2000/svg'


def gate(index):
    values=['1' if i==index else '0' for i in range(len(STEPS))]
    values.append(values[0])
    times=[str(i/len(STEPS)) for i in range(len(STEPS)+1)]
    return f'<animate attributeName="opacity" values="{";".join(values)}" keyTimes="{";".join(times)}" calcMode="discrete" dur="{DURATION}s" repeatCount="indefinite"/>'


def static_root():
    root=ET.fromstring(brand.build(current=0,animated=False))
    for element in root.iter():element.tag=element.tag.split('}')[-1]
    root.set('xmlns',SVG_NS)
    root.find('title').text='Craft backend meta-types · one connection at a time'
    root.find('desc').text='One definition box per meta-type. Exactly one connection is highlighted at a time, together with its source and target. Twenty-two canonical branches and one dashed field-typing reference are shown separately, two seconds each, in a 46-second loop. The Lab logo, Paper & crimson palette and crossing-free layout are preserved.'
    # Remove the obsolete group-phase caption. There are no hidden earlier animations left behind.
    for parent in list(root.iter()):
        for child in list(parent):
            if child.get('class')=='motion':parent.remove(child)
    for element in root.iter():
        if element.tag=='path' and element.get('data-signature'):element.set('opacity','.36')
        if element.tag=='text' and (element.get('x'),element.get('y')) in {(str(a[5][0]),str(a[5][1])) for a in graph.ARCS}:
            element.set('opacity','.65')
        if element.tag=='text' and element.get('y')=='2222':
            element.text='One highlighted connection at a time. All definitions remain visible. Saga is represented by Workflow.'
    return root


def fragment(value):return ET.fromstring(value)


def overlay(index,animated=False):
    source,target,verb,_,points,(lx,ly)=STEPS[index]
    path='M'+' L'.join(f'{x},{y}' for x,y in points)
    group=ET.Element('g',{'class':'motion' if animated else 'selected-connection','data-sequence-step':str(index),'data-connection':f'{source}|{verb}|{target}','opacity':'1' if not animated or index==0 else '0'})
    if animated:group.append(fragment(gate(index)))
    dashed=' stroke-dasharray="6 8"' if index==22 else ''
    group.append(fragment(f'<path data-active-arrow="true" d="{path}" fill="none" stroke="{brand.ACCENT}" stroke-width="3.3" marker-end="url(#activeArrow)"{dashed}/>'))
    if animated:
        group.append(fragment(f'<circle r="5" fill="{brand.ACCENT}"><animateMotion dur="2s" repeatCount="indefinite" path="{path}"/></circle>'))
    width=len(verb)*9.5+20
    group.append(fragment(base.rect(lx-width/2,ly-21,width,29,brand.SOFT,'none',3)))
    group.append(fragment(art.label(lx,ly,verb,17,700,brand.ACCENT,'middle')))
    for name in dict.fromkeys([source,target]):
        x,y=graph.POSITIONS[name]
        group.append(fragment(base.rect(x,y,graph.NW,graph.NH,'none',brand.ACCENT,3,'stroke-width="4" data-selected-type="'+name+'"')))
    group.append(fragment(art.label(60,2275,f'{index+1:02d} / {len(STEPS):02d}',18,700,brand.ACCENT)))
    caption=f'{source}  →  {verb}  →  {target}'
    group.append(fragment(art.label(220,2275,caption,20,700,brand.INK)))
    return group


def build(index=0,animated=False):
    root=static_root()
    if animated:
        for i in range(len(STEPS)):root.append(overlay(i,True))
    else:root.append(overlay(index))
    return ET.tostring(root,encoding='unicode')


def check(svg):
    graph.check()
    root=ET.fromstring(svg)
    assert root.tag=='{'+SVG_NS+'}svg'
    assert len([e for e in root.iter() if e.get('data-meta-type')])==13
    assert len({e.get('data-signature') for e in root.iter() if e.get('data-signature')})==17
    groups=[e for e in root if e.get('data-sequence-step') is not None]
    assert len(groups)==23
    for step in range(23):
        selected=[]
        for group in groups:
            animation=next(e for e in group if e.tag.endswith('animate'))
            assert animation.get('dur')=='46s'
            values=animation.get('values').split(';')
            if values[step]=='1':selected.append(group)
        assert len(selected)==1
        assert selected[0].get('data-sequence-step')==str(step)
        assert len([e for e in selected[0] if e.get('data-active-arrow')])==1
        assert len([e for e in selected[0] if e.get('data-selected-type')])==len(set(STEPS[step][:2]))


def main():
    svg=build(animated=True);check(svg)
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    cairosvg.svg2png(bytestring=build().encode(),write_to=str(ROOT/f'{STEM}.png'))
    width,height=round(graph.W*graph.SCALE),round(graph.H*graph.SCALE)
    first=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=build(0).encode(),output_width=width,output_height=height))).convert('RGB')
    palette=first.quantize(colors=240)
    previous=None;sample_expected={};frame_number=0
    with (ROOT/f'{STEM}.gif').open('wb') as out:
        for step in range(len(STEPS)):
            if step==0:bg=first
            else:bg=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=build(step).encode(),output_width=width,output_height=height))).convert('RGB')
            points=STEPS[step][4]
            for f in range(16):
                frame=bg.copy();draw=ImageDraw.Draw(frame)
                # One moving marker; it follows only this step's arrow.
                x,y=base.at_distance(points,(f+.5)/16);x*=graph.SCALE;y*=graph.SCALE
                draw.ellipse((x-6,y-6,x+6,y+6),fill=brand.SOFT)
                draw.ellipse((x-3.7,y-3.7,x+3.7,y+3.7),fill=brand.ACCENT)
                indexed=frame.quantize(palette=palette,dither=Image.Dither.NONE)
                delay=120 if f%2==0 else 130
                if previous is None:
                    headers,_=GifImagePlugin.getheader(indexed,info={'loop':0,'optimize':False})
                    for chunk in headers:out.write(chunk)
                    crop=indexed;offset=(0,0)
                else:
                    bounds=ImageChops.difference(previous,indexed).getbbox()
                    if bounds is None:bounds=(0,0,1,1)
                    crop=indexed.crop(bounds);offset=bounds[:2]
                for chunk in GifImagePlugin.getdata(crop,offset=offset,duration=delay,disposal=1,include_color_table=False):out.write(chunk)
                if frame_number in {0,16,176,367}:sample_expected[frame_number]=indexed.convert('RGB')
                previous=indexed;frame_number+=1
        out.write(b';')
    with Image.open(ROOT/f'{STEM}.gif') as gif:
        assert gif.n_frames==368,gif.n_frames
        assert gif.info['loop']==0
        total=0
        for i in range(gif.n_frames):
            gif.seek(i);total+=gif.info['duration']
            if i in sample_expected:assert ImageChops.difference(gif.convert('RGB'),sample_expected[i]).getbbox() is None,('delta playback mismatch',i)
        assert total==46000,total
        info={'design':'single-connection-reading-sequence','unique_types':13,'canonical_signatures':17,'canonical_branches':22,'additional_field_typing_step':1,'total_steps':23,'seconds_per_step':2,'loop_seconds':46,'simultaneous_highlighted_connections':1,'highlighted_nodes':'source and target only; one unique node for Entity loops','crossings':0,'definition_font_size':24,'palette':'website Paper & crimson','official_lab_logo':True,'svg_dimensions':[graph.W,graph.H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'gif_delta_playback_checked':True,'sequence':[{'source':a[0],'verb':a[2],'target':a[1]} for a in STEPS]}
    (ROOT/f'{STEM}.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps({k:v for k,v in info.items() if k!='sequence'}))


if __name__=='__main__':main()
