"""Public original-envelope dispatch composes with frozen-v6 compatible host APIs."""
from .dependencies import P,OPERATIONS
from .host import need
from .service import GovernanceService
class IntegrationService:
 def __init__(self,base_service,governance_service):
  need(hasattr(base_service,'call') and hasattr(base_service,'schemas') and type(governance_service) is GovernanceService and base_service.schemas is governance_service.schemas,'invalid-contract','Actual original-schema-compatible dispatchers required.')
  self.base=base_service;self.governance=governance_service;self.schemas=base_service.schemas
 def call(self,raw):
  try:value=P.frame_parse(raw)
  except Exception:return self.base.call(raw)
  owned=isinstance(value,dict) and (value.get('operation') in OPERATIONS or (value.get('operation')=='operation.inspect' and value.get('message',{}).get('lookup',{}).get('operation') in OPERATIONS))
  return self.governance.call(raw) if owned else self.base.call(raw)
 def close(self):
  try:self.governance.close()
  finally:self.base.close()
