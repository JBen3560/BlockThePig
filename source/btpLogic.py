import pyautogui
from PIL import ImageGrab
from utils import minimax, print_table

# Check whether the game can be won in opening placements
def check_instant_win(hex_grid):
    # Setup
    screenshot = ImageGrab.grab()
    temp_hex_grid = hex_grid.copy()
    empty_at_start = []
    block_at_start = []
    
    # See how many blocks start around the pig
    list_to_check = [22,23,26,28,32,33]
    for i in list_to_check:
        hex = temp_hex_grid[i]
        screenshot_pixel = screenshot.getpixel((hex[0], hex[1]))
        r, g, b = screenshot_pixel[:3]
        if abs(r - g) < 15 and abs(g - b) < 15:
            block_at_start.append(i)
        else:
            empty_at_start.append(i)
    
    # If there are 3 or more blocks around the pig, place in empty spaces
    if len(block_at_start) >= 3:
        for i in empty_at_start:
            pyautogui.moveTo(hex_grid[i])
            pyautogui.click()
    
    # If there were 4 or more blocks around the pig, place extras
    if len(block_at_start) >= 4:
        pyautogui.useImageNotFoundException()
        extra_placement = 0
        while True:
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
                pyautogui.moveTo(hex_grid[extra_placement])
                pyautogui.click()
                extra_placement += 1
    
    # If there's nothing to do, return False
    return False

def solve_level(table, depth):
    # Setup
    best_move = None
    best_value = -float('inf')

    # Figure out all legal moves
    legal_moves = []
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j] == 'E':
                legal_moves.append((i, j))
    
    for move in legal_moves:
        table[move[0]][move[1]] = 'B'
        legal_moves.remove(move)
        table_value = minimax(table, legal_moves, depth, -float('inf'), float('inf'), True)
        table[move[0]][move[1]] = 'E'
        legal_moves.append(move)

        if table_value > best_value:
            best_value = table_value
            best_move = move

    return best_move # change this to actually place the block