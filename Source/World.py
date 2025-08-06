import random

# Constants
NUM_GOLD = 1
NUM_ARROW = 1
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
        self.action_count = 0  # Đếm số hành động để hỗ trợ Moving Wumpus

    def create_world(self):
        # Initialize world
        self.world = [['.' for _ in range(self.size)] for _ in range(self.size)]

        # Randomly place Wumpus, avoiding (0,0)
        wumpus_count = 0
        while wumpus_count < self.num_wumpus:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)

            if (row != 0 or col != 0) and not self.world[row][col] == WUMPUS:
                self.world[row][col] = WUMPUS
                self.add_effect(row, col, STENCH)
                wumpus_count += 1

        # Randomly place pits based on p_pit
        for i in range(self.size):
            for j in range(self.size):
                if (i != 0 or j != 0) and random.random() <= self.p_pit and not self.world[i][j] == WUMPUS:
                    if not self.world[i][j] == BREEZE and not self.world[i][j] == STENCH:
                        self.world[i][j] = PIT
                        self.add_effect(i, j, BREEZE)

        # Randomly place gold in an empty cell
        gold_count = 0
        while gold_count < self.num_gold:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)
            if not (self.world[row][col] == WUMPUS or self.world[row][col] == PIT):
                self.world[row][col] = GOLD
                gold_count += 1

        return self.world

    def add_effect(self, row, col, effect):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 < new_row < self.size and 0 < new_col < self.size:
                if not self.world[new_row][new_col] == WUMPUS and not self.world[new_row][new_col] == PIT:
                    if effect == STENCH or effect == BREEZE and self.world[new_row][new_col] == EMPTY:
                        self.world[new_row][new_col] = effect
                    elif effect == STENCH and STENCH not in self.world[new_row][new_col]:
                        self.world[new_row][new_col] += STENCH
                    elif effect == BREEZE and BREEZE not in self.world[new_row][new_col]:
                        self.world[new_row][new_col] += BREEZE

    def get_percepts(self, row, col):
        """Trả về percepts tại ô (row, col)"""
        percepts = [False, False, False] # Stench, Breeze, Glitter

        if self.world[row][col] == STENCH:
            percepts[0] = True
        if self.world[row][col] == BREEZE:
            percepts[1] = True
        if self.world[row][col] == GOLD:
            percepts[2] = True

        return percepts

    def move_wumpus(self):
        """Di chuyển Wumpus (cho chế độ Moving Wumpus)"""
        self.action_count += 1
        if self.action_count % 5 == 0:  # Di chuyển sau mỗi 5 hành động
            for i in range(self.size):
                for j in range(self.size):
                    if self.world[i][j] == WUMPUS:
                        # Xóa stench cũ
                        self.clear_effects(i, j, STENCH)
                        # Chọn ô lân cận ngẫu nhiên
                        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                        random.shuffle(directions)
                        for dr, dc in directions:
                            new_row, new_col = i + dr, j + dc
                            if (0 <= new_row < self.size and 0 <= new_col < self.size and
                                not self.world[new_row][new_col] == WUMPUS and
                                not self.world[new_row][new_col] == PIT):
                                # Di chuyển Wumpus
                                self.world[i][j] = '.'
                                self.world[new_row][new_col] = WUMPUS
                                self.add_effect(new_row, new_col, STENCH)
                                break  # Chỉ di chuyển một lần

    def clear_effects(self, row, col, effect):
        """Xóa hiệu ứng (stench) khỏi các ô lân cận"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                if effect == STENCH:
                    self.world[new_row][new_col] = self.world[new_row][new_col].replace(STENCH, EMPTY)

    def __str__(self):
        """Hiển thị lưới cho visualization"""
        result = []
        for i in range(self.size - 1, -1, -1):  # In từ trên xuống
            row = [self.world[i][j] for j in range(self.size)]
            result.append(" ".join(row))
        return "\n".join(result)