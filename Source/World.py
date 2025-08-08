import random
import GameCoords

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
        self.agent_position = (0, 0)  # Vị trí của agent
        self.agent_direction = "East"  # Hướng của agent
        self.action_count = 0  # Đếm số hành động để hỗ trợ Moving Wumpus

    def is_not_origin(self, row, col):
        start_row, start_col = GameCoords.game_to_array_coords(0, 0, self.size)
        return (row != start_row or col != start_col)

    def create_world(self):
        # Initialize world
        world = [['.' for _ in range(self.size)] for _ in range(self.size)]

        # Randomly place Wumpus, avoiding (0,0)
        wumpus_count = 0
        while wumpus_count < self.num_wumpus:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)

            if self.is_not_origin(row, col) and not world[row][col] == WUMPUS:
                world[row][col] = WUMPUS
                self.add_effect(world, row, col, STENCH)
                wumpus_count += 1

        # Randomly place pits based on p_pit
        for i in range(self.size):
            for j in range(self.size):
                if self.is_not_origin(i, j) and random.random() <= self.p_pit and not world[i][j] == WUMPUS:
                    if not world[i][j] == BREEZE and not world[i][j] == STENCH:
                        world[i][j] = PIT
                        self.add_effect(world, i, j, BREEZE)

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
        """Trả về percepts tại ô (row, col)"""
        row, col = GameCoords.game_to_array_coords(x, y, self.size)

        stench = STENCH in self.world[row][col]
        breeze = BREEZE in self.world[row][col]
        glitter = GOLD in self.world[row][col]
        return [stench, breeze, glitter]
    
    def perform_agent_action(self, action):
        percepts = self.get_percepts(self.agent_position[0], self.agent_position[1])
        x, y = self.agent_position
        row, col = GameCoords.game_to_array_coords(x, y, self.size)
        
        if action == "Grab":
            if GOLD in self.world[row][col]:
                self.world[row][col] = self.world[row][col].replace(GOLD, EMPTY)
                print(f"Agent đã nhặt vàng tại ({x}, {y})")
                percepts = self.get_percepts(self.agent_position[0], self.agent_position[1])
                return percepts + [False]            
            
        elif action == "Move Forward":
            if self.agent_direction == "East":
                percepts = self.get_percepts(x, y + 1)
                if y + 1 < self.size:
                    self.agent_position = (x, y + 1)

            elif self.agent_direction == "West":
                percepts = self.get_percepts(x, y - 1)
                if y - 1 >= 0:
                    self.agent_position = (x, y - 1)

            elif self.agent_direction == "North":
                percepts = self.get_percepts(x + 1, y)
                if x + 1 < self.size:
                    self.agent_position = (x + 1, y)

            elif self.agent_direction == "South":
                percepts = self.get_percepts(x - 1, y)
                if x - 1 >= 0:
                    self.agent_position = (x - 1, y)

            # Kiểm tra va chạm với Wumpus hoặc Pit
            if WUMPUS in self.world[row][col]:
                print(f"Agent bị Wumpus giết tại ({self.agent_position[0]}, {self.agent_position[1]})")
                return None
            elif PIT in self.world[row][col]:
                print(f"Agent rơi vào Pit tại ({self.agent_position[0]}, {self.agent_position[1]})")
                return None
            
            return percepts + [False]

        direction_list = ["East", "South", "West", "North"]
        direction_index = direction_list.index(self.agent_direction)
        if action == "Turn Left":
            self.agent_direction = direction_list[(direction_index - 1) % 4]
            return percepts + [False]

        if action == "Turn Right":
            self.agent_direction = direction_list[(direction_index + 1) % 4]
            return percepts + [False]
        
        if action == "Shoot":
            # Kiểm tra theo hướng của agent
            if self.agent_direction == "East":
                for j in range(col, self.size):
                    if WUMPUS in self.world[row][j]:
                        self.world[row][j] = self.world[row][j].replace(WUMPUS, EMPTY)
                        self.clear_effects(row, j, STENCH)
                        print(f"Mũi tên trúng Wumpus tại ({x}, {j})")
                        return percepts + [True]
                    
            elif self.agent_direction == "West":
                for j in range(y - 1, -1, -1):
                    if WUMPUS in self.world[row][j]:
                        self.world[row][j] = self.world[row][j].replace(WUMPUS, EMPTY)
                        self.clear_effects(row, j, STENCH)
                        print(f"Mũi tên trúng Wumpus tại ({x}, {j})")
                        return percepts + [True]
                    
            elif self.agent_direction == "North":
                for i in range(row - 1, self.size):
                    if WUMPUS in self.world[i][col]:
                        self.world[i][col] = self.world[i][col].replace(WUMPUS, EMPTY)
                        self.clear_effects(i, col, STENCH)
                        print(f"Mũi tên trúng Wumpus tại ({i}, {y})")
                        return percepts + [True]
            
            elif self.agent_direction == "South":
                for i in range(row + 1):
                    if WUMPUS in self.world[i][col]:
                        self.world[i][col] = self.world[i][col].replace(WUMPUS, EMPTY)
                        self.clear_effects(i, col, STENCH)
                        print(f"Mũi tên trúng Wumpus tại ({i}, {y})")
                        return percepts + [True]
            
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
    
        # Tạo một danh sách các chuỗi, mỗi chuỗi là một hàng của thế giới
        # Dùng list comprehension để code ngắn gọn
        map_rows = []
        for r in range(self.size):
            # Nối các phần tử trong một hàng bằng dấu cách
            # Dùng str.ljust() để mỗi ô có chiều rộng cố định, giúp căn chỉnh đẹp hơn
            formatted_row = [cell.ljust(4) for cell in self.world[r]]
            map_rows.append("".join(formatted_row))
        
        # Nối tất cả các hàng lại với nhau bằng ký tự xuống dòng
        return "\n".join(map_rows)
    
if __name__ == "__main__":
    world = World()
    print(world)
    for i in range(world.size):
        for j in range(world.size):
            print(f"({i, j})", world.get_percepts(i, j))