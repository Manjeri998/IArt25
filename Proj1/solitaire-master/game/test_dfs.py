import unittest
from deck import Deck
from card import Card
from pile import Pile
from searchAlgorithms import DFS

class TestDFS(unittest.TestCase):
    def setUp(self):
        """
        Set up a test deck with a simple configuration that can be solved in a few moves.
        """
        # Create cards for a simple test scenario
        self.ace_spades = Card("resources/cards/ace_of_spades.png", (100, 150), "ace", "spades")
        self.two_hearts = Card("resources/cards/2_of_hearts.png", (100, 150), "2", "hearts")
        self.three_clubs = Card("resources/cards/3_of_clubs.png", (100, 150), "3", "clubs")
        self.king_diamonds = Card("resources/cards/king_of_diamonds.png", (100, 150), "king", "diamonds")
        
        # Create piles
        tableau1 = Pile([self.two_hearts], 0, 0, (100, 150), pile_type="tableau")
        tableau2 = Pile([self.three_clubs], 100, 0, (100, 150), pile_type="tableau")
        foundation = Pile([], 200, 0, (100, 150), pile_type="foundation")
        free_cell = Pile([self.ace_spades], 300, 0, (100, 150), pile_type="free-cell")
        
        # Create the deck
        self.deck = Deck(piles=[tableau1, tableau2, foundation, free_cell])
        
        # Create the DFS solver
        self.dfs = DFS()
    
    def test_dfs_heuristic(self):
        """
        Test that the DFS heuristic returns a reasonable value.
        """
        score = self.dfs.dfs_heuristic(self.deck)
        self.assertIsInstance(score, int)
        
        # Create a better state (ace in foundation)
        better_deck = self.deck.clone()
        foundation_pile = better_deck.piles[2]
        free_cell_pile = better_deck.piles[3]
        
        # Move ace to foundation
        ace = free_cell_pile.cards[0]
        free_cell_pile.cards = []
        foundation_pile.cards = [ace]
        
        better_score = self.dfs.dfs_heuristic(better_deck)
        
        # Better state should have a lower score
        self.assertLess(better_score, score)
    
    def test_get_valid_moves(self):
        """
        Test that get_valid_moves returns a list of valid moves.
        """
        moves = self.dfs.get_valid_moves(self.deck)
        self.assertIsInstance(moves, list)
        self.assertGreater(len(moves), 0)
        
        # Check that each move is properly formatted
        for move in moves:
            self.assertEqual(len(move), 3)
            self.assertIsInstance(move[0], int)  # source pile index
            self.assertIsInstance(move[1], int)  # target pile index
            self.assertIsInstance(move[2], list)  # selected cards
    
    def test_apply_move(self):
        """
        Test that apply_move correctly modifies the deck.
        """
        # Get a valid move
        moves = self.dfs.get_valid_moves(self.deck)
        self.assertGreater(len(moves), 0)
        
        # Clone the deck and apply the move
        test_deck = self.deck.clone()
        initial_state = str(test_deck)
        
        self.dfs.apply_move(test_deck, moves[0])
        
        # Deck should be modified
        self.assertNotEqual(str(test_deck), initial_state)
    
    def test_dfs_search_simple(self):
        """
        Test DFS search on a simple configuration.
        """
        # Create a very simple deck that can be solved in one move
        ace_spades = Card("resources/cards/ace_of_spades.png", (100, 150), "ace", "spades")
        
        tableau = Pile([], 0, 0, (100, 150), pile_type="tableau")
        foundation = Pile([], 100, 0, (100, 150), pile_type="foundation")
        free_cell = Pile([ace_spades], 200, 0, (100, 150), pile_type="free-cell")
        
        simple_deck = Deck(piles=[tableau, foundation, free_cell])
        
        # Run DFS search
        solution = self.dfs.dfs_search(simple_deck, max_depth=5)
        
        # Should find a solution
        self.assertIsNotNone(solution)
        self.assertGreater(len(solution), 1)  # At least initial and final states

if __name__ == "__main__":
    unittest.main()