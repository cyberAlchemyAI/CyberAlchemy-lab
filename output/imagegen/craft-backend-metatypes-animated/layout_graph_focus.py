"""Slower neighborhood reading, with strong visual separation from unrelated content."""
from pathlib import Path
import io
import json
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw, ImageChops, GifImagePlugin
import build as base
import layout_graph_clear as graph
import layout_graph_brand as brand
import layout_graph_neighborhoods as neighborhoods

ROOT=Path(__file__).resolve().parent
STEM='craft-backend-metatypes-v9'
SECONDS=8
DURATION=SECONDS*len(neighborhoods.GROUPS)
UNRELATED_NODE_OPACITY='0.18'
UNRELATED_ARROW_OPACITY='0.07'
UNRELATED_LABEL_OPACITY='0.14'


def related_types(index):
    focal,branches=neighborhoods.GROUPS[index]
    return {focal}|{name for i in branches for name in neighborhoods.BRANCHES[i][:2]}


def opacity_animation(values):
    values=list(values)+[values[0]]
    times=[str(i/len(neighborhoods.GROUPS)) for i in range(len(neighborhoods.GROUPS)+1)]
    return ET.fromstring(f'<animate attributeName="opacity" values="{";".join(values)}" keyTimes="{";".join(times)}" calcMode="discrete" dur="{DURATION}s" repeatCount="indefinite"/>')


def build(index=0,animated=False):
    root=ET.fromstring(neighborhoods.build(index=index,animated=animated))
    for element in root.iter():element.tag=element.tag.split('}')[-1]
    root.set('xmlns',neighborhoods.sequential.SVG_NS)
    root.find('title').text='Craft backend meta-types · slow focused neighborhoods'
    root.find('desc').text='Eight seconds per focal meta-type, in a 56-second loop. The focal definition and neighbors in its selected connections stay fully readable. Unrelated definitions fade to 18 percent opacity, unrelated arrows to 7 percent, and unrelated relationship labels to 14 percent. Operation is first; later groups exclude previously shown branches. The bottom legend and caption remain removed.'
    for element in root.iter():
        if element.tag=='animate':element.set('dur',f'{DURATION}s')
        elif element.tag=='animateMotion':element.set('dur',f'{SECONDS}s')
    labels={(str(a[5][0]),str(a[5][1])) for a in neighborhoods.BRANCHES}
    for element in root:
        name=element.get('data-meta-type')
        if name:
            values=['1' if name in related_types(i) else UNRELATED_NODE_OPACITY for i in range(len(neighborhoods.GROUPS))]
            element.set('opacity',values[0] if animated else values[index])
            element.set('data-neighborhood-visibility',name)
            if animated:element.append(opacity_animation(values))
        elif element.tag=='path' and element.get('data-signature'):
            element.set('opacity',UNRELATED_ARROW_OPACITY)
        elif element.tag=='path' and element.get('d')=='M440 220V180H1970V220':
            element.set('opacity',UNRELATED_ARROW_OPACITY)
        elif element.tag=='text' and (element.get('x'),element.get('y')) in labels:
            element.set('opacity',UNRELATED_LABEL_OPACITY)
    # Group opacity includes marker heads in raster renderers as well as native SVG viewers.
    for element in list(root):
        if element.tag=='path' and (element.get('data-signature') or element.get('d')=='M440 220V180H1970V220'):
            position=list(root).index(element)
            root.remove(element)
            element.set('opacity','1')
            muted=ET.Element('g',{'opacity':UNRELATED_ARROW_OPACITY,'data-muted-arrow':'true'})
            muted.append(element)
            root.insert(position,muted)
    return ET.tostring(root,encoding='unicode')


def check(svg):
    neighborhoods.check(svg)
    root=ET.fromstring(svg)
    nodes=[e for e in root if e.get('data-meta-type')]
    for phase in range(len(neighborhoods.GROUPS)):
        visible=set()
        for node in nodes:
            opacity=next(e for e in node if e.get('attributeName')=='opacity')
            values=opacity.get('values').split(';')
            if values[phase]=='1':visible.add(node.get('data-meta-type'))
            else:assert values[phase]==UNRELATED_NODE_OPACITY
        assert visible==related_types(phase)
    for element in root.iter():
        if element.tag.endswith('animate'):assert element.get('dur')=='56s'
        if element.tag.endswith('animateMotion'):assert element.get('dur')=='8s'
    muted=[e for e in root if e.get('data-muted-arrow')]
    assert len(muted)==23
    assert all(e.get('opacity')==UNRELATED_ARROW_OPACITY for e in muted)


