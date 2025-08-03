from heapq import heappush, heappop
from collections import defaultdict

class Planner:
    def __init__(self, size):
        self.size = size
        self.directions = ["East", "North", "West", "South"]

    def manhattan_distance(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def get_neighbors(self, state, kb):
        x, y, direction, has_arrow, has_gold = state
        neighbors = []
        dir_idx = self.directions.index(direction)

        # Move Forward (chỉ đến ô an toàn)
        if direction == "East" and x < self.size - 1 and kb.is_safe(x + 1, y):
            neighbors.append(((x + 1, y, direction, has_arrow, has_gold), "Move Forward", 1))
        elif direction == "West" and x > 0 and kb.is_safe(x - 1, y):
            neighbors.append(((x - 1, y, direction, has_arrow, has_gold), "Move Forward", 1))
        elif direction == "North" and y < self.size - 1 and kb.is_safe(x, y + 1):
            neighbors.append(((x, y + 1, direction, has_arrow, has_gold), "Move Forward", 1))
        elif direction == "South" and y > 0 and kb.is_safe(x, y - 1):
            neighbors.append(((x, y - 1, direction, has_arrow, has_gold), "Move Forward", 1))

        # Turn Left
        new_dir = self.directions[(dir_idx - 1) % 4]
        neighbors.append(((x, y, new_dir, has_arrow, has_gold), "Turn Left", 1))

        # Turn Right
        new_dir = self.directions[(dir_idx + 1) % 4]
        neighbors.append(((x, y, new_dir, has_arrow, has_gold), "Turn Right", 1))

        # Grab (nếu có glitter)
        if kb.kb[(x, y)].get("glitter", False) and not has_gold:
            neighbors.append(((x, y, direction, has_arrow, True), "Grab", 1))

        # Shoot (nếu có mũi tên và Wumpus được xác định)
        if has_arrow:
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and kb.kb[(nx, ny)].get("wumpus") == True:
                    neighbors.append(((x, y, direction, False, has_gold), f"Shoot ({nx},{ny})", 10))

        # Climb (nếu ở (0,0) và có vàng)
        if x == 0 and y == 0 and has_gold:
            neighbors.append(((x, y, direction, has_arrow, has_gold), "Climb", 1))

        return neighbors

    def plan(self, start_state, kb, goal=None):
        """A* tìm kiếm đường đi chi phí thấp nhất dựa trên KB"""
        # Chọn mục tiêu: ô an toàn chưa thăm hoặc ô có vàng
        if goal is None:
            safe_unvisited = [(x, y) for x in range(self.size) for y in range(self.size)
                             if kb.is_safe(x, y) and not kb.kb[(x, y)]["visited"]]
            if not safe_unvisited:
                return []  # Không còn ô an toàn
            goal = min(safe_unvisited, key=lambda p: self.manhattan_distance(start_state[0], start_state[1], p[0], p[1]))
        elif kb.kb[goal].get("glitter"):
            goal = goal  # Ô có vàng
        elif start_state[4]:  # Đã có vàng
            goal = (0, 0)  # Quay về (0,0)

        open_list = [(0, start_state, [])]  # (f_score, state, actions)
        closed = set()
        g_score = defaultdict(lambda: float('inf'))
        g_score[start_state] = 0

        while open_list:
            f_score, current, actions = heappop(open_list)
            if (current[0], current[1]) == goal:
                return actions

            if current in closed:
                continue
            closed.add(current)

            for next_state, action, cost in self.get_neighbors(current, kb):
                if next_state in closed:
                    continue
                tentative_g_score = g_score[current] + cost
                if tentative_g_score < g_score[next_state]:
                    g_score[next_state] = tentative_g_score
                    f_score = tentative_g_score + self.manhattan_distance(next_state[0], next_state[1], goal[0], goal[1])
                    heappush(open_list, (f_score, next_state, actions + [action]))

        return []  # Không tìm thấy đường đi