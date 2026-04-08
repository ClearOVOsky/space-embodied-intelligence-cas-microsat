import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class ClientState:
    client_id: str
    contact_minutes: int
    link_quality: float
    energy_margin: float
    staleness: int
    times_selected: int = 0


def generate_clients(rng: random.Random, num_clients: int) -> list[ClientState]:
    clients = []
    for index in range(num_clients):
        clients.append(
            ClientState(
                client_id=f"sat-{index + 1:02d}",
                contact_minutes=rng.randint(6, 24),
                link_quality=round(rng.uniform(0.45, 0.98), 3),
                energy_margin=round(rng.uniform(0.35, 0.95), 3),
                staleness=rng.randint(0, 4),
            )
        )
    return clients


def score_client(client: ClientState, max_selected: int) -> float:
    fairness_penalty = client.times_selected / max(1, max_selected)
    contact_score = client.contact_minutes / 24.0
    staleness_score = min(client.staleness / 4.0, 1.0)
    score = (
        0.32 * contact_score
        + 0.26 * client.link_quality
        + 0.18 * client.energy_margin
        + 0.24 * staleness_score
        - 0.16 * fairness_penalty
    )
    return round(score, 4)


def run_demo(rounds: int, num_clients: int, select_k: int, seed: int) -> dict:
    rng = random.Random(seed)
    clients = generate_clients(rng, num_clients)
    history = []

    for round_index in range(1, rounds + 1):
        max_selected = max(client.times_selected for client in clients) + 1
        scored = []
        for client in clients:
            client.contact_minutes = max(4, min(28, client.contact_minutes + rng.randint(-3, 3)))
            client.link_quality = round(min(0.99, max(0.35, client.link_quality + rng.uniform(-0.06, 0.06))), 3)
            client.energy_margin = round(min(0.99, max(0.20, client.energy_margin + rng.uniform(-0.08, 0.05))), 3)
            client.staleness = min(6, client.staleness + 1)
            scored.append(
                {
                    "client_id": client.client_id,
                    "score": score_client(client, max_selected),
                    "contact_minutes": client.contact_minutes,
                    "link_quality": client.link_quality,
                    "energy_margin": client.energy_margin,
                    "staleness": client.staleness,
                    "times_selected": client.times_selected,
                }
            )

        selected = sorted(scored, key=lambda item: item["score"], reverse=True)[:select_k]
        selected_ids = {item["client_id"] for item in selected}

        for client in clients:
            if client.client_id in selected_ids:
                client.times_selected += 1
                client.staleness = 0

        history.append(
            {
                "round": round_index,
                "selected": selected,
                "mean_score": round(sum(item["score"] for item in selected) / len(selected), 4),
            }
        )

    return {
        "config": {
            "rounds": rounds,
            "num_clients": num_clients,
            "select_k": select_k,
            "seed": seed,
        },
        "final_clients": [asdict(client) for client in clients],
        "history": history,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic satellite federated learning client-selection demo")
    parser.add_argument("--rounds", type=int, default=8)
    parser.add_argument("--num-clients", type=int, default=10)
    parser.add_argument("--select-k", type=int, default=4)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    result = run_demo(args.rounds, args.num_clients, args.select_k, args.seed)

    print("Satellite FL client-selection demo")
    print(f"Rounds: {args.rounds}, clients: {args.num_clients}, selected per round: {args.select_k}")
    for entry in result["history"]:
        selected_ids = ", ".join(item["client_id"] for item in entry["selected"])
        print(f"Round {entry['round']:02d} -> {selected_ids} | mean score={entry['mean_score']:.4f}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"JSON log written to: {args.json_out}")


if __name__ == "__main__":
    main()

