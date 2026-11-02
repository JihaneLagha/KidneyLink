
import csv
import random
from collections import defaultdict
from pathlib import Path
from time import perf_counter

import networkx as nx

from kidneylink.exact_solver import solve_exact
from kidneylink.randomized_solver import solve_randomized


# ---------------------------------------------------------
# Experimental configuration
# ---------------------------------------------------------

NUMBER_OF_INSTANCES = 20
TRIALS_PER_INSTANCE = 10
RANDOMIZED_REPETITIONS = 50

MIN_PAIRS = 6
MAX_PAIRS = 10

MIN_DONORS = 0
MAX_DONORS = 2

EDGE_PROBABILITIES = [0.15, 0.30, 0.50]

MAX_CYCLE_LENGTH = 3
MAX_PATH_LENGTH = 3

BASE_SEED = 3026

OUTPUT_DIR = Path("results")

RAW_FILE = OUTPUT_DIR / "reliability_trials.csv"
SUMMARY_FILE = OUTPUT_DIR / "reliability_summary.csv"


# ---------------------------------------------------------
# Random graph generation
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
# Run reliability experiment
# ---------------------------------------------------------

def run_experiment():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    rng = random.Random(BASE_SEED)

    raw_records = []
    summary_records = []

    total_false_positives = 0
    total_false_negatives = 0

    feasible_instances = 0
    infeasible_instances = 0

    print("=" * 70)
    print("KIDNEYLINK RANDOMIZED RELIABILITY EXPERIMENT")
    print("=" * 70)

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

        # Obtain the exact reference decision.
        exact_result = solve_exact(
            graph=graph,
            altruistic_donors=donors,
            max_cycle_length=MAX_CYCLE_LENGTH,
            max_path_length=MAX_PATH_LENGTH,
        )

        exact_decision = (
            exact_result.maximum_patients >= target
        )

        if exact_decision:
            feasible_instances += 1
        else:
            infeasible_instances += 1

        successful_trials = 0
        false_positives = 0
        false_negatives = 0

        attempts = []
        execution_times = []

        print(
            f"\nInstance {instance:02d}/{NUMBER_OF_INSTANCES} "
            f"| Pairs={pair_count} "
            f"| Target={target} "
            f"| Density={edge_probability}"
        )

        # Independent randomized executions.
        for trial in range(
            1,
            TRIALS_PER_INSTANCE + 1,
        ):

            trial_seed = (
                BASE_SEED
                + instance * 10000
                + trial
            )

            randomized_result = solve_randomized(
                graph=graph,
                altruistic_donors=donors,
                target=target,
                max_cycle_length=MAX_CYCLE_LENGTH,
                max_path_length=MAX_PATH_LENGTH,
                repetitions=RANDOMIZED_REPETITIONS,
                base_seed=trial_seed,
            )

            randomized_decision = (
                randomized_result.decision
            )

            false_positive = (
                randomized_decision
                and not exact_decision
            )

            false_negative = (
                exact_decision
                and not randomized_decision
            )

            if randomized_decision and exact_decision:
                successful_trials += 1

            if false_positive:
                false_positives += 1
                total_false_positives += 1

            if false_negative:
                false_negatives += 1
                total_false_negatives += 1

            attempts.append(
                randomized_result.attempts
            )

            execution_times.append(
                randomized_result.elapsed_seconds
            )

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
                "randomized_decision": randomized_decision,
                "randomized_attempts": (
                    randomized_result.attempts
                ),
                "randomized_elapsed_seconds": (
                    randomized_result.elapsed_seconds
                ),
                "false_positive": false_positive,
                "false_negative": false_negative,
            })

            status = (
                "SUCCESS"
                if randomized_decision
                else "MISSED"
                if exact_decision
                else "CORRECT NO"
            )

            print(
                f"  Trial {trial:02d}: "
                f"{status:12s} "
                f"Attempts={randomized_result.attempts:2d} "
                f"Time={randomized_result.elapsed_seconds:.5f}s"
            )

        success_rate = (
            100 * successful_trials / TRIALS_PER_INSTANCE
            if exact_decision
            else None
        )

        average_attempts = (
            sum(attempts) / len(attempts)
        )

        average_time = (
            sum(execution_times) / len(execution_times)
        )

        summary_records.append({
            "instance": instance,
            "pair_count": pair_count,
            "donor_count": donor_count,
            "edge_count": graph.number_of_edges(),
            "edge_probability": edge_probability,
            "target": target,
            "exact_maximum_patients": (
                exact_result.maximum_patients
            ),
            "exact_decision": exact_decision,
            "trials": TRIALS_PER_INSTANCE,
            "successful_trials": successful_trials,
            "success_rate_percent": (
                success_rate
                if success_rate is not None
                else ""
            ),
            "average_attempts": average_attempts,
            "average_execution_seconds": average_time,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
        })

        if exact_decision:
            print(
                f"  SUCCESS RATE: "
                f"{success_rate:.2f}%"
            )
        else:
            print(
                "  Exact reference: NO "
                "| Randomized solver should always return NO"
            )

    # -----------------------------------------------------
    # Save raw trial results
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
    # Save per-instance summary
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

    # -----------------------------------------------------
    # Overall results
    # -----------------------------------------------------

    feasible_records = [
        row for row in summary_records
        if row["exact_decision"]
    ]

    total_feasible_trials = (
        len(feasible_records) * TRIALS_PER_INSTANCE
    )

    total_successful_trials = sum(
        row["successful_trials"]
        for row in feasible_records
    )

    overall_success_rate = (
        100 * total_successful_trials / total_feasible_trials
        if total_feasible_trials
        else 0
    )

    print("\n" + "=" * 70)
    print("RELIABILITY EXPERIMENT SUMMARY")
    print("=" * 70)

    print(f"Total graph instances:       {NUMBER_OF_INSTANCES}")
    print(f"Feasible instances:          {feasible_instances}")
    print(f"Infeasible instances:        {infeasible_instances}")
    print(f"Independent trials/instance: {TRIALS_PER_INSTANCE}")
    print(f"Colorings/trial:             {RANDOMIZED_REPETITIONS}")
    print(f"Total randomized runs:       {len(raw_records)}")

    print(
        f"Overall success rate:        "
        f"{overall_success_rate:.2f}%"
    )

    print(
        f"False positives:             "
        f"{total_false_positives}"
    )

    print(
        f"False negatives:             "
        f"{total_false_negatives}"
    )

    print(f"\nRaw results:     {RAW_FILE}")
    print(f"Instance summary: {SUMMARY_FILE}")

    print("=" * 70)


if __name__ == "__main__":
    run_experiment()
