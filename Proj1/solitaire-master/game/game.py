import pygame
from deck import Deck
from ui import Text, Button, RadioGroup, Radio, Checkbox
import settings_manager, history_manager
import time
from queue import PriorityQueue


white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 200, 0)
blue = (50, 50, 190)
red = (190, 50, 50)
grey = (100, 100, 100)

al_deck = Deck()

is_a_star = False

display_dimensions = (1100, 800)

pygame.init()

game_display = pygame.display.set_mode(display_dimensions)

pygame.display.set_caption('Solitare')

clock = pygame.time.Clock()
FPS = 10


def quit_game():
    pygame.quit()
    quit()

def win_screen():
    quit_button = Button(display_dimensions, "Quit", (250, 0), (200, 100), red, text_color=white, text_size=25, action="quit")
    play_again_button = Button(display_dimensions, "Play Again", (0, 0), (200, 100), blue, text_color=white, text_size=25, action="play_again")
    start_menu_button = Button(display_dimensions, "Start Menu", (-250, 0), (200, 100), green, text_color=white, text_size=25, action="start_menu")
    buttons = [quit_button, play_again_button, start_menu_button]

    win_text = Text(display_dimensions, (0, -200), "You Win!!!", 60, black)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if event.button == 1:
                        for button in buttons:
                            if button.check_if_clicked(mouse_pos):
                                if button.action == "quit":
                                    quit_game()
                                elif button.action == "play_again":
                                    game_loop()
                                elif button.action == "start_menu":
                                    start_menu()
                                else:
                                    print("Button action: {} does not exist".format(button.action))

        game_display.fill(white)

        for button in buttons:
            button.display(game_display, pygame.mouse.get_pos())

        win_text.display(game_display)

        pygame.display.update()
        clock.tick(FPS)

def game_loop():
    undo_button = Button(display_dimensions, "Undo", (10, 10), (30, 30), grey, centered=False, text_size=11, action="undo")
    pause_button = Button(display_dimensions, "Pause", (display_dimensions[0]-50, 10), (40, 30), grey, centered=False, text_size=10, action="pause")
    astar_button = Button(display_dimensions, "A*", (10, 60), (30, 30), grey, centered=False, text_size=10, action="astar")
    next_button = Button(display_dimensions, "Next", (10, 110), (30, 30), grey, centered=False, text_size=10, action="next")
    buttons = [undo_button, pause_button, astar_button, next_button ]
    a_star_states = []

    deck = Deck()
    deck.load_cards()
    deck.shuffle_cards()
    deck.load_piles(display_dimensions)

    hm = history_manager.HistoryManager(deck)

    while True:
        if deck.check_for_win():
            win_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_loop()
                elif event.key == pygame.K_w:
                    win_screen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:
                    piles_to_update, valid_move = deck.handle_click(mouse_pos)
                    print(piles_to_update)
                    deck.update(piles_to_update, display_dimensions[1])
                    if valid_move:
                        hm.valid_move_made(deck)

                    for button in buttons:
                        if button.check_if_clicked(mouse_pos):
                            if button.action == "undo":
                                deck = hm.undo(deck)
                            if button.action == "astar":
                                a_star_states = a_star_solve(deck)
                                print(a_star_states)
                            if button.action == "next":
                                print(deck)
                                deck = a_star_states.pop(0)

                if event.button == 3:
                    deck.handle_right_click(mouse_pos)

        game_display.fill(blue)

        for button in buttons:
            button.display(game_display, pygame.mouse.get_pos())

        deck.display(game_display)
        pygame.display.update()
        clock.tick(FPS)


def options_menu():
    settings = settings_manager.load_settings()

    title_text = Text(display_dimensions, (0, -370), "Options", 40, black)
    about_text = Text(display_dimensions, (0, 350), "Made in 2017 by Aaron Buckles", 14, black)

    back_button = Button(display_dimensions, "Back", (10, 25), (75, 25), red, centered=False, text_color=white, text_size=14, action="back")
    buttons = [back_button]

    draw_three_checkbox = Checkbox(display_dimensions, (10, 100), centered=False, checked=settings['draw_three'])
    draw_three_label = Text(display_dimensions, (40, 100), "Draw three cards from deck", 14, black, centered=False)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:
                    for button in buttons:
                        if button.check_if_clicked(mouse_pos):
                            if button.action == "back":
                                settings_manager.save_settings({'draw_three': draw_three_checkbox.checked})
                                start_menu()
                            else:
                                print("Button action: {} does not exist".format(button.action))

                    draw_three_checkbox.check_if_clicked(mouse_pos)

        game_display.fill(white)

        title_text.display(game_display)
        about_text.display(game_display)

        draw_three_label.display(game_display)
        draw_three_checkbox.display(game_display)

        for button in buttons:
            button.display(game_display, pygame.mouse.get_pos())

        pygame.display.update()
        clock.tick(FPS)


