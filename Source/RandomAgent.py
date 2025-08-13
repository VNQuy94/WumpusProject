import random

class RandomAgent:
    def __init__(self, size):
        """
        Initialize a RandomAgent that moves randomly in the Wumpus World.
        
        Args:
            size (int): The size of the world (N x N grid).
        """
        self.size = size
        self.current_pos = (0, 0)      # Agent starts at the bottom-left corner (0,0)
        self.direction = "East"        # Initial facing direction
        self.has_gold = False          # Whether the agent has collected gold
        self.has_arrow = True          # Whether the agent still has the arrow

        # Weights for each action (used for probability-based random choice)
        self.weight_actions = {
            "Move Forward": 45,
            "Turn Left": 20,
            "Turn Right": 20,
            "Shoot": 5
        }

        self.climb_weight = 20         # Weight for the "Climb" action
        self.direction_list = ["East", "South", "West", "North"]  # Clockwise direction order

    def set_arrow(self, value):
        """
        Set whether the agent has an arrow.
        """
        self.has_arrow = value

    def valid_action(self):
        """
        Check if the agent can move forward in the current direction 
        without going out of bounds.

        Returns:
            bool: True if the move is within bounds, False otherwise.
        """
        x, y = self.current_pos
        if self.direction == "East" and y + 1 >= self.size:
            return False
        if self.direction == "West" and y - 1 < 0:
            return False
        if self.direction == "North" and x + 1 >= self.size:  # Assume (0,0) is bottom-left
            return False
        if self.direction == "South" and x - 1 < 0:
            return False
        return True
        
    def make_decision(self, percepts):
        """
        Decide the next action randomly based on weighted probabilities.

        Args:
            percepts (list): A list of percepts [Stench, Breeze, Glitter, Scream].

        Returns:
            str: The chosen action.
        """
        possible_actions = []
        weights = []

        # Add base actions and their weights
        possible_actions.extend(self.weight_actions.keys())
        weights.extend(self.weight_actions.values())

        # If gold is detected (Glitter), grab it immediately
        if percepts[2]:
            self.has_gold = True
            return "Grab"
        
        # If at the starting position (0,0), add the option to climb
        if self.current_pos == (0, 0):
            possible_actions.append("Climb")
            weights.append(self.climb_weight)

        # Add "Move Forward" again if valid (increases its selection chance)
        if self.valid_action():
            possible_actions.append("Move Forward")
            weights.append(self.weight_actions["Move Forward"])

        # Add turning actions
        possible_actions.append("Turn Left")
        weights.append(self.weight_actions["Turn Left"])
        possible_actions.append("Turn Right")
        weights.append(self.weight_actions["Turn Right"])

        # Add shooting action
        possible_actions.append("Shoot")
        weights.append(self.weight_actions["Shoot"])

        # Randomly choose one action based on weights
        chosen_action = random.choices(possible_actions, weights=weights, k=1)[0]
        return chosen_action
    
    def agent_update_state(self, action):
        """
        Update the agent's internal state after performing an action.
        
        Args:
            action (str): The action that the agent performed.
        """
        if action == "Move Forward":
            if self.valid_action():
                x, y = self.current_pos
                if self.direction == "East":
                    self.current_pos = (x, y + 1)
                elif self.direction == "West":
                    self.current_pos = (x, y - 1)
                elif self.direction == "North":
                    self.current_pos = (x + 1, y)
                elif self.direction == "South":
                    self.current_pos = (x - 1, y)
        
        elif action == "Turn Left":
            current_index = self.direction_list.index(self.direction)
            self.direction = self.direction_list[(current_index - 1 + 4) % 4]

        elif action == "Turn Right":
            current_index = self.direction_list.index(self.direction)
            self.direction = self.direction_list[(current_index + 1) % 4]
