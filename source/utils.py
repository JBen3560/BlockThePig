import pyautogui
from collections import deque
from PIL import ImageGrab
from colorama import Fore, init

# TODO
# - Consider removing alpha beta altogether
# - Consider combining the won and min distance algs in evaluate_table,
#   depending on depth and how often the min distance seems to be used

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
                print(color + char + ' ', end='')
            print()


# Check if the level is over by looking for specific buttons     
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
                if abs(r - g) < 20 and abs(g - b) < 20:
                    table[i][j] = 'B'
                # Pig
                elif r > 200 and g < 200 and b > 150:
                    table[i][j] = 'P'
                
    return table


# Evaluate the current state of the table
def evaluate_table(table):
    # Variables for whether the level is won or lost
    won = True
    lost = False
    
    # Find the pig
    pig_position = None
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j] == 'P':
                pig_position = (i, j)
                break
        if pig_position:
            break
    
    # Level is won if the pig is boxed in
    visited = set()
    queue = deque([pig_position])
    visited.add(pig_position)
    
    while queue:
        r, c = queue.popleft()

        # If we can reach an 'X', pig is NOT boxed in
        if table[r][c] == 'X':
            won = False
            break

        # Explore 6-directionally
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
            nr, nc = r + dr, c + dc

            if (0 <= nr < len(table) and 0 <= nc < len(table[0]) and
               (nr, nc) not in visited and table[nr][nc] in ('E', 'X')):
                visited.add((nr, nc))
                queue.append((nr, nc))
                
    # Level is lost if the pig is adjacent to an X
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
        nr, nc = pig_position[0] + dr, pig_position[1] + dc
        
        if table[nr][nc] == 'X':
            lost = True
            break

    # Evaluate based on won or lost
    if won:
        return 9999
    if lost:
        return -9999
    
    # Otherwise, evaluate based on the closest 'X' to the pig
    eval_visited = set()
    eval_queue = deque([(pig_position, 0)])  # position, distance
    eval_visited.add(pig_position)
    min_distance = float('inf')
    
    while eval_queue:
        (r, c), dist = eval_queue.popleft()

        if table[r][c] == 'X' and dist < min_distance:
            min_distance = dist

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < len(table) and 0 <= nc < len(table[0]) and
                (nr, nc) not in eval_visited and table[nr][nc] in ('E', 'X')):
                eval_visited.add((nr, nc))
                eval_queue.append(((nr, nc), dist + 1))
    
    return min_distance


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
    
    # Find the all closest 'X' positions
    goal_visited = set()
    goal_queue = deque([(pig_position, 0)])  # position, distance
    goal_visited.add(pig_position)
    min_distance = float('inf')
    x_positions = []
    
    while goal_queue:
        (r, c), dist = goal_queue.popleft()

        if table[r][c] == 'X':
            xpos = ((r, c), dist)
            x_positions.append(xpos)
            if dist < min_distance:
                min_distance = dist

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < len(table) and 0 <= nc < len(table[0]) and
                (nr, nc) not in goal_visited and table[nr][nc] in ('E', 'X')):
                goal_visited.add((nr, nc))
                goal_queue.append(((nr, nc), dist + 1))
    
    # Figure out where the pig is trying to go
    goal = None
    if len(x_positions) == 0:
        # Pig has no moves
        return (pig_position, None)
    elif len(x_positions) > 1:
        # Sort by distance, then col, then row
        x_positions.sort(key=lambda pos: (pos[1], pos[0][1], pos[0][0]))
        goal = x_positions[0][0]
    else:
        goal = x_positions[0][0]
        
    # Figure out the pig's move
    move = None
    move_visited = set()
    move_queue = deque()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
    
    move_queue.append([pig_position])
    move_visited.add(pig_position)

    while move_queue:
        path = move_queue.popleft()
        r, c = path[-1]

        # Correct path
        if (r, c) == goal:
            move = path[1] if len(path) > 1 else pig_position
            break
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (0 <= nr < len(table) and 0 <= nc < len(table[0]) and
               (nr, nc) not in move_visited and table[nr][nc] in ('E', 'X')):
                move_visited.add((nr, nc))
                move_queue.append(path + [(nr, nc)])
    
    return (pig_position, move)


# Minimax algorithm with alpha-beta pruning
def minimax(table, legal_moves, depth, alpha, beta, maximizing):
    # Base case: if depth is 0 or the game is over
    if depth == 0 or level_over():
        return evaluate_table(table)

    # If it's the player's turn
    if maximizing:
        max_eval = -float('inf')
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
        pig_pos, move = pig_move(table)
        if move is None:
            # No moves available
            return evaluate_table(table)
        
        # Do the move
        table[pig_pos[0]][pig_pos[1]] = 'E'
        table[move[0]][move[1]] = 'P'
        eval = minimax(table, legal_moves, depth - 1, alpha, beta, True)
        table[move[0]][move[1]] = 'E'
        table[pig_pos[0]][pig_pos[1]] = 'P'
        return eval