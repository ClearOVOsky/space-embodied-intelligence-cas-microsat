import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Satellite:
    satellite_id: str
    capacity: int
    agility: float


@dataclass
class Task:
    task_id: str
    duration: int
    value: int


def build_problem(seed: int) -> tuple[list[Satellite], list[Task], dict[str, dict[str, float]]]:
    rng = random.Random(seed)
    satellites = [
        Satellite("sat-a", capacity=22, agility=0.92),
        Satellite("sat-b", capacity=19, agility=0.85),
        Satellite("sat-c", capacity=18, agility=0.78),
        Satellite("sat-d", capacity=16, agility=0.73),
    ]
    tasks = [
        Task(task_id=f"task-{index + 1:02d}", duration=rng.randint(2, 6), value=rng.randint(8, 20))
        for index in range(14)
    ]
    compatibility: dict[str, dict[str, float]] = {}
    for task in tasks:
        compatibility[task.task_id] = {}
        for satellite in satellites:
            compatibility[task.task_id][satellite.satellite_id] = round(
                max(0.20, min(1.00, rng.uniform(0.35, 0.98) * satellite.agility)),
                3,
            )
    return satellites, tasks, compatibility


def random_solution(rng: random.Random, satellites: list[Satellite], tasks: list[Task]) -> dict[str, str | None]:
    choices = [sat.satellite_id for sat in satellites] + [None, None]
    return {task.task_id: rng.choice(choices) for task in tasks}


def repair_solution(
    solution: dict[str, str | None],
    satellites: list[Satellite],
    tasks: list[Task],
    compatibility: dict[str, dict[str, float]],
) -> dict[str, str | None]:
    capacities = {sat.satellite_id: sat.capacity for sat in satellites}
    task_map = {task.task_id: task for task in tasks}
    repaired = dict(solution)
    grouped: dict[str, list[str]] = {sat.satellite_id: [] for sat in satellites}

    for task_id, sat_id in repaired.items():
        if sat_id is not None:
            grouped[sat_id].append(task_id)

    for sat in satellites:
        while sum(task_map[task_id].duration for task_id in grouped[sat.satellite_id]) > capacities[sat.satellite_id]:
            worst_task = min(
                grouped[sat.satellite_id],
                key=lambda task_id: task_map[task_id].value * compatibility[task_id][sat.satellite_id],
            )
            grouped[sat.satellite_id].remove(worst_task)
            repaired[worst_task] = None

    return repaired


def evaluate(
    solution: dict[str, str | None],
    satellites: list[Satellite],
    tasks: list[Task],
    compatibility: dict[str, dict[str, float]],
) -> float:
    task_map = {task.task_id: task for task in tasks}
    loads = {sat.satellite_id: 0 for sat in satellites}
    reward = 0.0
    assigned_count = 0

    for task_id, sat_id in solution.items():
        if sat_id is None:
            continue
        task = task_map[task_id]
        loads[sat_id] += task.duration
        reward += task.value * compatibility[task_id][sat_id]
        assigned_count += 1

    overload_penalty = 0.0
    for sat in satellites:
        overload_penalty += max(0, loads[sat.satellite_id] - sat.capacity) * 12.0

    load_values = list(loads.values())
    imbalance_penalty = (max(load_values) - min(load_values)) * 1.2
    return round(reward + assigned_count * 0.8 - overload_penalty - imbalance_penalty, 4)


def teacher_phase(
    rng: random.Random,
    learner: dict[str, str | None],
    teacher: dict[str, str | None],
    adapt_rate: float,
) -> dict[str, str | None]:
    updated = dict(learner)
    for task_id in updated:
        if rng.random() < adapt_rate:
            updated[task_id] = teacher[task_id]
    return updated


def learner_phase(
    rng: random.Random,
    learner: dict[str, str | None],
    peer: dict[str, str | None],
    mutate_rate: float,
) -> dict[str, str | None]:
    updated = dict(learner)
    for task_id in updated:
        if rng.random() < mutate_rate:
            updated[task_id] = peer[task_id]
    return updated


def run_demo(iterations: int, population_size: int, seed: int) -> dict:
    satellites, tasks, compatibility = build_problem(seed)
    rng = random.Random(seed)

    population = [
        repair_solution(random_solution(rng, satellites, tasks), satellites, tasks, compatibility)
        for _ in range(population_size)
    ]

    history = []

    for iteration in range(1, iterations + 1):
        scored = [
            (evaluate(candidate, satellites, tasks, compatibility), candidate)
            for candidate in population
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        teacher_score, teacher = scored[0]

        adapt_rate = 0.55 + 0.35 * (iteration / iterations)
        mutate_rate = 0.30 - 0.18 * (iteration / iterations)

        next_population = [teacher]
        for index in range(1, population_size):
            learner = scored[index][1]
            peer = scored[rng.randrange(population_size)][1]
            candidate = teacher_phase(rng, learner, teacher, adapt_rate)
            candidate = learner_phase(rng, candidate, peer, mutate_rate)
            candidate = repair_solution(candidate, satellites, tasks, compatibility)
            next_population.append(candidate)

        population = next_population
        history.append(
            {
                "iteration": iteration,
                "best_score": teacher_score,
                "adapt_rate": round(adapt_rate, 3),
                "mutate_rate": round(mutate_rate, 3),
            }
        )

    final_scored = [
        (evaluate(candidate, satellites, tasks, compatibility), candidate)
        for candidate in population
    ]
    final_scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_solution = final_scored[0]
    assignments = [
        {"task_id": task.task_id, "assigned_to": best_solution[task.task_id], "duration": task.duration, "value": task.value}
        for task in tasks
    ]

    return {
        "config": {"iterations": iterations, "population_size": population_size, "seed": seed},
        "satellites": [asdict(sat) for sat in satellites],
        "tasks": [asdict(task) for task in tasks],
        "compatibility": compatibility,
        "history": history,
        "best_score": best_score,
        "best_assignments": assignments,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Teaching-learning-based optimization demo for multi-satellite planning")
    parser.add_argument("--iterations", type=int, default=60)
    parser.add_argument("--population-size", type=int, default=20)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    result = run_demo(args.iterations, args.population_size, args.seed)

    print("Multi-satellite mission planning TLBO demo")
    print(
        f"Iterations: {args.iterations}, population: {args.population_size}, best score: {result['best_score']:.4f}"
    )
    for assignment in result["best_assignments"]:
        if assignment["assigned_to"] is not None:
            print(
                f"{assignment['task_id']} -> {assignment['assigned_to']} "
                f"(duration={assignment['duration']}, value={assignment['value']})"
            )

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"JSON log written to: {args.json_out}")


if __name__ == "__main__":
    main()
