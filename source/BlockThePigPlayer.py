import pyautogui
from btpLogic import analyze_screen, check_instant_win, solve_level
from utils import print_table, get_depth
from colorama import Fore

# TODO possible issues
# 1. Check each pig movement of the winning plan to make sure it keeps lining up
# 2. Make sure the "Place X blocks more blocks" doesn't mess stuff up
# 3. Put alpha pruning back in or something

def main():    
    pyautogui.FAILSAFE = True
    turn = 1
    level = 1
    post_abort = False
    while True:
        print(f"\n\n----- Turn {turn} -----")
        level_over = False
        
        # Analyze the screen and find the pig
        pig_position = None
        while not pig_position:
            pos_list, table = analyze_screen()
            if pos_list and table:
                for i in range(len(table)):
                    for j in range(len(table[i])):
                        if table[i][j] == 'P':
                            pig_position = (i, j)
                            break
                    if pig_position:
                        break
        
        # Check whether the level can be won in the opening blocks
        if turn == 1:
            level_over = check_instant_win(pos_list)
                        
        # Use minimax to find the best move
        if not level_over:
            # Adjust depth at the start or if a winning path was aborted
            curr_depth = get_depth()
            if turn <= 3 or post_abort:
                curr_depth -= 1
                if post_abort:
                    curr_depth -= 1

            # Solve the level with the current depth and pig position
            move, value, path = solve_level(table, curr_depth, pig_position, post_abort)
            post_abort = False
            
            # If the move is valid, update the table and print it
            table[move[0]][move[1]] = 'N'
            print_table(table)
            
            # Print the best path trace
            print("\nBest path trace:")
            for step_type, pos in path:
                print(f"{step_type} → {pos}")
            print(f"Final score: {value}\n")
            print(move, value)

            # If the path is winning, do the path
            if (value >= 9999 and turn >= 3):                
                # Execute each step
                for step_type, pos in path:
                    if step_type == "B":
                        row, col = pos
                        index = (row * 5) + col - 11 + ((row - 1) // 2)
                        pyautogui.moveTo(pos_list[index][0], pos_list[index][1])
                        pyautogui.click()
                    elif step_type == "P":
                        pig_position = None
                        while not pig_position:
                            pos_list, table = analyze_screen()
                            if pos_list and table:
                                for i in range(len(table)):
                                    for j in range(len(table[i])):
                                        if table[i][j] == 'P':
                                            pig_position = (i, j)
                                            break
                                    if pig_position:
                                        break
                        
                        # Abort if things aren't as planned
                        print("pig moves",pig_position, pos) 
                        if pig_position != pos:
                            print("ABORT")
                            row, col = pos
                            index = (row * 5) + col - 11 + ((row - 1) // 2)
                            pyautogui.moveTo(pos_list[index][0], pos_list[index][1])
                            post_abort = True
                            break
                        
                        pyautogui.sleep(0.1)
            
            # If the path is not winning, do the move
            else:
                row, col = move
                index = (row * 5) + col - 11 + ((row - 1) // 2)
                if 0 <= index < len(pos_list):
                    pyautogui.moveTo(pos_list[index][0], pos_list[index][1])
                    pyautogui.click()              
                    
        # Find the buttons
        try:
            cont = pyautogui.locateOnScreen('.\\images\\continue.png', confidence=0.7)
            if cont:
                pyautogui.moveTo(cont,duration=0.2)
                pyautogui.click()
                turn = 0
                level += 1
                pyautogui.sleep(1.5)
        except pyautogui.ImageNotFoundException:
            pass        
                    
        try:
            fail = pyautogui.locateOnScreen('.\\images\\try_again.png', confidence=0.7)
            if fail:
                pyautogui.moveTo(fail,duration=0.1)
                pyautogui.click()
                turn = 0
                print(Fore.RED + "\n\nLasted for", level, "levels!\n\n" + Fore.RESET)
                level = 1
                pyautogui.sleep(1.5)
        except pyautogui.ImageNotFoundException:
            pass
        
        try:
            cont = pyautogui.locateOnScreen('.\\images\\return.png', confidence=0.7)
            if cont:
                pyautogui.moveTo(cont,duration=0.1)
                pyautogui.click()
                pyautogui.sleep(1.5)
        except pyautogui.ImageNotFoundException:
            pass        
        
        turn += 1

if __name__ == "__main__":
    main()