"""Supervise the unchanged loopback controller and its bounded HTTP gateway."""
import os,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
APP=ROOT/'language/capabilities/alchlang/plans/general-compiler-v1/extensions/host-lifecycle-v1/control_plane.py'
Path('/var/lib/alch/registry').mkdir(mode=0o700,exist_ok=True)
os.chmod('/var/lib/alch/registry',0o700)
children=[]
def stop(*_):
    for child in children:
        if child.poll() is None:child.terminate()
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
try:
    children.append(subprocess.Popen([sys.executable,str(APP),'--root','/var/lib/alch/registry','--config','/run/alch/operator.json','--port','8080']))
    children.append(subprocess.Popen([sys.executable,'/opt/alch/gateway.py']))
    while all(p.poll() is None for p in children):time.sleep(.2)
finally:
    stop()
    for child in children:
        try:child.wait(timeout=60)
        except subprocess.TimeoutExpired:child.kill();child.wait()
