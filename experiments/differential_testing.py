
import csv
import random
from pathlib import Path
from time import perf_counter

import networkx as nx

from kidneylink.exact_solver import solve_exact
from kidneylink.randomized_solver import solve_randomized


# ---------------------------------------------------------
# Experimental configuration
# ---------------------------------------------------------

NUMBER_OF_INSTANCES = 50
MIN_PAIRS = 6
MAX_PAIRS = 10

MIN_ALTRUISTIC_DONORS = 0
MAX_ALTRUISTIC_DONORS = 2

EDGE_PROBABILITIES = [0.15, 0.30, 0.50]

MAX_CYCLE_LENGTH = 3
MAX_PATH_LENGTH = 3

RANDOMIZED_REPETITIONS = 50

BASE_SEED = 2026

OUTPUT_DIR = Path("results")
OUTPUT_FILE = OUTPUT_DIR / "differential_results.csv"


# ---------------------------------------------------------
# Random graph generation
# ---------------------------------------------------------

def generate_kidney_graph(seed, pair_count, donor_count, edge_probability):
    rng = random.Random(seed)

    graph = nx.DiGraph()

    pairs = [f"P{i}" for i in range(1, pair_count + 1)]
    donors = [f"A{i}" for i in range(1, donor_count + 1)]

    # Add patient-donor pairs.
    for pair in pairs:
        graph.add_node(pair, node_type="pair")

    # Add altruistic donors.
    for donor in donors:
        graph.add_node(donor, node_type="altruistic")

    # Generate compatibility edges between patient pairs.
    for source in pairs:
        for destination in pairs:
            if source == destination:
                continue

            if rng.random() < edge_probability:
                graph.add_edge(source, destination)

    # Altruistic donors can only initiate chains.
    for donor in donors:
        for pair in pairs:
            if rng.random() < edge_probability:
                graph.add_edge(donor, pair)

    return graph, set(donors)


# ---------------------------------------------------------
# Differential experiment
# ---------------------------------------------------------

def run_experiment():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rng = random.Random(BASE_SEED)

    records = []

    false_positives = 0
    false_negatives = 0
    exact_yes = 0
    randomized_yes = 0

    print("=" * 65)
    print("KIDNEYLINK DIFFERENTIAL TESTING")
    print("=" * 65)

    for instance in range(1, NUMBER_OF_INSTANCES + 1):

        pair_count = rng.randint(MIN_PAIRS, MAX_PAIRS)

        donor_count = rng.randint(
            MIN_ALTRUISTIC_DONORS,
            min(MAX_ALTRUISTIC_DONORS, pair_count),
        )

        edge_probability = rng.choice(EDGE_PROBABILITIES)

        target = rng.randint(2, min(4, pair_count))

        graph_seed = BASE_SEED + instance

        graph, donors = generate_kidney_graph(
            seed=graph_seed,
            pair_count=pair_count,
            donor_count=donor_count,
            edge_probability=edge_probability,
        )

        # Run the exact reference solver.
        exact_start = perf_counter()

        exact_result = solve_exact(
            graph=graph,
            altruistic_donors=donors,
            max_cycle_length=MAX_CYCLE_LENGTH,
            max_path_length=MAX_PATH_LENGTH,
        )

        exact_elapsed = perf_counter() - exact_start

        exact_decision = (
            exact_result.maximum_patients >= target
        )

        # Run the randomized solver.
        randomized_result = solve_randomized(
            graph=graph,
            altruistic_donors=donors,
            target=target,
            max_cycle_length=MAX_CYCLE_LENGTH,
            max_path_length=MAX_PATH_LENGTH,
            repetitions=RANDOMIZED_REPETITIONS,
            base_seed=BASE_SEED + instance * 1000,
        )

        randomized_decision = randomized_result.decision

        # Compare the two algorithms.
        false_positive = (
            randomized_decision and not exact_decision
        )

        false_negative = (
            exact_decision and not randomized_decision
        )

        if exact_decision:
            exact_yes += 1

        if randomized_decision:
            randomized_yes += 1

        if false_positive:
            false_positives += 1

        if false_negative:
            false_negatives += 1

        record = {
            "instance": instance,
            "graph_seed": graph_seed,
            "pair_count": pair_count,
            "donor_count": donor_count,
            "vertex_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
            "edge_probability": edge_probability,
            "target": target,
            "max_cycle_length": MAX_CYCLE_LENGTH,
            "max_path_length": MAX_PATH_LENGTH,
            "exact_maximum_patients": exact_result.maximum_patients,
            "exact_decision": exact_decision,
            "exact_elapsed_seconds": exact_elapsed,
            "randomized_decision": randomized_decision,
            "randomized_attempts": randomized_result.attempts,
            "randomized_elapsed_seconds": (
                randomized_result.elapsed_seconds
            ),
            "false_positive": false_positive,
            "false_negative": false_negative,
        }

        records.append(record)

        status = (
            "FALSE POSITIVE" if false_positive
            else "FALSE NEGATIVE" if false_negative
            else "MATCH"
        )

        print(
            f"[{instance:03d}/{NUMBER_OF_INSTANCES}] "
            f"Pairs={pair_count:2d} "
            f"Donors={donor_count} "
            f"Target={target} "
            f"Exact={'YES' if exact_decision else 'NO':3s} "
            f"Random={'YES' if randomized_decision else 'NO':3s} "
            f"Result={status}"
        )

        # A randomized YES must always be supported
        # by the exact reference solver.
        if false_positive:
            print("ERROR: Randomized solver produced an unsupported YES.")
            raise AssertionError(
                f"False positive detected in instance {instance}."
            )

    # Save detailed results.
    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=records[0].keys(),
        )

        writer.writeheader()
        writer.writerows(records)

    # Calculate summary statistics.
    total = len(records)

    exact_agreements = (
        sum(
            1 for row in records
            if row["exact_decision"] == row["randomized_decision"]
        )
    )

    agreement_percentage = 100 * exact_agreements / total

    false_negative_percentage = (
        100 * false_negatives / exact_yes
        if exact_yes else 0
    )

    print("\n" + "=" * 65)
    print("EXPERIMENT SUMMARY")
    print("=" * 65)

    print(f"Total instances:             {total}")
    print(f"Exact YES instances:         {exact_yes}")
    print(f"Randomized YES instances:    {randomized_yes}")
    print(f"False positives:             {false_positives}")
    print(f"False negatives:             {false_negatives}")
    print(f"Decision agreement:          {agreement_percentage:.2f}%")
    print(f"False-negative rate:         {false_negative_percentage:.2f}%")

    print(f"\nDetailed results saved to: {OUTPUT_FILE}")

    print("=" * 65)


if __name__ == "__main__":
    run_experiment()
