import random

# Constants
NUM_GOLD = 1
NUM_ARROW = 1

# Cell contents
PIT = 'P'
WUMPUS = 'W'
GOLD = 'G'
STENCH = 'S'
BREEZE = 'B'
EMPTY = '.'

class World:
    def __init__(self, N=8, num_wumpus=2, p_pit=0.2):
        self.num_gold = NUM_GOLD
        self.num_arrow = NUM_ARROW
        self.size = N
        self.num_wumpus = num_wumpus
        self.p_pit = p_pit

        self.world = self.create_world()

    def create_world(self):
        # Initialize an empty world
        result = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]

        # Randomly place Wumpus, avoiding the start cell (0, 0)
        for i in range(self.num_wumpus):
            row = 0
            col = 0
            while (row == 0 and col == 0) or result[row][col] != '.': 
                row = random.randint(0, self.size - 1)
                col = random.randint(0, self.size - 1)

            result[row][col] = WUMPUS

        # Randomly place pits based on the probability p_pit
        for i in range(self.size):
            for j in range(self.size):
                rand_num = random.random()
                if rand_num <= self.p_pit and result[i][j] == '.':
                    result[i][j] = PIT

        # Randomly place gold in an empty cell
        for i in range(self.num_gold):
            row = random.randint(0, self.size-1)
            col = random.randint(0, self.size-1)
            while result[row][col] != '.':
                row = random.randint(0, self.size-1)
                col = random.randint(0, self.size-1)

            result[row][col] = GOLD

        # Add "stench" near Wumpus and "breeze" near pits
        for i in range(len(result)):
            for j in range(len(result)):
                if result[i][j] == WUMPUS:
                    self.add_effect(result, i, j, STENCH)

                if result[i][j] == PIT:
                    self.add_effect(result, i, j, BREEZE)

        return result
    
    def add_effect(self, world, row, col, effect):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                if world[new_row][new_col] == EMPTY:
                    world[new_row][new_col] = effect
                else:
                    # If there's already an effect, we don't overwrite it
                    if effect not in world[new_row][new_col]:
                        world[new_row][new_col] += f", {effect}"