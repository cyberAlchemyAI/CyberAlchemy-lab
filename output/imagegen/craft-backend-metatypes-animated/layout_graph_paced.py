"""A quicker five-second neighborhood cadence and the requested exact title."""
from pathlib import Path
import io
import json
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageFont, ImageChops, GifImagePlugin
import layout_atlas as art
import layout_graph_clear as graph
import layout_graph_brand as brand
import layout_graph_neighborhoods as neighborhoods
import layout_graph_smooth as previous

ROOT=Path(__file__).resolve().parent
STEM='craft-backend-metatypes-v11'
TITLE='Craft: Taxanomy & Ontology for software'
SECONDS=5
FADE=previous.FADE
HOLD=SECONDS-FADE
DURATION=SECONDS*len(neighborhoods.GROUPS)


def build(index=0,animated=False):
    root=ET.fromstring(previous.build(index=index,animated=animated))
    for element in root.iter():element.tag=element.tag.split('}')[-1]
    root.set('xmlns',neighborhoods.sequential.SVG_NS)
    root.find('title').text=TITLE
    root.find('desc').text='Five seconds per focal meta-type: a 4.2-second steady reading hold and a 0.8-second eased fade. The complete loop is 35 seconds. The exact requested title, official Lab logo, Paper & crimson palette, measured labels, faded unrelated content and non-repeating connection groups are retained.'
    times=[0.0]
    for phase in range(7):times += [(phase*SECONDS+HOLD)/DURATION,((phase+1)*SECONDS)/DURATION]
    for element in root.iter():
        if element.tag=='animate':
            element.set('dur',f'{DURATION}s')
            element.set('keyTimes',';'.join(f'{t:.10f}' for t in times))
    for child in list(root):
        if child.tag=='text' and child.get('x')=='560' and child.get('y') in {'61','103','138'}:root.remove(child)
    root.append(ET.fromstring(art.label(560,79,TITLE,34,700,brand.INK)))
    root.append(ET.fromstring(art.label(560,122,'13 meta-types · 17 relationship signatures',20,400,brand.MUTED)))
    return ET.tostring(root,encoding='unicode')


def check(svg):
    previous.validate_layout()
    root=ET.fromstring(svg)
    assert root.find('{*}title').text==TITLE
    titles=[e for e in root if e.tag.endswith('text') and e.text==TITLE]
    assert len(titles)==1
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',34)
    assert 560+font.getlength(TITLE)<1500,'Title would overlap the category key'
    assert len([e for e in root.iter() if e.get('data-meta-type')])==13
    assert len({e.get('data-signature') for e in root.iter() if e.get('data-signature')})==17
    for animation in [e for e in root.iter() if e.tag.endswith('animate')]:
        assert animation.get('dur')=='35s' and animation.get('calcMode')=='spline'
        assert len(animation.get('keyTimes').split(';'))==len(animation.get('values').split(';'))==15
        assert len(animation.get('keySplines').split(';'))==14
    assert not any(e.tag.endswith('animateMotion') for e in root.iter())


def main():
    svg=build(animated=True);check(svg)
    (ROOT/f'{STEM}.svg').write_text(svg,encoding='utf-8')
    cairosvg.svg2png(bytestring=build().encode(),write_to=str(ROOT/f'{STEM}.png'))
    width,height=round(graph.W*graph.SCALE),round(neighborhoods.H*graph.SCALE)
    phases=[]
    for phase in range(7):
        png=cairosvg.svg2png(bytestring=build(phase).encode(),output_width=width,output_height=height)
        phases.append(Image.open(io.BytesIO(png)).convert('RGB'))
    thumbs=[im.resize((500,round(height*500/width))) for im in phases+[Image.blend(phases[0],phases[1],.5)]]
    sample=Image.new('RGB',(500,thumbs[0].height*len(thumbs)))
    for i,im in enumerate(thumbs):sample.paste(im,(0,i*im.height))
    palette=sample.quantize(colors=240);del sample
    last=None;frame_number=0;samples={}
    def write(out,rgb,delay):
        nonlocal last,frame_number
        indexed=rgb.quantize(palette=palette,dither=Image.Dither.NONE)
        if last is None:
            header,_=GifImagePlugin.getheader(indexed,info={'loop':0,'optimize':False})
            for chunk in header:out.write(chunk)
            crop=indexed;offset=(0,0)
        else:
            bounds=ImageChops.difference(last,indexed).getbbox() or (0,0,1,1)
            crop=indexed.crop(bounds);offset=bounds[:2]
        for chunk in GifImagePlugin.getdata(crop,offset=offset,duration=delay,disposal=1,include_color_table=False):out.write(chunk)
        if frame_number in {0,8,17,118}:samples[frame_number]=indexed.convert('RGB')
        last=indexed;frame_number+=1
    with (ROOT/f'{STEM}.gif').open('wb') as out:
        for phase in range(7):
            write(out,phases[phase],round(HOLD*1000))
            for f in range(previous.FADE_FRAMES):
                t=(f+.5)/previous.FADE_FRAMES
                write(out,Image.blend(phases[phase],phases[(phase+1)%7],t*t*(3-2*t)),round(1000/previous.FPS))
        out.write(b';')
    with Image.open(ROOT/f'{STEM}.gif') as gif:
        assert gif.n_frames==119 and gif.info['loop']==0
        duration=0
        for i in range(gif.n_frames):
            gif.seek(i);duration+=gif.info['duration']
            if i in samples:assert ImageChops.difference(gif.convert('RGB'),samples[i]).getbbox() is None
        assert duration==35000
        info={'title':TITLE,'design':'quicker-eased-neighborhood-crossfades','seconds_per_group':SECONDS,'previous_seconds_per_group':8,'steady_reading_seconds':HOLD,'transition_seconds':FADE,'loop_seconds':DURATION,'gif_fade_fps':previous.FPS,'moving_particles':False,'unique_types':13,'canonical_signatures':17,'crossings':0,'label_overlaps':0,'label_font_size':19,'definition_font_size':24,'official_lab_logo':True,'palette':'website Paper & crimson','bottom_legend':False,'svg_dimensions':[graph.W,neighborhoods.H],'gif_dimensions':list(gif.size),'frames':gif.n_frames,'gif_delta_playback_checked':True}
    (ROOT/f'{STEM}.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__=='__main__':main()
