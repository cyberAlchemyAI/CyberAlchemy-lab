"""Eased neighborhood crossfades and measured, stationary relationship labels."""
from pathlib import Path
import io
import json
import math
import sys
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageFont, ImageChops, GifImagePlugin
import build as base
import layout_atlas as art
import layout_graph_clear as graph
import layout_graph_brand as brand
import layout_graph_neighborhoods as neighborhoods
import layout_graph_focus as focus

ROOT=Path(__file__).resolve().parent
STEM='craft-backend-metatypes-v10'
SECONDS=8
FADE=0.8
HOLD=SECONDS-FADE
DURATION=SECONDS*len(neighborhoods.GROUPS)
FPS=20
FADE_FRAMES=round(FADE*FPS)
LABEL_FONT_SIZE=19
LABEL_FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',LABEL_FONT_SIZE)
LABEL_HEIGHT=32

ARCS=[]
for source,target,verb,phase,points,position in graph.ARCS:
    if verb=='produces':points=[(x,1590 if y==1595 else y) for x,y in points]
    if verb=='triggers-cross':points=[(x,1628 if y==1625 else y) for x,y in points]
    ARCS.append((source,target,verb,phase,points,position))
CENTERS=[
 (715,1270),(830,1590),(900,1510),(920,1080),(830,1628),(1220,1360),
 (1595,1550),(440,1770),(1660,1200),(1595,820),(1220,1770),(1600,1770),
 (1970,1770),(800,610),(830,300),(1660,610),(440,610),(830,820),
 (860,1135),(440,1200),(130,785),(135,1035),
]
LOOKUP={}
for arc,center in zip(ARCS,CENTERS):
    source,target,verb,phase,points,_=arc
    LOOKUP[(source,verb,target)]=(source,target,verb,phase,points,center)
LOOKUP[('Value Object','typed field reference','Enum')]=('Value Object','Enum','typed field reference',None,[(440,220),(440,180),(1970,180),(1970,220)],(1670,180))
BRANCHES=[LOOKUP[(a[0],a[2],a[1])] for a in neighborhoods.BRANCHES]


def key_for(arc):return (arc[0],arc[2],arc[1])


def path_for(points):return 'M'+' L'.join(f'{x},{y}' for x,y in points)


def capsule_bounds(arc):
    verb=arc[2];x,y=arc[5]
    width=math.ceil(LABEL_FONT.getlength(verb))+24
    return x-width/2,y-LABEL_HEIGHT/2,x+width/2,y+LABEL_HEIGHT/2


def capsule(arc,active=False):
    source,target,verb,_,_,(x,y)=arc
    left,top,right,bottom=capsule_bounds(arc)
    group=ET.Element('g',{'data-label-key':'|'.join(key_for(arc)),'data-label-state':'active' if active else 'context'})
    # The opaque background masks the wire under the text; only contextual text/border are subdued.
    rect=ET.fromstring(base.rect(left,top,right-left,bottom-top,brand.SURFACE if active else brand.PAPER,brand.LINE,5,'stroke-width="0.8"'))
    rect.set('stroke-opacity','1' if active else '.16')
    group.append(rect)
    label=ET.fromstring(art.label(x,y+6.5,verb,LABEL_FONT_SIZE,700,brand.ACCENT if active else brand.MUTED,'middle'))
    if not active:label.set('opacity',focus.UNRELATED_LABEL_OPACITY)
    group.append(label)
    return group


def ease_animation(element):
    old=element.get('values','').split(';')
    if len(old)!=len(neighborhoods.GROUPS)+1:return
    states=[brand.SURFACE if value=='url(#card)' else value for value in old[:-1]]
    values=[states[0]];times=[0.0];splines=[]
    for phase in range(len(states)):
        times += [(phase*SECONDS+HOLD)/DURATION,((phase+1)*SECONDS)/DURATION]
        values += [states[phase],states[(phase+1)%len(states)]]
        splines += ['0 0 1 1','0.333333 0 0.666667 1']
    element.set('values',';'.join(values));element.set('keyTimes',';'.join(f'{t:.10f}' for t in times))
    element.set('calcMode','spline');element.set('keySplines',';'.join(splines));element.set('dur',f'{DURATION}s')


