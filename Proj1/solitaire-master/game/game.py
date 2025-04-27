import pygame
from deck import Deck
import history_manager
from ui import Text, Button, Checkbox
from searchAlgorithms import ASTAR, BFS, Greedy, DFS
import os
import math
import tkinter as tk
from tkinter import filedialog
import re
import random

white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 200, 0)
blue = (50, 50, 190)
red = (190, 50, 50)
grey = (100, 100, 100)
dark_green = (0, 120, 0)
light_blue = (100, 150, 255)
purple = (150, 50, 200)
gold = (212, 175, 55)

display_dimensions = (1100, 800)

pygame.init()

game_display = pygame.display.set_mode(display_dimensions)

pygame.display.set_caption('FreeCell')

clock = pygame.time.Clock()
FPS = 10

try:
    background_image = pygame.image.load(os.path.join("assets", "card_background.jpg"))
    background_image = pygame.transform.scale(background_image, display_dimensions)
except:
    background_image = None

def quit_game():
    pygame.quit()
    quit()


def win_screen():
    quit_button = Button(display_dimensions, "Quit", (250, 0), (200, 100), red, text_color=white, text_size=25,
                         action="quit")
    play_again_button = Button(display_dimensions, "Play Again", (0, 0), (200, 100), blue, text_color=white,
                               text_size=25, action="play_again")
    start_menu_button = Button(display_dimensions, "Start Menu", (-250, 0), (200, 100), green, text_color=white,
                               text_size=25, action="start_menu")
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
                                return "play_again"
                            elif button.action == "start_menu":
                                return "start_menu"
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
        Button(display_dimensions, "DFS", (start_x + (button_width + 4 * spacing), start_y),
               (button_width - 40, button_height), grey, centered=False, text_size=10, action="dfs"),
        Button(display_dimensions, "A*", (start_x + (button_width + 4 * spacing) * 1.5 + 10, start_y),
               (button_width - 40, button_height), grey, centered=False, text_size=10, action="astar"),
        Button(display_dimensions, "BFS", (start_x + (button_width + 4 * spacing) * 2.5 - 50, start_y),
               (button_width - 30, button_height), grey, centered=False, text_size=10, action="bfs"),
        Button(display_dimensions, "Greedy", (start_x + (button_width + 4 * spacing) * 3.5 - 100, start_y),
               (button_width - 30, button_height), grey, centered=False, text_size=10, action="greedy"),
        Button(display_dimensions, "Next", (start_x + (button_width + 4 * spacing) * 3.5, start_y),
               (button_width, button_height), grey, centered=False, text_size=10, action="next"),
        Button(display_dimensions, "Load State", (start_x + (button_width + 6 * spacing) * 4, start_y),
               (button_width, button_height), grey, centered=False, text_size=10, action="load_state"),
        Button(display_dimensions, "New Deck", (start_x + (button_width + 6 * spacing) * 5, start_y),
               (button_width, button_height), grey, centered=False, text_size=10, action="new_deck"),
        Button(display_dimensions, "Save State", (start_x + (button_width + 6*spacing) * 6, start_y),
               (button_width, button_height), grey, centered=False, text_size=10, action="save_state"),
        Button(display_dimensions, "Back to Menu", (10, display_dimensions[1] - 40), 
               (120, button_height), red, centered=False, text_size=10, action="back_to_menu"),
        Button(display_dimensions, "Quit Game", (display_dimensions[0] - 110, display_dimensions[1] - 40), 
               (100, button_height), red, centered=False, text_size=10, action="quit"),
    ]

    a_star_states = []
    deck = Deck.load_deck_from_file("states/deck11.txt")
    deck.update(None, display_dimensions[1])

    hm = history_manager.HistoryManager(deck.clone())

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
            result = win_screen()
            if result == "play_again":
                deck = Deck.load_deck_from_file("states/deck8.txt")
                deck.update(None, display_dimensions[1])
                hm = history_manager.HistoryManager(deck.clone())
                a_star_states = []
                continue
            elif result == "start_menu":
                return
            
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
                    if valid_move:
                        deck.update(piles_to_update, display_dimensions[1])
                        hm.valid_move_made(deck.clone())

                    for button in buttons:
                        if button.check_if_clicked(mouse_pos):
                            if button.action == "undo":
                                deck = hm.undo(deck)
                                deck.update(None, display_dimensions[1])
                            if button.action == "astar":
                                astar_solver = ASTAR()
                                score = [None] * 6
                                astar_solver.run(deck, score)
                                if score[0]:
                                    a_star_states = score[0]
                                    print("A* solution path loaded.")
                            if button.action == "dfs":
                                dfs_solver = DFS()
                                score = [None] * 6
                                dfs_solver.run(deck, score)
                                if score[0]:  
                                    a_star_states = score[0]
                                    a_star_states = score[0]
                                    print("DFS solution path loaded.")
                            if button.action == "bfs":
                                bfs_solver = BFS()
                                score = [None] * 6
                                bfs_solver.run(deck, score)
                                if score[3]:
                                    a_star_states = score[0]
                            if button.action == "greedy":
                                greedy_solver = Greedy()
                                score = [None] * 6
                                greedy_solver.run(deck, score)
                                if score[0]:
                                    a_star_states = score[0]
                            if button.action == "next":
                                if a_star_states and len(a_star_states) > 0:
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
                            if button.action == "save_state":
                                save_deck_to_file(deck)
                            if button.action == "back_to_menu":
                                start_menu()
                            if button.action == "quit":
                                quit_game()

                if event.button == 3:
                    deck.handle_right_click(mouse_pos)

        dark_green = (41, 71, 38)
        game_display.fill(dark_green)

        for button in buttons:
            button.display(game_display, pygame.mouse.get_pos())

        deck.display(game_display)
        pygame.display.update()
        clock.tick(FPS)

