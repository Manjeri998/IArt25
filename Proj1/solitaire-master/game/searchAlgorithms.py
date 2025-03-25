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
        source_pile, target_pile, selected_cards = move
        new_deck = deepcopy(deck)
        new_deck.transfer_cards(selected_cards, new_deck.piles[source_pile], new_deck.piles[target_pile])
        return new_deck
    

    def child_states(self, board):
        new_states = []

        return new_states

    def win(self, board):
        foundation_piles = [pile for pile in board.piles if pile.pile_type == "foundation"]
        for pile in foundation_piles:
            if len(pile.cards) != 13:  # Each foundation pile must have 13 cards
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
        """
        Solves the game using the A* algorithm and stores the solution path in the score list.

        Args:
            board (Deck): The initial state of the game.
            score (list): A list to store the solution path and other results.
        """
        print("Starting A* algorithm...")  # Debugging start of A*
        start_time = time()

        # Define the goal state function
        def goal_state_func(deck):
            return deck.check_for_win()

        # Define the operators function (generates child states)
        def operators_func(deck):
            valid_moves = self.get_valid_moves(deck)
            child_states = []
            for move in valid_moves:
                print("Move:")
                print(move)
                new_deck = deck.clone()
                new_deck.make_move(move)
                child_states.append(new_deck)
            return child_states

        # Run the A* search
        solution_node = self.a_star_search(
            initial_state=board,
            goal_state_func=goal_state_func,
            operators_func=operators_func,
            heuristic_func=self.heuristic
        )

        if solution_node is None:
            print("No solution found within the time limit.")
            score[0] = None  # No solution
            score[1] = time() - start_time  # Time taken
            return

        # Reconstruct the solution path
        solution_path = []
        current_node = solution_node
        while current_node is not None:
            solution_path.append(current_node.state)
            current_node = current_node.parent
        solution_path.reverse()  # Reverse to get the path from start to goal

        # Store the results in the score list
        score[0] = solution_path  # Solution path
        score[1] = time() - start_time  # Time taken
        score[2] = len(solution_path) - 1  # Number of moves
        print(f"Solution found in {score[1]:.2f} seconds with {score[2]} moves.")
    
            
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

        root = TreeNode(initial_state)  # create the root node in the search tree
        stack = [(root, heuristic_func(initial_state))]  # initialize the queue to store the nodes
        filtered_states = [initial_state]

        print("Starting A* search...")  # Debugging start of A*
        print(f"Initial state heuristic: {heuristic_func(initial_state)}")

        while len(stack):

            node, _ = stack.pop()  # get first element in the queue
            print(f"Exploring node with state:\n{node.state}") 
            #print("nó com valor", v)
            if goal_state_func(node.state):  # check goal state
                return node

            children = operators_func(node.state)
            evaluated_children = [(child, heuristic_func(child) + self.depth(node) + 1) for child in children]

            for (child, value) in evaluated_children:  # go through next states
                if child in filtered_states:
                    continue
                
                filtered_states.append(child)

                # create tree node with the new state
                child_tree = TreeNode(child, node)

                node.add_child(child_tree)

                # enqueue the child node
                stack.append((child_tree, value))

                print(f"  Child state added with heuristic {value}:\n{child}")
            
            print("\nCurrent graph structure:")
            self.print_graph(root)
            stack = sorted(stack, key = lambda node: node[1], reverse=True)

        return None
    
    def heuristic(self, deck):
        """
        Heurística aprimorada para A* no FreeCell.

        Considera:
        - Cartas prontas para ir à fundação (benefício maior)
        - Cartas bloqueadas (penalidade)
        - Número de espaços livres (colunas e células)
        - Penaliza o uso excessivo de células livres
        """
        h_score = 0

        # 🏆 Benefício para cartas na fundação
        for pile in deck.piles:
            if pile.is_foundation():
                h_score -= len(pile.cards) * 15  # Mais cartas na fundação = melhor

        # 🔓 Penalizar cartas bloqueadas que deveriam ir para a fundação
        for pile in deck.piles:
            if pile.pile_type == "tableau":
                for i, card in enumerate(pile.cards):
                    if deck.can_move_to_foundation(card):  
                        h_score -= 10  # Recompensa por estar pronto para a fundação
                        
                        # Penalizar todas as cartas acima dela
                        cards_above = pile.cards[i+1:]  
                        h_score += len(cards_above) * 3  # Penaliza cada carta acima

        # 🏗️ Benefício por colunas vazias
        empty_columns = sum(1 for pile in deck.piles if pile.pile_type == "tableau" and len(pile.cards) == 0)
        h_score -= empty_columns * 4  # Mais colunas vazias = melhor

        # 🚧 Penalizar células livres ocupadas
        free_cells_used = sum(1 for pile in deck.piles if pile.pile_type == "freecell" and len(pile.cards) > 0)
        h_score += free_cells_used * 3  # Evitar sobrecarregar células livres

        return h_score
    
    def get_valid_moves(self, deck):
        """
        Returns a list of valid moves as tuples (source_pile, target_pile, selected_card).
        Ensures the base card is moved individually and the move is valid.
        """
        valid_moves = []
        moved_to_free_cell = set()

        for source_pile in deck.piles:
            if not source_pile.cards:
                continue  # Skip empty piles

            base_card = source_pile.cards[-1]  # Only consider the topmost card

            for target_pile in deck.piles:
                if source_pile == target_pile:
                    continue  # Skip moving within the same pile

                # Check if moving the base card is valid
                if source_pile.valid_transfer(target_pile, [base_card], deck.ranks):
                    valid_moves.append((source_pile, target_pile, [base_card]))

        return valid_moves
    
    def print_graph(self, root):
        """
        Prints the graph structure for debugging.

        Args:
            root (TreeNode): The root node of the graph.
        """
        def traverse(node, depth=0):
            print("  " * depth + f"Node (State): {node.state}")
            for child in node.children:
                traverse(child, depth + 1)

        print("Graph:")
        traverse(root)
    '''
    def a_star_solve(self, deck):
        """
        Resolve o jogo de Paciência usando o algoritmo A* e exibe o estado atual no jogo.
        """
        open_set = PriorityQueue()
        initial_state = deck.clone()  # Clone para evitar modificações no original
        open_set.put((0, initial_state))
        
        came_from = {}
        g_score = {initial_state: 0}
        f_score = {initial_state: self.heuristic(initial_state)}
        
        visited_states = set()
        start_time = time.time()

        while not open_set.empty():
            _, current_deck = open_set.get()
            print(current_deck)
            print(g_score[current_deck])
            print(f_score[current_deck])
            # Se o estado já foi visitado, pule
            if current_deck in visited_states:
                continue
            visited_states.add(current_deck)

            if current_deck.check_for_win():
                return self.reconstruct_path(came_from, current_deck)

            for move in self.get_valid_moves(current_deck):
                neighbor_state = current_deck.clone()
                neighbor_state.make_move(move)

                if neighbor_state in visited_states:
                    continue

                temp_g_score = g_score[current_deck] + 1

                if neighbor_state not in g_score or temp_g_score < g_score[neighbor_state]:
                    came_from[neighbor_state] = current_deck
                    g_score[neighbor_state] = temp_g_score
                    f_score[neighbor_state] = temp_g_score + self.heuristic(neighbor_state)
                    open_set.put((f_score[neighbor_state], neighbor_state))

        return None 

    def reconstruct_path(slcame_from, current):
        """
        Reconstrói e imprime o caminho da solução.
        """
        path = []
        
        return path; # Aqui poderia ser uma renderização do estado
    '''

