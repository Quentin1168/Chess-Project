from cmath import pi
from PIL import Image, ImageTk

piece_to_string = {
    ("black", "rook"): "r",
    ("black", "knight"): "k",
    ("black", "bishop"): "b",
    ("black", "king"): "l",
    ("black", "queen"): "q",
    ("black", "pawn"): "p",
    ("white", "rook"): "R",
    ("white", "knight"): "K",
    ("white", "bishop"): "B",
    ("white", "king"): "L",
    ("white", "queen"): "Q",
    ("white", "pawn"): "P"
}

team = {
    "black": "white",
    "white": "black"
}


"""
Piece Class covers the chess pieces of the board.
Parameters:
position -> the x and y coordiantes of the chess piece
type -> the type of chess piece (e.g. knight, rook queen)
colour -> the colour of the chess piece (black or white)
"""
class Piece():
    """
    Pieces have an "untouched" flag to cater for special rules in the chessboard such as Castling 
    and the pawn moving 2 spaces ahead if untouched.
    """

    def __init__(self, position, type, colour):
        self.position = position
        self.id = "Piece"
        self.type = type
        self.colour = colour
        self.untouched = True
        if type == "Entity":
            self.piece = False
        else:
            self.piece = True


    def get_position(self):
        return self.position

    def get_type(self):
        return self.type
    
    def get_colour(self):
        return self.colour

    def get_id(self):
        return self.id

    def get_untouched(self):
        return self.untouched

    def set_untouched(self):
        self.untouched = False
    
    def is_piece(self):
        return self.piece
    
    def __repr__(self):
        return "Piece(" + str(self.position) + " ," + self.type + " ," + self.colour + " )"