def start_menu():
    title = Text(display_dimensions, (0, -100), "Solitaire", 50, black)

    play_button = Button(display_dimensions, "Play", (0, 0), (100, 50), blue, text_color=white, text_size=26,
                         action="start_game")
    quit_button = Button(display_dimensions, "Quit", (200, 0), (100, 50), red, text_color=white, action="quit")
    buttons = [play_button, quit_button]


def tutorial_screen():
    """Display a tutorial screen with game instructions"""
    title_text = Text(display_dimensions, (0, -350), "How to Play FreeCell", 40, black)
    
    instructions = [
        "1. The goal is to move all cards to the foundation piles (top right).",
        "2. Foundation piles are built up by suit from Ace to King.",
        "3. Tableau piles (main columns) are built down by alternate colors.",
        "4. Free cells (top left) can hold one card each temporarily.",
        "5. You can move a card or a sequence of cards to another tableau pile.",
        "6. Empty tableau piles can be filled with any card or sequence.",
        "7. Use the 'DFS' button to get a hint using Depth-First Search.",
        "8. Use the 'A*' button to get a hint using A* algorithm.",
        "9. After using DFS or A*, press 'Next' to follow the solution.",
        "10. Use 'Undo' to revert your last move.",
        "11. 'Save State' and 'Load State' let you save and resume games."
    ]
    
    instruction_texts = []
    for i, instruction in enumerate(instructions):
        y_pos = -280 + i * 40
        instruction_texts.append(Text(display_dimensions, (0, y_pos), instruction, 18, black))
    
    back_button = Button(display_dimensions, "Back", (10, 25), (75, 25), red, centered=False, text_color=white, text_size=14, action="back")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:
                    if back_button.check_if_clicked(mouse_pos):
                        return
        
        game_display.fill(white)
        
        title_text.display(game_display)
        for text in instruction_texts:
            text.display(game_display)
        
        back_button.display(game_display, pygame.mouse.get_pos())
        
        pygame.display.update()
        clock.tick(FPS)

