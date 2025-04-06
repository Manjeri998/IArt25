from time import time
from collections import deque
from deck import CompressedDeck


class TreeNode:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self

    def __hash__(self):
        return hash((tuple(tuple(inner_list) for inner_list in self.state)))


class SearchAlgorithm:
    def __init__(self):
        self.tree_nodes = []

    def move(self, deck, move):
        source_pile_index, target_pile_index, selected_cards = move

        source_pile = deck.piles[source_pile_index]
        target_pile = deck.piles[target_pile_index]

        for card in selected_cards:
            source_pile.cards.pop()
            target_pile.cards.append(card)

        deck.piles[source_pile_index] = source_pile
        deck.piles[target_pile_index] = target_pile

        return deck

    def child_states(self, board):
        new_states = []

        return new_states

    def win(self, board):
        foundation_piles = [pile for pile in board.piles if pile.pile_type == "foundation"]
        for pile in foundation_piles:
            if len(pile.cards) != 13:
                return False
        return True

    def depth(self, node) -> int:
        depth = 0
        while node.parent is not None:
            node = node.parent
            depth += 1
        return depth

    def timed_out(self, before) -> bool:
        return time() - before > 60


class ASTAR(SearchAlgorithm):
    def __init__(self):
        super().__init__()
        self.visited_states = set()

    def run(self, board, score):
        start_time = time()

        # Define the goal state function as a lambda for efficiency
        goal_state_func = lambda deck: deck.check_for_win()

        # Optimized operator function
        def operators_func(deck):
            valid_moves = self.get_valid_moves(deck)
            return [self.move(deck.clone(), move) for move in valid_moves]

        # Compress the initial state
        compressed_board = CompressedDeck(board.piles, board.card_size, board.ranks)

        solution_node = self.a_star_search(
            initial_state=compressed_board,
            goal_state_func=goal_state_func,
            operators_func=operators_func,
            heuristic_func=self.heuristic
        )

        # If no solution is found
        if solution_node is None:
            score[0] = None
            score[1] = time() - start_time
            return

        # Efficiently construct solution path using a deque
        solution_path = deque()
        current_node = solution_node

        while current_node:
            solution_path.appendleft(current_node.state)
            current_node = current_node.parent

        # Decompress the solution path
        decompressed_path = [node.decompress() for node in solution_path]

        # Store the results in score
        score[0] = decompressed_path
        score[1] = time() - start_time
        score[2] = len(decompressed_path) - 1

        # Print solution details
        print("Solução encontrada!")
        print("Número de movimentos:", score[2])
        print("Tempo total:", score[1], "segundos")

    def a_star_search(self, initial_state, goal_state_func, operators_func, heuristic_func):
        root = TreeNode(initial_state)
        stack = [(root, heuristic_func(initial_state))]
        filtered_states = set()
        filtered_states.add(initial_state)

        while len(stack):
            node, value = stack.pop()
            self.visited_states.add(node.state)
            print("Exploring node:", node.state, "Value:", value)

            if goal_state_func(node.state):
                return node

            children = operators_func(node.state)
            evaluated_children = [(child, heuristic_func(child) + self.depth(node) + 1) for child in children]

            for child, value in evaluated_children:
                if child in filtered_states:
                    continue

                filtered_states.add(child)
                child_tree = TreeNode(child, node)
                node.add_child(child_tree)
                stack.append((child_tree, value))

            stack = sorted(stack, key=lambda node: node[1], reverse=True)

        return None

    def heuristic(self, deck):
        h_score = 0
        empty_columns = 0
        free_cells_used = 0

        for pile in deck.piles:
            pile_type = pile.pile_type

            if pile_type == "foundation":
                h_score -= len(pile.cards) * 15

            elif pile_type == "tableau":
                if not pile.cards:
                    empty_columns += 1
                    continue

                for i, card in enumerate(pile.cards):
                    if deck.can_move_to_foundation(card):
                        h_score -= 10
                        h_score += len(pile.cards[i + 1:]) * 5

            elif pile_type == "free-cell":
                if pile.cards:
                    free_cells_used += 1

        h_score -= empty_columns * 3
        h_score += free_cells_used * 4

        return h_score

    def get_valid_moves(self, deck):
        valid_moves = []

        for x, source_pile in enumerate(deck.piles):
            if not source_pile.cards or source_pile.pile_type == "foundation":
                continue

            # Calculate the maximum number of cards that can be moved
            empty_tableaus = sum(1 for pile in deck.piles if pile.pile_type == "tableau" and not pile.cards)
            free_cells = sum(1 for pile in deck.piles if pile.pile_type == "free-cell" and not pile.cards)
            max_cards_to_move = (empty_tableaus + 1) * (free_cells + 1)

            for num_cards in range(1, max_cards_to_move + 1):
                if len(source_pile.cards) < num_cards:
                    break

                selected_cards = source_pile.cards[-num_cards:]

                for y, target_pile in enumerate(deck.piles):
                    if x == y:
                        continue

                    if source_pile.valid_transfer(target_pile, selected_cards, deck.ranks):
                        valid_moves.append((x, y, selected_cards))

        return valid_moves


