from PIL import Image, ImageTk



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

    def get_type(self):
        return self.type
    
    def get_colour(self):
        return self.colour

    def get_id(self):
        return self.id
    

