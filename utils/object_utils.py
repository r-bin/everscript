from injector import Injector, inject
_injector = Injector()

import ujson


class ObjectUtils():
    def deepcopy(self, object):
        if False:
            return copy.deepcopy(object)
        else:
            return ujson.loads(ujson.dumps(object))
        
object_utils = _injector.get(ObjectUtils)