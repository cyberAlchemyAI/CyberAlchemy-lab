"""Common API entrypoint preserves the frozen reader and separate Action channel."""
from .dependencies import P,require
from .runtime import OPERATIONS
from .service import ActionService

class IntegrationService:
 def __init__(self,base_service,action_service):
  from .dependencies import name
  BaseService=__import__(name+'.service',fromlist=['Service']).Service
  require(type(base_service) is BaseService and type(action_service) is ActionService,'actual frozen and additive public dispatchers required')
  require(base_service.schemas is action_service.schemas,'common exact original API schema selection required')
  self.base=base_service;self.actions=action_service;self.schemas=base_service.schemas
 def call(self,raw):
  try:value=P.frame_parse(raw)
  except Exception:return self.base.call(raw)
  if isinstance(value,dict) and value.get('operation') in OPERATIONS:return self.actions.call(raw)
  return self.base.call(raw)
 def close(self):
  try:self.actions.close()
  finally:self.base.close()