class BFS(SearchAlgorithm):
    def __init__(self):
        super().__init__()
        self.visited_states = set()

    def run(self, board, score):
        print("Starting BFS algorithm...")
        start_time = time()

        # Define the goal state function
        goal_state_func = lambda deck: deck.check_for_win()

        # Define the operators function (generates child states)
        def operators_func(deck):
            valid_moves = self.get_valid_moves(deck)
            child_states = []
            for move in valid_moves:
                new_deck = deck.clone()
                new_deck = self.move(new_deck, move)
                child_states.append((new_deck, move))
            return child_states

        # Compress the initial state
        compressed_board = CompressedDeck(board.piles, board.card_size, board.ranks)

        # Run BFS
        solution_path = self.bfs_search(
            initial_state=compressed_board,
            goal_state_func=goal_state_func,
            operators_func=operators_func
        )

        if not solution_path:
            print("No solution found within the time limit.")
            score[0] = None  # No solution
            score[1] = time() - start_time  # Time taken
            return

        # Decompress the solution path
        decompressed_path = [node.decompress() for node, _ in solution_path]

        # Store the results in the score list
        score[0] = decompressed_path  # Solution states
        score[1] = time() - start_time  # Time taken
        score[2] = len(decompressed_path) - 1  # Number of moves
        score[3] = [move for _, move in solution_path[1:]]  # Moves to make

        print("\nSolution found!")
        print(f"Time taken: {score[1]:.2f} seconds")
        print(f"Number of moves: {score[2]}")
        print("\nMoves to make:")
        for i, move in enumerate(score[3], 1):
            src = move[0]
            dest = move[1]
            card = move[2][0]  # Get the first card in selected_cards
            print(f"{i}. Move {card} from pile {src} to pile {dest}")

    def bfs_search(self, initial_state, goal_state_func, operators_func):
        visited = set()
        queue = deque()

        # Store (state, move, parent_node) in queue
        initial_node = (initial_state, None, None)
        queue.append(initial_node)
        visited.add(hash(initial_state))

        while queue:
            current_state, move, parent_node = queue.popleft()
            self.visited_states.add(current_state)
            if goal_state_func(current_state):
                # Reconstruct path
                path = []
                node = (current_state, move, parent_node)
                while node:
                    path.append((node[0], node[1]))
                    node = node[2]
                path.reverse()
                return path
            for new_state, new_move in operators_func(current_state):
                state_hash = hash(new_state)
                if state_hash not in visited:
                    visited.add(state_hash)
                    new_node = (new_state, new_move, (current_state, move, parent_node))
                    queue.append(new_node)

        return None

    def get_valid_moves(self, deck):
        valid_moves = []

        for x, source_pile in enumerate(deck.piles):
            if not source_pile.cards or source_pile.pile_type == "foundation":
                continue

            # Calculate the maximum number of cards that can be moved
            empty_tableaus = sum(1 for pile in deck.piles if pile.pile_type == "tableau" and not pile.cards)
            free_cells = sum(1 for pile in deck.piles if pile.pile_type == "free-cell" and not pile.cards)
            max_cards_to_move = (empty_tableaus + 1) * (free_cells + 1)

            free_move = False
            free_cell = False

            for num_cards in range(1, max_cards_to_move + 1):
                if len(source_pile.cards) < num_cards:
                    break

                selected_cards = source_pile.cards[-num_cards:]

                for y, target_pile in enumerate(deck.piles):
                    if x == y:
                        continue

                    if source_pile.valid_transfer(target_pile, selected_cards, deck.ranks):
                        if target_pile.pile_type == "tableau":
                            if not target_pile.cards:
                                if free_move:
                                    continue
                                else:
                                    valid_moves.append((x, y, selected_cards))
                                    free_move = True
                            elif not free_move:
                                valid_moves.append((x, y, selected_cards))
                        elif target_pile.pile_type == "free-cell":
                            if free_cell or free_move:
                                continue
                            else:
                                valid_moves.append((x, y, selected_cards))
                                free_cell = True
                        elif target_pile.pile_type == "foundation":
                            valid_moves.append((x, y, selected_cards))
        return valid_moves

