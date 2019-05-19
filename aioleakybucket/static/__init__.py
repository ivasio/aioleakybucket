class TooManyRequestsError(RuntimeError):
    pass


class Zone:

    def __init__(self, size, rate):
        self.size = size
        self.rate = rate

        self.clients = {}

    def get_client(self, client_id):
        if client_id not in self.clients:
            self.clients[client_id] = {
                'excess': 0,
                'last_request_time': -1,
            }

        return self.clients[client_id]

    def get_request_delay(self, request_time, client_id, burst, delay):
        client = self.get_client(client_id)
        time_delta = request_time - client['last_request_time']
        assert time_delta >= 0

        excess = max(0, round(client['excess'] - time_delta * self.rate + 1, 4))
        if excess > burst:
            raise TooManyRequestsError()

        client['excess'] = excess
        client['last_request_time'] = request_time

        if excess <= delay:
            return 0
        else:
            return round((excess - delay) / self.rate, 4)


class RequestLimiter:

    def __init__(self, zones, resources):
        self.zones = {zone_name: Zone(**zones[zone_name]) for zone_name
                      in zones}

        for resource in resources:
            if 'burst' not in resources[resource]:
                resources[resource]['burst'] = 0
            if 'delay' not in resources[resource]:
                resources[resource]['delay'] = float('inf')  # check nginx default
        self.resources = resources

    def get_request_delay(self, timestamp, requester_id, requested_object):
        resource = self.resources[requested_object]
        zone = self.zones[resource['zone']]
        return zone.get_request_delay(timestamp, requester_id,
                                      resource['burst'], resource['delay'])
