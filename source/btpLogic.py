import pyautogui
from PIL import ImageGrab
from utils import minimax, setup_pos_list, setup_table, get_depth
 
# Translate the screen into a position list and a table
def analyze_screen():
    # Variables
    location1 = None
    location2 = None
    pos_list = []
    table = []
    
    # Try to find the top corner
    try:
        location1 = pyautogui.locateOnScreen('.\\images\\firstHex.png', confidence=0.7)
        location2 = pyautogui.locateOnScreen('.\\images\\secondHex.png', confidence=0.7)
    except pyautogui.ImageNotFoundException:
        print("Could not recognize the grid.")
        return None, None
    
    # If the corner is found, set up the hex grid
    if location1 and location2:
        bottom_right1 = (location1.left + location1.width, location1.top + location1.height)
        bottom_right2 = (location2.left + location2.width, location2.top + location2.height)
        pos_list = setup_pos_list(bottom_right1, bottom_right2)
        
    # Set up the table with the game state
    if pos_list:
        table = setup_table(pos_list)
        
    return pos_list, table

# Check whether the game can be won in opening placements
def check_instant_win(pos_list):
    # Setup
    screenshot = ImageGrab.grab()
    temp_pos_list = pos_list.copy()
    empty_at_start = []
    block_at_start = []
    
    # See how many blocks start around the pig
    list_to_check = [22,23,26,28,32,33]
    for i in list_to_check:
        hex = temp_pos_list[i]
        screenshot_pixel = screenshot.getpixel((hex[0], hex[1]))
        r, g, b = screenshot_pixel[:3]
        if abs(r - g) < 15 and abs(g - b) < 15:
            block_at_start.append(i)
        else:
            empty_at_start.append(i)
    
    # If there are 3 or more blocks around the pig, place in empty spaces
    if len(block_at_start) == 3:
        for i in empty_at_start:
            pyautogui.moveTo(pos_list[i])
            pyautogui.click()
        return True
    
    # If there were 4 or more blocks around the pig, place extras
    if len(block_at_start) >= 4:
        for i in empty_at_start:
            pyautogui.moveTo(pos_list[i])
            pyautogui.click()
        extra_placement = 0
        while True:
            # Check for continue button
            try:
                pyautogui.locateOnScreen('.\\images\\continue.png', confidence=0.7)
                return True
            except pyautogui.ImageNotFoundException:
                pass
            
            # Check for try again button
            try:
                pyautogui.locateOnScreen('.\\images\\try_again.png', confidence=0.7)
                return True
            except pyautogui.ImageNotFoundException:
                pyautogui.moveTo(pos_list[extra_placement])
                pyautogui.click()
                extra_placement += 1
    
    # If there's nothing to do, return False
    return False

def solve_level(table, depth, pig_pos, post_abort):
    # Setup
    best_move = None
    best_value = -float('inf')
    best_path = []

    # Figure out all legal moves
    legal_moves = []
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j] == 'E' and abs(i - pig_pos[0]) <= 3:
                legal_moves.append((i, j))
        
    for move in legal_moves:        
        table[move[0]][move[1]] = 'B'
        table_value, move_path = minimax(table, depth - 1, False, path=[("B", move)])
        table[move[0]][move[1]] = 'E'

        if table_value > best_value:
            best_value = table_value
            best_move = move
            best_path = move_path
            
            # Simple pruning if the winning path was not aborted last move
            if best_value >= get_depth() and not post_abort:
                print("PRUNE")
                break
    
    return best_move, best_value, best_path