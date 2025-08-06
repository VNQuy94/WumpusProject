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

    def is_not_origin(self, row, col):
        return (row != 0 or col != 0)

    def create_world(self):
        # Initialize world
        self.world = [['.' for _ in range(self.size)] for _ in range(self.size)]

        # Randomly place Wumpus, avoiding (0,0)
        wumpus_count = 0
        while wumpus_count < self.num_wumpus:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)

            if self.is_not_origin(row, col) and not self.world[row][col] == WUMPUS:
                self.world[row][col] = WUMPUS
                self.add_effect(row, col, STENCH)
                wumpus_count += 1

        # Randomly place pits based on p_pit
        for i in range(self.size):
            for j in range(self.size):
                if self.is_not_origin(i, j) and random.random() <= self.p_pit and not self.world[i][j] == WUMPUS:
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
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                    if effect == STENCH and STENCH not in self.world[new_row][new_col]:
                        if not WUMPUS in self.world[new_row][new_col] and not PIT in self.world[new_row][new_col]:
                            if EMPTY in self.world[new_row][new_col]:
                                self.world[new_row][new_col] = STENCH
                            else:
                                self.world[new_row][new_col] += STENCH

                    elif effect == BREEZE and BREEZE not in self.world[new_row][new_col]:
                        if not WUMPUS in self.world[new_row][new_col] and not PIT in self.world[new_row][new_col]:
                            if EMPTY in self.world[new_row][new_col]:
                                self.world[new_row][new_col] = BREEZE
                            else:
                                self.world[new_row][new_col] += BREEZE

    def get_percepts(self, row, col):
        """Trả về percepts tại ô (row, col)"""
        percepts = [False, False, False] # Stench, Breeze, Glitter
        string = self.world[row][col]

        for i in range(len(string)):
            if string[i] == STENCH:
                percepts[0] = True
            if string[i] == BREEZE:
                percepts[1] = True
            if string[i] == GOLD:
                percepts[2] = True

        return percepts
    
    def check_agent_action(self, x, y, direction, action):
        if action == "Grab":
            if GOLD in self.world[x][y]:
                self.world[x][y] = self.world[x][y].replace(GOLD, EMPTY)
                print(f"Agent nhặt vàng tại ({x}, {y})")
                return True

        elif action == "Shoot":
            hit_wumpus = False
            # Kiểm tra theo hướng của agent
            if direction == "East":
                for i in range(x + 1, self.size):
                    if WUMPUS in self.world[i][y]:
                        self.world[i][y] = self.world[i][y].replace(WUMPUS, EMPTY)
                        self.clear_effects(i, y, STENCH)
                        print(f"Mũi tên trúng Wumpus tại ({i}, {y})")
                        hit_wumpus = True
                        break
            elif direction == "West":
                for i in range(x - 1, -1, -1):
                    if WUMPUS in self.world[i][y]:
                        self.world[i][y] = self.world[i][y].replace(WUMPUS, EMPTY)
                        self.clear_effects(i, y, STENCH)
                        print(f"Mũi tên trúng Wumpus tại ({i}, {y})")
                        hit_wumpus = True
                        break
            elif direction == "North":
                for j in range(y + 1, self.size):
                    if WUMPUS in self.world[x][j]:
                        self.world[x][j] = self.world[x][j].replace(WUMPUS, EMPTY)
                        self.clear_effects(x, j, STENCH)
                        print(f"Mũi tên trúng Wumpus tại ({x}, {j})")
                        hit_wumpus = True
                        break
            elif direction == "South":
                for j in range(y - 1, -1, -1):
                    if WUMPUS in self.world[x][j]:
                        self.world[x][j] = self.world[x][j].replace(WUMPUS, EMPTY)
                        self.clear_effects(x, j, STENCH)
                        print(f"Mũi tên trúng Wumpus tại ({x}, {j})")
                        hit_wumpus = True
                        break

            if hit_wumpus:
                return True
            else:
                return False

    def check_agent_position(self, x, y):
        if WUMPUS in self.world[x][y] and PIT in self.world[x][y]:
            return False
        else:
            return True
            
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
    
if __name__ == "__main__":
    world = World()
    print(world)
    for i in range(world.size):
        for j in range(world.size):
            print(f"({i, j})", world.get_percepts(i, j))