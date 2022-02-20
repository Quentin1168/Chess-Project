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

class Entity:
    def __init__(self, position):
        self.position = position
        self.id = "Entity"

    def get_position(self):
        return self.position

    def get_id(self):
        return self.id

class Piece(Entity):
    def __init__(self, position, type, colour):
        super().__init__(position)
        self.id = "Piece"
        self.type = type
        self.colour = colour
        self.untouched = True

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

class ChessBoard:
    def __init__(self):
        self.string = "rkbqlbkrpppppppp~~~~~~~~~~~~~~~~~~~~~~~~PPPPPPPPRKBQLBKR"
        self.board = []
        self.convert_to_string()
        self.selected = None

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

    def convert_to_string(self):
        string = ""
        for i in self.board:
            if i.get_type() == "Entity":
                string += "~"
            else:
                string += piece_to_string[(i.get_colour(), i.get_type())]

        return string

    def get_piece_from_coords(self, coords):
        x = coords[0]
        y = coords[1]

        for i in self.board:
            if i.get_position()[0] == x and i.get_position()[1] == y:
                return i
        
    def get_possible_positions(self, piece):
        type = piece.get_type()
        coords = piece.get_position()
        colour = piece.get_colour()
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
            for i in range(1:8):
                possible.append((coords[0]+i, coords[1]+i))
                possible.append((coords[0]+i, coords[1]-i))
                possible.append((coords[0]-i, coords[1]+i))
                possible.append((coords[0]-i, coords[1]-i))
        elif type == "rook":
            for i in range(1:8):
                possible.append((coords[0]+i, coords[1]))
                possible.append((coords[0]-i, coords[1]))
                possible.append((coords[0], coords[1]+i))
                possible.append((coords[0], coords[1]-i))
        elif type == "queen":
            for i in range(1:8):
                possible.append((coords[0]+i, coords[1]+i))
                possible.append((coords[0]+i, coords[1]-i))
                possible.append((coords[0]-i, coords[1]+i))
                possible.append((coords[0]-i, coords[1]-i))
                possible.append((coords[0]+i, coords[1]))
                possible.append((coords[0]-i, coords[1]))
                possible.append((coords[0], coords[1]+i))
                possible.append((coords[0], coords[1]-i))
        elif type == "king":
            possible.append((coords[0]+1, coords[1]+1))
            possible.append((coords[0]+1, coords[1]-1))
            possible.append((coords[0]-1, coords[1]+1))
            possible.append((coords[0]-1, coords[1]-1))
            possible.append((coords[0]+1, coords[1]))
            possible.append((coords[0]-1, coords[1]))
            possible.append((coords[0], coords[1]+1))
            possible.append((coords[0], coords[1]-1))
        elif type == "pawn":
            if piece.get_untouched() == True:
                possible.append((coords[0], coords[1]+2))
            possible.append((coords[0], coords[1]+1))
        
