import random


def try_requests(limiter, requests):
    granted = 0
    denied = 0
    for i, request in enumerate(requests, 1):
        result = limiter.get_request_delay(request)
        #print(request, " => ", result)
        if result[2]:
            granted += 1
        else:
            denied += 1
    #print(granted / (granted + denied))
    return (denied, granted / (granted + denied))


def generate_times(first_second, last_second, rate):
    result = []
    for i in range(first_second, last_second):
        result.extend(sorted([i+random.random() for _ in range(rate)]))
    return result


def generate_times_from_sample(sample):
    result = []
    for i, rate in enumerate(sample):
        result.extend(sorted([i+random.random() for _ in range(rate)]))
    return result


def generate_times_from_distribution(distribution, length):
    return generate_times_from_sample(random.choices(*distribution, k=length))


def combine_lists(*args):
    result = []
    for lst in args:
        result.extend(lst)
    return result
