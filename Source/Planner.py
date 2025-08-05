from heapq import heappush, heappop
from collections import defaultdict

class Planner:
    def __init__(self, size):
        self.size = size
        self.directions = ["East", "North", "West", "South"]

    def manhattan_distance(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def get_neighbors(self, state, kb_world):
        """
        Lấy danh sách các trạng thái hàng xóm hợp lệ từ trạng thái hiện tại.
        state: (x, y, direction, has_arrow, has_gold, action_count)
        kb_world: World object để kiểm tra trạng thái môi trường
        """
        x, y, direction, has_arrow, has_gold, action_count = state
        neighbors = []
        dir_idx = self.directions.index(direction)

        # Move Forward (chỉ đến ô an toàn)
        if direction == "East" and x < self.size - 1:
            if kb_world[x + 1][y].is_safe:
                neighbors.append(((x + 1, y, direction, has_arrow, has_gold, action_count + 1), "Move Forward", 1))
        elif direction == "West" and x > 0:
            if kb_world[x - 1][y].is_safe:
                neighbors.append(((x - 1, y, direction, has_arrow, has_gold, action_count + 1), "Move Forward", 1))
        elif direction == "North" and y < self.size - 1:
            if kb_world[x][y + 1].is_safe:
                neighbors.append(((x, y + 1, direction, has_arrow, has_gold, action_count + 1), "Move Forward", 1))
        elif direction == "South" and y > 0:
            if kb_world[x][y - 1].is_safe:
                neighbors.append(((x, y - 1, direction, has_arrow, has_gold, action_count + 1), "Move Forward", 1))

        # Turn Left
        new_dir = self.directions[(dir_idx - 1) % 4]
        neighbors.append(((x, y, new_dir, has_arrow, has_gold, action_count + 1), "Turn Left", 1))

        # Turn Right
        new_dir = self.directions[(dir_idx + 1) % 4]
        neighbors.append(((x, y, new_dir, has_arrow, has_gold, action_count + 1), "Turn Right", 1))

        # Grab (nếu có glitter)
        if kb_world[x][y].has_glitter and not has_gold:
            neighbors.append(((x, y, direction, has_arrow, True, action_count + 1), "Grab", 1))

        # Shoot (nếu có mũi tên và xác định được Wumpus)
        if has_arrow:
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                while 0 <= nx < self.size and 0 <= ny < self.size:
                    if kb_world[nx][ny].has_wumpus:
                        neighbors.insert(0, (((x, y, direction, False, has_gold, action_count + 1), f"Shoot ({nx},{ny})", 10)))
                    nx += dx
                    ny += dy

        # Climb (nếu ở (0,0) và có vàng)
        if x == 0 and y == 0 and has_gold:
            neighbors.append(((x, y, direction, has_arrow, has_gold, action_count + 1), "Climb", 1))

        return neighbors

    def plan(self, start_state, kb_world):
        """
        Thuật toán A* để tìm đường đi tối ưu dựa trên cơ sở tri thức và trạng thái môi trường.
        start_state: (x, y, direction, has_arrow, has_gold, action_count)
        kb_world: World object để kiểm tra trạng thái môi trường
        Returns: List of (action, state) tuples representing the plan
        """
        goal = None

        # Chọn mục tiêu nếu không có vàng
        if not start_state[4]:
            # Ưu tiên ô có vàng nếu đã biết
            glitter_cells = [(x, y) for x in range(self.size) for y in range(self.size)
                            if kb_world[x][y].has_glitter]
            if glitter_cells:
                goal = glitter_cells[0]
            else:
                # Nếu không có vàng, chọn ô an toàn chưa thăm gần nhất
                safe_unvisited = [(x, y) for x in range(self.size) for y in range(self.size)
                                if kb_world[x][y].is_safe and not kb_world[x][y].is_visited]
                if not safe_unvisited:
                    # Nếu đã có vàng, quay về (0,0)
                    if start_state[4]:
                        goal = (0, 0)
                    else:
                        return []  # Không còn ô an toàn để khám phá
                else:
                    goal = min(safe_unvisited, key=lambda p: self.manhattan_distance(start_state[0], start_state[1], p[0], p[1]))
        elif start_state[4]:  # Đã có vàng, mục tiêu là quay về (0,0)
            goal = (0, 0)

        open_list = [(0, start_state, [])]  # (f_score, state, actions)
        closed = set()
        g_score = defaultdict(lambda: float('inf'))
        g_score[start_state] = 0
        f_score = defaultdict(lambda: float('inf'))
        f_score[start_state] = self.manhattan_distance(start_state[0], start_state[1], goal[0], goal[1])
        came_from = {}  # Dictionary to store parent state and action: {state: (parent_state, action)}

        while open_list:
            current_f, current_state, actions = heappop(open_list)
            x, y, direction, has_arrow, has_gold, action_count = current_state

            # Kiểm tra mục tiêu
            if (x, y) == goal:
                if not has_gold and kb_world[x][y].has_glitter:
                    return [(action, state) for action, state in actions + [("Grab", current_state)]]
                elif has_gold and goal == (0, 0):
                    return [(action, state) for action, state in actions + [("Climb", current_state)]]
                elif actions:
                    return [(action, state) for action, state in actions]

            if current_state in closed:
                continue
            closed.add(current_state)

            for next_state, action, cost in self.get_neighbors(current_state, kb_world):
                if next_state in closed:
                    continue

                tentative_g_score = g_score[current_state] + cost

                if tentative_g_score < g_score[next_state]:
                    # Update parent and action for backtracking
                    came_from[next_state] = (current_state, action)
                    g_score[next_state] = tentative_g_score
                    h_score = self.manhattan_distance(next_state[0], next_state[1], goal[0], goal[1])

                    # Điều chỉnh h_score để ưu tiên nhặt vàng hoặc quay về
                    if next_state[4]:  # Nếu đã có vàng
                        h_score += 100  # Ưu tiên quay về (0,0)
                    elif kb_world[next_state[0]][next_state[1]].has_glitter:
                        h_score -= 100  # Ưu tiên nhặt vàng

                    f_score[next_state] = tentative_g_score + h_score
                    heappush(open_list, (f_score[next_state], next_state, actions + [(action, next_state)]))

        return []  # Trả về rỗng nếu không tìm thấy đường đi