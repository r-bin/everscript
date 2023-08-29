from injector import Injector, inject
_injector = Injector()

import copy
import ujson


class ObjectUtils():
    def deepcopy(self, object:any) -> any:
        if True:
            return copy.deepcopy(object)
        if False:
            return ujson.loads(ujson.dumps(object))
        
object_utils = _injector.get(ObjectUtils)