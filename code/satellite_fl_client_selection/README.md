# Satellite FL Client Selection Demo

This script is a local reproduction demo inspired by satellite federated learning client-selection work.

What it does:

- generates a synthetic satellite network over multiple communication rounds
- scores candidate clients using contact duration, link quality, energy margin, staleness, and fairness pressure
- selects the best subset of clients for each round
- writes a JSON log for later inspection

Run:

```powershell
python .\client_selection_demo.py --json-out ..\..\run_logs\client_selection_demo.json
```

