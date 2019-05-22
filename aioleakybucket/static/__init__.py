import time
from math import floor


class TooManyRequestsError(RuntimeError):
    pass


class RequestQueue:

    def __init__(self, rate):
        self._last_cleanup_time = None
        self._queue = []

        assert rate > 0
        self._rate = rate

    def schedule(self, request_time, burst, delay):
        self._remove_old(request_time)
        queue_length = len(self._queue)

        if queue_length >= burst:
            return (False, 0, queue_length)

        if queue_length == 0:
            resulting_time = request_time
        else:
            last_scheduled_time = self._queue[-1]
            resulting_time = max(request_time, last_scheduled_time)
            if queue_length >= delay:
                resulting_time += 1 / self._rate

        self._queue.append(resulting_time)
        return (True, resulting_time - request_time, queue_length + 1)

    def _remove_old(self, incoming_time):
        if len(self._queue) == 0:
            self._last_cleanup_time = incoming_time
        else:
            time_delta = incoming_time - self._last_cleanup_time
            items_to_remove = min(floor(time_delta * self._rate),
                                  len(self._queue))
            if items_to_remove > 0:
                self._queue = self._queue[items_to_remove:]
                self._last_cleanup_time += items_to_remove / self._rate


class Zone:

    def __init__(self, size, rate):
        self.size = size
        self.rate = rate
        self._client_queues = {}

    def get_client_queue(self, client_id):
        if client_id not in self._client_queues:
            self._client_queues[client_id] = RequestQueue(self.rate)
        return self._client_queues[client_id]

    def get_request_delay(self, request_time, client_id, burst, delay):
        client_queue = self.get_client_queue(client_id)
        (access_granted, resulting_delay, excess) = client_queue.schedule(
            request_time, burst, delay)
        return (request_time, client_id, access_granted, resulting_delay,
                excess)


class RequestLimiter:

    def __init__(self, zones, resources):
        self.zones = {zone_name: Zone(**zones[zone_name]) for zone_name
                      in zones}

        for resource in resources:
            if 'burst' not in resources[resource]:
                resources[resource]['burst'] = 0
            if 'delay' not in resources[resource]:
                resources[resource]['delay'] = float('inf')
        self.resources = resources

    def get_request_delay(self, request):
        (timestamp, requester_id, requested_object) = request
        resource = self.resources[requested_object]
        zone = self.zones[resource['zone']]
        return zone.get_request_delay(timestamp, requester_id,
                                      resource['burst'], resource['delay'])
