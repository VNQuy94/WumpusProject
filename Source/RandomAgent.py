from heapq import heappush, heappop
from collections import defaultdict, deque

class RandomAgent:
    def __init__(self, size):
        self.size = size
        self.directions = ["East", "South", "West", "North"]

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
        if direction == "East" and y < self.size - 1:
            if kb_world[x][y + 1].is_safe:
                neighbors.append(((x, y + 1, direction), "Move Forward", 1))
        elif direction == "West" and y > 0:
            if kb_world[x][y - 1].is_safe:
                neighbors.append(((x, y - 1, direction), "Move Forward", 1))
        elif direction == "North" and x < self.size - 1:
            if kb_world[x + 1][y].is_safe:
                neighbors.append(((x + 1, y, direction), "Move Forward", 1))
        elif direction == "South" and x > 0:
            if kb_world[x - 1][y].is_safe:
                neighbors.append(((x - 1, y, direction), "Move Forward", 1))

        # Turn Left
        new_dir = self.directions[(dir_idx - 1) % 4]
        neighbors.append(((x, y, new_dir), "Turn Left", 1))

        # Turn Right
        new_dir = self.directions[(dir_idx + 1) % 4]
        neighbors.append(((x, y, new_dir), "Turn Right", 1))

        return neighbors

    def randomPlan(self, start_state, goal_position, kb_world):
        """
        Thuật toán BFS cho random agent.
        start_state: (x, y, direction)
        kb_world: World object để kiểm tra trạng thái môi trường
        Returns: Danh sách hành động
        """
        queue = deque()
        visited_states = {}
        
        queue.append([start_state, []])  # (state, actions)
        visited_states[start_state] = (start_state, None)
        
        while queue:
            current_state, actions = queue.popleft()
            x, y, _ = current_state
            
            for next_state, action, _ in self.get_neighbors(current_state, kb_world):
                if next_state not in visited_states:
                    # Kiểm tra mục tiêu
                    if (x, y) == goal_position:
                        return [action for action in actions]
            
                queue.append([next_state, action])
                visited_states[next_state] = (next_state, current_state)

        return []  # Trả về rỗng nếu không tìm thấy đường đi
    

