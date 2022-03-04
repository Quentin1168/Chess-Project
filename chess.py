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
        self.string = "~~~rr~l~~pqk~pp~~~~~~~~p~~p~~~~~p~~kKK~QP~~P~~~~~PP~~~PP~L~~RR~~"
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
    def convert_to_string(self):
        string = ""
        for i in self.board:
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
    def get_coords(self, coords):
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
    def get_pieces_by_type(self, type, colour):
        pieces = []
        for i in self.board:
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
    def get_positions(self, piece):
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
            possible += self.diagonal_expansion(piece)
        elif type == "rook":
            possible += self.perpedicular_expansion(piece)
        elif type == "queen":
            possible += self.perpedicular_expansion(piece)
            possible += self.diagonal_expansion(piece)
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
            
            if self.check == False and self.get_pieces_by_type("king", self.team)[0].get_untouched() == True and \
                self.get_pieces_by_type("rook", self.team)[0].get_untouched() == True and self.get_pieces_by_type("rook", self.team)[1].get_untouched() == True:
                    possible += self.castling_possible_positions(coords)
            
        elif type == "pawn":
            if self.team != piece.get_colour():
                if self.get_coords((coords[0], coords[1]-1)).piece == False:
                    possible.append((coords[0], coords[1]-1))
                    if piece.get_untouched() == True:
                        possible.append((coords[0], coords[1]-2))

                #Check if the future coords are out of bounds or not
                if 0 < coords[0]+1 < 9 and 0 < coords[1]-1 < 9 and self.get_coords((coords[0]+1, coords[1]-1)).is_piece():
                    if team[self.get_coords((coords[0]+1, coords[1]-1)).get_colour()] == piece.get_colour():
                        possible.append((coords[0]+1, coords[1]-1))
                if 0 < coords[0]-1 < 9 and 0 < coords[1]-1 < 9 and self.get_coords((coords[0]-1, coords[1]-1)).is_piece():
                    if team[self.get_coords((coords[0]-1, coords[1]-1)).get_colour()] == piece.get_colour():
                        possible.append((coords[0]-1, coords[1]-1))
            else:
                if self.get_coords((coords[0], coords[1]+1)).piece == False:
                    possible.append((coords[0], coords[1]+1))
                    if piece.get_untouched() == True:
                        possible.append((coords[0], coords[1]+2))

                if 0 < coords[0]+1 < 9 and 0 < coords[1]+1 < 9 and self.get_coords((coords[0]+1, coords[1]+1)).is_piece():
                    if team[self.get_coords((coords[0]+1, coords[1]+1)).get_colour()] == piece.get_colour():
                        possible.append((coords[0]+1, coords[1]+1))
                if 0 < coords[0]-1 < 9 and 0 < coords[1]+1 < 9 and self.get_coords((coords[0]-1, coords[1]+1)).is_piece():
                    if team[self.get_coords((coords[0]-1, coords[1]+1)).get_colour()] == piece.get_colour():
                        possible.append((coords[0]-1, coords[1]+1))


        if len(possible) != 0:
            pruned_possible = []
            
            for i in possible:
                if 0 < i[0] < 9 and 0 < i[1] < 9 and self.get_coords(i).get_colour() != piece.get_colour():
                    pruned_possible.append(i)
            possible = pruned_possible
        return possible
        


    """
    Gets all the possible positions if the castling special move is movable. Specified for both teams.

    Parameters: coords -> the coordinates of the piece in question
    Returns: the possible castling positions of the king
    """
    def castling_possible_positions(self, coords):
        possible = []
        castling_flag_left = True
        castling_flag_right = True
        if self.team == "black":
            for i in [2,3,4]:
                if self.get_coords((i,1)).get_type() != "Entity":
                    castling_flag_left = False
            for i in [7,8]:
                if self.get_coords((i,1)).get_type() != "Entity":
                    castling_flag_right = False
        else:
            for i in [2,3]:
                if self.get_coords((i,1)).get_type() != "Entity":
                    castling_flag_right = False
            for i in [5,6,7]:
                if self.get_coords((i,1)).get_type() != "Entity":
                    castling_flag_left = False
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
    def perpedicular_expansion(self, piece):
        possible = []
        coords = piece.get_position()
        x = coords[0]
        y = coords[1]
        while self.get_coords(coords).get_colour() != self.team\
                 and x < 9:
            x += 1
            possible.append((x, coords[1]))
            if self.get_coords(coords).get_colour() != self.team \
                and self.get_coords(coords).piece == True:
                break
        x = coords[0]
        while self.get_coords(coords).get_colour() != self.team\
                and x > 0:
            x -= 1
            possible.append((x, coords[1]))
            if self.get_coords(coords).get_colour() != self.team \
                and self.get_coords(coords).piece == True:
                break
        x = coords[0]
        while self.get_coords(coords).get_colour() != self.team\
                and y < 9:
            y += 1
            possible.append((coords[0], y))
            if self.get_coords(coords).get_colour() != self.team \
                and self.get_coords(coords).piece == True:
                break
        y = coords[1]
        while self.get_coords(coords).get_colour() != self.team\
                and y > 0:
            y -= 1
            possible.append((coords[0], y))
            if self.get_coords(coords).get_colour() != self.team \
                and self.get_coords(coords).piece == True:
                break
        y = coords[1]
        return possible

    """
    Used for the bishop and the queen, for finding the possible diagonal positions those given pieces can go
    before they come in contact with the border of the board or an enemy piece.

    Parameters: piece -> the piece in question
    Returns: the possible diagonal positons that the piece can move to
    """
    def diagonal_expansion(self, piece):
        possible = []
        coords = piece.get_position()
        x = coords[0]
        y = coords[1]
        while self.get_coords(coords).get_colour() != self.team\
                 and x < 9 and y < 9:
            x += 1
            y += 1
            possible.append((x,y))
            if self.get_coords(coords).get_colour() != self.team \
                and self.get_coords(coords).piece == True:
                break
        x = coords[0]
        y = coords[1]
        while self.get_coords(coords).get_colour() != self.team\
                and x < 9 and y > 0:
            x += 1
            y -= 1
            possible.append((x, y))
            if self.get_coords(coords).get_colour() != self.team \
                and self.get_coords(coords).piece == True:
                break
        x = coords[0]
        y = coords[1]
        while self.get_coords(coords).get_colour() != self.team\
                and x > 0 and y < 9:
            x -= 1
            y += 1
            possible.append((x, y))
            if self.get_coords(coords).get_colour() != self.team \
                and self.get_coords(coords).piece == True:
                break
        x = coords[0]
        y = coords[1]
        while self.get_coords(coords).get_colour() != self.team\
                and x > 0 and y > 0:
            x -= 1
            y -= 1
            possible.append((x, y))
            if self.get_coords(coords).get_colour() != self.team \
                and self.get_coords(coords).piece == True:
                break

        return possible

    """
    Moves the specified piece to the specified coordinates, if the coordinates contain a piece there, take it.coords=
    Also implements the castling special move, if get_positions allows for a castling move.

    Parameters: piece -> the piece in question
                coords -> the coordinates the piece will move to

    """
    def move_piece(self, piece, coords):
        if coords in self.get_positions(piece):
            print("bruh")
            if piece.get_type() == "king" and piece.get_untouched() == True:
                #since get_positions already checks if castling is possible, move_piece does not need to check
                if piece.get_position()[0] - coords[0] < -1:
                    index1 = self.board.index(self.get_coords((coords[0]-1, coords[1])))
                    index2 = self.board.index(self.get_coords((1,1)))
                    self.self.board[index1], self.board[index2] = self.board[index2], self.board[index1]
                elif piece.get_position()[0] - coords[0] > 1:
                    index1 = self.board.index(self.get_coords((coords[0]+1, coords[1])))
                    index2 = self.board.index(self.get_coords((8,1)))
                    self.board[index1], self.board[index2] = self.board[index2], self.board[index1]
                piece.position = coords
            else:
                print("bruh")
                index1 = self.board.index(piece)
                index2 = self.board.index(self.get_coords(coords))
                position1 = piece.get_position()
                if self.get_coords(coords).piece == True:
                    self.board[index1], self.board[index2] = self.board[index2], Piece(position1, "Entity", "neutral")
                else:
                    self.board[index1], self.board[index2] = self.board[index2], self.board[index1]
                    self.get_coords(coords).position = position1
                piece.position = coords
            piece.set_untouched()
            self.convert_to_string()
            self.post_move_analysis()

    """
    Checks if this team is in check

    Returns: True/False depending if the team is in check
    """
    def check_checker(self):
        for i in self.board:
            if i.get_type() != "Entity" and i.get_colour() != self.team:
                for j in self.get_positions(i):
                    if j == self.get_pieces_by_type("king", self.team)[0].get_position():
                        return True
        
        return False

    """
    Checks if this team is in checkmate

    Returns: True/False depending if the team is in checkmate
    """
    def checkmate_checker(self):
        possible = self.get_positions(self.get_pieces_by_type("king", self.team)[0])
        possible2 = []
        possible.append(self.get_pieces_by_type("king", self.team)[0].get_position())
        enemy = [piece for piece in self.board if piece.piece == True and piece.get_colour() != self.team]
        
        for i in possible:
            match = False
            for j in enemy:
                if match:
                    continue
                for k in self.get_positions(j):
                    if i == k:
                        possible2.append(i)
                        match = True
                        break

        if len(possible2) == len(possible):
            return True
        else:
            return False

    """
    Checks for check and checkmate, done after the client moves
    If the client was in check and is still in check after the move, declare checkmate
    If the checkmate checker returns True, declare checkmate
    """
    def post_move_analysis(self):
        if self.check == True and self.check_checker() == True:
            self.checkmate = True
        elif self.check_checker() == True and self.check == False:
            self.check = True
        elif self.checkmate_checker() == True:
            self.checkmate = True

                


    


