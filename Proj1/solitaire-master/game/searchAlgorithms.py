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

        def goal_state_func(deck):
            return deck.check_for_win()

        def operators_func(deck):
            print("Generating child states...")
            
            valid_moves = self.get_valid_moves(deck)
            
            start_time = time()
            child_states = [self.move(deck.clone(), move) for move in valid_moves]
            end_time = time()
            
            print(f"Time to generate child states: {end_time - start_time:.4f} seconds")
            
            return child_states

        solution_node = self.a_star_search(
            initial_state=board,
            goal_state_func=goal_state_func,
            operators_func=operators_func,
            heuristic_func=self.heuristic
        )

        if solution_node is None:
            score[0] = None  
            score[1] = time() - start_time  
            return

        solution_path = []
        current_node = solution_node
        while current_node is not None:
            solution_path.append(current_node.state)
            current_node = current_node.parent
        solution_path.reverse() 

        score[0] = solution_path  
        score[1] = time() - start_time  
        score[2] = len(solution_path) - 1  
        print("Solução encontrada!")
        print("Número de movimentos:", len(solution_path) - 1)
        print("Tempo total:", time() - start_time, "segundos")
    
            
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
                        h_score += len(cards_above) * 5  # Penaliza cada carta acima

        # 🏗️ Benefício por colunas vazias
        empty_columns = sum(1 for pile in deck.piles if pile.pile_type == "tableau" and len(pile.cards) == 0)
        h_score -= empty_columns * 3  # Mais colunas vazias = melhor

        # 🚧 Penalizar células livres ocupadas
        free_cells_used = sum(1 for pile in deck.piles if pile.pile_type == "free-cell" and len(pile.cards) > 0)
        h_score += free_cells_used * 4  # Evitar sobrecarregar células livres

        return h_score
    
    def get_valid_moves(self, deck):
        valid_moves = []

        free_cell = False
        free_move = False
        x = 0
        for source_pile in deck.piles:
            if (not source_pile.cards) or (source_pile.pile_type == "foundation"):
                x += 1
                continue 

            base_card = source_pile.cards[-1] 
            free_cell = False
            free_move = False
            y = 0
            for target_pile in deck.piles:
                if x == y:
                    y += 1
                    continue  

                if source_pile.valid_transfer(target_pile, [base_card], deck.ranks):
                    if target_pile.pile_type == "free-cell":
                        if    free_cell:
                            y+=1
                            continue
                        else:
                            valid_moves.append((x, y, [base_card]))
                            free_cell = True
                    else: 
                        if (not target_pile.cards) and target_pile.pile_type == "tableau":
                            if free_move:
                                y += 1
                                continue
                            else:
                                valid_moves.append((x, y, [base_card]))
                                free_move = True
                        valid_moves.append((x, y, [base_card]))
                    
                y += 1
            x += 1
                    

        return valid_moves
    

