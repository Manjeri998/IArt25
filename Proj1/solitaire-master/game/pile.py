from collections import namedtuple


class Pile:
    def __init__(self, cards, x, y, card_size, pile_type="tableau"):
        self.Order = namedtuple('Order', ['foundation', 'rank', 'color_suit'])
        self.card_width, self.card_height = card_size

        self.pile_type = pile_type
        if self.pile_type == 'tableau':
            self.fanned = True
            self.order = self.Order(foundation='king', rank=-1, color_suit='alt-color')
            self.height = 500
        elif self.pile_type == 'foundation':
            self.fanned = False
            self.order = self.Order(foundation='ace', rank=1, color_suit='same-suit')
            self.height = self.card_height
        elif self.pile_type == 'free-cell':
            self.fanned = False
            self.order = self.Order(foundation=None, rank=None, color_suit=None)
            self.height = self.card_height

        self.max_card_spacing = 60
        self.min_card_spacing = 10
        self.card_spacing = self.max_card_spacing
        self.bottom_margin = 10

        self.cards = cards
        self.x = x
        self.y = y

        self.update()

    def __str__(self):
        """
        Returns a string representation of the pile, including its type and cards.
        """
        card_list = ', '.join([f"{card.rank} of {card.suit}" for card in self.cards])
        return f"Pile(type={self.pile_type}, cards=[{card_list}])"

    def __repr__(self):
        """
        Returns a detailed string representation of the pile for debugging.
        """
        return self.__str__()
    
    def __len__(self):
        return len(self.cards)

    @property
    def pile_bottom(self):
        return self.cards[-1].position[1] + self.card_height
    
    def is_foundation(self):
        return self.pile_type == "foundation"

    def update_positions(self):
        if len(self.cards) != 0:
            for index, card in enumerate(self.cards):
                if self.fanned == True:
                    card.position = (self.x, self.y + (index * self.card_spacing))
                else:
                    card.position = (self.x, self.y)

    def update(self):
        self.update_positions()

    def fit_pile_to_screen(self, display_height):

        screen_bottom = display_height - self.bottom_margin

        if len(self.cards) > 0:
            if self.pile_bottom > screen_bottom:
                while self.card_spacing > self.min_card_spacing:
                    if self.pile_bottom < screen_bottom:
                        break
                    else:
                        self.card_spacing -= 1 / len(self.cards)
                        self.update_positions()
            elif self.pile_bottom < screen_bottom:
                while self.card_spacing < self.max_card_spacing:
                    if self.pile_bottom > screen_bottom:
                        break
                    else:
                        self.card_spacing += 1 / len(self.cards)
                        self.update_positions()

            self.card_spacing = round(self.card_spacing)

    def selected(self, mouse_position, piles):
        selection = False
        selected_cards = []
        deselect_pile = False

        for index, card in enumerate(self.cards):
                card_clicked = card.check_if_clicked(mouse_position)
                if card_clicked:
                    selection = True
                    selected_cards = self.cards[index:]

        return selection, selected_cards, deselect_pile

    def valid_transfer(self, pile_to_transfer_to, selected_cards, ranks):
        if not self.is_valid_moving_pile(selected_cards, ranks):
            return False
        
        if len(pile_to_transfer_to.cards) != 0:
            bottom_card = pile_to_transfer_to.cards[-1]
        else:
            bottom_card = None
        top_card = selected_cards[0]

        valid = True

        if pile_to_transfer_to.pile_type == 'free-cell':
            if bottom_card is not None:
                return False
            else:
                if len(selected_cards) > 1:
                    return False
            return True
        
        if pile_to_transfer_to.pile_type == 'foundation':
            if len(selected_cards) > 1:
                return False
            if len(pile_to_transfer_to.cards) == 0:
                # The foundation pile is empty, only an Ace can be placed
                if top_card.rank != 'ace':
                    return False
            else:
                # The foundation pile has cards, check if the card can be placed on top
                top_foundation_card = pile_to_transfer_to.cards[-1]
                if top_card.suit != top_foundation_card.suit:
                    return False  # The suit must match
                if ranks.index(top_card.rank) != ranks.index(top_foundation_card.rank) + 1:
                    return False 
            return True

        # if a pile is empty only certain cards can be placed there
        if bottom_card is None :
            if pile_to_transfer_to.pile_type == 'tableau':
                valid = True
        else:
            # cards must be ordered depending on the pile they are in
                rank_index = ranks.index(bottom_card.rank)
                target_index = rank_index + pile_to_transfer_to.order.rank
                if target_index < 0 or target_index >= len(ranks):
                    valid = False
                elif top_card.rank != ranks[target_index]:
                    valid = False
                if top_card.color == bottom_card.color:
                    valid = False

        return valid
    
    def is_valid_moving_pile(self, cards, ranks):
        """
        Checks if the given list of cards forms a valid moving pile.

        Args:
            cards (list): A list of Card objects to validate.
            ranks (list): A list of card ranks in order (e.g., ['ace', '2', ..., 'king']).

        Returns:
            bool: True if the cards form a valid moving pile, False otherwise.
        """
        
        if self.cards[-len(cards):] != cards:
            return False

        for i in range(len(cards) - 1):
            card1, card2 = cards[i], cards[i + 1]

            # Check descending order based on rank
            if ranks.index(card1.rank) != ranks.index(card2.rank) + 1:
                return False

            # Check alternating colors (assuming card has 'color' attribute)
            if card1.color == card2.color:
                return False

        return True


    def transfer_cards(self, selected_cards, pile_to_transfer_to, ranks):
        if self.valid_transfer(pile_to_transfer_to, selected_cards, ranks):
            for card in selected_cards:
                pile_to_transfer_to.cards.append(card)
                # Find and remove the card from self.cards by matching its unique attribute
                self.cards = [c for c in self.cards if c.name_of_image != card.name_of_image]
            return True
        else:
            return False

    def selection_rect(self, card):
        padding = 10
        rect_x = card.x - padding
        rect_y = card.y - padding + 40

        card_index = self.cards.index(card)
        card_negative_index = card_index - len(self.cards) - 1
        distance_from_top = abs(card_negative_index)

        rect_w = card.card_size[0] + (padding * 2)
        rect_h = (self.card_spacing * (distance_from_top - 2)) + self.card_height + (padding * 2)

        return [rect_x, rect_y, rect_w, rect_h]

    def check_if_clicked(self, mouse_position):
        mouse_x, mouse_y = mouse_position

        if self.x < mouse_x < self.x + self.card_width and self.y < mouse_y < self.y + self.height:
            return True
        else:
            return False
