import random
import GameCoords
import Agent

# Constants representing objects/effects in the Wumpus World
NUM_GOLD = 1       # Number of gold pieces in the world
PIT = 'P'          # Pit symbol
WUMPUS = 'W'       # Wumpus symbol
GOLD = 'G'         # Gold symbol
STENCH = 'S'       # Stench symbol (near Wumpus)
BREEZE = 'B'       # Breeze symbol (near Pit)
EMPTY = '.'        # Empty cell symbol

class World:
    def __init__(self, N, num_wumpus, p_pit):
        self.num_gold = NUM_GOLD              # Always 1 piece of gold
        self.size = N                         # Size of the grid (NxN)
        self.num_wumpus = num_wumpus          # Number of Wumpus to place
        self.p_pit = p_pit                    # Probability of placing a pit in a cell
        self.world = self.create_world()      # Generate the world grid
        self.agent_position = (0, 0)          # Agent starts at coordinate (0, 0)
        self.agent_direction = "East"         # Initial facing direction
        self.action_count = 0                 # Tracks actions for moving Wumpus mode

    def is_not_origin(self, row, col):
        # Check if a position is NOT the starting cell (0,0) in array coordinates
        start_row, start_col = GameCoords.game_to_array_coords(0, 0, self.size)
        return (row != start_row or col != start_col)

    def create_world(self):
        # Initialize an empty NxN world grid
        world = [['.' for _ in range(self.size)] for _ in range(self.size)]

        # Randomly place Wumpus in cells (avoiding start cell)
        wumpus_count = 0
        while wumpus_count < self.num_wumpus:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)

            if self.is_not_origin(row, col) and not world[row][col] == WUMPUS:
                world[row][col] = WUMPUS
                self.add_effect(world, row, col, STENCH)  # Add stench to adjacent cells
                wumpus_count += 1

        # Randomly place pits based on probability p_pit
        for i in range(self.size):
            for j in range(self.size):
                if self.is_not_origin(i, j) and random.random() <= self.p_pit and not world[i][j] == WUMPUS:
                    if not world[i][j] == BREEZE and not world[i][j] == STENCH:
                        world[i][j] = PIT
                        self.add_effect(world, i, j, BREEZE)  # Add breeze to adjacent cells

        # Randomly place gold in an empty cell
        gold_count = 0
        while gold_count < self.num_gold:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)
            if not (world[row][col] == WUMPUS or world[row][col] == PIT):
                if EMPTY in world[row][col]:
                    world[row][col] = GOLD
                    gold_count += 1
                else:
                    world[row][col] += GOLD
                    gold_count += 1
        
        return world

    def add_effect(self, world, row, col, effect):
        # Add an effect (Stench/Breeze) to the adjacent cells around (row, col)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                if effect == STENCH and STENCH not in world[new_row][new_col]:
                    if not WUMPUS in world[new_row][new_col] and not PIT in world[new_row][new_col]:
                        if EMPTY in world[new_row][new_col]:
                            world[new_row][new_col] = STENCH
                        else:
                            world[new_row][new_col] += STENCH

                elif effect == BREEZE and BREEZE not in world[new_row][new_col]:
                    if not WUMPUS in world[new_row][new_col] and not PIT in world[new_row][new_col]:
                        if EMPTY in world[new_row][new_col]:
                            world[new_row][new_col] = BREEZE
                        else:
                            world[new_row][new_col] += BREEZE

    def get_percepts(self, x, y):
        """Return percepts at cell (x, y) as a list: [stench, breeze, glitter]"""
        row, col = GameCoords.game_to_array_coords(x, y, self.size)

        stench = STENCH in self.world[row][col]
        breeze = BREEZE in self.world[row][col]
        glitter = GOLD in self.world[row][col]
        return [stench, breeze, glitter]
    
    def perform_agent_action(self, action):
        # Perform an action and return percepts + scream indicator if applicable
        percepts = self.get_percepts(self.agent_position[0], self.agent_position[1])
        x, y = self.agent_position
        row, col = GameCoords.game_to_array_coords(x, y, self.size)
        
        # Grab action: pick up gold if present
        if action == "Grab":
            if GOLD in self.world[row][col]:
                self.world[row][col] = self.world[row][col].replace(GOLD, EMPTY)
                print(f"Agent picked up gold at ({x}, {y})")
                percepts = self.get_percepts(self.agent_position[0], self.agent_position[1])
                return percepts + [False]            
        
        # Move Forward: move agent in the current facing direction
        elif action == "Move Forward":
            if self.agent_direction == "East":
                if y + 1 < self.size:
                    self.agent_position = (x, y + 1)
                    percepts = self.get_percepts(x, y + 1)

            elif self.agent_direction == "West":
                if y - 1 >= 0:
                    self.agent_position = (x, y - 1)
                    percepts = self.get_percepts(x, y - 1)

            elif self.agent_direction == "North":
                if x + 1 < self.size:
                    self.agent_position = (x + 1, y)
                    percepts = self.get_percepts(x + 1, y)

            elif self.agent_direction == "South":
                if x - 1 >= 0:
                    self.agent_position = (x - 1, y)
                    percepts = self.get_percepts(x - 1, y)

            # After moving, check if agent encounters a hazard
            row, col = GameCoords.game_to_array_coords(self.agent_position[0], self.agent_position[1], self.size)
            if WUMPUS in self.world[row][col]:
                print(f"Agent killed by Wumpus at ({self.agent_position[0]}, {self.agent_position[1]})")
                return None
            elif PIT in self.world[row][col]:
                print(f"Agent fell into Pit at ({self.agent_position[0]}, {self.agent_position[1]})")
                return None
            
            return percepts + [False]

        # Turning left changes direction counter-clockwise
        direction_list = ["East", "South", "West", "North"]
        direction_index = direction_list.index(self.agent_direction)
        if action == "Turn Left":
            self.agent_direction = direction_list[(direction_index - 1) % 4]
            return percepts + [False]

        # Turning right changes direction clockwise
        if action == "Turn Right":
            self.agent_direction = direction_list[(direction_index + 1) % 4]
            return percepts + [False]
        
        # Shooting: check in the facing direction if Wumpus is hit
        if action == "Shoot":
            if self.agent_direction == "East":
                for j in range(col + 1, self.size):
                    if WUMPUS in self.world[row][j]:
                        self.world[row][j] = self.world[row][j].replace(WUMPUS, '')
                        self.clear_effects(row, j, STENCH)
                        percepts = self.get_percepts(x, y)
                        return percepts + [True]
                return percepts + [False]
                    
            elif self.agent_direction == "West":
                for j in range(col - 1, -1, -1):
                    if WUMPUS in self.world[row][j]:
                        self.world[row][j] = self.world[row][j].replace(WUMPUS, '')
                        self.clear_effects(row, j, STENCH)
                        percepts = self.get_percepts(x, y)
                        return percepts + [True]
                return percepts + [False]
                    
            elif self.agent_direction == "North":
                for i in range(row - 1, -1, -1):
                    if WUMPUS in self.world[i][col]:
                        self.world[i][col] = self.world[i][col].replace(WUMPUS, '')
                        self.clear_effects(i, col, STENCH)
                        percepts = self.get_percepts(x, y)
                        return percepts + [True]
                return percepts + [False]
            
            elif self.agent_direction == "South":
                for i in range(row + 1, self.size):
                    if WUMPUS in self.world[i][col]:
                        self.world[i][col] = self.world[i][col].replace(WUMPUS, '')
                        self.clear_effects(i, col, STENCH)
                        percepts = self.get_percepts(x, y)
                        return percepts + [True]
                return percepts + [False]

    def move_wumpus(self):
        """Move Wumpus to a random adjacent valid cell (for Moving Wumpus mode)"""
        wumpus_locations = []
        # Find all current Wumpus positions
        for r in range(self.size):
            for c in range(self.size):
                if WUMPUS in self.world[r][c]:
                    wumpus_locations.append((r, c))
        
        occupied_cells = set(wumpus_locations)  # Track cells currently occupied by Wumpus
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Possible move directions: N, S, W, E
        moves = []
        for (row, col) in wumpus_locations:
            random.shuffle(directions)  # Randomize movement order
            for dr, dc in directions:
                new_r, new_c = row + dr, col + dc
                if (0 <= new_r < self.size and 0 <= new_c < self.size and
                    PIT not in self.world[new_r][new_c] and
                    (new_r, new_c) not in occupied_cells):
                    # Move Wumpus to new cell
                    occupied_cells.discard((row, col))
                    occupied_cells.add((new_r, new_c))
                    moves.append(((row, col), (new_r, new_c)))
                    break

        # Apply all recorded moves
        for (old_r, old_c), (new_r, new_c) in moves:
            self.world[old_r][old_c] = self.world[old_r][old_c].replace(WUMPUS, '')
            if self.world[old_r][old_c] == '':
                self.world[old_r][old_c] = EMPTY
            self.clear_effects(old_r, old_c, STENCH)  # Remove stench from around old position

            self.world[new_r][new_c] += WUMPUS
            self.add_effect(self.world, new_r, new_c, STENCH)  # Add stench around new position

    def clear_effects(self, row, col, effect):
        """Remove a specific effect (e.g., Stench) from adjacent cells"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                if effect in self.world[new_row][new_col]:
                    if self.world[new_row][new_col] == effect:
                        self.world[new_row][new_col] = self.world[new_row][new_col].replace(effect, EMPTY)
                    else:
                        self.world[new_row][new_col] = self.world[new_row][new_col].replace(effect, '')

    def check_wumpus_eat_agent(self):
        """Check if the agent is in the same cell as a Wumpus (agent dies)"""
        x, y = self.agent_position
        row, col = GameCoords.game_to_array_coords(x, y, self.size)
        if WUMPUS in self.world[row][col]:
            return True
        return False 
    
    def perform_agent_random(self, action, agent: Agent):
        """Perform agent's random action (used for simulation/testing)"""
        x, y = self.agent_position
        row, col = GameCoords.game_to_array_coords(x, y, self.size)
        
        # Climb out of the cave
        if action == "Climb":
            if agent.has_gold and agent.current_pos == (0, 0):
                print("Agent climbed out at (0,0) with gold!")
            else:
                print("Agent climbed out without gold")
        
        # Grab gold if present
        if action == "Grab":
            if GOLD in self.world[row][col]:
                self.world[row][col] = self.world[row][col].replace(GOLD, EMPTY)
                print(f"Agent picked up gold at ({x}, {y})")      
        
        # Move forward in the current facing direction
        elif action == "Move Forward":
            if self.agent_direction == "East":
                if y + 1 < self.size:
                    self.agent_position = (x, y + 1)

            elif self.agent_direction == "West":
                if y - 1 >= 0:
                    self.agent_position = (x, y - 1)

            elif self.agent_direction == "North":
                if x + 1 < self.size:
                    self.agent_position = (x + 1, y)

            elif self.agent_direction == "South":
                if x - 1 >= 0:
                    self.agent_position = (x - 1, y)

            # Check hazards after moving
            row, col = GameCoords.game_to_array_coords(self.agent_position[0], self.agent_position[1], self.size)
            if WUMPUS in self.world[row][col]:
                print(f"Agent killed by Wumpus at ({self.agent_position[0]}, {self.agent_position[1]})")
                return False
            elif PIT in self.world[row][col]:
                print(f"Agent fell into Pit at ({self.agent_position[0]}, {self.agent_position[1]})")
                return False

        # Turn left (counter-clockwise)
        direction_list = ["East", "South", "West", "North"]
        direction_index = direction_list.index(self.agent_direction)
        if action == "Turn Left":
            self.agent_direction = direction_list[(direction_index - 1) % 4]

        # Turn right (clockwise)
        if action == "Turn Right":
            self.agent_direction = direction_list[(direction_index + 1) % 4]
        
        # Shoot an arrow if the agent has one
        if action == "Shoot" and agent.has_arrow is True:
            if self.agent_direction == "East":
                for j in range(col, self.size):
                    if WUMPUS in self.world[row][j]:
                        self.world[row][j] = self.world[row][j].replace(WUMPUS, '')
                        self.clear_effects(row, j, STENCH)
                        print(f"Arrow hit Wumpus at ({x}, {j})")
                    
            elif self.agent_direction == "West":
                for j in range(y - 1, -1, -1):
                    if WUMPUS in self.world[row][j]:
                        self.world[row][j] = self.world[row][j].replace(WUMPUS, '')
                        self.clear_effects(row, j, STENCH)
                        print(f"Arrow hit Wumpus at ({x}, {j})")
                    
            elif self.agent_direction == "North":
                for i in range(row - 1, self.size):
                    if WUMPUS in self.world[i][col]:
                        self.world[i][col] = self.world[i][col].replace(WUMPUS, '')
                        self.clear_effects(i, col, STENCH)
                        print(f"Arrow hit Wumpus at ({i}, {y})")
            
            elif self.agent_direction == "South":
                for i in range(row + 1):
                    if WUMPUS in self.world[i][col]:
                        self.world[i][col] = self.world[i][col].replace(WUMPUS, '')
                        self.clear_effects(i, col, STENCH)
                        print(f"Arrow hit Wumpus at ({i}, {y})")
                        
            agent.has_arrow = False  # Arrow is used up
                        
        return True
    
    def __str__(self):
        """Return a formatted string representation of the world grid"""
        map_rows = []
        for r in range(self.size):
            # Format each cell to a fixed width for alignment
            formatted_row = [cell.ljust(4) for cell in self.world[r]]
            map_rows.append("".join(formatted_row))
        
        # Join all rows into a multi-line string
        return "\n".join(map_rows)