class Greedy(SearchAlgorithm):
    def __init__(self):
        super().__init__()
        self.visited_states = set()

    def run(self, board, score):
        start_time = time()

        # Define the goal state function
        goal_state_func = lambda deck: deck.check_for_win()

        # Define the operators function (generates child states)
        def operators_func(deck):
            valid_moves = self.get_valid_moves(deck)
            return [self.move(deck.clone(), move) for move in valid_moves]

        # Compress the initial state
        compressed_board = CompressedDeck(board.piles, board.card_size, board.ranks)

        solution_node = self.greedy_search(
            initial_state=compressed_board,
            goal_state_func=goal_state_func,
            operators_func=operators_func,
            heuristic_func=self.heuristic
        )

        if solution_node is None:
            score[0] = None
            score[1] = time() - start_time
            return

        solution_path = deque()
        current_node = solution_node

        while current_node:
            solution_path.appendleft(current_node.state)
            current_node = current_node.parent

        decompressed_path = [node.decompress() for node in solution_path]

        score[0] = decompressed_path
        score[1] = time() - start_time
        score[2] = len(decompressed_path) - 1

        print("Solution found!")
        print("Number of moves:", score[2])
        print("Total time:", score[1], "seconds")

    def greedy_search(self, initial_state, goal_state_func, operators_func, heuristic_func):
        root = TreeNode(initial_state)
        stack = [(root, heuristic_func(initial_state))]
        filtered_states = set()
        filtered_states.add(initial_state)

        while stack:
            node, value = stack.pop()
            print("Exploring node:", node.state, "Value:", value)
            self.visited_states.add(node.state)
            if goal_state_func(node.state):
                return node

            children = operators_func(node.state)
            evaluated_children = [(child, heuristic_func(child)) for child in children]

            for child, value in evaluated_children:
                if child in filtered_states:
                    continue

                filtered_states.add(child)
                child_tree = TreeNode(child, node)
                node.add_child(child_tree)
                stack.append((child_tree, value))

            stack = sorted(stack, key=lambda node: node[1], reverse=True)

        return None

    def heuristic(self, deck):
        h_score = 0

        for pile in deck.piles:
            if pile.pile_type == "foundation":
                h_score -= len(pile.cards) * 10
            elif pile.pile_type == "tableau":
                h_score += len(pile.cards)
                for i in range(len(pile.cards) - 1):
                    if not deck.is_sequential(pile.cards[i], pile.cards[i + 1]):
                        h_score += 5

        return h_score

    def get_valid_moves(self, deck):
        valid_moves = []

        for x, source_pile in enumerate(deck.piles):
            if not source_pile.cards or source_pile.pile_type == "foundation":
                continue

            # Calculate the maximum number of cards that can be moved
            empty_tableaus = sum(1 for pile in deck.piles if pile.pile_type == "tableau" and not pile.cards)
            free_cells = sum(1 for pile in deck.piles if pile.pile_type == "free-cell" and not pile.cards)
            max_cards_to_move = (empty_tableaus + 1) * (free_cells + 1)

            for num_cards in range(1, max_cards_to_move + 1):
                if len(source_pile.cards) < num_cards:
                    break

                selected_cards = source_pile.cards[-num_cards:]

                for y, target_pile in enumerate(deck.piles):
                    if x == y:
                        continue

                    if source_pile.valid_transfer(target_pile, selected_cards, deck.ranks):
                        valid_moves.append((x, y, selected_cards))

        return valid_moves