def high_scores():
    """Display high scores screen"""
    title_text = Text(display_dimensions, (0, -350), "High Scores", 40, black)
    
    scores = [
        {"name": "Player 1", "score": 1250, "time": "2:45"},
        {"name": "Player 2", "score": 1100, "time": "3:12"},
        {"name": "Player 3", "score": 950, "time": "3:30"},
        {"name": "Player 4", "score": 800, "time": "4:05"},
        {"name": "Player 5", "score": 650, "time": "4:22"}
    ]
    
    score_texts = []
    for i, score in enumerate(scores):
        y_pos = -250 + i * 50
        text = f"{i+1}. {score['name']} - {score['score']} points - {score['time']}"
        score_texts.append(Text(display_dimensions, (0, y_pos), text, 24, black))
    
    back_button = Button(display_dimensions, "Back", (10, 25), (75, 25), red, centered=False, text_color=white, text_size=14, action="back")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:
                    if back_button.check_if_clicked(mouse_pos):
                        return
        
        game_display.fill(white)
        
        title_text.display(game_display)
        for text in score_texts:
            text.display(game_display)
        
        back_button.display(game_display, pygame.mouse.get_pos())
        
        pygame.display.update()
        clock.tick(FPS)

def start_menu():
    title = Text(display_dimensions, (0, -200), "FreeCell", 80, black)
    subtitle = Text(display_dimensions, (0, -130), "Card Game", 30, dark_green)
    
    card_back = None
    card_faces = []
    
    possible_card_back_paths = [
        os.path.join("game", "resources", "card_back.png"),
        os.path.join("resources", "card_back.png"),
        os.path.join("assets", "card_back.png"),
        os.path.join("..", "resources", "card_back.png"),
        os.path.join(".", "resources", "card_back.png")
    ]
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for rel_path in possible_card_back_paths:
        try:
            full_path = os.path.join(current_dir, rel_path)
            if os.path.exists(full_path):
                card_back = pygame.image.load(full_path)
                card_back = pygame.transform.scale(card_back, (40, 60))
                break
        except Exception as e:
            continue
    
    if not card_back:
        try:
            temp_deck = Deck()
            if hasattr(temp_deck, 'card_back_image') and temp_deck.card_back_image is not None:
                card_back = pygame.transform.scale(temp_deck.card_back_image, (40, 60))
        except Exception as e:
            print(f"Error loading card back from deck: {e}")
    
    hearts_loaded = False
    try:
        hearts_ranks = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
        for rank in hearts_ranks:
            card_path = os.path.join("assets", f"{rank}_of_hearts.png")
            if os.path.exists(card_path):
                img = pygame.image.load(card_path)
                scaled_img = pygame.transform.scale(img, (40, 60))
                card_faces.append(scaled_img)
                hearts_loaded = True
    except Exception as e:
        print(f"Error loading hearts cards: {e}")
    
    if not hearts_loaded:
        try:
            temp_deck = Deck()
            temp_deck.add_all_cards()
            
            if hasattr(temp_deck, 'card_images') and temp_deck.card_images:
                for card_name, img in temp_deck.card_images.items():
                    if 'hearts' in card_name and img is not None:
                        scaled_img = pygame.transform.scale(img, (40, 60))
                        card_faces.append(scaled_img)
                
                if len(card_faces) < 5:
                    for card_name, img in temp_deck.card_images.items():
                        if img is not None and 'hearts' not in card_name:
                            scaled_img = pygame.transform.scale(img, (40, 60))
                            card_faces.append(scaled_img)
                            if len(card_faces) >= 10:
                                break
        except Exception as e:
            print(f"Error loading cards from deck: {e}")
    
    if len(card_faces) < 5:
        try:
            suits = ['clubs', 'diamonds', 'spades']
            ranks = ['ace', 'king', 'queen', 'jack']
            
            for suit in suits:
                for rank in ranks:
                    if len(card_faces) >= 10:
                        break
                    try:
                        card_path = os.path.join("assets", f"{rank}_of_{suit}.png")
                        if os.path.exists(card_path):
                            img = pygame.image.load(card_path)
                            scaled_img = pygame.transform.scale(img, (40, 60))
                            card_faces.append(scaled_img)
                    except:
                        pass
        except Exception as e:
            print(f"Error loading additional cards: {e}")
    
    
    button_width = 200
    button_height = 60
    button_spacing = 30
    
    # Updated button colors with various green shades
    play_button = Button(display_dimensions, "Play Game", (0, -80), (button_width, button_height), 
                        (0, 150, 50), text_color=white, text_size=30, action="start_game")
    
    tutorial_button = Button(display_dimensions, "Tutorial", (0, -10), 
                            (button_width, button_height), (20, 130, 70), text_color=white, 
                            text_size=30, action="tutorial")
    
    scores_button = Button(display_dimensions, "High Scores", (0, 60), 
                          (button_width, button_height), (40, 110, 90), text_color=white, 
                          text_size=30, action="scores")
    
    options_button = Button(display_dimensions, "Options", (0, 130), 
                           (button_width, button_height), (60, 90, 110), text_color=white, 
                           text_size=30, action="options")
    
    quit_button = Button(display_dimensions, "Quit Game", (0, 200), 
                        (button_width, button_height), red, text_color=white, 
                        text_size=30, action="quit")
    
    buttons = [play_button, tutorial_button, scores_button, options_button, quit_button]
    
    version_text = Text(display_dimensions, (display_dimensions[0] - 100, display_dimensions[1] - 30), 
                        "v1.0", 16, grey, centered=False)
    
    credits_text1 = Text(display_dimensions, (10, display_dimensions[1] - 70), 
                       "By Artur Telo Luís", 14, grey, centered=False)
    credits_text2 = Text(display_dimensions, (10, display_dimensions[1] - 50), 
                       "Gonçalo Joaquim Vale Remelhe", 14, grey, centered=False)
    credits_text3 = Text(display_dimensions, (10, display_dimensions[1] - 30), 
                       "Nuno Pinho Fernandes", 14, grey, centered=False)

    animation_time = 0
    num_cards = 15
    card_positions = [(random.randint(0, display_dimensions[0]), random.randint(-50, 50)) for _ in range(num_cards)]
    card_speeds = [random.randint(4, 8) for _ in range(num_cards)]  # Increased speed range from 2-5 to 4-8
    card_depths = [random.uniform(0.5, 1.0) for _ in range(num_cards)]
    card_rotations = [random.randint(-15, 15) for _ in range(num_cards)]
    
    while True:
        animation_time += 1
        
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
                            elif button.action == "tutorial":
                                tutorial_screen()
                            elif button.action == "scores":
                                high_scores()
                            else:
                                print("Button action: {} does not exist".format(button.action))

        if background_image:
            game_display.blit(background_image, (0, 0))
        else:
            dark_green_rgb = (41, 71, 38)
            
            for y in range(0, display_dimensions[1], 2):
                intensity = 1 - (y / display_dimensions[1])
                
                color_value = (
                    int(dark_green_rgb[0] * intensity),
                    int(dark_green_rgb[1] * intensity),
                    int(dark_green_rgb[2] * intensity)
                )
                
                pygame.draw.rect(game_display, color_value, 
                                [0, y, display_dimensions[0], 2])

        for i in range(len(card_positions)):
            card_positions[i] = (card_positions[i][0], card_positions[i][1] + card_speeds[i])
            
            if card_positions[i][1] > display_dimensions[1]:
                card_positions[i] = (random.randint(0, display_dimensions[0]), -50)
                card_depths[i] = random.uniform(0.5, 1.0)
                card_rotations[i] = random.randint(-15, 15)
                card_speeds[i] = random.randint(2, 5)
            
            use_card_back = True
            if card_faces and len(card_faces) > 0:
                use_card_back = (i % 3 == 0)
            
            if use_card_back and card_back:
                card_surface = pygame.Surface((40, 60), pygame.SRCALPHA)
                card_surface.blit(card_back, (0, 0))
                
                if card_depths[i] < 0.8:
                    blur_strength = int((1 - card_depths[i]) * 10)
                    overlay = pygame.Surface((40, 60), pygame.SRCALPHA)
                    overlay.fill((255, 255, 255, blur_strength * 20))
                    card_surface.blit(overlay, (0, 0))
                
                scale_factor = 0.7 + (0.3 * card_depths[i])
                scaled_width = int(40 * scale_factor)
                scaled_height = int(60 * scale_factor)
                scaled_card = pygame.transform.scale(card_surface, (scaled_width, scaled_height))
                
                rotated_card = pygame.transform.rotate(scaled_card, card_rotations[i])
                
                rot_rect = rotated_card.get_rect(center=(card_positions[i][0] + scaled_width//2, 
                                                        card_positions[i][1] + scaled_height//2))
                
                game_display.blit(rotated_card, rot_rect.topleft)
            elif card_faces and len(card_faces) > 0:
                card_idx = i % len(card_faces)
                card_surface = pygame.Surface((40, 60), pygame.SRCALPHA)
                card_surface.blit(card_faces[card_idx], (0, 0))
                
                if card_depths[i] < 0.8:
                    blur_strength = int((1 - card_depths[i]) * 10)
                    overlay = pygame.Surface((40, 60), pygame.SRCALPHA)
                    overlay.fill((255, 255, 255, blur_strength * 20))
                    card_surface.blit(overlay, (0, 0))
                
                scale_factor = 0.7 + (0.3 * card_depths[i])
                scaled_width = int(40 * scale_factor)
                scaled_height = int(60 * scale_factor)
                scaled_card = pygame.transform.scale(card_surface, (scaled_width, scaled_height))
                
                rotated_card = pygame.transform.rotate(scaled_card, card_rotations[i])
                
                rot_rect = rotated_card.get_rect(center=(card_positions[i][0] + scaled_width//2, 
                                                        card_positions[i][1] + scaled_height//2))
                
                game_display.blit(rotated_card, rot_rect.topleft)
            else:
                scale_factor = 0.7 + (0.3 * card_depths[i])
                rect_width = int(40 * scale_factor)
                rect_height = int(60 * scale_factor)
                
                rect_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
                
                color_value = int(220 * card_depths[i])
                border_value = int(180 * card_depths[i])
                pygame.draw.rect(rect_surface, (color_value, color_value, color_value), 
                               [0, 0, rect_width, rect_height], 0, 3)
                pygame.draw.rect(rect_surface, (border_value, border_value, border_value), 
                               [0, 0, rect_width, rect_height], 1, 3)
                
                rotated_rect = pygame.transform.rotate(rect_surface, card_rotations[i])
                
                rot_rect = rotated_rect.get_rect(center=(card_positions[i][0] + rect_width//2, 
                                                        card_positions[i][1] + rect_height//2))
                
                game_display.blit(rotated_rect, rot_rect.topleft)

        shadow_offset = 3
        shadow_title = Text(display_dimensions, (shadow_offset, -200 + shadow_offset), "FreeCell", 80, grey)
        shadow_title.display(game_display)
        title.display(game_display)
        subtitle.display(game_display)

        current_time = pygame.time.get_ticks()
        for button in buttons:
            mouse_pos = pygame.mouse.get_pos()
            hover = False
            if hasattr(button, 'check_if_clicked'):
                hover = button.check_if_clicked(mouse_pos)
            
            button.display(game_display, mouse_pos)
            
            if hover:
                pulse_value = int(3 * math.sin(current_time / 200))
                if hasattr(button, 'rect'):
                    highlight_rect = button.rect.copy()
                    highlight_rect.inflate_ip(pulse_value * 2, pulse_value * 2)
                    pygame.draw.rect(game_display, gold, highlight_rect, 2)
        
        version_text.display(game_display)
        credits_text1.display(game_display)
        credits_text2.display(game_display)
        credits_text3.display(game_display)

        pygame.display.update()
        clock.tick(FPS)

def save_deck_to_file(deck):
    """
    Saves the current state of the deck to a new file in the 'states' folder.
    """
    states_folder = "states"
    if not os.path.exists(states_folder):
        os.makedirs(states_folder)
    existing_files = [f for f in os.listdir(states_folder) if re.match(r"deck(\d+)\.txt$", f)]
    existing_numbers = sorted([int(re.search(r"deck(\d+)\.txt$", f).group(1)) for f in existing_files])

    next_index = 1
    for num in existing_numbers:
        if num == next_index:
            next_index += 1
        else:
            break
    file_path = os.path.join(states_folder, f"deck{next_index}.txt")

    with open(file_path, "w") as file:
        for pile in deck.piles:
            pile_type = pile.pile_type
            cards = ";".join([f"{card.rank}_of_{card.suit}" for card in pile.cards])
            file.write(f"{pile_type};{cards}\n")

    print(f"Deck saved to {file_path}")
    
start_menu()
