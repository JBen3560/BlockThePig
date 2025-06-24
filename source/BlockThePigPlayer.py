import pyautogui
from btpLogic import check_instant_win, solve_level
from utils import setup_hex_grid, setup_table, print_table

def main():
    # ------------------------- Initialization -------------------------
    
    # Variables
    location1 = None
    location2 = None
    hex_grid = []
    table = []
    
    # Try to find the top corner
    try:
        location1 = pyautogui.locateOnScreen('.\\images\\firstHex.png', confidence=0.7)
        location2 = pyautogui.locateOnScreen('.\\images\\secondHex.png', confidence=0.7)
    except pyautogui.ImageNotFoundException:
        print("Could not recognize the grid.")
    
    # If the corner is found, set up the hex grid
    if location1 and location2:
        bottom_right1 = (location1.left + location1.width, location1.top + location1.height)
        bottom_right2 = (location2.left + location2.width, location2.top + location2.height)
        hex_grid = setup_hex_grid(bottom_right1, bottom_right2)
        
    # Set up the table with the game state
    if hex_grid:
        table = setup_table(hex_grid)
        
        # Print in color
        print_table(table)

    # ------------------------- Gameplay Loop -------------------------

    if table:
        round_start = True
        while True:
            # See whether it's possible to win with the starting blocks
            if round_start:
                if check_instant_win(hex_grid):
                    round_start = True # maybe redundant
                    continue
                else:
                    round_start = False

            pyautogui.sleep(1)
            print("No instant win found, continuing with the game...")

            # Main logic
            #solve_level(table, 3)
            break #testing

if __name__ == "__main__":
    main()