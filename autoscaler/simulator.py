"""Reproducible capacity simulation. One replica serves capacity requests per tick."""
import argparse
import csv
import json
import math
from collections import deque


def forecast(history):
    if not history:
        return 0
    recent = list(history)[-5:]
    trend = (recent[-1] - recent[0]) / max(1, len(recent) - 1)
    return max(0, recent[-1] + 2 * trend)


def desired(load, capacity, minimum, maximum, target=.7):
    return max(minimum, min(maximum, math.ceil(max(0, load) / (capacity * target))))


def simulate(loads, capacity=100, delay=2, minimum=1, maximum=10, policy='predictive'):
    if capacity <= 0 or delay < 0 or minimum < 1 or maximum < minimum:
        raise ValueError('Invalid capacity, delay or replica bounds')
    active = minimum
    pending = []
    history = deque(maxlen=10)
    records = []
    for tick, load in enumerate(loads):
        if load < 0:
            raise ValueError('Load must be nonnegative')
        due = [count for ready, count in pending if ready <= tick]
        pending = [(ready, count) for ready, count in pending if ready > tick]
        if due:
            active = due[-1]
        history.append(load)
        predicted = forecast(history) if policy == 'predictive' else load
        requested = desired(predicted, capacity, minimum, maximum)
        scheduled = pending[-1][1] if pending else active
        if requested != scheduled:
            pending.append((tick + delay + 1, requested))
        served = min(load, active * capacity)
        records.append({'tick': tick, 'load': load, 'replicas': active, 'served': served,
                        'dropped': load - served, 'requested_replicas': requested})
    return {'policy': policy, 'replica_ticks': sum(r['replicas'] for r in records),
            'dropped_requests': sum(r['dropped'] for r in records), 'records': records}


def read_load(path):
    with open(path, newline='', encoding='utf8') as file:
        return [float(row['requests']) for row in csv.DictReader(file)]


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--csv', help='CSV with requests column; omitted for synthetic demonstration')
    p.add_argument('--capacity', type=float, default=100)
    p.add_argument('--delay', type=int, default=2)
    args = p.parse_args()
    loads = read_load(args.csv) if args.csv else [30] * 8 + [50, 80, 120, 180, 250, 290, 200, 90] + [30] * 8
    print(json.dumps({name: simulate(loads, args.capacity, args.delay, policy=name)
                      for name in ('reactive', 'predictive')}, indent=2))
