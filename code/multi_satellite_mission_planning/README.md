# Multi-Satellite Mission Planning TLBO Demo

This script is a small discrete optimization demo inspired by teaching-learning-based optimization for multi-satellite collaborative mission planning.

What it does:

- creates a synthetic set of earth-observation tasks
- evaluates task-to-satellite assignments under capacity limits and compatibility scores
- uses a teacher phase and a learner phase to improve the assignment population
- writes the best plan to a JSON log

Run:

```powershell
python .\tlbo_demo.py --json-out ..\..\run_logs\tlbo_demo.json
```

