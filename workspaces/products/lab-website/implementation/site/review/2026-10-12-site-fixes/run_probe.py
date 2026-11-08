import json
import os
from pathlib import Path
import sys
from run_browser import cli,OUT,BASE,AXE,ROOT
script=Path(sys.argv[1]);name=sys.argv[2] if len(sys.argv)>2 else script.stem
site=Path(os.environ.get('LAB_SITE_FIXES_SITE',str(ROOT/'website/dist'))).resolve()
config={'base':BASE,'output':str(OUT),'run':name,'axe':str(AXE),'fileRoot':site.as_uri()+'/'}
filename=OUT/'measurements'/(name+'.js');filename.write_text(script.read_text().replace('/*CONFIG*/ {}',json.dumps(config)))
session='lab-site-fixes'+('-'+sys.argv[3] if len(sys.argv)>3 and sys.argv[3]!='chromium' else '')
result=cli(session,['run-code','--filename',str(filename)])
(OUT/'measurements'/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':str(OUT/'measurements'/(name+'.json'))}))