def start_menu():
    title = Text(display_dimensions, (0, -100), "Solitaire", 50, black)

    play_button = Button(display_dimensions, "Play", (0, 0), (100, 50), blue, text_color=white, text_size=26, action="start_game")
    quit_button = Button(display_dimensions, "Quit", (200, 0), (100, 50), red, text_color=white, action="quit")
    options_button = Button(display_dimensions, "Options", (-200, 0), (100, 50), grey, text_color=white, action="options")
    buttons = [play_button, quit_button, options_button]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:
                    for button in buttons:
                        if button.check_if_clicked(mouse_pos):
                            if button.action == "start_game":
                                game_loop()
                            elif button.action == "quit":
                                quit_game()
                            elif button.action == "options":
                                options_menu()
                                pass
                            else:
                                print("Button action: {} does not exist".format(button.action))

        game_display.fill(white)

        title.display(game_display)

        for button in buttons:
            button.display(game_display, pygame.mouse.get_pos())

        pygame.display.update()
        clock.tick(FPS)

def a_star_solve(deck):
    """
    Resolve o jogo de Paciência usando o algoritmo A* e exibe o estado atual no jogo.
    """
    is_a_star = True
    open_set = PriorityQueue()
    initial_state = deck
    open_set.put((0, initial_state))  # Use the hashable state
    came_from = {}
    g_score = {initial_state: 0}
    f_score = {initial_state: heuristic(deck)}
    visited_states = set()  # Track visited states
    start_time = time.time()
    best_state = initial_state

    while not open_set.empty():
        _, current_deck = open_set.get()

        if (time.time() - start_time) > 10:
            print("Time limit reached")
            return reconstruct_path(came_from, best_state)

        # Skip if the state has already been visited
        if current_deck in visited_states:
            continue
        visited_states.add(current_deck)

        print("Current state: {}".format(current_deck))
        # Display the current state of the dec

        if current_deck.check_for_win():
            reconstruct_path(came_from, current_deck)
            return True

        for neighbor in get_valid_moves(current_deck):
            print(neighbor)
            neighbor_deck = current_deck.clone()
            neighbor_deck.make_move(neighbor)
            print("Neighbor deck: {}".format(neighbor_deck))
            neighbor_state = neighbor_deck

            if neighbor_state in visited_states:
                continue

            temp_g_score = g_score[current_deck] + 1

            if neighbor_state not in g_score or temp_g_score < g_score[neighbor_state]:
                came_from[neighbor_state] = current_deck
                g_score[neighbor_state] = temp_g_score
                f_score[neighbor_state] = temp_g_score + heuristic(neighbor_deck)
                open_set.put((f_score[neighbor_state], neighbor_state))
                best_state = neighbor_state

    return []  # Se não encontrar solução

def heuristic(deck):
    """
    Heurística simples: conta o número de cartas que ainda precisam ser movidas para as bases.
    """
    return sum(len(pile) for pile in deck.piles if not pile.is_foundation())

def get_valid_moves(self):
    """
    Returns a list of valid moves as tuples (source_pile, target_pile, selected_cards).
    Ensures selected cards are valid, in order, and on top of the pile.
    """
    valid_moves = []

    for source_pile in self.piles:
        if not source_pile.cards:
            continue  # Skip empty piles

        for target_pile in self.piles:
            if source_pile == target_pile:
                continue  # Skip moving within the same pile

            for i in range(len(source_pile.cards)):
                selected_cards = source_pile.cards[i:]

                # Ensure the selected cards are in valid order
                if not self.is_valid_sequence(selected_cards):
                    continue

                # Check if the move is valid based on game rules
                if source_pile.valid_transfer(target_pile, selected_cards, self.ranks):
                    valid_moves.append((source_pile, target_pile, selected_cards))

    return valid_moves

def reconstruct_path(came_from, current):
    """
    Reconstrói e imprime o caminho da solução.
    """
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    
    return path; # Aqui poderia ser uma renderização do estado

start_menu()
