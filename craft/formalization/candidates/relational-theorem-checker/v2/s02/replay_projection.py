"""Fixed successor projection catalog: exact independent proposition replay."""
from pathlib import Path
import sys,os,subprocess,json,time
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'execution'))
import support as s
HERE=Path(__file__).resolve().parent
CATALOG=[('RequiredProjection','projection_exact'),('RequiredKinds','kind_projection_exact'),('RequiredUnary','existential_view_exact'),('RequiredSupport','support_exact'),('RequiredKindEncoding','kind_encoding_injective')]
def replay(build):
 logs=s.compile_modules(build,[('ProjectionCatalog',HERE/'ProjectionCatalog.lean'),('ProjectionVerifier',HERE/'ProjectionVerifier.lean')]);audits=[];lean=s.lean_path()
 for required,proof in CATALOG:
  submitted=Path(build)/'Submitted.lean';submitted.write_text('import ProjectionProofs\nimport ProjectionCatalog\n\nnamespace SuccessorSubmission\ntheorem '+proof+' : Successor.Projection.Catalog.'+required+' := Successor.Projection.'+proof+'\nend SuccessorSubmission\n')
  compile_log=s.compile_modules(build,[('Submitted',submitted)])
  r=subprocess.run([str(lean),'--run',str(Path(build)/'ProjectionVerifier.lean'),'ProjectionCatalog','Successor.Projection.Catalog.'+required,'definition-value','SuccessorSubmission.'+proof],cwd=build,env={**os.environ,'LEAN_PATH':str(build),'PATH':str(lean.parent)+os.pathsep+os.environ.get('PATH','')},text=True,capture_output=True,timeout=60)
  s.require(r.returncode==0,'Projection fresh replay failed '+proof+'\n'+r.stdout+r.stderr)
  audit=json.loads(r.stdout);s.require(audit['accepted'] and audit['fresh_kernel_replay'],'missing fresh replay')
  audits.append({'required':required,'proof':proof,'audit':audit,'submission_source_sha256':s.digest(submitted),'stderr':r.stderr})
 return {'result':'pass','method':'Fixed independently defined proposition catalog, exact trusted definition comparisons, transitive allowed axiom audit and fresh same-kernel replay','catalog':CATALOG,'verifier':s.binding(HERE/'ProjectionVerifier.lean'),'modules':logs,'audits':audits,'authority_effect':'none'}
if __name__=='__main__':
 result=replay(HERE/'build');s.write(HERE/'fresh-replay-audit.json',result);print('Five exact projection targets freshly replayed.')