"""
ChessBoard class covers the board and the tiles on it
"""
class ChessBoard:
    """
    The board can be represented by a 64 character long string, which each character representing a tile of the board.
    The reason for this compact representation is for ease of transmitting the information to the server and other players.
    It also makes it easy for both players having different perspecitves of the board, where they are "facing" each other.

    Client-side, the board is represented as a list of Piece objects. From the Client's perspective, all the objects on the left corner
    start from (8,1) and the objects on the right corner are (1,1). This is the same for every client, and the board just gets inverted
    whenever it is sent.
    """
    def __init__(self):
        #self.string = "rkbqlbkrpppppppp~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PPPPPPPPRKBqLBKR"
        self.string = "~~~rr~l~~pqk~pp~~~~~~~~p~~p~~~~~p~~kKK~QP~~P~~~~~PP~~~PP~L~~rR~~"
        self.board = []
        self.convert_from_string()
        self.selected = None
        self.check = False
        self.checkmate = False
        self.team = "white"

    """
    Convert the string to a list of Entity and Piece Objects
    """
    def convert_from_string(self):
        x = 8
        y = 8
        colour = "black"
        board = []
        for i in self.string:
            
            

            if i.isupper():
                colour = "white"
            else:
                colour = "black"
            if i.lower() == "r":
                board.append(Piece((x,y), "rook", colour))
            elif i.lower() == "k":
                board.append(Piece((x,y), "knight", colour))
            elif i.lower() == "b":
                board.append(Piece((x,y), "bishop", colour))
            elif i.lower() == "q":
                board.append(Piece((x,y), "queen", colour))
            elif i.lower() == "l":
                board.append(Piece((x,y), "king", colour))
            elif i.lower() == "p":
                board.append(Piece((x,y), "pawn", colour))
            else:
                board.append(Piece((x,y), "Entity", "neutral"))
            x -= 1

            if x < 1:
                x = 8
                y -= 1
        self.board = board

    """
    Converts the list of Piece and Entity Objects into string format
    """
    def convert_to_string(self, board = None):
        if board == None:
            board = self.board
        string = ""
        for i in board:
            if i.get_type() == "Entity":
                string += "~"
            else:
                string += piece_to_string[(i.get_colour(), i.get_type())]

        self.string = string

    """
    Gets the specific Entity or Piece Object from the coordinates specified.
    
    Parameters: coords -> the coordinates in tuple form
    Returns: Entity or Piece object
    """
    def get_piece(self, coords, board = None):
        if board == None:
            board = self.board
        x = coords[0]
        y = coords[1]

        for i in board:
            if i.get_position()[0] == x and i.get_position()[1] == y:
                return i

    """
    Gets Piece objects by type

    Parameter: type -> the type of the piece specified
    Returns: list of Piece objects of the type
    """
    def get_pieces_by_type(self, type, colour, board = None):
        if board == None:
            board = self.board
        pieces = []
        for i in board:
            if i.get_type() == type and i.get_colour() == colour:
                pieces.append(i)

        return pieces
        
    """
    Gets all the possible movable positions of the specified position. Bad positions
    are pruned out using prune_possible_positions().
    Special rules such as Castling and Pawn diagonal piece taking are covered here.

    Parameters: piece -> A Piece Object of the Chess board
    Returns: a list of the possible positions that the piece can go.
    """
    def get_positions(self, piece, board = None, prune = False):
        if board == None:
            board = self.board
        type = piece.get_type()
        coords = piece.get_position()
        possible = []

        if type == "knight":
            possible.append((coords[0]+1, coords[1]+2))
            possible.append((coords[0]-1, coords[1]+2))
            possible.append((coords[0]+2, coords[1]+1))
            possible.append((coords[0]+2, coords[1]-1))
            possible.append((coords[0]-2, coords[1]+1))
            possible.append((coords[0]-2, coords[1]-1))
            possible.append((coords[0]-1, coords[1]-2))
            possible.append((coords[0]+1, coords[1]-2))
        elif type == "bishop":
            possible += self.diagonal_expansion(piece, board)
        elif type == "rook":
            possible += self.perpendicular_expansion(piece, board)
        elif type == "queen":
            possible += self.perpendicular_expansion(piece, board)
            possible += self.diagonal_expansion(piece, board)
        elif type == "king":
            possible.append((coords[0]+1, coords[1]+1))
            possible.append((coords[0]+1, coords[1]-1))
            possible.append((coords[0]-1, coords[1]+1))
            possible.append((coords[0]-1, coords[1]-1))
            possible.append((coords[0]+1, coords[1]))
            possible.append((coords[0]-1, coords[1]))
            possible.append((coords[0], coords[1]+1))
            possible.append((coords[0], coords[1]-1))

            # Conditions for the "Castling" special move.
            
            if self.check == False and self.get_pieces_by_type("king", self.team, board)[0].get_untouched() == True:
                    possible += self.castling_possible_positions(coords, board)
            
        elif type == "pawn":
            if self.team != piece.get_colour():
                if self.get_piece((coords[0], coords[1]-1)).piece == False:
                    possible.append((coords[0], coords[1]-1))
                    if piece.get_untouched() == True:
                        possible.append((coords[0], coords[1]-2))

                #Check if the future coords are out of bounds or not
                if 0 < coords[0]+1 < 9 and 0 < coords[1]-1 < 9 and self.get_piece((coords[0]+1, coords[1]-1), board).is_piece():
                    if team[self.get_piece((coords[0]+1, coords[1]-1), board).get_colour()] == piece.get_colour():
                        possible.append((coords[0]+1, coords[1]-1))
                if 0 < coords[0]-1 < 9 and 0 < coords[1]-1 < 9 and self.get_piece((coords[0]-1, coords[1]-1), board).is_piece():
                    if team[self.get_piece((coords[0]-1, coords[1]-1), board).get_colour()] == piece.get_colour():
                        possible.append((coords[0]-1, coords[1]-1))
            else:
                if self.get_piece((coords[0], coords[1]+1), board).piece == False:
                    possible.append((coords[0], coords[1]+1))
                    if piece.get_untouched() == True:
                        possible.append((coords[0], coords[1]+2))

                if 0 < coords[0]+1 < 9 and 0 < coords[1]+1 < 9 and self.get_piece((coords[0]+1, coords[1]+1), board).is_piece():
                    if team[self.get_piece((coords[0]+1, coords[1]+1), board).get_colour()] == piece.get_colour():
                        possible.append((coords[0]+1, coords[1]+1))
                if 0 < coords[0]-1 < 9 and 0 < coords[1]+1 < 9 and self.get_piece((coords[0]-1, coords[1]+1), board).is_piece():
                    if team[self.get_piece((coords[0]-1, coords[1]+1), board).get_colour()] == piece.get_colour():
                        possible.append((coords[0]-1, coords[1]+1))


        if len(possible) != 0:
            pruned_possible = []
            
            for i in possible:
                if 0 < i[0] < 9 and 0 < i[1] < 9 and self.get_piece(i, board).get_colour() != piece.get_colour():
                    pruned_possible.append(i)
            possible = pruned_possible
        if prune == True:
            possible = self.prune_checks(piece, possible, board)

        return possible
        


    """
    Gets all the possible positions if the castling special move is movable. Specified for both teams.

    Parameters: coords -> the coordinates of the piece in question
    Returns: the possible castling positions of the king
    """
    def castling_possible_positions(self, coords, board):
        possible = []
        castling_flag_left = True
        castling_flag_right = True
        if self.team == "black":
            for i in [2,3,4]:
                if self.get_piece((i,1), board).get_type() != "Entity":
                    castling_flag_left = False
            for i in [6,7]:
                if self.get_piece((i,1), board).get_type() != "Entity":
                    castling_flag_right = False
                
        else:
            for i in [2,3]:
                if self.get_piece((i,1), board).get_type() != "Entity":
                    castling_flag_right = False
            for i in [5,6,7]:
                if self.get_piece((i,1), board).get_type() != "Entity":
                    castling_flag_left = False
        if self.get_piece((8,1), board).get_type() != "rook" or self.get_piece((8,1), board).get_colour != self.team \
                or self.get_piece((8,1), board).get_untouched() == False:
                castling_flag_left = False
        if self.get_piece((1,1), board).get_type() != "rook" or self.get_piece((1,1), board).get_colour != self.team \
            or self.get_piece((1,1), board).get_untouched() == False:
            castling_flag_right = False
            
        if castling_flag_left == True:
            possible.append((coords[0]+2, coords[1]))
        if castling_flag_right == True:
            possible.append((coords[0]-2, coords[1]))
        return possible
    """
    Used for the rook and the queen, for finding the possible horizontal and vertical positions those given pieces can go
    before they come in contact with the border of the board or an enemy piece

    Parameters: piece -> the piece in question
    Returns: the possible perpendicular positons that the piece can move to
    """
    def perpendicular_expansion(self, piece, board):
        possible = []
        coords = piece.get_position()
        x = coords[0]+1
        y = coords[1]
        while x < 9 and self.get_piece((x,y), board).get_colour() != piece.get_colour():
            
            possible.append((x, coords[1]))
            
            if self.get_piece((x,y), board).get_colour() != piece.get_colour() \
                and self.get_piece((x,y), board).piece == True:
                break
            x += 1
        x = coords[0]-1
        while x > 0 and self.get_piece((x,y), board).get_colour() != piece.get_colour():            
            possible.append((x, coords[1]))
            if self.get_piece((x,y), board).get_colour() != piece.get_colour() \
                and self.get_piece((x,y), board).piece == True:
                break
            x -= 1
        x = coords[0]
        y = coords[1] + 1
        while y < 9 and self.get_piece((x,y), board).get_colour() != piece.get_colour(): 
            
            possible.append((coords[0], y))
            if self.get_piece((x,y), board).get_colour() != piece.get_colour() \
                and self.get_piece((x,y), board).piece == True:
                break
            y += 1
        x = coords[0]
        y = coords[1] - 1
        while y > 0 and self.get_piece((x,y), board).get_colour() != piece.get_colour():
                
            
            possible.append((coords[0], y))
            if self.get_piece((x,y), board).get_colour() != piece.get_colour() \
                and self.get_piece((x,y), board).piece == True:
                break
            y -= 1
        y = coords[1]
        return possible

    """
    Used for the bishop and the queen, for finding the possible diagonal positions those given pieces can go
    before they come in contact with the border of the board or an enemy piece.

    Parameters: piece -> the piece in question
    Returns: the possible diagonal positons that the piece can move to
    """
    def diagonal_expansion(self, piece, board):
        possible = []
        coords = piece.get_position()
        x = coords[0]+1
        y = coords[1]+1
        while x < 9 and y < 9 and self.get_piece((x,y), board).get_colour() != self.team:
            possible.append((x,y))
            if self.get_piece((x,y), board).get_colour() != self.team \
                and self.get_piece((x,y), board).piece == True:
                break
            x += 1
            y += 1
        x = coords[0]+1
        y = coords[1]-1
        while x < 9 and y > 0 and self.get_piece((x,y), board).get_colour() != self.team:
            possible.append((x, y))
            if self.get_piece((x,y), board).get_colour() != self.team \
                and self.get_piece((x,y), board).piece == True:
                break
            x += 1
            y -= 1
        x = coords[0]-1
        y = coords[1]+1
        while x > 0 and y < 9 and self.get_piece((x,y), board).get_colour() != self.team:
            possible.append((x, y))
            if self.get_piece((x,y), board).get_colour() != self.team \
                and self.get_piece((x,y), board).piece == True:
                break
            x -= 1
            y += 1
        x = coords[0]-1
        y = coords[1]-1
        while x > 0 and y > 0 and self.get_piece((x,y), board).get_colour() != self.team:
            possible.append((x, y))
            if self.get_piece((x,y), board).get_colour() != self.team \
                and self.get_piece((x,y), board).piece == True:
                break
            x -= 1
            y -= 1

        return possible

    """
    Moves the specified piece to the specified coordinates, if the coordinates contain a piece there, take it.coords=
    Also implements the castling special move, if get_positions allows for a castling move.

    Parameters: piece -> the piece in question
                coords -> the coordinates the piece will move to
                board -> the board in question

    """
    def move_piece(self, piece, coords, board = None):
        if board == None:
            board = self.board
        #if coords in self.get_positions(piece, board):
        if piece.get_type() == "king" and piece.get_untouched() == True and \
            (piece.get_position()[0] - coords[0] < -1 or piece.get_position()[0] - coords[0] > 1):
            #since get_positions already checks if castling is possible, move_piece does not need to check
            if piece.get_position()[0] - coords[0] < -1:
                index1 = board.index(self.get_piece((coords[0]-1, coords[1])))
                index2 = board.index(self.get_piece((1,1)))
                board[index1], board[index2] = board[index2], board[index1]
            elif piece.get_position()[0] - coords[0] > 1:
                index1 = board.index(self.get_piece((coords[0]+1, coords[1])))
                index2 = board.index(self.get_piece((8,1)))
                board[index1], board[index2] = board[index2], board[index1]
            piece.position = coords
        else:
            index1 = board.index(piece)
            index2 = board.index(self.get_piece(coords, board))
            position1 = piece.get_position()
            if self.get_piece(coords, board).piece == True:
                board[index1], board[index2] = board[index2], Piece(position1, "Entity", "neutral")
            else:
                board[index1], board[index2] = board[index2], board[index1]
                self.get_piece(coords, board).position = position1
            piece.position = coords
        piece.set_untouched()
        return board
        

    """
    Checks if this team is in check

    Returns: True/False depending if the team is in check
    """
    def check_checker(self, board = None):
        if board == None:
            board = self.board
        for i in board:
            if i.get_type() != "Entity" and i.get_colour() != self.team:
                for j in self.get_positions(i, board, prune = False):
                    print(i,self.get_pieces_by_type("king", self.team, board)[0].get_position(), j)
                    if j == self.get_pieces_by_type("king", self.team, board)[0].get_position():
                        return True
        
        return False

    """
    Prunes all possible move coordinates that would result in a check
    """
    def prune_checks(self, piece, possible, board):
        possible2 = []
        for i in possible:
            board_copy = self.move_piece(piece, i, board)
            if self.check_checker(board_copy) == False:
                possible2.append(i)
        return possible2

    """
    Checks if this team is in checkmate

    Returns: True/False depending if the team is in checkmate
    """
    def checkmate_checker(self):
        board = self.board
        king = self.get_pieces_by_type("king", self.team, board)[0]
        possible = self.get_positions(king, board)
        if len(possible) == 0:
            return True
        return False

         
            
   





                


    


