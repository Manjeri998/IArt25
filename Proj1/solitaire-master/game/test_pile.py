import unittest
from pile import Pile
from card import Card

class TestValidTransfer(unittest.TestCase):
    def setUp(self):
        """
        Set up test piles with predefined cards.
        """
        self.card1 = Card("resources/cards/ace_of_spades.png", (100, 150), "ace", "spades")
        self.card2 = Card("resources/cards/2_of_spades.png", (100, 150), "2", "spades")
        self.card3 = Card("resources/cards/3_of_hearts.png", (100, 150), "3", "hearts")
        self.card4 = Card("resources/cards/4_of_clubs.png", (100, 150), "4", "clubs")

        # Create a tableau pile with cards
        self.source_pile = Pile([self.card2, self.card1], 0, 0, (100, 150), pile_type="tableau")

        # Create an empty foundation pile
        self.target_pile_foundation = Pile([], 0, 0, (100, 150), pile_type="foundation")

        # Create a tableau pile with one card
        self.target_pile_tableau = Pile([self.card3], 0, 0, (100, 150), pile_type="tableau")

        # Define ranks for validation
        self.ranks = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']

    def test_valid_transfer_to_foundation(self):
        """
        Test transferring a valid card to a foundation pile.
        """
        selected_cards = [self.card1]  # Select the Ace of Spades
        result = self.source_pile.valid_transfer(self.target_pile_foundation, selected_cards, self.ranks)
        self.assertTrue(result)  # Transfer should be valid

    def test_invalid_transfer_to_foundation(self):
        """
        Test transferring an invalid card to a foundation pile.
        """
        selected_cards = [self.card2]  # Select the 2 of Spades (invalid for empty foundation)
        result = self.source_pile.valid_transfer(self.target_pile_foundation, selected_cards, self.ranks)
        self.assertFalse(result)  # Transfer should be invalid

    def test_valid_transfer_to_tableau(self):
        """
        Test transferring a valid card to a tableau pile.
        """
        selected_cards = [self.card4]  # Select the 4 of Clubs
        result = self.source_pile.valid_transfer(self.target_pile_tableau, selected_cards, self.ranks)
        self.assertTrue(result)  # Transfer should be valid

    def test_invalid_transfer_to_tableau(self):
        """
        Test transferring an invalid card to a tableau pile.
        """
        selected_cards = [self.card2]  # Select the 2 of Spades (invalid for tableau with 3 of Hearts)
        result = self.source_pile.valid_transfer(self.target_pile_tableau, selected_cards, self.ranks)
        self.assertFalse(result)  # Transfer should be invalid

    def test_transfer_to_free_cell(self):
        """
        Test transferring a card to a free cell pile.
        """
        free_cell_pile = Pile([], 0, 0, (100, 150), pile_type="free-cell")
        selected_cards = [self.card1]  # Select the Ace of Spades
        result = self.source_pile.valid_transfer(free_cell_pile, selected_cards, self.ranks)
        self.assertTrue(result)  # Transfer should be valid

        # Test transferring multiple cards to a free cell (invalid)
        selected_cards = [self.card1, self.card2]
        result = self.source_pile.valid_transfer(free_cell_pile, selected_cards, self.ranks)
        self.assertFalse(result)  # Transfer should be invalid

