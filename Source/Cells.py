class Cell:
    def __init__(self, x, y):
        # Represents a single cell in the Wumpus World knowledge base.
        self.is_visited = False   # Whether the agent has visited this cell
        self.is_safe = None       # Safety status: True (safe), False (unsafe), None (unknown)
        self.has_wumpus = False   # Whether the cell is known to contain a Wumpus
        self.has_pit = False      # Whether the cell is known to contain a Pit
        self.turn_visited = 0     # Turn number when the cell was visited

    def set_is_safe(self, value: bool):
        """
        Set whether the cell is safe.
        
        Args:
            value (bool): True if safe, False if unsafe.
        """
        self.is_safe = value

    def set_is_visited(self, value: bool):
        """
        Mark the cell as visited or unvisited.
        
        Args:
            value (bool): True if visited, False otherwise.
        """
        self.is_visited = value

    def set_has_wumpus(self, value: bool):
        """
        Set whether the cell contains a Wumpus.
        
        Args:
            value (bool): True if it contains a Wumpus, False otherwise.
        """
        self.has_wumpus = value

    def set_has_pit(self, value: bool):
        """
        Set whether the cell contains a Pit.
        
        Args:
            value (bool): True if it contains a Pit, False otherwise.
        """
        self.has_pit = value

    def set_turn_visited(self, value):
        """
        Record the turn number when the cell was visited.
        
        Args:
            value (int): The turn count when visited.
        """
        self.turn_visited = value
