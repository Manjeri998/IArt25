import unittest
from deck import Deck
from card import Card
from pile import Pile

class TestDeck(unittest.TestCase):
    def setUp(self):
        """
        Set up a test deck with predefined piles and cards.
        """
        self.card1 = Card("resources/cards/ace_of_spades.png", (100, 150), "ace", "spades")
        self.card2 = Card("resources/cards/2_of_hearts.png", (100, 150), "2", "hearts")
        self.card3 = Card("resources/cards/3_of_clubs.png", (100, 150), "3", "clubs")

        pile1 = Pile([self.card1, self.card2], 0, 0, (100, 150), pile_type="tableau")
        pile2 = Pile([self.card3], 0, 0, (100, 150), pile_type="foundation")

        self.deck = Deck(piles=[pile1, pile2])

    def test_find_card_in_tableau(self):
        """
        Test finding a card in a tableau pile.
        """
        pile_index, card_index = self.deck.find_card(self.card1)
        self.assertEqual(pile_index, 0)
        self.assertEqual(card_index, 0)

    def test_find_card_in_foundation(self):
        """
        Test finding a card in a foundation pile.
        """
        pile_index, card_index = self.deck.find_card(self.card3)
        self.assertEqual(pile_index, 1)
        self.assertEqual(card_index, 0)

    def test_card_not_found(self):
        """
        Test finding a card that does not exist in the deck.
        """
        card_not_in_deck = Card("resources/cards/4_of_diamonds.png", (100, 150), "4", "diamonds")
        pile_index, card_index = self.deck.find_card(card_not_in_deck)
        self.assertIsNone(pile_index)
        self.assertIsNone(card_index)

if __name__ == "__main__":
    unittest.main()