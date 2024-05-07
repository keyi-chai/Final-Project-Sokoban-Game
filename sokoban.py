import pygame
import sys
import os
from pygame.locals import *
 
def move_box(level, i):
    """
    Move the box in the level map.

    Changes the character at position `i` in the list `level` to represent a box.
    If the current position contains a space or the player, it becomes a box ('$').
    If there's a target point, it becomes a box at the target point ('*').

    Args:
    level (list): The level data represented as a list of strings.
    i (int): The index in the list where the box is to be moved.
    """
    if level[i] == '-' or level[i] == '@':
        level[i] = '$'
    else:
        level[i] = '*'


def move_man(level, i):
    """
    Move the player in the level map.

    Changes the character at position `i` in the list `level` to represent the player ('@').
    If the target position is a space or a box, it becomes the player.
    If the target position is a target point, it becomes the player at the target point ('+').

    Args:
    level (list): The level data represented as a list of strings.
    i (int): The index in the list where the player is to be moved.
    """
    if level[i] == '-' or level[i] == '$':
        level[i]='@'
    else:
        level[i]='+'
 

def move_floor(level, i):
    """
    Reset the position after the player has moved.

    Changes the character at position `i` in the list `level` to represent an empty space ('-').
    If the original position was a player or a box, it becomes an empty space.
    If it was a target point, it becomes just a target point ('.').

    Args:
    level (list): The level data represented as a list of strings.
    i (int): The index in the list where the floor is to be reset.
    """
    if level[i] == '@' or level[i] == '$':
        level[i] = '-'
    else:
        level[i] = '.'

 
def get_offset(d, width):
    """
    Get the offset in the level map based on the direction of movement.

    Maps a direction ('l', 'u', 'r', 'd') to an offset value based on the level's width,
    which helps in determining the new position of the player or box after a move.

    Args:
    d (str): The direction of movement ('l', 'left', 'u', 'up', 'r', 'right', 'd', 'down').
    width (int): The width of the level in characters.

    Returns:
    int: The offset value to be added to the current index in the level list.
    """
    offset_map = {'l': -1, 'u': -width, 'r': 1, 'd': width}
    return offset_map[d.lower()]


