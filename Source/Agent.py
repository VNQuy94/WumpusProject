class Agent:
    def __init__(self, world, kb, planner):
        self.world = world  # Đối tượng World
        self.kb = kb       # Đối tượng KnowledgeBase
        self.planner = planner  # Đối tượng Planner
        self.x = 0         # Tọa độ x ban đầu
        self.y = 0         # Tọa độ y ban đầu
        self.direction = "East"  # Hướng ban đầu
        self.has_arrow = True    # Có 1 mũi tên ban đầu
        self.has_gold = False    # Chưa nhặt vàng
        self.score = 0           # Điểm số ban đầu
        self.action_count = 0    # Số hành động đã thực hiện

    def act(self):
        # Nhận percepts và cập nhật KB
        percepts = self.world.get_percepts(self.x, self.y)
        self.kb.update(self.x, self.y, percepts)
        self.kb.infer()

        # Kiểm tra glitter để nhặt vàng
        if percepts["glitter"] and not self.has_gold:
            self.world.world[self.x][self.y].remove_content("G")
            self.has_gold = True
            self.score -= 1
            self.action_count += 1
            return "Grab"

        # Kiểm tra climb nếu ở (0,0) và có vàng
        if self.x == 0 and self.y == 0 and self.has_gold:
            self.score += 1000  # Thưởng khi trèo ra với vàng
            self.score -= 1     # Chi phí hành động Climb
            self.action_count += 1
            return "Climb"

        # Tạo kế hoạch bằng thuật toán tìm kiếm
        state = (self.x, self.y, self.direction, self.has_arrow, self.has_gold)
        actions = self.planner.plan(state, self.kb)

        if not actions:
            # Không còn ô an toàn, tạm dừng hoặc chọn ô không chắc chắn
            return "Stop"

        # Thực hiện hành động đầu tiên trong kế hoạch
        action = actions[0]
        self.score -= 1 if action != "Shoot" else 10
        self.action_count += 1

        if action == "Move Forward":
            if self.direction == "East" and self.x < self.world.size - 1:
                self.x += 1

            elif self.direction == "West" and self.x > 0:
                self.x -= 1

            elif self.direction == "North" and self.y < self.world.size - 1:
                self.y += 1

            elif self.direction == "South" and self.y > 0:
                self.y -= 1
                
        elif action == "Turn Left":
            dir_idx = self.planner.directions.index(self.direction)
            self.direction = self.planner.directions[(dir_idx - 1) % 4]

        elif action == "Turn Right":
            dir_idx = self.planner.directions.index(self.direction)
            self.direction = self.planner.directions[(dir_idx + 1) % 4]

        elif action.startswith("Shoot"):
            self.has_arrow = False
            # Giả sử bắn đúng ô có Wumpus (cần logic kiểm tra trong World)
            # Ví dụ: world.remove_wumpus(target_x, target_y)
            # Cập nhật KB với scream = True nếu Wumpus chết

        # Kiểm tra Moving Wumpus
        if self.action_count % 5 == 0:
            self.world.move_wumpus()

        return action