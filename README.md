# Block the Pig Player
An automated [Block the Pig](https://www.coolmathgames.com/0-block-the-pig#immersiveModal) solver and player. It uses a minimax algorithm with a heuristic evaluation to plan block placements and stop the pig from escaping. Includes computer-vision-based board detection and automated mouse control to play the game in a browser.

## Features
- Detects the game board on-screen with PyAutoGUI image matching
- Builds an internal representation of the hex grid
- Runs a minimax search with configurable depth
- Handles the pig’s deterministic movement logic
- Clicks on-screen to place blocks automatically
- Color-coded console output of board state for debugging

## How It Works
1. **Screen Detection:** Uses image matching to find two reference hexes on the board to calibrate the grid.
   
![screen](https://github.com/JBen3560/BlockThePig/blob/main/readme%20media/btp.png)

2. **Table Setup:** Builds a 2D representation of the game grid.

![table]()

3. **Solver Algorithm**
- Runs minimax with pruning based on depth and game state
- Determines pig escape paths using 6-direction BFS flood fill
- Evaluates board by finding shortest path to an escape

4. **Automation**
- Translates the hex grid table coordinates into screen positions
- Clicks to place blocks in the browser game
```python
row, col = move
index = (row * 5) + col - 11 + ((row - 1) // 2)
if 0 <= index < len(pos_list):
    pyautogui.moveTo(pos_list[index][0], pos_list[index][1])
    pyautogui.click()
```

## Requirements
PyAutoGUI, Pillow, OpenCV-Python, Colorama
```bash
pip install -r requirements.txt
```

## Usage
1. **Adjust the Window size:** While the program uses reference images to automatically position itself on the game board, due to the resolution of the images, for best functionality adjust the size of the board to approximately 860 x 1290 px.

![resolution]()

2. **Run the Script**
```bash
python BlockThePigPlayer.py
```

3. **Watch it play!** The AI will detect the board, compute moves, and click automatically. When you want to stop the program, move your mouse to the top left corner.

## Demo
![demo]()