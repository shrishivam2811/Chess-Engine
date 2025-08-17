'''
This class is responsible for storing the information about the current state of a chess game. It will also be
responsible for determining the valid moves at the current state. It will also keep a move Log.
'''
 
class GameState():
    def __init__(self):
        """
        Board is an 8x8 2d list, each element in list has 2 characters.
        The first character represents the color of the piece: 'b' or 'w'.
        The second character represents the type of the piece: 'R', 'N', 'B', 'Q', 'K' or 'p'.
        "--" represents an empty space with no piece.
        """
    
        self.board = [

            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"] ]
        
        self.moveFunctions = {
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }

        self.whiteToMove = True
        self.moveLog = []

        self.whiteKingLocation = (7, 4)  
        self.blackKingLocation = (0, 4) 

        self.checkMate = False
        self.staleMate = False

        self.enPassantPossible = ()  # coordinates for the square where en passant is possible



    # take a move as a parameter and execute it (this will not work for castling, pawn promotion, en passant)
    def makeMove(self, move):
        """
        Updates the board and the move log with the given move.
        """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove
        
        # update the king's location if the move is a king move
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)


        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'  # promote to queen, can be changed to other pieces later
        
        # en passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"
        # update en passant possible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # only pawns can move two squares from their starting position
            self.enPassantPossible = ((move.endRow + move.startRow) // 2, move.endCol)  # the square behind the pawn that can be captured en passant
        else:
            self.enPassantPossible = ()



    def undoMove(self):
        """
        Undo the last move made.
        """
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turn back
            # update the king's location 
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # restore the captured pawn
                self.enPassantPossible = (move.endRow,move.endCol)
            # undo a 2 squares pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()  




    # all moves considering checks
    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible  # save the current en passant possible square
        # 1. generate all possible moves
        moves = self.getAllPossibleMoves()
        # 2. for each move, make the move
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            # 3. generate all opponent's moves
            # 4. for each opponent's move, check if the king is under attack
            self.whiteToMove = not self.whiteToMove  # switch turn because makeMove() switches the turn
            if self.inCheck():
                moves.remove(moves[i])  # 5. if they do attack the king, remove the move , not a valid move
            self.whiteToMove = not self.whiteToMove  # switch turn back
            self.undoMove()  # undo the move to restore the board
        if len(moves) == 0: # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        self.enPassantPossible = tempEnPassantPossible  # restore the en passant possible square
        return moves
    
    def inCheck(self):
        """
        Returns True if the current player is in check.
        """
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
        

    def squareUnderAttack(self, r, c):
        """
        Returns True if the square at (r, c) is under attack by any piece of the opposite color.
        """
        self.whiteToMove = not self.whiteToMove  # switch turn to check if the square is under attack
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turn back
        # check if any of the opponent's moves can attack the square
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: # square is under attack
                return True
        return False



    def getAllPossibleMoves(self):
        moves = []  # Example move for testing
        # This method should return all possible moves for the current game state
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # 'w' or 'b'
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)  # Call the appropriate move function based on the piece type       
        return moves
    



    # get all pawn moves for the pawn located at (r, c) and add these moves to the moves list
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: # white pawns move
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":  # double move from starting position
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >=0 :
                if self.board[r-1][c-1][0] == 'b':   # enemy piece to capture -  left
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1,c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':  # enemy piece to capture -  right
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1,c+1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
        
        else:  # black pawns move
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":  # double move from starting position
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':   # enemy piece to capture - left
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1,c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':  # enemy piece to capture - right
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1,c+1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))



    # get all rook moves for the rook located at (r, c) and add these moves to the moves list
    def getRookMoves(self, r, c, moves):
        # pair: (row, col)
        directions = ((-1,0), (0,-1), (1,0), (0,1))  # up, left, down, right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # check if the square is on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece 
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece
                        break  
                else:  # off the board
                    break


    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2,-1), (-1,-2), (1,-2), (2,-1), (2,1), (1,2), (-1,2), (-2,1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not a ally piece (empty or enemy piece )
                    moves.append(Move((r, c), (endRow, endCol), self.board))
                

    def getBishopMoves(self, r, c, moves):
        # pair: (row, col)
        directions = ((-1,-1), (-1,1), (1,-1), (1,1))  # up-left, up-right, down-left, down-right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):   # bishop can move max 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece  
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece
                        break
                else:  # off the board
                    break




        





    def getQueenMoves(self, r, c, moves):  
        # example  of abbraction
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in kingMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    










class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        # en passant
        self.isEnpassantMove = isEnpassantMove 
        if isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'





        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol


    # overriding the equals method
    def __eq__(self, other):
        if  isinstance(other, Move):
            return self.moveID == other.moveID
    
    def getChessNotation(self):
        """
        Returns the chess notation for the move.
        """
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        """
        Returns the rank and file of the square.
        """
        return self.colsToFiles[c] + self.rowsToRanks[r]
    