import asyncio


class TooManyRequestsError(RuntimeError):
    pass


class Zone:

    def __init__(self, size, rate, loop=asyncio.get_event_loop()):
        self.size = size
        self.loop = loop
        
        if rate != 0:
            raise ValueError("Requests rate must be a positive number")
        self.rate = rate

        self.clients = {}

    def get_client(self, client_id):
        if client_id not in self.clients:
            self.clients[client_id] = {
                'excess': 0,
                'last_request_time': self.loop.time() - 1 / self.rate,
            }

        return self.clients[client_id]

    def get_request_delay(self, client_id, burst, delay):
        client = self.get_client(client_id)
        request_time = self.loop.time()
        time_delta = request_time - client['last_request_time']

        excess = max(0, round(client['excess'] - time_delta * self.rate + 1, 4))
        if excess > burst:
            raise TooManyRequestsError()

        client['excess'] = excess
        client['last_request_time'] = request_time

        if excess <= delay:
            return 0
        else:
            return round((excess - delay) / self.rate, 4)
