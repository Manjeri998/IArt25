import time
import tracemalloc
from searchAlgorithms import ASTAR, BFS, Greedy, DFS
from deck import Deck
import matplotlib

matplotlib.use('MacOSX')  # Try using the MacOSX backend instead of TkAgg
import matplotlib.pyplot as plt


def run_algorithm(algorithm, deck):
    tracemalloc.start()
    start_time = time.time()

    score = [None] * 6
    algorithm.run(deck, score)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Check if the algorithm has visited_states attribute
    states_count = 0
    if hasattr(algorithm, 'visited_states'):
        states_count = len(algorithm.visited_states)
    elif hasattr(algorithm, 'visited'):  # Some implementations might use 'visited' instead
        states_count = len(algorithm.visited)
    
    return {
        'time_spent': end_time - start_time,
        'memory_used': peak,
        'states_generated': states_count
    }


def main():
    deck = Deck.load_deck_from_file("states/deck8.txt")
    algorithms = {
        'A*': ASTAR(),
        'Greedy': Greedy(),
        'BFS': BFS(),
        'DFS': DFS()
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
    # At the end of the main function, add:
    plt.savefig('algorithm_comparison.png')  # Save to a file
    plt.show()  # Still try to show it as well


if __name__ == "__main__":
    main()
