class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_visited = False # True/False
        self.is_safe = None  # True/False/None
        self.risky_score_pit = 0
        self.risky_score_wumpus = 0

    def set_is_safe(self, bool):
        self.is_safe = bool
        self.risky_score_pit = 0 if bool else self.risky_score_pit
        self.risky_score_wumpus = 0 if bool else self.risky_score_wumpus


    def set_is_visited(self, bool):
        self.is_visited = bool