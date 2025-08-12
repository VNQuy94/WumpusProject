import random

class RandomAgent:
    def __init__(self, size):
        self.size = size
        self.current_position = (0, 0)
        self.direction = "East"
        self.has_gold = False
        self.has_arrow = True
        self.weight_actions = {
            "Move Forward": 45,
            "Turn Left": 20,
            "Turn Right": 20,
            "Shoot": 5
        }

        self.climb_weight = 20
        self.direction_list = ["East", "South", "West", "North"]

    def valid_action(self):
        x, y = self.current_position
        if self.direction == "East" and y + 1 >= self.size:
            return False
        if self.direction == "West" and y - 1 < 0:
            return False
        if self.direction == "North" and x + 1 >= self.size: # Giả sử (0,0) là góc dưới-trái
            return False
        if self.direction == "South" and x - 1 < 0:
            return False
        return True
        
    def make_decision(self, percepts):
        possible_actions = []
        weights = []

        possible_actions.extend(self.weight_actions.keys())
        weights.extend(self.weight_actions.values())

        if percepts[2]:
            self.has_gold = True
            return "Grab"
        
        if self.current_position == (0, 0):
            possible_actions.append("Climb")
            weights.append(self.climb_weight)

        if self.valid_action():
            possible_actions.append("Move Forward")
            weights.append(self.weight_actions["Move Forward"])

        possible_actions.append("Turn Left")
        weights.append(self.weight_actions["Turn Left"])
        possible_actions.append("Turn Right")
        weights.append(self.weight_actions["Turn Right"])
        possible_actions.append("Shoot")
        weights.append(self.weight_actions["Shoot"])

        chosen_action = random.choices(possible_actions, weights=weights, k=1)[0]
        return chosen_action
    
    def agent_update_state(self, action):
        if action == "Move Forward":
            if self.valid_action():
                x, y = self.current_position
                if self.direction == "East": self.current_position = (x, y + 1)
                elif self.direction == "West": self.current_position = (x, y - 1)
                elif self.direction == "North": self.current_position = (x + 1, y)
                elif self.direction == "South": self.current_position = (x - 1, y)
        
        elif action == "Turn Left":
            current_index = self.direction_list.index(self.direction)
            self.direction = self.direction_list[(current_index - 1 + 4) % 4]

        elif action == "Turn Right":
            current_index = self.direction_list.index(self.direction)
            self.direction = self.direction_list[(current_index + 1) % 4]



