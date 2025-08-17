'''
This our driver responsible handling input Gnd displaying object.
'''


import pygame as p
import ChessEngine

WIDTH = 512 
HEIGHT = 512 
DIMENSIONS = 8 # dimensions of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSIONS
MAX_FPS = 15 
IMAGES = {}

"""
    Initialize a global dictionary of images. This will be called exactly once in the main.
"""
def loadImages():

    # IMAGES['wp'] = p.image.load("images/wp.png")
   
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wp']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
# This main driver for our code. THis will handle user input and updating the graphics

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()  # Get all valid moves for the current game state
    moveMade = False  # Flag to check if a move has been made
    loadImages() # Load images only once, before the while loop
    running = True
    sqSelected = ()  # No square is selected initially , keep track of the last click (tuple: (row, col))
    playerClicks = []  # Keep track of player clicks (two tuples: [(row, col), (row, col)])
    while running:
        for e in p.event.get():  # proces all the user interactions
            if e.type == p.QUIT:  # When user clicks the X button
                running = False
            
            # mouse handling
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col): # If the user clicked the same square again, deselect it
                    sqSelected = () 
                    playerClicks = []
                else:
                    sqSelected = (row, col)  
                    playerClicks.append(sqSelected) 
                if len(playerClicks) == 2:  # If the user has clicked two squares
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())  # Print the move in chess notation
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:  # If the move is valid
                            moveMade = True
                            gs.makeMove(validMoves[i])
                            sqSelected = ()  # reset the selected square
                            playerClicks = []  # reset the player clicks
                    if not moveMade:  # If the move is not valid, reset the selected square and player clicks
                        playerClicks = [sqSelected]
            # key handling
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo the last move
                    gs.undoMove()
                    moveMade = True

        if moveMade:  # If a move has been made, update the valid moves
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS) # Limit the game to MAX_FPS
        p.display.flip() # Update the display

# responsible for all the graphics within a current game state
def drawGameState(screen, gs):
    drawBoard(screen) # Draw the squares on the board
    drawPieces(screen, gs.board) # Draw the pieces on top of the squares

# Draw the squares on the chess board

def drawBoard(screen):
    # the top left square is always light
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Draw the pieces on the board using the current GameState.board
def drawPieces(screen, board):
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()