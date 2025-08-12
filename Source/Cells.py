class Cell:
    def __init__(self, x, y):
        self.is_visited = False  # True/False
        self.is_safe = None      # True/False/None
        self.has_wumpus = False
        self.turn_visited = 0

    def set_is_safe(self, value: bool):
        self.is_safe = value

    def set_is_visited(self, value: bool):
        self.is_visited = value

    def set_has_wumpus(self, value: bool):
        self.has_wumpus = value

    def set_turn_visited(self, value):
        self.turn_visited = value