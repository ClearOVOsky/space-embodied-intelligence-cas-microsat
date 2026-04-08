# Space Embodied Intelligence Repository

This repository curates public materials related to "space embodied intelligence" around the Innovation Academy for Microsatellites of the Chinese Academy of Sciences.

Because the public web rarely uses the exact phrase "space embodied intelligence" for this institute, this repository uses a practical scope:

- satellite federated learning
- on-orbit autonomous planning and scheduling
- satellite edge computing and task offloading
- autonomous timing and navigation
- swarm intelligence for lunar formation systems

The repository is organized into two top-level directories:

- `paper/`: PDFs, conference abstracts, and metadata notes for relevant papers
- `code/`: lightweight local reproductions and concept demos inspired by those papers

## Quick Start

Run the two local demos:

```powershell
python .\code\satellite_fl_client_selection\client_selection_demo.py --json-out .\run_logs\client_selection_demo.json
python .\code\multi_satellite_mission_planning\tlbo_demo.py --json-out .\run_logs\tlbo_demo.json
```

## Paper Collection

Available local files:

- `paper/long_term_autonomous_timekeeping_sparse_sampling_lstm_2024.pdf`
- `paper/towards_client_selection_in_satellite_federated_learning_iac2024_abstract.pdf`
- `paper/graphfed_swarms_lunar_formation_iac2025_abstract.pdf`

Metadata notes for additional related papers:

- `paper/metadata/towards_client_selection_in_satellite_federated_learning_2024.md`
- `paper/metadata/on_orbit_task_offloading_satellite_edge_computing_2023.md`
- `paper/metadata/efficient_fair_ppo_scheduling_satech01_2024.md`
- `paper/metadata/adaptive_teaching_learning_multi_satellite_mission_planning_2026.md`

## Notes

- Some publisher endpoints blocked scripted PDF download, so those entries are preserved as metadata notes with official links.
- The code in `code/` is not claimed to be the official source release of the papers. It is a local, runnable reproduction or concept demo aligned with the paper topic and algorithmic idea.

