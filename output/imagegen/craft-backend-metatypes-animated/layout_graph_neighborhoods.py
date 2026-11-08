"""Focus one meta-type and its remaining neighborhood; never repeat a branch."""
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
import layout_graph_sequential as sequential

ROOT=Path(__file__).resolve().parent
STEM='craft-backend-metatypes-v8'
W,H=graph.W,2180
SECONDS=4
BRANCHES=sequential.STEPS
FOCUS_ORDER=['Operation','Entity','Mapping','Interface','Policy','Event','Value Object']
GROUPS=[]
unseen=set(range(len(BRANCHES)))
for name in FOCUS_ORDER:
    selected=[i for i in sorted(unseen) if name in BRANCHES[i][:2]]
    if selected:
        GROUPS.append((name,selected))
        unseen.difference_update(selected)
assert not unseen
DURATION=SECONDS*len(GROUPS)


def animation(attribute,values):
    values=list(values)+[values[0]]
    times=[str(i/len(GROUPS)) for i in range(len(GROUPS)+1)]
    return f'<animate attributeName="{attribute}" values="{";".join(str(v) for v in values)}" keyTimes="{";".join(times)}" calcMode="discrete" dur="{DURATION}s" repeatCount="indefinite"/>'


def fragment(value):return ET.fromstring(value)


def static_root(index=0,animated=False):
    root=sequential.static_root()
    root.set('height',str(H));root.set('viewBox',f'0 0 {W} {H}')
    root.find('title').text='Craft backend meta-types · connected neighborhoods'
    root.find('desc').text='Focus one meta-type at a time. Operation first shows all its incoming and outgoing relationships. Entity then shows only its relationships not already covered by Operation. Remaining types follow the same non-repetition rule. Every canonical branch appears exactly once per loop. The dashed field-typing reference is separate from the seventeen canonical signatures. Entity loops relate distinct Entity instances. One focal definition is emphasized at a time; all definitions remain visible.'
    # Remove every bottom note, legend and caption bar; keep the category key in the masthead.
    for child in list(root):
        if child.tag in {'text','rect'} and float(child.get('y','0'))>=2160:root.remove(child)
    for node in root:
        name=node.get('data-meta-type')
        if not name:continue
        frame=next(e for e in node if e.tag=='rect')
        original_fill=frame.get('fill');original_stroke=frame.get('stroke')
        if animated:
            focus=[name==focal for focal,_ in GROUPS]
            if any(focus):
                frame.set('data-focal-frame',name)
                frame.set('fill',brand.SOFT if focus[0] else original_fill)
                frame.set('stroke',brand.ACCENT if focus[0] else original_stroke)
                frame.set('stroke-width','4' if focus[0] else '1.8')
                frame.append(fragment(animation('fill',[brand.SOFT if yes else original_fill for yes in focus])))
                frame.append(fragment(animation('stroke',[brand.ACCENT if yes else original_stroke for yes in focus])))
                frame.append(fragment(animation('stroke-width',[4 if yes else 1.8 for yes in focus])))
        elif name==GROUPS[index][0]:
            frame.set('fill',brand.SOFT);frame.set('stroke',brand.ACCENT);frame.set('stroke-width','4')
            frame.set('data-focused-type',name)
    return root


def overlay(index,animated=False):
    name,branches=GROUPS[index]
    group=ET.Element('g',{'class':'motion' if animated else 'active-neighborhood','data-focus-type':name,'data-neighborhood-index':str(index),'opacity':'1' if not animated or index==0 else '0'})
    if animated:group.append(fragment(animation('opacity',[1 if i==index else 0 for i in range(len(GROUPS))])))
    for branch_index in branches:
        source,target,verb,_,points,(lx,ly)=BRANCHES[branch_index]
        path='M'+' L'.join(f'{x},{y}' for x,y in points)
        dashed=' stroke-dasharray="6 8"' if branch_index==22 else ''
        group.append(fragment(f'<path data-active-branch="{branch_index}" data-connection="{source}|{verb}|{target}" d="{path}" fill="none" stroke="{brand.ACCENT}" stroke-width="3.3" marker-end="url(#activeArrow)"{dashed}/>'))
        if animated:group.append(fragment(f'<circle r="4.4" fill="{brand.ACCENT}"><animateMotion dur="{SECONDS}s" repeatCount="indefinite" path="{path}"/></circle>'))
        width=len(verb)*9.5+20
        group.append(fragment(base.rect(lx-width/2,ly-21,width,29,brand.SOFT,'none',3)))
        group.append(fragment(art.label(lx,ly,verb,17,700,brand.ACCENT,'middle')))
    return group


