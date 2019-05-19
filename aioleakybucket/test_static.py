import static

zones = {
    'login': {
        'size': 1000,
        'rate': 1,
    }
}

resources = {
    '/login' : {
        'zone': 'login',
        'burst': 2,
        'delay': 0,
    }
}



def try_requests(limiter, requests):
    for i, request in enumerate(requests, 1):
        (timestamp, requester_id, requested_object) = request
        print(f"Request {i} from {requester_id} for {requested_object}", 
            f"recieved at {timestamp} s")

        try:
            delay = limiter.get_request_delay(timestamp, requester_id,
                                              requested_object)
            print(f"Request {i} processed at {timestamp + delay} s",
                  f"(delay {delay} s)")
        except TooManyRequestsError:
            pass
            print(f"Request {i} is denied.")
        print()


def test_all():
    limiter = static.RequestLimiter(zones, resources)
    request_times = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
    try_requests(
        limiter, [(time, 0, '/login') for time in request_times]
    )