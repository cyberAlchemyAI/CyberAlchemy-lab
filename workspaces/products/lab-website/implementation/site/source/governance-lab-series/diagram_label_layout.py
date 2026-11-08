"""Place explanatory SVG captions beside paths, with room for their text.

Both article figures and interactive maps use this conservative layout. Browser
inspection provides the final check against actual font metrics.
"""
import re
import textwrap
import xml.etree.ElementTree as ET


def points(path):
    values=[float(v) for v in re.findall(r'-?\d+(?:\.\d+)?',path)]
    return list(zip(values[::2],values[1::2]))


def overlaps(a,b,padding=5):
    x,y,w,h=a;u,v,s,t=b
    return x-padding<u+s and x+w+padding>u and y-padding<v+t and y+h+padding>v


def crosses(rect,a,b,padding=5):
    x,y,w,h=rect;x-=padding;y-=padding;w+=padding*2;h+=padding*2
    if a[0]==b[0]:
        return x<a[0]<x+w and min(a[1],b[1])<y+h and max(a[1],b[1])>y
    if a[1]==b[1]:
        return y<a[1]<y+h and min(a[0],b[0])<x+w and max(a[0],b[0])>x
    return False


def arrange_labels(body,width,height,font_size,monospaced=False):
    root=ET.fromstring('<g>'+body+'</g>')
    parents={child:parent for parent in root.iter() for child in parent}
    nodes=[];segments=[];labels=[]
    for el in root.iter():
        cls=el.get('class','').split()
        parent=parents.get(el)
        if el.tag=='rect' and ('node' in cls or (parent is not None and 'smap-node' in parent.get('class','').split())):
            nodes.append(tuple(float(el.get(k,0)) for k in ['x','y','width','height']))
        if el.tag=='path' and ('connector' in cls or 'smap-edge-path' in cls):
            route=points(el.get('d',''))
            segments.extend(zip(route,route[1:]))
        if el.tag=='text' and (el.get('data-connection-label')=='true' or 'smap-edge-label' in cls):
            path=next((p for p in parent if p.tag=='path'),None)
            if path is not None:
                labels.append((el,points(path.get('d',''))))
    occupied=[]
    for label,route in labels:
        original=label.get('data-label-text') or ''.join(label.itertext()).strip()
        # Short lines fit the corridors beside vertical arrows and stay readable.
        lines=textwrap.wrap(original,width=25 if monospaced else 29,break_long_words=False,break_on_hyphens=False)
        line_height=font_size*1.35
        w=max(map(len,lines))*font_size*(.62 if monospaced else .59)
        h=len(lines)*line_height
        candidates=[]
        # Prefer the longest segments; captions sit beside vertical paths and
        # above/below horizontal paths, never centered across a vertical arrow.
        runs=sorted(zip(route,route[1:]),key=lambda s:abs(s[0][0]-s[1][0])+abs(s[0][1]-s[1][1]),reverse=True)
        for run_index,(a,b) in enumerate(runs):
            for fraction in [.5,.35,.65,.2,.8]:
                cx=a[0]+(b[0]-a[0])*fraction;cy=a[1]+(b[1]-a[1])*fraction
                for offset in [16,30,44]:
                    if a[0]==b[0]:
                        variants=[(cx+offset,cy-h/2,w,h),(cx-offset-w,cy-h/2,w,h)]
                    elif a[1]==b[1]:
                        variants=[(cx-w/2,cy-offset-h,w,h),(cx-w/2,cy+offset,w,h)]
                    else:
                        continue
                    for side,rect in enumerate(variants):
                        x,y,_,_=rect
                        clipped=x<8 or y<8 or x+w>width-8 or y+h>height-8
                        hits=sum(overlaps(rect,n) for n in nodes)+sum(overlaps(rect,n) for n in occupied)
                        crossings=sum(crosses(rect,p,q) for p,q in segments)
                        score=(100000 if clipped else 0)+hits*10000+crossings*1000+run_index*20+abs(fraction-.5)*10+offset+side
                        candidates.append((score,rect))
        _,rect=min(candidates,key=lambda c:c[0])
        occupied.append(rect)
        label.clear()
        label.set('class','smap-edge-label' if monospaced else 'edge-label')
        label.set('data-connection-label','true')
        label.set('data-label-text',original)
        label.set('x',str(round(rect[0],2)))
        label.set('y',str(round(rect[1]+font_size,2)))
        label.set('text-anchor','start')
        for i,line in enumerate(lines):
            span=ET.SubElement(label,'tspan',x=label.get('x'),dy='0' if i==0 else str(round(line_height,2)))
            span.text=line+(' ' if i<len(lines)-1 else '')
    return ''.join(ET.tostring(child,encoding='unicode') for child in root)
