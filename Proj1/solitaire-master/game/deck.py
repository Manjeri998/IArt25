from copy import copy, deepcopy
import os
import random
import pygame
from itertools import count
from pile import Pile
from card import Card


# the deck class should handle the clicking of the cards
class Deck:
    def __lt__(self, other):
        return id(self) < id(other)
    

    def __init__(self, piles=[], card_images={}, card_size=(100, 150)):
        # cards list is only used when starting/restarting a game
        self.cards = []

        self.suits = ['clubs', 'diamonds', 'hearts', 'spades']
        self.ranks = ['ace', '2', '3', '4', '5', '6', '7', '8',
                      '9', '10', 'jack', 'queen', 'king']

        self.selection = False
        self.selected_cards = []
        self.selected_pile = None
        self.selection_rect = None
        self.selection_color = (255, 255, 0)
        self.empty_color = (100, 100, 200)
        self.empty_color2 = (100, 100, 230)

        # these attributes can be modified when undoing/redoing
        self.piles = piles
        self.card_images = card_images
        self.card_size = card_size

        name_of_image = os.path.join('resources', 'card_back.png')
        self.card_back_image = pygame.image.load(name_of_image)
        self.card_back = self.resize_card_back()
    
    def __str__(self):
        """
        Returns a string representation of the deck's state.
        Each pile and its cards are displayed.
        """
        result = []
        for i, pile in enumerate(self.piles):
            pile_cards = [card.name_of_image for card in pile.cards]
            result.append(f"Pile {i}: {pile_cards}")
        return "\n".join(result)

    def resize_card_back(self):
        return pygame.transform.scale(self.card_back_image, self.card_size)

    def clone(self):
        """
        Creates a deep copy of the current deck, ensuring that cards are properly cloned.
        """
        new_piles = deepcopy(self.piles)  # Deep copy piles

        # Ensure each card in each pile is a new instance
        for pile in new_piles:
            pile.cards = [Card(card.name_of_image, card.card_size, card.rank, card.suit, card.face_up) for card in pile.cards]

        new_deck = Deck(
            piles=new_piles,
            card_images=self.card_images,  # Pass the existing card images
            card_size=self.card_size
        )
        return new_deck
    
    def resize_card_images(self):
        for name_of_image, card_image in self.card_images.items():
            self.card_images[name_of_image] = pygame.transform.scale(card_image, self.card_size)

    def load_cards(self):
        for suit in self.suits:
            for rank in self.ranks:
                name_of_image = os.path.join('resources', 'cards', '{}_of_{}.png'.format(rank, suit))
                self.card_images[name_of_image] = pygame.image.load(name_of_image)
                self.cards.append(Card(name_of_image, self.card_size, rank, suit))
        self.resize_card_images()

    def load_piles(self, display_size):
        display_width, display_height = display_size
        pile_spacing = 25

        start_x = 50
        start_y = self.card_size[1] + 100

        foundation_x_step = self.card_size[0] + pile_spacing
        foundation_start_x = 50

        tableau1 = Pile(self.cards[0:7], start_x, start_y, self.card_size)
        tableau2 = Pile(self.cards[7:14], start_x + self.card_size[0] + pile_spacing, start_y, self.card_size)
        tableau3 = Pile(self.cards[14:21], start_x + self.card_size[0]*2 + pile_spacing*2, start_y, self.card_size)
        tableau4 = Pile(self.cards[21:28], start_x + self.card_size[0]*3 + pile_spacing*3, start_y, self.card_size)
        tableau5 = Pile(self.cards[28:34], start_x + self.card_size[0]*4 + pile_spacing*4, start_y, self.card_size)
        tableau6 = Pile(self.cards[34:40], start_x + self.card_size[0]*5 + pile_spacing*5, start_y, self.card_size)
        tableau7 = Pile(self.cards[40:46], start_x + self.card_size[0]*6 + pile_spacing*6, start_y, self.card_size)
        tableau8 = Pile(self.cards[46:52], start_x + self.card_size[0]*7 + pile_spacing*7, start_y, self.card_size)
        

        foundation1 = Pile([], foundation_start_x, pile_spacing, self.card_size, pile_type="free-cell")
        foundation2 = Pile([], foundation_start_x + foundation_x_step, pile_spacing, self.card_size, pile_type="free-cell")
        foundation3 = Pile([], foundation_start_x + foundation_x_step*2, pile_spacing, self.card_size, pile_type="free-cell")
        foundation4 = Pile([], foundation_start_x + foundation_x_step*3, pile_spacing, self.card_size, pile_type="free-cell")
        foundation5 = Pile([], foundation_start_x + foundation_x_step*4, pile_spacing, self.card_size, pile_type="foundation")
        foundation6 = Pile([], foundation_start_x + foundation_x_step*5, pile_spacing, self.card_size, pile_type="foundation")
        foundation7 = Pile([], foundation_start_x + foundation_x_step*6, pile_spacing, self.card_size, pile_type="foundation")
        foundation8 = Pile([], foundation_start_x + foundation_x_step*7, pile_spacing, self.card_size, pile_type="foundation")

        self.piles = [tableau1, tableau2, tableau3, tableau4, tableau5, tableau6, tableau7, tableau8,
                      foundation1, foundation2, foundation3, foundation4, foundation5, foundation6, foundation7, foundation8]

    def shuffle_cards(self):
        random.shuffle(self.cards)
    
    def get_possible_moves(deck):
        """
        Retorna uma lista de estados possíveis do baralho após realizar movimentos válidos.
        """
        valid_moves = []
        
        for source_pile in deck.piles:  # Itera sobre todas as pilhas como possíveis fontes de movimento
            if not source_pile.cards:  # Se a pilha estiver vazia, não há movimento possível
                continue
            
            for dest_pile in deck.piles:  # Itera sobre todas as pilhas como possíveis destinos
                if source_pile == dest_pile:  # Evita mover para a mesma pilha
                    continue
                
                # Tenta mover diferentes quantidades de cartas do topo da pilha
                for i in range(len(source_pile.cards)):
                    selected_cards = source_pile.cards[i:]  # Seleciona um subconjunto das cartas
                    if source_pile.valid_transfer(dest_pile, selected_cards, deck.ranks):
                        new_deck = deck.clone()  # Clona o baralho para um novo estado
                        new_source_pile = new_deck.piles[deck.piles.index(source_pile)]
                        new_dest_pile = new_deck.piles[deck.piles.index(dest_pile)]
                        
                        new_source_pile.transfer_cards(selected_cards, new_dest_pile, deck.ranks)
                        valid_moves.append(new_deck)
        
        return valid_moves



    def deselect(self):
        self.selection = False
        self.selected_pile = None
        self.selected_cards = []

    def which_pile_clicked(self, mouse_position):
        for pile in self.piles:
                if pile.check_if_clicked(mouse_position):
                    return pile
        else:
            return None

    def update(self, piles_to_update, display_height):
        for pile in self.piles:
            pile.update()

        if piles_to_update != None:
            for pile in piles_to_update:
                pile.fit_pile_to_screen(display_height)
                pile.update_positions()

    def handle_click(self, mouse_position):
        piles_to_update = None
        valid_move = False

        if self.selection == False:
            # the player selects card/s
            self.selected_pile = self.which_pile_clicked(mouse_position)

            if self.selected_pile != None:
                if self.selected_pile.pile_type == 'stock':
                    valid_move = True

            if self.selected_pile != None:
                self.selection, self.selected_cards, deselect_pile = self.selected_pile.selected(mouse_position, self.piles)
                if deselect_pile:
                    self.deselect()
                else:
                    if len(self.selected_cards) != 0:
                        self.selection_rect = self.selected_pile.selection_rect(self.selected_cards[0])
        else:
            pile_to_transfer_to = self.which_pile_clicked(mouse_position)
            if self.selected_pile != None and pile_to_transfer_to != None:
                valid_move = self.selected_pile.transfer_cards(self.selected_cards, pile_to_transfer_to, self.ranks)
                piles_to_update = self.selected_pile, pile_to_transfer_to
            else:
                piles_to_update = None

            self.deselect()
        
        return piles_to_update, valid_move

    def handle_right_click(self, mouse_position):
        self.deselect()

    def check_for_win(self):
        foundation_piles = [pile for pile in self.piles if pile.pile_type == 'foundation']
        for pile in foundation_piles:
            if len(pile.cards) < 13:
                return False
        else:
            return True

    def display(self, game_display):
        for pile in self.piles:
            if pile.pile_type == 'foundation' and len(pile.cards) == 0:
                pygame.draw.rect(game_display, self.empty_color, [pile.x, pile.y, pile.card_width, pile.card_height])
            if pile.pile_type == 'free-cell' and len(pile.cards) == 0:
                pygame.draw.rect(game_display, self.empty_color2, [pile.x, pile.y, pile.card_width, pile.card_height])
            for card in pile.cards:
                if self.selection and self.selection_rect != None and card == self.selected_cards[0]:
                    pygame.draw.rect(game_display, self.selection_color, self.selection_rect)

                img = self.card_images[card.name_of_image]

                game_display.blit(img, [card.x, card.y])

    def make_move(self, move):
        """
        Applies the given move to the deck.
        A move is represented as a tuple containing the source pile, target pile, and the selected cards.
        """
        source_pile, target_pile, selected_cards = move

        source_index = next(i for i, p in enumerate(self.piles) if p.pile_type == source_pile.pile_type and len(p.cards) == len(source_pile.cards))
        target_index = next(i for i, p in enumerate(self.piles) if p.pile_type == target_pile.pile_type and len(p.cards) == len(target_pile.cards))

        self.piles[source_index].transfer_cards(selected_cards, self.piles[target_index], self.ranks)

    def is_valid_sequence(self, cards):
        """
        Checks if the given list of cards is in a valid order to be moved.
        Example rules: Descending order, alternating colors.
        """
        if not cards or len(cards) == 1:
            return True  # A single card is always valid

        for i in range(len(cards) - 1):
            card1, card2 = cards[i], cards[i + 1]

            # Check descending order based on rank
            if self.ranks.index(card1.rank) != self.ranks.index(card2.rank) + 1:
                return False

            # Check alternating colors (assuming card has 'color' attribute)
            if card1.color == card2.color:
                return False

        return True
    
    def can_move_to_foundation(self, card):
        """
        Checks if the given card can be moved to any foundation pile.
        """
        for pile in self.piles:
            if pile.pile_type == "foundation":
                # If the foundation pile is empty, only an Ace can be placed
                if not pile.cards and card.rank == "ace":
                    return True
                # If the foundation pile has cards, check if the card can be placed on top
                elif pile.cards:
                    top_card = pile.cards[-1]
                    if top_card.suit == card.suit and self.ranks.index(card.rank) == self.ranks.index(top_card.rank) + 1:
                        return True
        return False


class CompressedDeck:
    _ids = count(0)

    def __init__(self, piles):
        self.id = next(self._ids)
        self.piles = piles

    def decompress(self, card_images, card_size):
        return Deck(self.piles, card_images, card_size)

    def __str__(self):
        return str([card for card in self.piles if card.face_up == True])

    def __repr__(self):
        return "CompressedDeck #{}".format(self.id)
