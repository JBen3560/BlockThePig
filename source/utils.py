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
    'N': Fore.RED,
    'C': Fore.BLUE,
}

def print_table(table):
    print("   0  1  2  3  4  5  6  7  8  9  10 11")  # column headers
    for i, row in enumerate(table):
        print(f"{i:>2} ", end='')  # row number, right-aligned
        for char in row:
            color = color_map.get(char, Fore.RESET)
            print(color + char, end='  ')
        print()  # new line after each row


# Check if the level is over by looking for specific buttons     
""" def level_over():
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
        return False """
    
def pig_escape(table, pig_position):
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
        nr, nc = pig_position[0] + dr, pig_position[1] + dc
        
        if table[nr][nc] == 'X':
            return True
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
    if not pig_position:
        print("Pig not found in the table.")
        return -9999
    
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
    lost = pig_escape(table, pig_position)

    # Evaluate based on won or lost
    if won:
        #print("Level won!") #debugging
        return 9999
    if lost:
        #print("Level lost!") #debugging
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
    
    #print(f"Distance evaluated: {min_distance}") #debugging
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
        return (pig_position, None)
    elif len(x_positions) > 1:
        # Sort by distance, then whether row is 0 or 12 (preferred), then col, then row
        x_positions.sort(
            key=lambda pos: (
                pos[1],                               
                0 if pos[0][0] in (0, 12) else 1,     
                pos[0][1],                            
                pos[0][0]                             
            )
        )
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
def minimax(table, depth, alpha, beta, maximizing, path=None):
    if path is None:
        path = []
    
    pig_position = None
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j] == 'P':
                pig_position = (i, j)
                break
        if pig_position:
            break
    
    # Base case: if depth is 0 or the game is over
    if depth == 0:
        #print("EVAL: depth reached") #debugging
        return evaluate_table(table), path
    
    if pig_escape(table, pig_position):
        #print(f"EVAL: pig escaped: {pig_position}") #debugging
        #print_table(table) #debugging
        #pyautogui.sleep(1) #debugging
        return evaluate_table(table), path

    # If it's the player's turn
    if maximizing:
        max_eval = -float('inf')
        best_path = None
        legal_moves = []
        
        for i in range(len(table)):
            for j in range(len(table[i])):
                if table[i][j] == 'E' and abs(i - pig_position[0]) <= 1:
                    legal_moves.append((i, j))
        
        for move in legal_moves:            
            # Do the move
            #table[move[0]][move[1]] = 'N' # debugging
            #table[0][0] = str(depth) # debugging
            #print_table(table) #debugging
            table[move[0]][move[1]] = 'B'
            #pyautogui.sleep(1) #debugging
            eval_score, new_path = minimax(table, depth - 1, alpha, beta, False, path + [("B", move)])
            table[move[0]][move[1]] = 'E'
            
            # Update the maximum evaluation
            if eval_score > max_eval:
                max_eval = eval_score
                best_path = new_path
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_path
    # If it's the pig's turn
    else:
        # Determine the pig's move
        pig_pos, move = pig_move(table)
        if move is None:
            # No moves available
            #print("EVAL: no moves") #debugging
            return evaluate_table(table), path
        
        # Do the move
        table[pig_pos[0]][pig_pos[1]] = 'E'
        table[move[0]][move[1]] = 'P'
        eval_score, new_path = minimax(table, depth, alpha, beta, True, path + [("P", move)])
        table[move[0]][move[1]] = 'E'
        table[pig_pos[0]][pig_pos[1]] = 'P'
        return eval_score, new_path