def build(index=0,animated=False):
    root=ET.fromstring(focus.build(index=index,animated=animated))
    for element in root.iter():element.tag=element.tag.split('}')[-1]
    root.set('xmlns',neighborhoods.sequential.SVG_NS)
    root.find('title').text='Craft backend meta-types · smooth reading transitions'
    root.find('desc').text='Eight seconds per neighborhood: a 7.2-second steady reading hold followed by a 0.8-second eased crossfade to the next focal type. Unrelated definitions and arrows remain faded. Stationary, measured relationship-label capsules preserve legibility. No moving particles. Operation first, then Entity links not already shown, followed by the other non-repeating groups. Official Lab logo, website Paper & crimson palette and large definitions are retained.'
    verbs={a[2] for a in BRANCHES}
    for child in list(root):
        if child.tag=='text' and child.text in verbs:root.remove(child)
        elif child.tag=='rect' and float(child.get('width','9999'))<600:root.remove(child)
    for element in root.iter():
        if element.tag=='rect' and element.get('fill')=='url(#card)':element.set('fill',brand.SURFACE)
        if element.tag=='animate':ease_animation(element)
        if element.get('data-signature'):
            arc=ARCS[int(element.get('id').split('-')[-1])]
            element.set('d',path_for(arc[4]))
    # Strip particles and old label fragments before adding fixed capsules in a consistent layer.
    overlays=[e for e in root if e.get('data-focus-type')]
    first_overlay=list(root).index(overlays[0])
    for offset,arc in enumerate(BRANCHES):root.insert(first_overlay+offset,capsule(arc))
    for overlay in overlays:
        phase=int(overlay.get('data-neighborhood-index'))
        for child in list(overlay):
            if child.tag in {'circle','rect','text'}:overlay.remove(child)
            elif child.get('data-active-branch') is not None:
                arc=BRANCHES[int(child.get('data-active-branch'))]
                child.set('d',path_for(arc[4]))
        for branch in neighborhoods.GROUPS[phase][1]:overlay.append(capsule(BRANCHES[branch],True))
    return ET.tostring(root,encoding='unicode')


def validate_layout():
    graph.check()
    assert graph.crossings(ARCS)==([],[])
    for arc in ARCS:
        for (x1,y1),(x2,y2) in zip(arc[4],arc[4][1:]):
            for name,(nx,ny) in graph.POSITIONS.items():
                hit=(nx+1<x1<nx+graph.NW-1 and max(min(y1,y2),ny+1)<min(max(y1,y2),ny+graph.NH-1)) if x1==x2 else (ny+1<y1<ny+graph.NH-1 and max(min(x1,x2),nx+1)<min(max(x1,x2),nx+graph.NW-1))
                assert not hit,('arrow intersects definition',key_for(arc),name)
    for i,arc in enumerate(BRANCHES):
        left,top,right,bottom=capsule_bounds(arc)
        assert 0<left<right<graph.W and 145<top<bottom<neighborhoods.H
        for name,(nx,ny) in graph.POSITIONS.items():
            assert not(max(left,nx)<min(right,nx+graph.NW) and max(top,ny)<min(bottom,ny+graph.NH)),('label intersects definition',key_for(arc),name)
        for j,other in enumerate(BRANCHES):
            if i==j:continue
            ol,ot,orr,ob=capsule_bounds(other)
            assert not(max(left,ol)<min(right,orr) and max(top,ot)<min(bottom,ob)),('label overlaps label',key_for(arc),key_for(other))
            for (x1,y1),(x2,y2) in zip(other[4],other[4][1:]):
                hit=(left<x1<right and max(min(y1,y2),top)<min(max(y1,y2),bottom)) if x1==x2 else (top<y1<bottom and max(min(x1,x2),left)<min(max(x1,x2),right))
                assert not hit,('label obscures another arrow',key_for(arc),key_for(other))


def check(svg):
    validate_layout()
    root=ET.fromstring(svg)
    assert len([e for e in root.iter() if e.get('data-meta-type')])==13
    assert len({e.get('data-signature') for e in root.iter() if e.get('data-signature')})==17
    assert not any(e.tag.endswith('animateMotion') for e in root.iter())
    animations=[e for e in root.iter() if e.tag.endswith('animate')]
    assert animations and all(e.get('calcMode')=='spline' and e.get('dur')=='56s' for e in animations)
    for e in animations:
        assert len(e.get('values').split(';'))==15
        assert len(e.get('keyTimes').split(';'))==15
        assert len(e.get('keySplines').split(';'))==14
        assert e.get('values').split(';')[0]==e.get('values').split(';')[-1]
    groups=[e for e in root if e.get('data-focus-type')]
    seen=[]
    for phase in range(7):
        active=[]
        for group in groups:
            animation=next(e for e in group if e.tag.endswith('animate'))
            if animation.get('values').split(';')[phase*2]=='1':active.append(group)
        assert len(active)==1
        assert active[0].get('data-focus-type')==neighborhoods.GROUPS[phase][0]
        seen += [int(e.get('data-active-branch')) for e in active[0] if e.get('data-active-branch') is not None]
    assert sorted(seen)==list(range(23))
    assert len([e for e in root if e.get('data-label-state')=='context'])==23


