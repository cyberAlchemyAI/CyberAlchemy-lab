"""No original protected imports/reads. This required oracle is unavailable."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--temp-root',required=True,type=Path);p.parse_args()
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'NOT_RUN','checks':0,
                  'effect_state':'none','cleanup':'clean'}))
