import random
from aioleakybucket import static
from . import utils


def test_constant_overflow():
    zones = {'login': {'size': 1000, 'rate': 5}}
    resources = {'/login': {'zone': 'login', 'burst': 12, 'delay': 8}}
    limiter = static.RequestLimiter(zones, resources)
    request_times = utils.generate_times(0, 1000, 8)
    (fails, success_rate) = utils.try_requests(
        limiter, [(time, 0, '/login') for time in request_times])
    assert success_rate >= 0.6 and success_rate <= 0.63


def test_handcrafted_website_simulation():
    zones = {'login': {'size': 1000, 'rate': 5}}
    resources = {'/login': {'zone': 'login', 'burst': 12, 'delay': 8}}
    limiter = static.RequestLimiter(zones, resources)

    request_intervals = [
        (0, 3, 5),
        (3, 5, 8),
        (5, 6, 7),
        (6, 10, 4),
        (10, 12, 3),
        (12, 13, 7),
        (13, 15, 10),
        (15, 18, 4)
    ]
    request_times = utils.combine_lists(*[utils.generate_times(*interval) for
                                          interval in request_intervals])
    (fails, success_rate) = utils.try_requests(
        limiter, [(time, 0, '/login') for time in request_times])
    assert success_rate >= 0.95


def test_generated_website_simulation():
    zones = {'main': {'size': 1000, 'rate': 5}}
    resources = {
        '/static': {'zone': 'main', 'burst': 100, 'delay': 90},
        '/login': {'zone': 'main', 'burst': 20, 'delay': 15},
    }
    limiter = static.RequestLimiter(zones, resources)

    user_ids = list(range(6))
    requests = []

    static_sample = random.choices(
        [0,  1,  2,  3,  39, 40, 83, 94],
        [60, 16, 10, 10, 1,  1,  1,  1],
        k=6000
    )
    login_sample = random.choices(
        [0,  1,  2,  10,  17],
        [60, 20, 12, 5,  3],
        k=6000
    )

    for user_id in user_ids:
        requests.extend([(time, user_id, '/static') for time in
                         utils.generate_times_from_sample(static_sample)])
        requests.extend([(time, user_id, '/login') for time in
                         utils.generate_times_from_sample(login_sample)])

    requests.sort(key=lambda request: request[0])
    (fails, success_rate) = utils.try_requests(limiter, requests)
    assert success_rate >= 0.95