class DFS(SearchAlgorithm):
    def __init__(self):
        super().__init__()

    def run(self, board, score):
        print("Starting DFS algorithm...")
        start_time = time()

        # Compress the initial state
        compressed_board = CompressedDeck(board.piles, board.card_size, board.ranks)
        
        print("Initial state compressed, starting search...")

        # Run DFS search
        solution_node = self.dfs_search(
            initial_state=compressed_board,
            max_depth=20  # Reduced depth limit for faster results
        )

        # If no solution is found
        if solution_node is None:
            print("No solution found within the depth limit.")
            score[0] = None
            score[1] = time() - start_time
            return

        print("Solution node found, constructing path...")
        
        # Construct solution path
        solution_path = []
        current_node = solution_node
        
        while current_node:
            solution_path.insert(0, current_node.state)
            current_node = current_node.parent

        print(f"Path constructed with {len(solution_path)} states")
        
        # Decompress the solution path
        decompressed_path = [node.decompress() for node in solution_path]

        # Store the results in score
        score[0] = decompressed_path
        score[1] = time() - start_time
        score[2] = len(decompressed_path) - 1

        # Print solution details
        print("Solução encontrada!")
        print("Número de movimentos:", score[2])
        print("Tempo total:", score[1], "segundos")

    def dfs_search(self, initial_state, max_depth=20):
        print("Starting DFS search with max depth:", max_depth)
        root = TreeNode(initial_state)
        stack = [(root, 0)]  # (node, depth)
        visited = set()
        visited_count = 0
        
        # Add initial state to visited set
        visited.add(hash(str(initial_state)))
        visited_count += 1
        
        nodes_explored = 0
        
        while stack:
            node, depth = stack.pop()  # DFS uses stack (LIFO)
            nodes_explored += 1
            
            if nodes_explored % 100 == 0:
                print(f"Explored {nodes_explored} nodes, current depth: {depth}, stack size: {len(stack)}")
            
            # Check if we've reached the goal state
            if node.state.check_for_win():
                print(f"Goal state found at depth {depth} after exploring {nodes_explored} nodes!")
                return node
                
            # Don't explore beyond max_depth
            if depth >= max_depth:
                continue
                
            # Get valid moves and create child states
            valid_moves = self.get_valid_moves(node.state)
            print(f"Found {len(valid_moves)} valid moves at depth {depth}")
            
            # Process moves in reverse order for better DFS performance
            for move in reversed(valid_moves):
                new_state = node.state.clone()
                self.move(new_state, move)
                
                # Create a hash for the state
                state_hash = hash(str(new_state))
                
                if state_hash in visited:
                    continue
                    
                visited.add(state_hash)
                visited_count += 1
                
                child_node = TreeNode(new_state, node)
                node.add_child(child_node)
                stack.append((child_node, depth + 1))
            
            if depth == 0:
                print(f"Finished processing root node. Added {len(node.children)} children to stack.")
                
        print(f"Search complete. Explored {nodes_explored} nodes, visited {visited_count} unique states.")
        return None  # No solution found

    def get_valid_moves(self, deck):
        valid_moves = []

        for x, source_pile in enumerate(deck.piles):
            if not source_pile.cards or source_pile.pile_type == "foundation":
                continue

            # Calculate the maximum number of cards that can be moved
            empty_tableaus = sum(1 for pile in deck.piles if pile.pile_type == "tableau" and not pile.cards)
            free_cells = sum(1 for pile in deck.piles if pile.pile_type == "free-cell" and not pile.cards)
            max_cards_to_move = (empty_tableaus + 1) * (free_cells + 1)

            free_move = False
            free_cell = False

            for num_cards in range(1, max_cards_to_move + 1):
                if len(source_pile.cards) < num_cards:
                    break

                selected_cards = source_pile.cards[-num_cards:]

                for y, target_pile in enumerate(deck.piles):
                    if x == y:
                        continue

                    if source_pile.valid_transfer(target_pile, selected_cards, deck.ranks):
                        if target_pile.pile_type == "tableau":
                            if not target_pile.cards:
                                if free_move:
                                    continue
                                else:
                                    valid_moves.append((x, y, selected_cards))
                                    free_move = True
                            elif not free_move:
                                valid_moves.append((x, y, selected_cards))
                        elif target_pile.pile_type == "free-cell":
                            if free_cell or free_move:
                                continue
                            else:
                                valid_moves.append((x, y, selected_cards))
                                free_cell = True
                        elif target_pile.pile_type == "foundation":
                            valid_moves.append((x, y, selected_cards))
        return valid_moves

    def apply_move(self, deck, move):
        """
        Applies a move to the deck.
        """
        source_idx, target_idx, selected_cards = move
        source_pile = deck.piles[source_idx]
        target_pile = deck.piles[target_idx]

        source_pile.transfer_cards(selected_cards, target_pile, deck.ranks)

    def dfs_heuristic(self, deck):
        """
        A heuristic function for DFS that estimates how close the state is to a solution.
        Lower values are better.
        """
        score = 0

        # Count cards in foundation piles (more is better)
        foundation_cards = 0
        for pile in deck.piles:
            if pile.pile_type == "foundation":
                foundation_cards += len(pile.cards)

        # Reward more cards in foundation (negative because lower is better)
        score -= foundation_cards * 10

        # Penalize cards in free cells (they're usually better elsewhere)
        for pile in deck.piles:
            if pile.pile_type == "free-cell" and pile.cards:
                score += 5

        # Reward empty tableau piles (more flexibility)
        empty_tableaus = 0
        for pile in deck.piles:
            if pile.pile_type == "tableau" and not pile.cards:
                empty_tableaus += 1
        score -= empty_tableaus * 8

        return score

    def state_to_hash(self, deck):
        """
        Converts a deck state to a hashable representation.
        """
        state_repr = []

        for pile in deck.piles:
            pile_repr = []
            for card in pile.cards:
                pile_repr.append((card.rank, card.suit))
            state_repr.append(tuple(pile_repr))
        return tuple(state_repr)
