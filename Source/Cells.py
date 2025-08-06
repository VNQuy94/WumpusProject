class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_visited = False # True/False
        self.is_safe = None  # True/False/None

    def set_is_safe(self, bool):
        self.is_safe = bool

    def set_is_visited(self, bool):
        self.is_visited = bool