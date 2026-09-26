# Predictive Autoscaler

A reproducible simulation comparing reactive thresholds with a trend forecast, including scaling delay, capacity, replicas and dropped requests.

```bash
python autoscaler/simulator.py
python autoscaler/simulator.py --csv my_traffic.csv --capacity 100 --delay 2
```

CSV column: `requests` (one interval per row). `replica_ticks` measures capacity usage, **not** cloud cost. `dropped_requests` is a simplified service-level proxy. Compare both together; a low replica count that drops traffic is not a saving. The project does not deploy to Kubernetes or provision AWS; supply recorded traffic, prices and measured latency for a credible comparison. No 80% result is asserted by this implementation.

Experimental tabular reinforcement learning baseline: `python autoscaler/qlearning.py --csv my_traffic.csv`. It trains only on the first 80% of intervals and reports scores on the remaining 20%. Actions become effective the next interval, which is a simplification of real Kubernetes readiness delay. The provided synthetic example is for learning and testing, not evidence of production savings.
