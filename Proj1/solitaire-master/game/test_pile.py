import unittest
from pile import Pile
from card import Card

class TestPile(unittest.TestCase):
    def setUp(self):
        """
        Set up test piles with predefined cards.
        """
        self.card1 = Card("resources/cards/ace_of_spades.png", (100, 150), "ace", "spades", face_up=True)
        self.card2 = Card("resources/cards/2_of_spades.png", (100, 150), "2", "spades", face_up=True)
        self.card3 = Card("resources/cards/3_of_spades.png", (100, 150), "3", "spades", face_up=True)
        self.card4 = Card("resources/cards/4_of_hearts.png", (100, 150), "4", "hearts", face_up=True)

        # Create a tableau pile with cards
        self.source_pile = Pile([self.card1, self.card2], 0, 0, (100, 150), pile_type="tableau")

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
        selected_cards = [self.card1, self.card2]  # Select Ace and 2 of Spades
        result = self.source_pile.transfer_cards(selected_cards, self.target_pile, self.ranks)

        self.assertTrue(result)  # Transfer should succeed
        self.assertEqual(len(self.source_pile.cards), 0)  # Source pile should be empty
        self.assertEqual(len(self.target_pile.cards), 2)  # Target pile should have 2 cards
        self.assertEqual(self.target_pile.cards[-1], self.card2)  # Target pile should contain the last transferred card

if __name__ == "__main__":
    unittest.main()