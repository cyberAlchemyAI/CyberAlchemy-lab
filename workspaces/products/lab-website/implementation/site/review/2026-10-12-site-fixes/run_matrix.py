"""Sequential batches per owned browser; engines run independently."""
import argparse
import subprocess
import sys
from pathlib import Path
from run_browser import routes

p=argparse.ArgumentParser();p.add_argument('--engine',default='chromium');p.add_argument('--widths',nargs='+',type=int,default=[1440,1024,390,320]);p.add_argument('--label',default='full-matrix');a=p.parse_args()
runner=Path(__file__).with_name('run_browser.py')
for width in a.widths:
    for start in range(0,len(routes()),6):
        result=subprocess.run([sys.executable,str(runner),'--engine',a.engine,'--width',str(width),'--start',str(start),'--limit','6','--label',a.label])
        if result.returncode:sys.exit(result.returncode)
