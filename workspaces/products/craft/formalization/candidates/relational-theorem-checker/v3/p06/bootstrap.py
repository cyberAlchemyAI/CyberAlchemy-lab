"""Small gate: all task imports and decoding occur after cgroup attachment."""
import os
import sys
import time
job=sys.argv[1]
while not os.path.isfile(os.path.join(job,'go')):time.sleep(.005)
os.environ['RELATIONAL_SUPERVISOR_JOB']=job
os.execv(sys.argv[2],sys.argv[2:])
