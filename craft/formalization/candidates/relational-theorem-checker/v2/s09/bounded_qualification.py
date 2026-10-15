"""Same concrete declarations/proofs, split compilation stages under the existing 60s ceiling."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'s06'));import runtime as r
s=r.s
_original_qualify=r.qualify

def split_source(source,stem):
 prefix,rest=source.split('def before : Theory := ',1);rest='def before : Theory := '+rest
 data,rest=rest.split('theorem before_valid : ',1);rest='theorem before_valid : '+rest
 typed,rest=rest.split('theorem complete_closure : ',1);rest='theorem complete_closure : '+rest
 closure,expansion=rest.split('def added := ',1);expansion='def added := '+expansion
 names=[stem+'_Data',stem+'_Typed',stem+'_Closure',stem+'_Expansion']
 body=[data,typed,closure,expansion]
 pieces=[]
 for index,(name,value) in enumerate(zip(names,body)):
  header=prefix if index==0 else prefix.replace('import RuntimeProofs','import '+names[index-1])
  # The final segment already contains the original namespace end and axiom prints.
  if index<3:value+='end Successor.Runtime.Actual\n'
  pieces.append((name,header+value))
 return pieces

def qualify(*args,**kwargs):
 compiler=s.compile_modules;combined=[]
 def staged(build,modules,timeout=60):
  if len(modules)==1 and modules[0][0].startswith('ActualRecursive_'):
   stem,path=modules[0];path=Path(path);source=path.read_text();parts=split_source(source,stem);projected=[]
   for name,text in parts:
    p=Path(build)/(name+'.lean');p.write_text(text);projected.append((name,p))
   logs=compiler(build,projected,timeout);combined.append({'combined_source':s.binding(path),'parts':[{'module':n,'source':s.binding(p)} for n,p in projected],'policy':'Original independent declarations/proofs are partitioned in order; imports reconnect the exact public definitions; no statement or evidence removed.'});return logs
  return compiler(build,modules,timeout)
 s.compile_modules=staged
 try:result=_original_qualify(*args,**kwargs)
 finally:s.compile_modules=compiler
 s.require(len(combined)==1,'missing concrete split witness');result['witness_layout']='split-independent-stages-v2';result['evidence']['layout']=combined[0];result['evidence']['layout']['generator']=s.binding(HERE/'bounded_qualification.py')
 return result

def check_layout(result):
 layout=result['evidence']['layout'];source=s.check(layout['combined_source']).read_text();old=r.witness_source(result['before_normal_form'],result['normal_form'],{'closure':result['closure'],'steps':result['certificates']},{})
 s.require(source==old,'combined concrete values/proofs changed')
 stem=Path(layout['combined_source']['path']).stem;parts=split_source(source,stem)
 s.require([x['module'] for x in layout['parts']]==[n for n,_ in parts],'split module inventory changed')
 for (name,text),part,compiled in zip(parts,layout['parts'],result['evidence']['actual']):
  p=s.check(part['source']);s.require(p.read_text()==text and compiled['module']==name and compiled['source']==part['source'],'concrete split source/type changed');s.check(compiled['olean'])
 s.check(layout['generator']);return True

def install(shadow):
 r.qualify=qualify;before=shadow.runtime_bindings
 def bindings():return before()+[s.binding(HERE/'bounded_qualification.py')]
 shadow.runtime_bindings=bindings
