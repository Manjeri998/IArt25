import time
import tracemalloc
from searchAlgorithms import ASTAR, BFS, Greedy, DFS
from deck import Deck
import matplotlib

matplotlib.use('TkAgg')  # Use TkAgg backend
import matplotlib.pyplot as plt


def run_algorithm(algorithm, deck):
    tracemalloc.start()
    start_time = time.time()

    score = [None] * 6
    algorithm.run(deck, score)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        'time_spent': end_time - start_time,
        'memory_used': peak,
        'states_generated': len(algorithm.visited_states)
    }


def main():
    deck = Deck.load_deck_from_file("states/deck8.txt")
    algorithms = {
        'A*': ASTAR(),
        'Greedy': Greedy(),
        'BFS': BFS()
    }

    results = {}
    for name, algorithm in algorithms.items():
        results[name] = run_algorithm(algorithm, deck.clone())

    fig, axs = plt.subplots(3, 1, figsize=(8, 12))  # Adjusted figure size

    names = list(results.keys())
    times = [results[name]['time_spent'] for name in names]
    memories = [results[name]['memory_used'] for name in names]
    states = [results[name]['states_generated'] for name in names]

    axs[0].bar(names, times, color='blue')
    axs[0].set_title('Time Spent (seconds)')

    axs[1].bar(names, memories, color='green')
    axs[1].set_title('Memory Used (bytes)')

    axs[2].bar(names, states, color='red')
    axs[2].set_title('States Generated')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
