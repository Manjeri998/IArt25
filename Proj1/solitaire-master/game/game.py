import pygame
from deck import Deck
from utils.ui import Text, Button, RadioGroup, Radio, Checkbox
from utils import settings_manager, history_manager
from searchAlgorithms import ASTAR  # Import the ASTAR class
import time
import os
from queue import PriorityQueue
import tkinter as tk
from tkinter import filedialog
import re


white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 200, 0)
blue = (50, 50, 190)
red = (190, 50, 50)
grey = (100, 100, 100)

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
    button_width = 100
    button_height = 30
    spacing = 10
    start_x = 10
    start_y = 10

    buttons = [
        Button(display_dimensions, "Undo", (start_x, start_y), (button_width, button_height), grey, centered=False,
               text_size=11, action="undo"),
        Button(display_dimensions, "A*", (start_x + (button_width + 4*spacing) * 2, start_y),
               (button_width, button_height), grey, centered=False, text_size=10, action="astar"),
        Button(display_dimensions, "Next", (start_x + (button_width + 4*spacing) * 3, start_y),
               (button_width, button_height), grey, centered=False, text_size=10, action="next"),
        Button(display_dimensions, "Load State", (start_x + (button_width + 6*spacing) * 4, start_y),
               (button_width, button_height), grey, centered=False, text_size=10, action="load_state"),
        Button(display_dimensions, "New Deck", (start_x + (button_width + 6*spacing) * 5, start_y),
               (button_width, button_height), grey, centered=False, text_size=10, action="new_deck"),
        Button(display_dimensions, "Save State", (start_x + (button_width + 6*spacing) * 6, start_y),
               (button_width, button_height), grey, centered=False, text_size=10, action="save_state")
    ]

    a_star_states = []
    deck = Deck()
    deck = Deck.load_deck_from_file("states/deck10.txt")
    deck.update(None, display_dimensions[1])

    hm = history_manager.HistoryManager(deck)

    def open_load_state_dialog():
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(initialdir="states", title="Select a state file",
                                               filetypes=[("Text files", "*.txt")])
        if file_path:
            return file_path
        return None

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
                    deck.update(piles_to_update, display_dimensions[1])
                    if valid_move:
                        hm.valid_move_made(deck)

                    for button in buttons:
                        if button.check_if_clicked(mouse_pos):
                            if button.action == "undo":
                                deck = hm.undo(deck)
                            if button.action == "astar":
                                astar_solver = ASTAR()
                                score = [None] * 6
                                astar_solver.run(deck, score)
                                if score[0]:  
                                    a_star_states = score[0]  
                                    print("A* solution path loaded.")
                            if button.action == "next":

                                deck = a_star_states.pop(0) 
                                deck.update(None, display_dimensions[1])
                            if button.action == "load_state":
                                selected_file = open_load_state_dialog()
                                if selected_file:
                                    print(selected_file)
                                    deck = Deck.load_deck_from_file(selected_file)
                                    deck.update(None, display_dimensions[1])
                            if button.action == "new_deck":
                                deck = Deck()
                                deck.add_all_cards()
                                deck.shuffle_cards()
                                deck.load_piles(display_dimensions)
                                deck.update(None, display_dimensions[1])
                                hm = history_manager.HistoryManager(deck)
                            if button.action == "save_state":
                                save_deck_to_file(deck)

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

def save_deck_to_file(deck):
    """
    Saves the current state of the deck to a new file in the 'states' folder.
    """
    states_folder = "states"
    if not os.path.exists(states_folder):
        os.makedirs(states_folder)
    # Find all existing deck files and extract their numbers
    existing_files = [f for f in os.listdir(states_folder) if re.match(r"deck(\d+)\.txt$", f)]
    existing_numbers = sorted([int(re.search(r"deck(\d+)\.txt$", f).group(1)) for f in existing_files])

    # Find the next available number
    next_index = 1
    for num in existing_numbers:
        if num == next_index:
            next_index += 1
        else:
            break  # Found a gap, use this number
    file_path = os.path.join(states_folder, f"deck{next_index}.txt")

    with open(file_path, "w") as file:
        for pile in deck.piles:
            pile_type = pile.pile_type
            cards = ";".join([f"{card.rank}_of_{card.suit}" for card in pile.cards])
            file.write(f"{pile_type};{cards}\n")

    print(f"Deck saved to {file_path}")

start_menu()