class Sokoban:
    """
    A class to manage the game state and behavior of the Sokoban game.

    Attributes:
        screen (pygame.Surface): The main screen for the game display.
        level_number (int): The current level number.
        mode (str): The difficulty mode of the game ('easy' or 'hard').
        levels_directory (str): The directory from which to load the level files.
        level (list): The current level map as a list of characters.
        completed_boxes (int): The count of boxes correctly placed on target spots.
        total_boxes (int): The total number of boxes in the current level.
        solution (list): A list recording the moves made.
        push (int): The number of times a box has been pushed.
        game_won (bool): A flag indicating whether the current level has been completed.
        todo (list): A list of moves that can be redone after an undo operation.
    """

    def __init__(self, level_number, screen, mode):
        """
        Initializes the Sokoban game with the given level number, screen, and mode.

        Args:
            level_number (int): The current level number.
            screen (pygame.Surface): The pygame display surface.
            mode (str): The game mode ('easy' or 'hard').
        """
        self.screen = screen
        self.level_number = level_number
        self.mode = mode  # Store the mode selected
        self.levels_directory = mode
        self.load_level_by_number(level_number)

        self.level = list(self.level_string)
        self.completed_boxes = 0
        self.total_boxes = sum(1 for x in self.level if x == '$' or x == '*')
        self.update_completed_boxes()
        self.solution = []
        self.push = 0
        self.game_won = False
        self.todo = []
    
    def load_level_by_number(self, level_number):
        """
        Loads the level by its number from the designated directory.

        Args:
            level_number (int): The number of the level to load.

        Raises:
            FileNotFoundError: If the level file cannot be found.
            ValueError: If the level file is empty.
        """
        level_filename = f"{self.levels_directory}/level{level_number}.txt"
        try:
            with open(level_filename, 'r') as file:
                level_lines = file.read().splitlines()
                if not level_lines:
                    raise ValueError("Level file is empty.")
                level_lines = [line.replace(' ', '-') for line in level_lines]
                max_length = max(len(line) for line in level_lines)
                level_lines = [line.ljust(max_length, '-') for line in level_lines]

                self.w = max_length
                self.h = len(level_lines)
                self.level_string = ''.join(level_lines)
                self.man = self.level_string.index('@') if '@' in self.level_string else None
        except FileNotFoundError:
            print(f"Error: Level file {level_filename} not found.")
            sys.exit()

    def update_completed_boxes(self):
        """
        Updates the count of boxes correctly placed on target spots.
        """
        self.completed_boxes = sum(1 for x in self.level if x == '*')
        
    def draw(self, screen, skin):
        """
        Draws the game level using the provided skin for graphical elements.

        Args:
            screen (pygame.Surface): The surface on which to draw the game elements.
            skin (pygame.Surface): The sprite sheet from which to blit the elements.
        """
        screen.fill(skin.get_at((0, 0)))
        w = skin.get_width() / 4
       
        for i in range(0, self.w):
            for j in range(0, self.h):
                item = self.level[j*self.w + i]               
                # # for position of wall
                if item == '#':
                    screen.blit(skin, (i*w, j*w), (0,2*w,w,w))
                # - for position of empty space   
                elif item == '-':
                    screen.blit(skin, (i*w, j*w), (0,0,w,w))
                # @ for position of man
                elif item == '@':
                    screen.blit(skin, (i*w, j*w), (w,0,w,w))
                # $ for position of box
                elif item == '$':
                    screen.blit(skin, (i*w, j*w), (2*w,0,w,w))
                # . for position of target
                elif item == '.':
                    screen.blit(skin, (i*w, j*w), (0,w,w,w))
                # + for man on a target
                elif item == '+':
                    screen.blit(skin, (i*w, j*w), (w,w,w,w))
                # * for box on a target
                elif item == '*':
                    screen.blit(skin, (i*w, j*w), (2*w,w,w,w))
   
    def move(self, d):
        """
        Processes a move in the specified direction, updates game state, and invalidates the redo stack.

        Args:
            d (str): The direction to move ('l', 'u', 'r', 'd').
        """
        self._move(d)
        # Reset todo list when a move is made
        # Rredo is only validate after an undo
        self.update_completed_boxes()
        self.todo = []
  
    def _move(self, d):
        """
        Performs the actual movement logic based on the direction. It determines if the move involves
        just the player or the player pushing a box, and updates positions accordingly.

        Args:
            d (str): The direction to move ('l', 'u', 'r', 'd').
        """
        h = get_offset(d, self.w)
       
        if self.level[self.man + h] == '-' or self.level[self.man + h] == '.':
            move_man(self.level, self.man + h)
            move_floor(self.level, self.man)
            self.man += h
            self.solution += d
        elif self.level[self.man + h] == '*' or self.level[self.man + h] == '$':
            h2 = h * 2
            # Check if the new position is space or target
            if self.level[self.man + h2] == '-' or self.level[self.man + h2] == '.':
                # Move the box to target
                move_box(self.level, self.man + h2)
                # Move the man to the target
                move_man(self.level, self.man + h)
                # Reset the position of man
                move_floor(self.level, self.man)
                self.man += h
                # Capitalize the move of boxes
                self.solution += d.upper()
                self.push += 1
       
    def undo(self):
        """
        Reverses the last move made, if possible, allowing the user to correct mistakes.
        """
        # Check if a move has been made
        if self.solution.__len__()>0:
            self.todo.append(self.solution[-1])
            self.solution.pop()

            h = get_offset(self.todo[-1],self.w) * -1
           
            # Check whether box has been moved
            if self.todo[-1].islower():
                move_man(self.level, self.man + h)
                move_floor(self.level, self.man)
                self.man += h
            else:
                move_floor(self.level, self.man - h)
                move_box(self.level, self.man)
                move_man(self.level, self.man + h)
                self.man += h
                self.push -= 1
            
    def redo(self):
        """
        Redoes the last undone move, if available.
        """
        # Check if there has been an undo
        if self.todo.__len__()>0:
            self._move(self.todo[-1].lower())
            # Delete the record after a redo
            self.todo.pop()

    def check_victory(self):
        """
        Checks if all boxes are on target spots to determine if the level has been completed.

        Returns:
            bool: True if all boxes are correctly placed, False otherwise.
        """
        return '$' not in self.level

    def display_victory(self, screen):
        """
        Displays a victory message when the level is completed.

        Args:
            screen (pygame.Surface): The display surface to render the victory message on.
        """
        font = pygame.font.Font(None, 36) 
        message_line1 = font.render("Congratulations!", True, (10, 150, 10))
        message_line2 = font.render("Level Completed!", True, (10, 150, 10))

        # Get the center of the screen to correctly position the text
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2

        rect1 = message_line1.get_rect(center=(center_x, center_y - 20))
        rect2 = message_line2.get_rect(center=(center_x, center_y + 20))

        screen.blit(message_line1, rect1)
        screen.blit(message_line2, rect2)

        pygame.display.update()  # Update the display to show the message
        pygame.time.delay(3000) 


    def draw_instructions(self, screen, map_height):
        """
        Draws game instructions on the screen at a position that does not overlap with the map.

        Args:
            screen (pygame.Surface): The surface to draw instructions on.
            map_height (int): The height of the game map, used to determine instruction placement.
        """
        font = pygame.font.Font(None, 28)  # Smaller font for instructions
        instructions = [
            "Move: Arrow keys (Up, Down, Left, Right)",
            "Undo: Backspace",
            "Redo: Space"
        ]
        
        # Calculate the y position based on the map height
        #start_y = map_height + 10 if map_height + 90 < screen.get_height() else map_height - 90
        start_y = screen.get_height() - 100
        
        # Ensure the instructions do not overlap with the map
        for index, instruction in enumerate(instructions):
            text = font.render(instruction, True, (0, 0, 0))
            text_rect = text.get_rect(top=start_y + (30 * index), left=10)
            screen.blit(text, text_rect)