class TestPile(unittest.TestCase):
    def setUp(self):
        """
        Set up test piles with predefined cards.
        """
        self.card1 = Card("resources/cards/ace_of_spades.png", (100, 150), "ace", "spades")
        self.card2 = Card("resources/cards/2_of_spades.png", (100, 150), "2", "spades")
        self.card3 = Card("resources/cards/3_of_spades.png", (100, 150), "3", "spades")
        self.card4 = Card("resources/cards/4_of_hearts.png", (100, 150), "4", "hearts")

        # Create a tableau pile with cards
        self.source_pile = Pile([self.card2, self.card1], 0, 0, (100, 150), pile_type="tableau")

        # Create an empty foundation pile
        self.target_pile = Pile([], 0, 0, (100, 150), pile_type="foundation")

        # Define ranks for validation
        self.ranks = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']

    def test_valid_transfer(self):
        """
        Test transferring a valid card to the target pile.
        """
        selected_cards = [self.card2]  # Select the 2 of Spades
        result = self.source_pile.transfer_cards(selected_cards, self.target_pile, self.ranks)

        self.assertTrue(result)  # Transfer should succeed
        self.assertEqual(len(self.source_pile.cards), 1)  # Source pile should have 1 card left
        self.assertEqual(len(self.target_pile.cards), 1)  # Target pile should have 1 card
        self.assertEqual(self.target_pile.cards[-1], self.card2)  # Target pile should contain the transferred card

    def test_invalid_transfer(self):
        """
        Test transferring an invalid card to the target pile.
        """
        selected_cards = [self.card4]  # Select the 4 of Hearts (invalid for foundation)
        result = self.source_pile.transfer_cards(selected_cards, self.target_pile, self.ranks)

        self.assertFalse(result)  # Transfer should fail
        self.assertEqual(len(self.source_pile.cards), 2)  # Source pile should remain unchanged
        self.assertEqual(len(self.target_pile.cards), 0)  # Target pile should remain empty

    def test_transfer_multiple_cards(self):
        """
        Test transferring multiple cards to the target pile.
        """
        selected_cards = [self.card2, self.card1]  # Select Ace and 2 of Spades
        result = self.source_pile.transfer_cards(selected_cards, self.target_pile, self.ranks)

        self.assertTrue(result)  # Transfer should succeed
        self.assertEqual(len(self.source_pile.cards), 0)  # Source pile should be empty
        self.assertEqual(len(self.target_pile.cards), 2)  # Target pile should have 2 cards
        self.assertEqual(self.target_pile.cards[-1], self.card2)  # Target pile should contain the last transferred card

class TestIsValidMovingPile(unittest.TestCase):
    def setUp(self):
        """
        Set up test piles with predefined cards.
        """
        self.card1 = Card("resources/cards/ace_of_spades.png", (100, 150), "ace", "spades")
        self.card2 = Card("resources/cards/2_of_hearts.png", (100, 150), "2", "hearts")
        self.card3 = Card("resources/cards/3_of_spades.png", (100, 150), "3", "spades")
        self.card4 = Card("resources/cards/4_of_hearts.png", (100, 150), "4", "hearts")

        # Create a tableau pile with cards
        self.pile = Pile([self.card4, self.card3, self.card2, self.card1], 0, 0, (100, 150), pile_type="tableau")

        # Define ranks for validation
        self.ranks = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']

    def test_valid_single_card(self):
        """
        Test that a single card is always a valid moving pile.
        """
        selected_cards = [self.card1]
        result = self.pile.is_valid_moving_pile(selected_cards, self.ranks)
        self.assertTrue(result)

    def test_valid_multiple_cards(self):
        """
        Test that a valid sequence of cards is a valid moving pile.
        """
        selected_cards = [self.card3, self.card2, self.card1]
        result = self.pile.is_valid_moving_pile(selected_cards, self.ranks)
        self.assertTrue(result)

    def test_invalid_order(self):
        """
        Test that cards not in descending order are not a valid moving pile.
        """
        selected_cards = [self.card2, self.card3]  # Invalid order
        result = self.pile.is_valid_moving_pile(selected_cards, self.ranks)
        self.assertFalse(result)

    def test_invalid_color(self):
        """
        Test that cards with the same color are not a valid moving pile.
        """
        selected_cards = [self.card4, self.card2]  # Same color (hearts)
        result = self.pile.is_valid_moving_pile(selected_cards, self.ranks)
        self.assertFalse(result)

    def test_not_last_cards(self):
        """
        Test that selected cards must be the last cards in the pile.
        """
        selected_cards = [self.card3, self.card2]  # Not the last cards
        result = self.pile.is_valid_moving_pile(selected_cards, self.ranks)
        self.assertFalse(result)