def build(index=0,animated=False):
    root=static_root(index,animated)
    if animated:
        for i in range(len(GROUPS)):root.append(overlay(i,True))
    else:root.append(overlay(index))
    return ET.tostring(root,encoding='unicode')


def check(svg):
    graph.check()
    root=ET.fromstring(svg)
    assert root.tag=='{'+sequential.SVG_NS+'}svg'
    assert len([e for e in root.iter() if e.get('data-meta-type')])==13
    assert len({e.get('data-signature') for e in root.iter() if e.get('data-signature')})==17
    groups=[e for e in root if e.get('data-focus-type')]
    assert [e.get('data-focus-type') for e in groups]==FOCUS_ORDER
    all_ids=[int(e.get('data-active-branch')) for group in groups for e in group if e.get('data-active-branch') is not None]
    assert sorted(all_ids)==list(range(23)) and len(all_ids)==len(set(all_ids))
    assert set(GROUPS[0][1])=={i for i,b in enumerate(BRANCHES) if 'Operation' in b[:2]}
    assert all('Operation' not in BRANCHES[i][:2] for i in GROUPS[1][1])
    for phase in range(len(GROUPS)):
        active=[]
        for group in groups:
            anim=next(e for e in group if e.tag.endswith('animate'))
            if anim.get('values').split(';')[phase]=='1':active.append(group)
        assert len(active)==1 and active[0].get('data-focus-type')==GROUPS[phase][0]
        frames=[e for e in root.iter() if e.get('data-focal-frame')]
        selected=[]
        for frame in frames:
            anim=next(e for e in frame if e.get('attributeName')=='stroke-width')
            if anim.get('values').split(';')[phase]=='4':selected.append(frame.get('data-focal-frame'))
        assert selected==[GROUPS[phase][0]]
    assert not [e for e in root if e.tag.endswith(('text','rect')) and float(e.get('y','0'))>=2160]


def main():
    svg=build(animated=True);check(svg)
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    cairosvg.svg2png(bytestring=build().encode(),write_to=str(ROOT/f'{STEM}.png'))
    # Save Entity's phase as a second QA still, checking the user's requested exclusion visually.
    cairosvg.svg2png(bytestring=build(1).encode(),write_to=str(ROOT/f'{STEM}-entity-check.png'))
    width,height=round(W*graph.SCALE),round(H*graph.SCALE)
    first=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=build().encode(),output_width=width,output_height=height))).convert('RGB')
    palette=first.quantize(colors=240)
    previous=None;samples={};frame_number=0
    frames_per_group=SECONDS*8
    total_frames=frames_per_group*len(GROUPS)
    with (ROOT/f'{STEM}.gif').open('wb') as out:
        for step,(_,branches) in enumerate(GROUPS):
            bg=first if step==0 else Image.open(io.BytesIO(cairosvg.svg2png(bytestring=build(step).encode(),output_width=width,output_height=height))).convert('RGB')
            for f in range(frames_per_group):
                frame=bg.copy();draw=ImageDraw.Draw(frame)
                for branch_index in branches:
                    points=BRANCHES[branch_index][4]
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
        total=0
        for i in range(gif.n_frames):
            gif.seek(i);total+=gif.info['duration']
            if i in samples:assert ImageChops.difference(gif.convert('RGB'),samples[i]).getbbox() is None
        assert total==DURATION*1000 and gif.info['loop']==0
        info={'design':'non-repeating-meta-type-neighborhoods','unique_types':13,'canonical_signatures':17,'canonical_branches':22,'field_type_references':1,'focus_groups':[{'meta_type':name,'connections':[{'source':BRANCHES[i][0],'verb':BRANCHES[i][2],'target':BRANCHES[i][1]} for i in indices]} for name,indices in GROUPS],'seconds_per_group':SECONDS,'loop_seconds':DURATION,'simultaneously_focused_meta_types':1,'repeated_connection_branches':0,'bottom_legend':False,'bottom_caption':False,'definition_font_size':24,'crossings':0,'official_lab_logo':True,'palette':'website Paper & crimson','svg_dimensions':[W,H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'gif_delta_playback_checked':True}
    (ROOT/f'{STEM}.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps({**{k:v for k,v in info.items() if k!='focus_groups'},'group_connection_counts':{name:len(ids) for name,ids in GROUPS}}))


if __name__=='__main__':main()
