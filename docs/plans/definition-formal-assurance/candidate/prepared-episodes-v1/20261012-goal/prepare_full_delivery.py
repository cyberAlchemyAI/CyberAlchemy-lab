"""Prepare Goal full seal/audit producers without altering the frozen typed stage."""
from pathlib import Path
import ast,json
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/CAV2-D59';prev=u.with_name('CAV2-D32')
with (u/'replay_delivery.py').open('x') as f:f.write((prev/'replay_delivery.py').read_text())
for name in ['capture_full_delivery.py','capture_fresh_delivery.py']:
 s=(p.parent/'20261012-generic-method'/name).read_text().replace('definitions/CAV2-D32','definitions/CAV2-D59')
 with (p/name).open('x') as f:f.write(s)
print('Goal six-fresh-check and separate seal/audit capture producers prepared;not executed.')
