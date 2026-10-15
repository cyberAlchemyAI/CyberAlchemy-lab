"""Exact selected original producer origins; revisions require a new candidate."""
from pathlib import Path
from .contracts import need,sha
ORIGINS = {'repository-publisher': ('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/candidates/repeatable-operation/lab_runtime/publisher.py', '255e4e11b9adf7251ebb1a7b7d9a439c185d3503044dadd10b3172b582dbd9b5'), 'repository-promotion': ('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/candidates/repeatable-operation/lab_runtime/promotion.py', '725c0e0cad4a73200c9f06ca042bb0055245ecbc464794b4b1ce36c7895b4f05'), 'owner-ingress': ('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/owner-response-ingress-v1-completion-0001/owner_ingress.py', '7f2623791fdf985c32be0e0a91cc04e65d14601c81244e2c084329fc92076fe4'), 'native-factory': ('/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-lifecycle-recovery-adoption-0003/selected_store.py', 'e6acda4c976ceae4c8047bc30454d910cd58fd8983b353c4b61947f0f6cfc6a8'), 'ontology-projection': ('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/api-integration-v17/ontology_projection.py', 'e9f52281e2f4cebb82cc95ad91ea0bad4d2f46ed88ba0c175d088b51cfb984af')}

def require_original(software,module,role):
    path,pin=ORIGINS[role]
    need(Path(module.__file__)==Path(path),'actual original producer origin differs: '+role)
    captured=[row for row in software.expected if row[0]is module and row[1]=={'path':path,'sha256':pin}]
    need(len(captured)==1 and sha(captured[0][2])==pin,'independently captured actual original producer absent: '+role)
    return module
