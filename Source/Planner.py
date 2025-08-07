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
        x, y, direction = state
        neighbors = []
        dir_idx = self.directions.index(direction)

        # Move Forward (chỉ đến ô an toàn)
        if direction == "East" and x < self.size - 1:
            if kb_world[x + 1][y].is_safe:
                neighbors.append(((x + 1, y, direction), "Move Forward", 1))
        elif direction == "West" and x > 0:
            if kb_world[x - 1][y].is_safe:
                neighbors.append(((x - 1, y, direction), "Move Forward", 1))
        elif direction == "North" and y < self.size - 1:
            if kb_world[x][y + 1].is_safe:
                neighbors.append(((x, y + 1, direction), "Move Forward", 1))
        elif direction == "South" and y > 0:
            if kb_world[x][y - 1].is_safe:
                neighbors.append(((x, y - 1, direction), "Move Forward", 1))

        # Turn Left
        new_dir = self.directions[(dir_idx - 1) % 4]
        neighbors.append(((x, y, new_dir), "Turn Left", 1))

        # Turn Right
        new_dir = self.directions[(dir_idx + 1) % 4]
        neighbors.append(((x, y, new_dir), "Turn Right", 1))

        return neighbors

    def plan(self, start_state, goal_position, kb_world):
        """
        Thuật toán A* để tìm đường đi tối ưu dựa trên cơ sở tri thức và trạng thái môi trường.
        start_state: (x, y, direction, has_gold, action_count)
        kb_world: World object để kiểm tra trạng thái môi trường
        Returns: List of action representing the plan
        """
        
        open_list = [(0, start_state, [])]  # (f_score, state, actions)
        visited_states = set()
        g_score = defaultdict(lambda: float('inf'))
        g_score[start_state] = 0
        f_score = defaultdict(lambda: float('inf'))
        f_score[start_state] = self.manhattan_distance(start_state[0], start_state[1], goal_position[0], goal_position[1])

        while open_list:
            current_f, current_state, actions = heappop(open_list)
            x, y, direction = current_state

            # Kiểm tra mục tiêu
            if (x, y) == goal_position:
                return [action for action in actions]

            if current_state in visited_states:
                continue
            visited_states.add(current_state)

            for next_state, action, cost in self.get_neighbors(current_state, kb_world):
                if next_state in visited_states:
                    continue

                tentative_g_score = g_score[current_state] + cost

                if tentative_g_score < g_score[next_state]:
                    # Update parent and action for backtracking
                    g_score[next_state] = tentative_g_score
                    h_score = self.manhattan_distance(next_state[0], next_state[1], goal_position[0], goal_position[1])

                    f_score[next_state] = tentative_g_score + h_score
                    heappush(open_list, (f_score[next_state], next_state, actions + [(action, next_state)]))

        return []  # Trả về rỗng nếu không tìm thấy đường đi