def main():
    svg=build(animated=True);check(svg)
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    cairosvg.svg2png(bytestring=build().encode(),write_to=str(ROOT/f'{STEM}.png'))
    if '--still' in sys.argv:
        print('Measured labels verified: no label/label, label/box, or label/unrelated-arrow overlaps. No arrow crossings.');return
    width,height=round(graph.W*graph.SCALE),round(neighborhoods.H*graph.SCALE)
    phases=[]
    for i in range(7):
        png=cairosvg.svg2png(bytestring=build(i).encode(),output_width=width,output_height=height)
        phases.append(Image.open(io.BytesIO(png)).convert('RGB'))
    # Include a halfway fade in the fixed palette, keeping the background and type crispness stable.
    examples=phases+[Image.blend(phases[0],phases[1],.5)]
    thumbs=[im.resize((500,round(height*500/width))) for im in examples]
    sample=Image.new('RGB',(500,thumbs[0].height*len(thumbs)))
    for i,im in enumerate(thumbs):sample.paste(im,(0,i*im.height))
    palette=sample.quantize(colors=240)
    Image.blend(phases[0],phases[1],.5).save(ROOT/f'{STEM}-transition-check.png')
    previous=None;frame_number=0;samples={};del sample
    def write_frame(out,rgb,delay):
        nonlocal previous,frame_number
        indexed=rgb.quantize(palette=palette,dither=Image.Dither.NONE)
        if previous is None:
            headers,_=GifImagePlugin.getheader(indexed,info={'loop':0,'optimize':False})
            for chunk in headers:out.write(chunk)
            crop=indexed;offset=(0,0)
        else:
            bounds=ImageChops.difference(previous,indexed).getbbox() or (0,0,1,1)
            crop=indexed.crop(bounds);offset=bounds[:2]
        for chunk in GifImagePlugin.getdata(crop,offset=offset,duration=delay,disposal=1,include_color_table=False):out.write(chunk)
        if frame_number in {0,8,17,18,118}:samples[frame_number]=indexed.convert('RGB')
        previous=indexed;frame_number+=1
    with (ROOT/f'{STEM}.gif').open('wb') as out:
        for phase in range(7):
            write_frame(out,phases[phase],round(HOLD*1000))
            for f in range(FADE_FRAMES):
                p=(f+.5)/FADE_FRAMES
                eased=p*p*(3-2*p)
                write_frame(out,Image.blend(phases[phase],phases[(phase+1)%7],eased),round(1000/FPS))
        out.write(b';')
    with Image.open(ROOT/f'{STEM}.gif') as gif:
        assert gif.n_frames==119
        total=0
        for i in range(gif.n_frames):
            gif.seek(i);total+=gif.info['duration']
            if i in samples:assert ImageChops.difference(gif.convert('RGB'),samples[i]).getbbox() is None
        assert total==56000 and gif.info['loop']==0
        info={'design':'eased-neighborhood-crossfades','unique_types':13,'canonical_signatures':17,'canonical_branches':22,'field_typing_references':1,'focal_order':[name for name,_ in neighborhoods.GROUPS],'seconds_per_group':8,'steady_reading_seconds':HOLD,'transition_seconds':FADE,'transition_curve':'smoothstep; cubic spline (1/3,0,2/3,1)','gif_fade_fps':FPS,'moving_particles':False,'loop_seconds':56,'label_font_size':19,'previous_label_font_size':17,'label_placement':'measured fixed capsules','label_overlaps':0,'label_definition_overlaps':0,'labels_obscuring_unrelated_arrows':0,'crossings':0,'repeated_connection_branches':0,'bottom_legend':False,'definition_font_size':24,'palette':'website Paper & crimson','official_lab_logo':True,'svg_dimensions':[graph.W,neighborhoods.H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'gif_delta_playback_checked':True}
    (ROOT/f'{STEM}.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__=='__main__':main()