def display_mode_selection(screen, mode, skin):
    """
    Displays the mode selection screen.

    Args:
        screen (pygame.Surface): The display surface where the mode is displayed.
        mode (str): Currently selected mode ('easy' or 'hard').
        skin (pygame.Surface): The skin used for the UI elements' background color.
    """
    screen.fill(skin.get_at((0, 0)))
    font = pygame.font.Font(None, 36)

    # Display the current mode selection
    mode_text = font.render(f"Select Mode: {mode.upper()}", True, (55, 55, 55))
    mode_text_rect = mode_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    screen.blit(mode_text, mode_text_rect)

    font_small = pygame.font.Font(None, 24)
    instructions_text1 = font_small.render("Use LEFT and RIGHT to change mode.", True, (55, 55, 55))
    instructions_text_rect1 = instructions_text1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 20))
    screen.blit(instructions_text1, instructions_text_rect1)
    instructions_text2 = font_small.render("PRESS ENTER to continue.", True, (55, 55, 55))
    instructions_text_rect2 = instructions_text2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    screen.blit(instructions_text2, instructions_text_rect2)

    pygame.display.update()


def display_level_selection(screen, mode, current_level, skin):
    """
    Displays the level selection screen for the specified mode.

    Args:
        screen (pygame.Surface): The display surface where the level is displayed.
        mode (str): The currently selected game mode ('easy' or 'hard').
        current_level (int): The currently selected level number.
        skin (pygame.Surface): The skin used for the UI elements' background color.
    """
    screen.fill(skin.get_at((0, 0)))
    font = pygame.font.Font(None, 36)

    # Display the current level number
    level_text = font.render(f"Select Level ({mode.upper()}): {current_level}", True, (55, 55, 55))
    level_text_rect = level_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    screen.blit(level_text, level_text_rect)

    font_small = pygame.font.Font(None, 24)
    instructions_text1 = font_small.render("Use LEFT and RIGHT to change levels.", True, (55, 55, 55))
    instructions_text_rect1 = instructions_text1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 20))
    screen.blit(instructions_text1, instructions_text_rect1)
    instructions_text2 = font_small.render("PRESS ENTER to start.", True, (55, 55, 55))
    instructions_text_rect2 = instructions_text2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    screen.blit(instructions_text2, instructions_text_rect2)

    pygame.display.update()


def main():
    """
    Initializes and runs the main game loop of the Sokoban game.
    """
    pygame.init()
    screen = pygame.display.set_mode((400, 550))
    skinfilename = os.path.join('icons.png')
    
    # Attempt to load the game skin and handle failure to load
    try:
        skin = pygame.image.load(skinfilename).convert()
    except pygame.error as msg:
        print('Cannot load skin:', msg)
        raise SystemExit(msg)
    
    screen.fill(skin.get_at((0, 0)))
    pygame.display.set_caption('Sokoban')

    mode = 'easy'
    current_level = 1
    mode_selected = False

    # Mode selection loop
    while not mode_selected:
        display_mode_selection(screen, mode, skin)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and mode == 'easy':
                    mode = 'hard'
                elif event.key == pygame.K_LEFT and mode == 'hard':
                    mode = 'easy'
                elif event.key == pygame.K_RETURN:
                    mode_selected = True

    selecting = True
    max_level = 101 if mode == 'easy' else 50  

    # Level selection loop
    while selecting:
        display_level_selection(screen, mode, current_level, skin)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and current_level < max_level:
                    current_level += 1
                elif event.key == pygame.K_LEFT and current_level > 1:
                    current_level -= 1
                elif event.key == pygame.K_RETURN:
                    selecting = False

    # Game initialization
    skb = Sokoban(current_level, screen, mode)
    skb.draw(screen, skin)
    map_pixel_height = skb.h * 20 
    skb.draw_instructions(screen, map_pixel_height)
    pygame.display.update()

    clock = pygame.time.Clock()
    pygame.key.set_repeat(200, 50)

    # Main game loop
    while not skb.game_won:
        clock.tick(60)
        redraw = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                direction_map = {
                    pygame.K_LEFT: 'l',
                    pygame.K_UP: 'u',
                    pygame.K_RIGHT: 'r',
                    pygame.K_DOWN: 'd'
                }
                if event.key in direction_map and not skb.game_won:
                    skb.move(direction_map[event.key])
                    redraw = True
                            
                elif event.key == pygame.K_BACKSPACE and not skb.game_won:
                    skb.undo()
                    redraw = True
                                               
                        
                elif event.key == pygame.K_SPACE and not skb.game_won:
                    skb.redo()
                    redraw = True

        if redraw:
            skb.draw(screen, skin)
            skb.draw_instructions(screen, map_pixel_height)
            pygame.display.set_caption(
                f"Sokoban: Lv {skb.level_number} - Move: {len(skb.solution)}/{skb.push} - Box: {skb.completed_boxes}/{skb.total_boxes}"
            )
            pygame.display.update()
            if skb.check_victory():  # Check for victory only after updating display
                skb.game_won = True
                skb.display_victory(screen)
                
    
    # Keep the victory message displayed until the user closes the window
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        
if __name__ == '__main__':
    main()