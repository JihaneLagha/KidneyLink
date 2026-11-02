
import csv
import random
from collections import defaultdict
from pathlib import Path

import networkx as nx

from kidneylink.exact_solver import solve_exact
from kidneylink.randomized_solver import solve_randomized


# ---------------------------------------------------------
# Experimental configuration
# ---------------------------------------------------------

NUMBER_OF_INSTANCES = 20
TRIALS_PER_INSTANCE = 5

REPETITION_BUDGETS = [1, 5, 10, 20, 50]

MIN_PAIRS = 6
MAX_PAIRS = 10

MIN_DONORS = 0
MAX_DONORS = 2

EDGE_PROBABILITIES = [0.15, 0.30, 0.50]

MAX_CYCLE_LENGTH = 3
MAX_PATH_LENGTH = 3

BASE_SEED = 3026

OUTPUT_DIR = Path("results")

RAW_FILE = OUTPUT_DIR / "repetition_sensitivity_trials.csv"
SUMMARY_FILE = OUTPUT_DIR / "repetition_sensitivity_summary.csv"


# ---------------------------------------------------------
# Random graph generation
# Same generator and seed as the reliability experiment
# ---------------------------------------------------------

def generate_kidney_graph(
    seed,
    pair_count,
    donor_count,
    edge_probability,
):
    rng = random.Random(seed)

    graph = nx.DiGraph()

    pairs = [
        f"P{i}"
        for i in range(1, pair_count + 1)
    ]

    donors = [
        f"A{i}"
        for i in range(1, donor_count + 1)
    ]

    for pair in pairs:
        graph.add_node(pair, node_type="pair")

    for donor in donors:
        graph.add_node(donor, node_type="altruistic")

    for source in pairs:
        for destination in pairs:

            if source == destination:
                continue

            if rng.random() < edge_probability:
                graph.add_edge(source, destination)

    for donor in donors:
        for pair in pairs:

            if rng.random() < edge_probability:
                graph.add_edge(donor, pair)

    return graph, set(donors)


# ---------------------------------------------------------
# Run repetition sensitivity experiment
# ---------------------------------------------------------