def main():
    svg=build(animated=True);check(svg)
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    cairosvg.svg2png(bytestring=build().encode(),write_to=str(ROOT/f'{STEM}.png'))
    cairosvg.svg2png(bytestring=build(1).encode(),write_to=str(ROOT/f'{STEM}-entity-check.png'))
    width,height=round(neighborhoods.W*graph.SCALE),round(neighborhoods.H*graph.SCALE)
    first=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=build().encode(),output_width=width,output_height=height))).convert('RGB')
    palette=first.quantize(colors=240)
    frames_per_group=SECONDS*8
    total_frames=frames_per_group*len(neighborhoods.GROUPS)
    samples={};previous=None;frame_number=0
    with (ROOT/f'{STEM}.gif').open('wb') as out:
        for step,(_,branches) in enumerate(neighborhoods.GROUPS):
            bg=first if step==0 else Image.open(io.BytesIO(cairosvg.svg2png(bytestring=build(step).encode(),output_width=width,output_height=height))).convert('RGB')
            for f in range(frames_per_group):
                frame=bg.copy();draw=ImageDraw.Draw(frame)
                for branch in branches:
                    points=neighborhoods.BRANCHES[branch][4]
                    x,y=base.at_distance(points,(f+.5)/frames_per_group);x*=graph.SCALE;y*=graph.SCALE
                    draw.ellipse((x-5,y-5,x+5,y+5),fill=brand.SOFT)
                    draw.ellipse((x-3.2,y-3.2,x+3.2,y+3.2),fill=brand.ACCENT)
                indexed=frame.quantize(palette=palette,dither=Image.Dither.NONE)
                if previous is None:
                    headers,_=GifImagePlugin.getheader(indexed,info={'loop':0,'optimize':False})
                    for chunk in headers:out.write(chunk)
                    crop=indexed;offset=(0,0)
                else:
                    bounds=ImageChops.difference(previous,indexed).getbbox() or (0,0,1,1)
                    crop=indexed.crop(bounds);offset=bounds[:2]
                for chunk in GifImagePlugin.getdata(crop,offset=offset,duration=120 if f%2==0 else 130,disposal=1,include_color_table=False):out.write(chunk)
                if frame_number in {0,frames_per_group,2*frames_per_group,total_frames-1}:samples[frame_number]=indexed.convert('RGB')
                previous=indexed;frame_number+=1
        out.write(b';')
    with Image.open(ROOT/f'{STEM}.gif') as gif:
        assert gif.n_frames==total_frames
        duration=0
        for i in range(gif.n_frames):
            gif.seek(i);duration+=gif.info['duration']
            if i in samples:assert ImageChops.difference(gif.convert('RGB'),samples[i]).getbbox() is None
        assert duration==DURATION*1000 and gif.info['loop']==0
        info={'design':'slow-focused-meta-type-neighborhoods','unique_types':13,'canonical_signatures':17,'canonical_branches':22,'field_typing_references':1,'focal_order':[name for name,_ in neighborhoods.GROUPS],'seconds_per_group':SECONDS,'previous_seconds_per_group':4,'loop_seconds':DURATION,'unrelated_box_opacity':float(UNRELATED_NODE_OPACITY),'unrelated_arrow_opacity':float(UNRELATED_ARROW_OPACITY),'unrelated_label_opacity':float(UNRELATED_LABEL_OPACITY),'related_box_opacity':1,'simultaneously_focused_meta_types':1,'repeated_connection_branches':0,'bottom_legend':False,'bottom_caption':False,'definition_font_size':24,'crossings':0,'palette':'website Paper & crimson','official_lab_logo':True,'svg_dimensions':[neighborhoods.W,neighborhoods.H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'gif_delta_playback_checked':True}
    (ROOT/f'{STEM}.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__=='__main__':main()
