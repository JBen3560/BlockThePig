import pyautogui
from btpLogic import analyze_screen, check_instant_win, solve_level
from utils import print_table, get_depth

def main():    
    turn = 1
    level_over = False
    while True:
        print(f"----- Turn {turn} -----")
        pos_list, table = analyze_screen()
        
        if turn == 1:
            level_over = check_instant_win(pos_list)
            
        if not level_over:
            pig_position = None
            for i in range(len(table)):
                for j in range(len(table[i])):
                    if table[i][j] == 'P':
                        pig_position = (i, j)
                        break
                if pig_position:
                    break
            
            move, value, path, won = solve_level(table, get_depth(), pig_position)     
            
            table[move[0]][move[1]] = 'N'
            print_table(table)
            
            print("\nBest path trace:")
            print(path)
            for step_type, pos in path:
                print(f"{step_type} → {pos}")
            print(f"Final score: {value}\n")
            print(move, value, won)
            

            if move:
                row, col = move
                index = (row * 5) + col - 11 + ((row - 1) // 2)
                if 0 <= index < len(pos_list):
                    pyautogui.moveTo(pos_list[index][0], pos_list[index][1])
                    pyautogui.click()
                    #pyautogui.sleep(0.5)
                    
            turn += 1

if __name__ == "__main__":
    main()