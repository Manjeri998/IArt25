from queue import PriorityQueue
from time import time
from collections import deque
from math import inf
from copy import deepcopy

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
    
    def run(self, board, score):
        start_time = time()

        # Define the goal state function as a lambda for efficiency
        goal_state_func = lambda deck: deck.check_for_win()

        # Optimized operator function
        def operators_func(deck):
            valid_moves = self.get_valid_moves(deck)
            return [self.move(deck.clone(), move) for move in valid_moves]

        solution_node = self.a_star_search(
            initial_state=board,
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

        # Store the results in score
        score[0] = list(solution_path)  
        score[1] = time() - start_time  
        score[2] = len(solution_path) - 1  

        # Print solution details
        print("Solução encontrada!")
        print("Número de movimentos:", score[2])
        print("Tempo total:", score[1], "segundos")

    
            
    def shortest_path(self, initial_coordinate, cluster):
        visited = set()
        queue = deque([(initial_coordinate, [])])

        while queue:
            (row, col), path = queue.popleft()
            if (row, col) in visited:
                continue
            visited.add((row, col))

            if cluster[row][col] == 1:
                return len(path)

        return None

    def get_distance(self, cluster1, cluster2):
        total = inf
        for (i, j) in [(i, j) for i in range(len(cluster1)) for j in range(len(cluster1))]:
            if cluster1[i][j] == 1:
                total = min(self.shortest_path((i, j), cluster2), total)
        return total

    def a_star_search(self, initial_state, goal_state_func, operators_func, heuristic_func):
        root = TreeNode(initial_state)
        stack = [(root, heuristic_func(initial_state))]
        filtered_states = set() 
        filtered_states.add(initial_state)

        while len(stack):
            node, value = stack.pop()  
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
            pile_type = pile.pile_type  # Avoid multiple attribute lookups

            if pile_type == "foundation":
                h_score -= len(pile.cards) * 15  # Reward more cards in the foundation

            elif pile_type == "tableau":
                if not pile.cards:
                    empty_columns += 1  # Count empty tableau columns
                    continue
                
                for i, card in enumerate(pile.cards):
                    if deck.can_move_to_foundation(card):
                        h_score -= 10  # Reward cards ready for foundation
                        h_score += len(pile.cards[i+1:]) * 5  # Penalize blocked cards

            elif pile_type == "free-cell":
                if pile.cards:
                    free_cells_used += 1  # Count occupied free cells

        # Apply penalties for empty tableau columns and occupied free cells
        h_score -= empty_columns * 3
        h_score += free_cells_used * 4

        return h_score
    
    def get_valid_moves(self, deck):
        valid_moves = []

        for x, source_pile in enumerate(deck.piles):
            if not source_pile.cards or source_pile.pile_type == "foundation":
                continue

            base_card = source_pile.cards[-1]
            free_cell_used = False
            free_move_used = False

            for y, target_pile in enumerate(deck.piles):
                if x == y:  
                    continue  

                if not source_pile.valid_transfer(target_pile, [base_card], deck.ranks):
                    continue  

                if target_pile.pile_type == "free-cell":
                    if free_cell_used:
                        continue
                    free_cell_used = True  

                elif not target_pile.cards and target_pile.pile_type == "tableau":
                    if free_move_used:
                        continue
                    free_move_used = True  

                valid_moves.append((x, y, [base_card]))

        return valid_moves


class DFS(SearchAlgorithm):
    def __init__(self):
        super().__init__()
        self.visited_states = set()
        
    def run(self, board, score):
        start_time = time()
        
        # Initialize the solution path
        solution_path = self.dfs_search(board)
        
        # If no solution is found
        if solution_path is None:
            score[0] = None
            score[1] = time() - start_time
            return
            
        # Store the results in score
        score[0] = solution_path
        score[1] = time() - start_time
        score[2] = len(solution_path) - 1
        
        # Print solution details
        print("Solution found with DFS!")
        print("Number of moves:", score[2])
        print("Total time:", score[1], "seconds")
    
    def dfs_search(self, initial_state, max_depth=100):
        """
        Performs a depth-first search to find a solution.
        """
        root = TreeNode(initial_state)
        stack = [(root, 0)]  # (node, depth)
        self.visited_states = set()
        
        while stack:
            node, depth = stack.pop()
            state_hash = self.state_to_hash(node.state)
            
            # Skip if we've seen this state or exceeded max depth
            if state_hash in self.visited_states or depth > max_depth:
                continue
                
            self.visited_states.add(state_hash)
            
            # Check if we've reached the goal state
            # Use check_for_win method if it exists, otherwise use win method
            if hasattr(node.state, 'check_for_win') and node.state.check_for_win():
                # Reconstruct the path
                path = []
                current = node
                while current:
                    path.append(current.state)
                    current = current.parent
                return list(reversed(path))
            elif self.win(node.state):
                # Reconstruct the path
                path = []
                current = node
                while current:
                    path.append(current.state)
                    current = current.parent
                return list(reversed(path))
            
            # Get valid moves and create child states
            if depth < max_depth:
                valid_moves = self.get_valid_moves(node.state)
                
                # Sort moves by heuristic value (most promising first for DFS)
                moves_with_scores = []
                for move in valid_moves:
                    new_state = node.state.clone()
                    self.apply_move(new_state, move)
                    score = self.dfs_heuristic(new_state)
                    moves_with_scores.append((move, score))
                
                # Sort by heuristic score (lower is better)
                moves_with_scores.sort(key=lambda x: x[1])
                
                # Add children to the stack (in reverse order so best moves are popped first)
                for move, _ in reversed(moves_with_scores):
                    new_state = node.state.clone()
                    self.apply_move(new_state, move)
                    
                    # Skip if we've already seen this state
                    if self.state_to_hash(new_state) in self.visited_states:
                        continue
                        
                    child = TreeNode(new_state, node)
                    node.add_child(child)
                    stack.append((child, depth + 1))
        
        return None  # No solution found
    
    def get_valid_moves(self, deck):
        """
        Gets all valid moves for the current deck state.
        """
        valid_moves = []
        
        for source_idx, source_pile in enumerate(deck.piles):
            if not source_pile.cards:
                continue
                
            for target_idx, target_pile in enumerate(deck.piles):
                if source_idx == target_idx:
                    continue
                    
                # Try moving different numbers of cards from the source pile
                for i in range(len(source_pile.cards)):
                    selected_cards = source_pile.cards[i:]
                    
                    if source_pile.valid_transfer(target_pile, selected_cards, deck.ranks):
                        valid_moves.append((source_idx, target_idx, selected_cards))
        
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
    

