"""Tabular Q-learning baseline for synthetic traffic traces (delayed scale actions)."""
import random
from collections import defaultdict
from simulator import forecast

ACTIONS = (-1, 0, 1)


def state(load, prior, replicas, capacity):
    utilization = load / (capacity * max(1, replicas))
    trend = (load - prior) / capacity
    return (min(4, int(utilization * 2)), -1 if trend < -.2 else 1 if trend > .2 else 0, replicas)


def run_episode(loads, q, capacity=100, minimum=1, maximum=10, epsilon=0, alpha=.15, gamma=.9, rng=None):
    rng = rng or random.Random(0)
    replicas, prior, cost, dropped = minimum, 0, 0, 0
    for index, load in enumerate(loads):
        s = state(load, prior, replicas, capacity)
        options = [a for a in ACTIONS if minimum <= replicas + a <= maximum]
        action = rng.choice(options) if rng.random() < epsilon else max(options, key=lambda a: (q[s, a], -abs(a)))
        # Current interval uses existing capacity; new replica becomes available next interval.
        loss = max(0, load - replicas * capacity)
        dropped += loss
        cost += replicas
        reward = -replicas - .2 * loss
        next_replicas = replicas + action
        next_load = loads[index + 1] if index + 1 < len(loads) else load
        ns = state(next_load, load, next_replicas, capacity)
        next_actions = [a for a in ACTIONS if minimum <= next_replicas + a <= maximum]
        q[s, action] += alpha * (reward + gamma * max(q[ns, a] for a in next_actions) - q[s, action])
        replicas, prior = next_replicas, load
    return {'replica_ticks': cost, 'dropped_requests': dropped}


def train(train_loads, epochs=300, seed=42):
    if not train_loads or any(v < 0 for v in train_loads):
        raise ValueError('Provide nonnegative training loads')
    q = defaultdict(float)
    rng = random.Random(seed)
    for i in range(epochs):
        run_episode(train_loads, q, epsilon=max(.05, .5 * (1 - i / epochs)), rng=rng)
    return q


def evaluate(loads, q):
    # Freeze Q values for held-out evaluation; never learn from the test trace.
    frozen = defaultdict(float, q)
    return run_episode(loads, frozen, epsilon=0, alpha=0)


if __name__ == '__main__':
    from simulator import read_load
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--csv', required=True)
    args = p.parse_args()
    loads = read_load(args.csv)
    cut = int(len(loads) * .8)
    if cut == 0 or cut == len(loads):
        raise SystemExit('Need at least two traffic intervals')
    q = train(loads[:cut])
    print({'train_intervals': cut, 'test_intervals': len(loads) - cut, 'q_learning': evaluate(loads[cut:], q)})
