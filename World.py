import random

NUM_GOLD = 1
NUM_ARROW = 1
PIT = 'P'
WUMPUS = 'W'
GOLD = 'G'
STENCH = 'S'
BREEZE = 'B'

class World:
    def _init_(self, N=8, num_wumpus=2, p_pit=0.2):
        self.num_gold = NUM_GOLD
        self.num_arrow = NUM_ARROW
        self.size = N
        self.num_wumpus = num_wumpus
        self.p_pit = p_pit

        self.world = self.create_world()

    def create_word(self):
        result = [['.' for _ in range(self.size)] for _ in range(self.size)]

        for i in range(self.num_wumpus):
            row = 0
            col = 0
            while (row == 0 and col == 0) or result[row][col] != '.': 
                row = random.randint(0, self.size - 1)
                col = random.randint(0, self.size - 1)

            result[row][col] = WUMPUS

        for i in range(self.size):
            for j in range(self.size):
                rand_num = random.random()
                if rand_num >= self.p_pit and result[i][j] == '.':
                    result[i][j] = PIT

        for i in range(self.num_gold):
            row = random.randint(0, self.size-1)
            col = random.randint(0, self.size-1)
            while result[row][col] != '.':
                row = random.randint(0, self.size-1)
                col = random.randint(0, self.size-1)

            result[row][col] = GOLD

        self.create_stench(result)

        for i in range(len(result)):
            for j in range(len(result)):
                if result[i][j] == WUMPUS:
                    self.create_stench(result, i, j)

                if result[i][j] == PIT:
                    self.create_breeze(result, i, j)

        return result
    
    def create_stench(world, row, col):
        if row - 1 >= 0:
            if world[row - 1][col] == '.':
                world[row - 1][col] = STENCH
            else:
                world[row - 1][col] += f", {STENCH}"

        if row + 1 <= len(world) - 1:
            if world[row + 1][col] == '.':
                world[row + 1][col] = STENCH
            else:
                world[row + 1][col] += f", {STENCH}"

        if col - 1 >= 0:
            if world[row][col - 1] == '.':
                world[row][col - 1] = STENCH
            else:
                world[row][col - 1] += f", {STENCH}"        
        if col + 1 <= len(world) - 1:
            if world[row][col + 1] == '.':
                world[row][col + 1] = STENCH
            else:
                world[row][col + 1] += f", {STENCH}"

    def create_breeze(world, row, col):
        if row - 1 >= 0:
            if world[row - 1][col] == '.':
                world[row - 1][col] = BREEZE
            else:
                world[row - 1][col] += f", {BREEZE}"

        if row + 1 <= len(world) - 1:
            if world[row + 1][col] == '.':
                world[row + 1][col] = BREEZE
            else:
                world[row + 1][col] += f", {BREEZE}"

        if col - 1 >= 0:
            if world[row][col - 1] == '.':
                world[row][col - 1] = BREEZE
            else:
                world[row][col - 1] += f", {BREEZE}"        
        if col + 1 <= len(world) - 1:
            if world[row][col + 1] == '.':
                world[row][col + 1] = BREEZE
            else:
                world[row][col + 1] += f", {BREEZE}"                   