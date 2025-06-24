import math
import pyautogui
from PIL import ImageGrab
from colorama import Fore, init

# Printing in color
init(autoreset=True)
color_map = {
    '-': Fore.LIGHTBLACK_EX,
    'X': Fore.WHITE,
    'E': Fore.GREEN,
    'B': Fore.YELLOW,
    'P': Fore.MAGENTA,
}

def print_table(table):
    for row in table:
            for char in row:
                color = color_map.get(char, Fore.RESET)
                print(color + char + ' ', end='')  # space between characters
            print()  # new line after each row
            
def level_over():
    # Check for continue button
    try:
        pyautogui.locateOnScreen('.\\images\\continue.png', confidence=0.8)
        return True
    except pyautogui.ImageNotFoundException:
        pass
    
    # Check for try again button
    try:
        pyautogui.locateOnScreen('.\\images\\try_again.png', confidence=0.8)
        return True
    except pyautogui.ImageNotFoundException:
        return False

# Get a list of coordinates for the hexagonal grid
def setup_hex_grid(first_hex, second_hex):
    hex_grid = []
    point = [first_hex[0], first_hex[1]]
    increment = second_hex[0] - first_hex[0]
    offset = increment * 0.5
    drop = increment * 0.76
    odd_row = True

    for i in range(0,11):
        # Set the starting point for the next row
        if odd_row:
            point[0] = first_hex[0]
            odd_row = False
        else:
            point[0] = first_hex[0] + offset
            odd_row = True
        
        # Input a row
        for j in range(0,5):
            new_point = point.copy()
            hex_grid.append(new_point)
            point[0] += increment

        # Increase the y value
        point[1] += drop
    
    return hex_grid


# Populate the table with what's in each position of the grid
def setup_table(hex_grid):
    # Default table
    table = [['-', '-', '-', '-', '-', '-', 'X', 'X', 'X', 'X', 'X', 'X'],
             ['-', '-', '-', '-', '-', 'X', 'E', 'E', 'E', 'E', 'E', 'X'],
             ['-', '-', '-', '-', '-', 'X', 'E', 'E', 'E', 'E', 'E', 'X'],
             ['-', '-', '-', '-', 'X', 'E', 'E', 'E', 'E', 'E', 'X', '-'],
             ['-', '-', '-', '-', 'X', 'E', 'E', 'E', 'E', 'E', 'X', '-'],
             ['-', '-', '-', 'X', 'E', 'E', 'E', 'E', 'E', 'X', '-', '-'],
             ['-', '-', '-', 'X', 'E', 'E', 'E', 'E', 'E', 'X', '-', '-'],
             ['-', '-', 'X', 'E', 'E', 'E', 'E', 'E', 'X', '-', '-', '-'],
             ['-', '-', 'X', 'E', 'E', 'E', 'E', 'E', 'X', '-', '-', '-'],
             ['-', 'X', 'E', 'E', 'E', 'E', 'E', 'X', '-', '-', '-', '-'],
             ['-', 'X', 'E', 'E', 'E', 'E', 'E', 'X', '-', '-', '-', '-'],
             ['X', 'E', 'E', 'E', 'E', 'E', 'X', '-', '-', '-', '-', '-'],
             ['X', 'X', 'X', 'X', 'X', 'X', '-', '-', '-', '-', '-', '-']]
    
    # Populate the table with blocks and the pig
    screenshot = ImageGrab.grab()
    temp_hex_grid = hex_grid.copy()
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j] == 'E':
                hex = temp_hex_grid.pop(0)
                screenshot_pixel = screenshot.getpixel((hex[0], hex[1]))
                r, g, b = screenshot_pixel[:3]
                # Block
                if abs(r - g) < 15 and abs(g - b) < 15:
                    table[i][j] = 'B'
                # Pig
                elif r > 200 and g < 200 and b > 150:
                    table[i][j] = 'P'
                
    return table


# Evaluate the current state of the table
def evaluate_table(table):
    if board.is_checkmate():
        return -9999 if board.turn else 9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    value = 0
    for piece_type in piece_values:
        value += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        value -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

    return value


# Determinstically move the pig based on the current board state
def pig_move(table):
    # Find the pig
    pig_position = None
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j] == 'P':
                pig_position = (i, j)
                break
        if pig_position:
            break
    
    # Spread out from the pig's position to closest edges
    visited = set([pig_position])
    frontier = [(pig_position, 0)]  # (position, distance)
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1)]
    while frontier:
        current_position, distance = frontier.pop(0)
        
        # Check if we reached the edge
        if current_position[0] == 0 or current_position[0] == len(table) - 1 or \
           current_position[1] == 0 or current_position[1] == len(table[0]) - 1:
            return current_position
        
        # Explore neighbors
        for direction in directions:
            neighbor = (current_position[0] + direction[0], current_position[1] + direction[1])
            if (0 <= neighbor[0] < len(table) and 
                0 <= neighbor[1] < len(table[0]) and 
                neighbor not in visited and 
                table[neighbor[0]][neighbor[1]] != 'B'):
                visited.add(neighbor)
                frontier.append((neighbor, distance + 1))
    
    

    # If no legal moves (should be game over), return None
    return None


# Minimax algorithm with alpha-beta pruning
def minimax(table, legal_moves, depth, alpha, beta, maximizing):
    # Base case: if depth is 0 or the game is over
    if depth == 0 or level_over():
        return evaluate_table(table)

    # If it's the player's turn
    if maximizing:
        max_eval = -math.inf
        for move in legal_moves:
            # Do the move
            table[move[0]][move[1]] = 'B'
            legal_moves.remove(move)
            eval = minimax(table, legal_moves, depth - 1, alpha, beta, False)
            table[move[0]][move[1]] = 'E'
            legal_moves.append(move)
            
            # Update the maximum evaluation
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    # If it's the pig's turn
    else:
        # Determine the pig's move
        move = pig_move(table)
        if move is None:
            # No moves available
            return evaluate_table(table)
        
        # Do the move
        table[move[0]][move[1]] = 'P'
        eval = minimax(table, legal_moves, depth - 1, alpha, beta, True)
        table[move[0]][move[1]] = 'E'
        return eval