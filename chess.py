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
    ("white", "pawn"): "P",
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
        super().__init__(position)
        self.id = "Piece"
        self.type = type
        self.colour = colour
        self.untouched = True

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
        self.untoouched = False

"""
ChessBoard class covers the board and the tiles on it
"""
class ChessBoard:
    """
    The board can be represented by a 64 character long string, which each character representing a tile of the board.
    The reason for this compact representation is for ease of transmitting the information to the server and other players.
    It also makes it easy for both players having different perspecitves of the board, where they are "facing" each other.

    Client-side, the board is represented as a list of Entity and Piece objects.
    """
    def __init__(self):
        self.string = "rkbqlbkrpppppppp~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PPPPPPPPRKBQLBKR"
        self.board = []
        self.convert_to_string()
        self.selected = None
        self.check = False
        self.team = "white"

    """
    Convert the string to a list of Entity and Piece Objects
    """
    def convert_from_string(self):
        x = 1
        y = 1
        colour = "black"
        board = []
        for i in self.string:
            
            if x == 8:
                x = 1
                y += 1

            if i.isupper():
                colour = "white"
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
                board.append(Entity((x,y)))
            x += 1
        self.board = board

    """
    Converts the list of Piece and Entity Objects into string format
    """
    def convert_to_string(self):
        string = ""
        for i in self.board:
            if i.get_type() == "Entity":
                string += "~"
            else:
                string += piece_to_string[(i.get_colour(), i.get_type())]

        return string

    """
    Gets the specific Entity or Piece Object from the coordinates specified.
    
    Parameters: coords -> the coordinates in tuple form
    Returns: Entity or Piece object
    """
    def get_piece_from_coords(self, coords):
        x = coords[0]
        y = coords[1]

        for i in self.board:
            if i.get_position()[0] == x and i.get_position()[1] == y:
                return i

    """
    Gets Piece objects by type

    Parameter: type -> the type of the piece specified
    Returns: list of Piece objects of the type
    """
    def get_pieces_by_type(self, type):
        pieces = []
        for i in self.board:
            if i.get_type() == type:
                pieces.append(i)

        return pieces
        
    """
    Gets all the possible movable positions of the specified position. Bad positions
    are pruned out using prune_possible_positions().
    Special rules such as Castling and Pawn diagonal piece taking are covered here.

    Parameters: piece -> A Piece Object of the Chess board
    Returns: a list of the possible positions that the piece can go.
    """
    def get_possible_positions(self, piece):
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
            possible.append(self.diagonal_expansion(piece))
        elif type == "rook":
            possible.append(self.perpedicular_expansion(piece))
        elif type == "queen":
            possible.append(self.perpedicular_expansion(piece))
            possible.append(self.diagonal_expansion(piece))
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
            if self.check == False and self.get_pieces_by_type("king")[0].get_untouched == True and self.get_pieces_by_type("rook")[0].get_untouched == True \
                and self.get_pieces_by_type("rook")[1].get_untouched == True:
                possible.append(self.castling_possible_positions(coords))

        elif type == "pawn":
            if piece.get_untouched() == True:
                possible.append((coords[0], coords[1]-2))
            possible.append((coords[0], coords[1]-1))
            # Append these two diagonal spots, pruned if they do not have opposing pieces on them.
            possible.append((coords[0]+1, coords[1]-1))
            possible.append((coords[0]-1, coords[1]-1))
        
        self.prune_possible_positions(possible)


    def prune_possible_positions(self, possible):
        pruned_possible = []
        pruned_possible2 = []
        for i in possible:
            if i[0] > 0 and i[0] < 9 and i[1] > 0 and i[1] < 9:
                pruned_possible.append(i)
        for i in pruned_possible:
            if self.get_piece_from_coords(i).get_id() == "Entity":
                pruned_possible2.append(i)
            elif self.get_piece_from_coords(i).get_colour != self.team:
                pruned_possible2.append(i)
        return pruned_possible2

    def castling_possible_positions(self, coords):
        possible = []
        castling_flag_left = True
        castling_flag_right = True
        if self.team == "white":
            for i in [2,3,4]:
                if self.get_piece_from_coords((i,8)).get_id() != "Entity":
                    castling_flag_left = False
            for i in [7,8]:
                if self.get_piece_from_coords((i,8)).get_id() != "Entity":
                    castling_flag_right = False
        else:
            for i in [2,3]:
                if self.get_piece_from_coords((i,8)).get_id() != "Entity":
                    castling_flag_left = False
            for i in [5,7,8]:
                if self.get_piece_from_coords((i,8)).get_id() != "Entity":
                    castling_flag_right = False
        if castling_flag_left == True:
            possible.append((coords[0]+2, coords[1]))
        if castling_flag_right == True:
            possible.append((coords[0]-2, coords[1]))
        
        return possible

    def move_piece(self, piece, coords):
        index1 = self.board.index(piece)
        index2 = self.board.index(self.get_piece_from_coords(coords))
        self.board[index1], self.board[index2] = self.board[index2], self.board[index1]

    def perpedicular_expansion(self, piece):
        possible = []
        coords = piece.get_position()
        while (self.get_piece_from_coords(coords).get_type() == "Entity" or self.get_piece_from_coords(coords).get_colour() != self.team)\
                 and coords[0] < 9:
            coords[0] += 1
            possible.append((coords[0], coords[1]))
            coords = piece.get_position()
        while (self.get_piece_from_coords(coords).get_type() == "Entity" or self.get_piece_from_coords(coords).get_colour() != self.team)\
                and coords[0] > 0:
            coords[0] -= 1
            possible.append((coords[0], coords[1]))
        coords = piece.get_position()
        while (self.get_piece_from_coords(coords).get_type() == "Entity" or self.get_piece_from_coords(coords).get_colour() != self.team)\
                and coords[1] < 9:
            coords[1] += 1
            possible.append((coords[0], coords[1]))
        coords = piece.get_position()
        while (self.get_piece_from_coords(coords).get_type() == "Entity" or self.get_piece_from_coords(coords).get_colour() != self.team)\
                and coords[1] > 0:
            coords[1] -= 1
            possible.append((coords[0], coords[1]))

        return possible
    def diagonal_expansion(self, piece):
        possible = []
        coords = piece.get_position()
        while (self.get_piece_from_coords(coords).get_type() == "Entity" or self.get_piece_from_coords(coords).get_colour() != self.team)\
                 and coords[0] < 9 and coords[1] < 8:
            coords[0] += 1
            coords[1] += 1
            possible.append((coords[0], coords[1]))
        coords = piece.get_position()
        while (self.get_piece_from_coords(coords).get_type() == "Entity" or self.get_piece_from_coords(coords).get_colour() != self.team)\
                and coords[0] < 9 and coords[1] > 0:
            coords[0] += 1
            coords[1] -= 1
            possible.append((coords[0], coords[1]))
        coords = piece.get_position()
        while (self.get_piece_from_coords(coords).get_type() == "Entity" or self.get_piece_from_coords(coords).get_colour() != self.team)\
                and coords[0] > 0 and coords[1] < 9:
            coords[0] -= 1
            coords[1] += 1
            possible.append((coords[0], coords[1]))
        coords = piece.get_position()
        while (self.get_piece_from_coords(coords).get_type() == "Entity" or self.get_piece_from_coords(coords).get_colour() != self.team)\
                and coords[0] > 0 and coords[1] > 0:
            coords[0] -= 1
            coords[1] -= 1
            possible.append((coords[0], coords[1]))

        return possible