def run_experiment():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    rng = random.Random(BASE_SEED)

    raw_records = []

    # Statistics indexed by repetition budget.
    statistics = defaultdict(
        lambda: {
            "feasible_trials": 0,
            "successful_trials": 0,
            "infeasible_trials": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "total_attempts": 0,
            "total_runtime": 0.0,
        }
    )

    print("=" * 75)
    print("KIDNEYLINK REPETITION SENSITIVITY EXPERIMENT")
    print("=" * 75)

    print(f"Graph instances: {NUMBER_OF_INSTANCES}")
    print(f"Trials per instance: {TRIALS_PER_INSTANCE}")
    print(f"Repetition budgets: {REPETITION_BUDGETS}")

    for instance in range(
        1,
        NUMBER_OF_INSTANCES + 1,
    ):

        pair_count = rng.randint(
            MIN_PAIRS,
            MAX_PAIRS,
        )

        donor_count = rng.randint(
            MIN_DONORS,
            MAX_DONORS,
        )

        edge_probability = rng.choice(
            EDGE_PROBABILITIES
        )

        target = rng.randint(
            2,
            min(4, pair_count),
        )

        graph_seed = BASE_SEED + instance

        graph, donors = generate_kidney_graph(
            seed=graph_seed,
            pair_count=pair_count,
            donor_count=donor_count,
            edge_probability=edge_probability,
        )

        # Exact solver provides the reference decision.
        exact_result = solve_exact(
            graph=graph,
            altruistic_donors=donors,
            max_cycle_length=MAX_CYCLE_LENGTH,
            max_path_length=MAX_PATH_LENGTH,
        )

        exact_decision = (
            exact_result.maximum_patients >= target
        )

        print(
            f"\nInstance {instance:02d}/{NUMBER_OF_INSTANCES} "
            f"| Pairs={pair_count} "
            f"| Target={target} "
            f"| Exact={'YES' if exact_decision else 'NO'}"
        )

        for trial in range(
            1,
            TRIALS_PER_INSTANCE + 1,
        ):

            # The same seed is used across repetition budgets.
            # This makes smaller budgets use prefixes of the
            # larger-budget coloring sequence.
            trial_seed = (
                BASE_SEED
                + instance * 10000
                + trial
            )

            for budget in REPETITION_BUDGETS:

                result = solve_randomized(
                    graph=graph,
                    altruistic_donors=donors,
                    target=target,
                    max_cycle_length=MAX_CYCLE_LENGTH,
                    max_path_length=MAX_PATH_LENGTH,
                    repetitions=budget,
                    base_seed=trial_seed,
                )

                randomized_decision = result.decision

                false_positive = (
                    randomized_decision
                    and not exact_decision
                )

                false_negative = (
                    exact_decision
                    and not randomized_decision
                )

                stats = statistics[budget]

                if exact_decision:
                    stats["feasible_trials"] += 1

                    if randomized_decision:
                        stats["successful_trials"] += 1

                else:
                    stats["infeasible_trials"] += 1

                if false_positive:
                    stats["false_positives"] += 1

                if false_negative:
                    stats["false_negatives"] += 1

                stats["total_attempts"] += result.attempts
                stats["total_runtime"] += result.elapsed_seconds

                raw_records.append({
                    "instance": instance,
                    "trial": trial,
                    "graph_seed": graph_seed,
                    "trial_seed": trial_seed,
                    "pair_count": pair_count,
                    "donor_count": donor_count,
                    "vertex_count": graph.number_of_nodes(),
                    "edge_count": graph.number_of_edges(),
                    "edge_probability": edge_probability,
                    "target": target,
                    "exact_maximum_patients": (
                        exact_result.maximum_patients
                    ),
                    "exact_decision": exact_decision,
                    "repetition_budget": budget,
                    "randomized_decision": randomized_decision,
                    "actual_attempts": result.attempts,
                    "elapsed_seconds": result.elapsed_seconds,
                    "false_positive": false_positive,
                    "false_negative": false_negative,
                })

                status = (
                    "FALSE POSITIVE"
                    if false_positive
                    else "FALSE NEGATIVE"
                    if false_negative
                    else "SUCCESS"
                    if exact_decision and randomized_decision
                    else "CORRECT NO"
                )

                print(
                    f"  Trial {trial:02d} "
                    f"| Budget={budget:02d} "
                    f"| {status:14s} "
                    f"| Attempts={result.attempts:02d} "
                    f"| Time={result.elapsed_seconds:.5f}s"
                )

                if false_positive:
                    raise AssertionError(
                        f"Unsupported YES at instance {instance}, "
                        f"trial {trial}, budget {budget}."
                    )

    # -----------------------------------------------------
    # Save raw results
    # -----------------------------------------------------

    with RAW_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=raw_records[0].keys(),
        )

        writer.writeheader()
        writer.writerows(raw_records)

    # -----------------------------------------------------
    # Calculate summary statistics
    # -----------------------------------------------------

    summary_records = []

    print("\n" + "=" * 75)
    print("REPETITION SENSITIVITY SUMMARY")
    print("=" * 75)

    for budget in REPETITION_BUDGETS:

        stats = statistics[budget]

        feasible_trials = stats["feasible_trials"]
        infeasible_trials = stats["infeasible_trials"]

        success_rate = (
            100 * stats["successful_trials"] / feasible_trials
            if feasible_trials
            else 0
        )

        false_positive_rate = (
            100 * stats["false_positives"] / infeasible_trials
            if infeasible_trials
            else 0
        )

        total_trials = feasible_trials + infeasible_trials

        average_attempts = (
            stats["total_attempts"] / total_trials
        )

        average_runtime = (
            stats["total_runtime"] / total_trials
        )

        record = {
            "repetition_budget": budget,
            "feasible_trials": feasible_trials,
            "successful_trials": stats["successful_trials"],
            "success_rate_percent": success_rate,
            "infeasible_trials": infeasible_trials,
            "false_positives": stats["false_positives"],
            "false_positive_rate_percent": false_positive_rate,
            "false_negatives": stats["false_negatives"],
            "average_attempts": average_attempts,
            "average_execution_seconds": average_runtime,
        }

        summary_records.append(record)

        print(
            f"Budget={budget:02d} "
            f"| Success={success_rate:6.2f}% "
            f"| FP={stats['false_positives']} "
            f"| FN={stats['false_negatives']} "
            f"| Avg attempts={average_attempts:.2f} "
            f"| Avg time={average_runtime:.5f}s"
        )

    # -----------------------------------------------------
    # Save summary
    # -----------------------------------------------------

    with SUMMARY_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=summary_records[0].keys(),
        )

        writer.writeheader()
        writer.writerows(summary_records)

    print("\n" + "=" * 75)
    print("EXPERIMENT COMPLETED")
    print("=" * 75)

    print(f"Total executions: {len(raw_records)}")
    print(f"Raw results: {RAW_FILE}")
    print(f"Summary: {SUMMARY_FILE}")

    print("=" * 75)


if __name__ == "__main__":
    run_experiment()
