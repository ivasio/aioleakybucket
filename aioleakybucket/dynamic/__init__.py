import asyncio
from .zone import TooManyRequestsError, Zone


class RequestLimiter:

    def __init__(self, zones):
        self.zones = {zone_name: Zone(**zones[zone_name]) for zone_name
                      in zones}
        self.resources = {}

    def get_request_delay(self, requester_id, resource):
        zone = self.zones[resource['zone']]
        return zone.get_request_delay(requester_id, resource['burst'],
                                      resource['delay'])

    def get_resource(self, name, burst, delay)
        if name not in self.resources:
            self.resources[name] = {
                'burst': burst,
                'delay': delay,
            }
        return self.resources[name]


limiter = None

def setup(zones):
    if limiter is None:
        limiter = RequestLimiter(zones)


def get_requester_id(requester_id_getter, args, kwargs):
    if type(requester_id_getter) == 'str':
        try:
            requester_id = kwargs[requester_id_getter]
            hash(requester_id)
        except KeyError:
            raise KeyError(f"Decorated coroutine must take "
                           f"{requester_id_getter} as a keyword "
                           "argument")
        except TypeError:
            raise TypeError(f"Value passed in {requester_id_getter} "
                           "must be hashable")
    else:
        try:
            requester_id = requester_id_getter(*args, **kwargs)
        except TypeError:
            raise TypeError("1st argument of limit_calls must be "
                            "either str or callable, got "
                            f"{type(requester_id_getter)}")
        try:
            hash(requester_id)
        except TypeError:
            raise TypeError(f"Result of {requester_id_getter} must "
                           "be hashable")
    return requester_id


def limit_calls(requester_id_getter, zone, burst=0, delay=float('inf')):
    def decorator(function):
        async def wrapper(*args, **kwargs):
            requester_id = get_requester_id(requester_id_getter, args, kwargs)
            resource = limits.get_resource(function.__name__, burst, delay)
            delay = limiter.get_request_delay(requester_id, resource)
            if delay > 0:
                asyncio.sleep(delay)
            return function(*args, **kwargs)
        return wrapper
    return decorator
