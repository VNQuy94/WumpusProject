from ResolutionEngine import ResolutionEngine
from KnowledgeBase import KnowledgeBase
from Planner import Planner
from Cells import Cell
import random

# Create symbols for the Wumpus World
def P(x, y): 
    return f"P{x}{y}"

def W(x, y): 
    return f"W{x}{y}"

def Gold(x, y): 
    return f"Gold{x}{y}"

def S(x, y): 
    return f"S{x}{y}"

def B(x, y): 
    return f"B{x}{y}"

def Glitter(x, y): 
    return f"Gliter{x}{y}"

def Not(literal):
    return f"~{literal}" if not literal.startswith('~') else literal[1:]

# Class Agent
class Agent:
    def __init__(self, size):
        self.size = size
        self.kb_world = [[Cell(x, y) for y in range(self.size)] for x in range(self.size)]
        self.kb = KnowledgeBase()
        self.engine = ResolutionEngine()
        self.planner = Planner(size)
        self.actions = []
        self.current_pos = (0, 0)
        self.direction = "East"
        self.has_arrow = True
        self.has_gold = False
        self.action_count = 0
        self.shooting_plan = None

    def set_arrow(self, value):
        self.has_arrow = value
        
    def manhattan_distance(self, x, y):
        return abs(x - self.current_pos[0]) + abs(y - self.current_pos[1])
    
    def create_kb_world(self):
        self.kb_world = [[Cell(i, j) for j in range(self.size)] for i in range(self.size)]
        self.kb_world[0][0].is_safe = True
        self.kb_world[0][0].is_visited = True
        self.kb.tell(Not(P(0, 0)))
        self.kb.tell(Not(W(0, 0)))

    def _get_neighbors(self, x, y):
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors

    def get_direction_to_neighbor(self, nx, ny):
        """Tính hướng cần quay đến để Move Forward vào ô (nx, ny) từ current_pos."""
        x, y = self.current_pos
        if nx == x and ny == y + 1:
            return "East"
        elif nx == x and ny == y - 1:
            return "West"
        elif nx == x + 1 and ny == y:
            return "North"
        elif nx == x - 1 and ny == y:
            return "South"
        return None  # Không phải neighbor

    def add_wumpus_rules(self, x, y):
        neighbors = self._get_neighbors(x, y)
        if not neighbors:
            return
    
        literals = [W(nx, ny) for nx, ny in neighbors]
        self.kb.add([Not(S(x,y))] + literals)

        for nx, ny in neighbors:
            self.kb.add([Not(W(nx, ny)), S(x, y)])
    
    def add_pit_rules(self, x, y):
        neighbors = self._get_neighbors(x, y)
        if not neighbors:
            return
        
        literals = [P(nx, ny) for nx, ny in neighbors]
        self.kb.add([Not(B(x,y))] + literals)

        for nx, ny in neighbors:
            self.kb.add([Not(P(nx, ny)), B(x, y)])

    def perceive_and_update(self, percepts):
        x, y = self.current_pos
        # Transform percepts into knowledge base clauses
        if percepts[0]:
            self.kb.tell(S(x, y))
            self.add_wumpus_rules(x, y)
        else:
            self.kb.tell(Not(S(x, y)))
            neighbors = self._get_neighbors(x, y)
            for nx, ny in neighbors:
                self.kb.tell(Not(W(nx, ny)))
            
        if percepts[1]:
            self.kb.tell(B(x, y))
            self.add_pit_rules(x, y)
        else:
            self.kb.tell(Not(B(x, y)))
            neighbors = self._get_neighbors(x, y)
            for nx, ny in neighbors:
                self.kb.tell(Not(P(nx, ny)))

        if percepts[3]:
            dx, dy = 0, 0
            if self.direction == 'East':
                dy = 1
            elif self.direction == 'West':
                dy = -1
            elif self.direction == 'North':
                dx = 1                 
            elif self.direction == 'South':
                dx = -1
            current_x, current_y = x + dx, y + dy

            while 0 <= current_x < self.size and 0 <= current_y < self.size:
                if not self.kb_world[current_x][current_y].is_visited:
                    self.kb.tell(Not(W(current_x, current_y)))
                    self.kb.remove(W(current_x, current_y))
                    self.kb_world[current_x][current_y].set_has_wumpus(False)
                    self.kb_world[current_x][current_y].set_is_safe(True)

                current_x += dx
                current_y += dy

        # Sau khi cập nhật KB, thử suy luận thêm các ô nguy hiểm duy nhất
        self.infer_local_hazards(x, y)

    def infer_local_hazards(self, x, y):
        """
        Nếu tại (x,y) có Stench (S) và tất cả neighbor trừ một đã chứng minh được ~W => ô còn lại là Wumpus.
        Cập nhật trực tiếp vào KB và kb_world để các bước sau không cần chờ suy luận bằng resolution tốn thời gian.
        """
        neighbors = self._get_neighbors(x, y)
        if not neighbors:
            return

        # Suy luận Wumpus duy nhất
        if self.engine.ask(self.kb, S(x, y)):
            unknown_wumpus_candidates = []
            for nx, ny in neighbors:
                # Nếu chưa chắc chắn ~W(nx,ny) thì vẫn là ứng viên
                if not self.engine.ask(self.kb, Not(W(nx, ny))):
                    unknown_wumpus_candidates.append((nx, ny))
            # Nếu chỉ còn đúng 1 ứng viên => đó là Wumpus
            if len(unknown_wumpus_candidates) == 1:
                wx, wy = unknown_wumpus_candidates[0]
                if not self.engine.ask(self.kb, W(wx, wy)):
                    self.kb.tell(W(wx, wy))  # Khẳng định Wumpus
                self.kb_world[wx][wy].set_has_wumpus(True)
                # Các neighbor còn lại là an toàn khỏi Wumpus
                for nx, ny in neighbors:
                    if (nx, ny) != (wx, wy):
                        self.kb.tell(Not(W(nx, ny)))

    def remove_rules_for_cell(self, x, y):
        neighbors = self._get_neighbors(x, y)
    # --- Xóa các quy tắc liên quan đến Wumpus ---
        if neighbors:
            wumpus_literals = [W(nx, ny) for nx, ny in neighbors]
            self.kb.remove([Not(S(x,y))] + wumpus_literals)

            for nx, ny in neighbors:
                self.kb.remove([Not(W(nx, ny)), S(x, y)])
                
        # --- Xóa các quy tắc liên quan đến Pit ---
        if neighbors:
            pit_literals = [P(nx, ny) for nx, ny in neighbors]
            self.kb.remove([Not(B(x,y))] + pit_literals)

            for nx, ny in neighbors:
                self.kb.remove([Not(P(nx, ny)), B(x, y)])


    def agent_update_state(self, action):
        x, y = self.current_pos

        directions = ["East", "South", "West", "North"]
        agent_direction_index = directions.index(self.direction)

        if action == "Turn Left":
            self.direction = directions[(agent_direction_index - 1) % 4]
            
        if action == "Turn Right":
            self.direction = directions[(agent_direction_index + 1) % 4]

        if action == "Move Forward":
            self.remove_rules_for_cell(x, y)
            if self.direction == "East":
                if y < self.size - 1:
                    y += 1

            elif self.direction == "West":
                if y > 0:
                    y -= 1

            elif self.direction == "South":
                if x > 0:
                    x -= 1

            elif self.direction == "North":
                if x < self.size - 1:
                    x += 1

        self.current_pos = (x, y)
        self.kb_world[x][y].set_is_visited(True)
        self.kb_world[x][y].set_turn_visited(self.action_count)

    def find_goal(self):
        if self.has_gold:
            return (0, 0)
        
        # Tìm ô an toàn chưa thăm
        safe_unvisited = [(x, y) for x in range(self.size) for y in range(self.size)
                          if self.kb_world[x][y].is_safe and not self.kb_world[x][y].is_visited]
        
        # Sắp xếp theo khoảng cách Manhattan từ vị trí hiện tại
        if safe_unvisited:
            safe_unvisited.sort(key=lambda p: self.manhattan_distance(p[0], p[1]))

            # Tìm ô an toàn gần nhất và thuận hướng agent nhất
            x, y = self.current_pos
            if self.direction == "East":
                if (x, y + 1) in safe_unvisited:
                    return (x, y + 1)
            elif self.direction == "West":
                if (x, y - 1) in safe_unvisited:
                    return (x, y - 1)

            elif self.direction == "South":
                if (x - 1, y) in safe_unvisited:
                    return (x - 1, y)

            elif self.direction == "North":
                if (x + 1, y) in safe_unvisited:
                    return (x + 1, y)
            
            return safe_unvisited[0]  # Trả về ô an toàn gần nhất nếu không có ô thuận hướng
        
        return None  # Không còn ô an toàn nào
    
    def find_wumpus_on_line(self):
        """
        Kiểm tra xem có Wumpus trên hàng ngang hoặc cột dọc theo hướng mặt hiện tại không.
        Trả về (hướng_so_với_agent) nếu phát hiện, ngược lại trả về None.
        """
        x, y = self.current_pos
        wumpus_dir = None

        if self.direction in ["East", "West"]:  # Quét hàng ngang
            for ny in range(self.size):
                if self.kb_world[x][ny].has_wumpus:
                    # Xác định hướng Wumpus
                    if ny > y:
                        wumpus_dir = "East"
                    elif ny < y:
                        wumpus_dir = "West"

                    return wumpus_dir

        elif self.direction in ["North", "South"]:  # Quét cột dọc
            for nx in range(self.size):
                if self.kb_world[nx][y].has_wumpus:
                    # Xác định hướng Wumpus
                    if nx > x:
                        wumpus_dir = "South"
                    elif nx < x:
                        wumpus_dir = "North"

                    return wumpus_dir

        return None

    def find_shooting_position(self):
        """
        Tìm vị trí an toàn gần nhất trên cùng hàng/cột với một Wumpus đã biết.
        Trả về (vị_trí_bắn, hướng_bắn) hoặc None nếu không có vị trí phù hợp.
        """
        wumpus_positions = [
            (i, j) 
            for i in range(self.size) 
            for j in range(self.size) 
            if self.kb_world[i][j].has_wumpus
        ]
        if not wumpus_positions:
            return None

        candidate_positions = []
        for wx, wy in wumpus_positions:
            # Vị trí an toàn trên cùng hàng (row)
            for y_pos in range(self.size):
                if self.kb_world[wx][y_pos].is_safe and (wx, y_pos) != (wx, wy):
                    candidate_positions.append(((wx, y_pos), wx, wy))  # Lưu cả tọa độ Wumpus
            # Vị trí an toàn trên cùng cột (column)
            for x_pos in range(self.size):
                if self.kb_world[x_pos][wy].is_safe and (x_pos, wy) != (wx, wy):
                    candidate_positions.append(((x_pos, wy), wx, wy))

        if not candidate_positions:
            return None

        # Loại trùng theo vị trí bắn
        seen = {}
        for shoot_pos, wx, wy in candidate_positions:
            seen[shoot_pos] = (wx, wy)
        candidate_positions = [(pos, seen[pos][0], seen[pos][1]) for pos in seen]

        # Sắp xếp theo khoảng cách Manhattan
        candidate_positions.sort(
            key=lambda item: self.manhattan_distance(item[0][0], item[0][1])
        )

        # Lấy vị trí gần nhất
        shoot_pos, wx, wy = candidate_positions[0]

        # Xác định hướng bắn dựa trên vị trí Wumpus
        if shoot_pos[0] == wx:
            shoot_dir = "East" if wy > shoot_pos[1] else "West"
        elif shoot_pos[1] == wy:
            shoot_dir = "South" if wx < shoot_pos[0] else "North"

        return shoot_pos, shoot_dir

    def handle_wumpus_move(self):
        clause_to_keep = []
        all_clauses = self.kb.get_clauses()
        for clause in all_clauses:
            is_wumpus_stench_related = False
            for literal in clause:
                if 'W' in literal or 'S' in literal:
                    is_wumpus_stench_related = True
                    break
            
            if not is_wumpus_stench_related:
                clause_to_keep.append(clause)

        self.kb.clauses = set(clause_to_keep)

        for row in range(self.size):
            for col in range(self.size):
                if self.kb_world[row][col].is_visited and self.action_count - self.kb_world[row][col].turn_visited <= 5 and S(row, col) not in all_clauses:
                    self.kb.tell(Not(W(row, col)))
                else:
                    self.kb_world[row][col].set_has_wumpus(False)
                    self.kb_world[row][col].set_is_safe(False)
                    self.kb_world[row][col].set_is_visited(False)

        self.actions = []
        self.shooting_plan = None

    def make_decision(self, percepts):
        directions = ["East", "South", "West", "North"]

        x, y = self.current_pos

        # Cập nhật percepts vào knowledge base
        self.perceive_and_update(percepts)

        if self.shooting_plan and self.current_pos == self.shooting_plan['target_pos']:
            target_dir = self.shooting_plan['target_dir']

            turn_actions = []
            current_idx = directions.index(self.direction)
            target_idx = directions.index(target_dir)
            turn = (target_idx - current_idx) % 4
            if turn == 1:
                turn_actions = ["Turn Right"]
            elif turn == 2:
                turn_actions = ["Turn Right", "Turn Right"]
            elif turn == 3:
                turn_actions = ["Turn Left"]
            self.actions = turn_actions + ["Shoot"]
            self.shooting_plan = None
            return self.actions.pop(0)

        # Kiểm tra và nhặt vàng nếu có
        if percepts[2] and not self.has_gold:  # Glitter = True
            self.has_gold = True
            self.actions = []  # Xóa danh sách hành động để lập kế hoạch mới
            return "Grab"

        # Kiểm tra nếu ở (0,0) và có vàng thì leo ra
        if self.has_gold and self.current_pos == (0, 0):
            print("Agent leo ra tại (0,0) với vàng!")
            return "Climb"

        # Nếu danh sách hành động của agent không rỗng    
        if self.actions:
            action = self.actions.pop(0)
            return action
        
        if self.has_gold and self.current_pos != (0, 0):
            if self.kb_world[0][0].is_safe:
                start_state = (x, y, self.direction)
                self.actions = self.planner.plan(start_state, (0, 0), self.kb_world)

                if self.actions:
                    action = self.actions.pop(0)
                    return action
            
        
        # Nếu danh sách hành động của agent là rỗng
        if not self.actions:
            neighbors = self._get_neighbors(x, y) # Tìm kiếm các ô xung quanh

            # Kiểm tra các ô xung quanh có an toàn hay không
            for nx, ny in neighbors:
                # hãy tạo thành một list query truyền vào 1 lần thôi
                is_safe_pit = self.engine.ask(self.kb, Not(P(nx, ny)))
                is_safe_wumpus = self.engine.ask(self.kb, Not(W(nx, ny)))

                # Cập nhật kb_world dựa trên kb
                if is_safe_pit and is_safe_wumpus:
                    self.kb_world[nx][ny].set_is_safe(True)
                else:
                    has_wumpus = self.engine.ask(self.kb, W(nx, ny))

                    if has_wumpus:
                        print(f"Wumpus found at ({nx}, {ny})")
                        self.kb.tell(W(nx, ny))
                        self.kb_world[nx][ny].set_has_wumpus(True)
                    
            # Tìm kiếm danh sách các hành động mới
            goal = self.find_goal()
            print(goal)
            if goal is not None:
                start_state = (x, y, self.direction)
                self.actions = self.planner.plan(start_state, goal, self.kb_world)
            
            # Nếu không có goal an toàn (danh sách hành động rỗng)
            else:
                print("Không còn ô an toàn")
                if self.has_arrow:
                    shoot_info = self.find_shooting_position()
                    print(shoot_info)
                    if shoot_info:
                        shoot_pos, shoot_dir = shoot_info

                        if shoot_pos and shoot_dir:
                            self.shooting_plan = {'target_pos': shoot_pos, 'target_dir': shoot_dir}
                            start_state = (x, y, self.direction)
                            self.actions = self.planner.plan(start_state, shoot_pos, self.kb_world)

                # Nếu không có action từ trên và không còn arrow, random di chuyển
            if not self.actions:
                neighbors = self._get_neighbors(x, y)
                unvisited_neighbors = [(nx, ny) for nx, ny in neighbors if not self.kb_world[nx][ny].is_visited]
                if unvisited_neighbors:
                    random.shuffle(unvisited_neighbors)  # Xáo trộn để random
                    for nx, ny in unvisited_neighbors:
                        target_dir = self.get_direction_to_neighbor(nx, ny)
                        if target_dir:  # Nếu là ô lân cận hợp lệ

                            current_idx = directions.index(self.direction)
                            target_idx = directions.index(target_dir)

                            turn = (target_idx - current_idx) % 4
                            turn_actions = []
                            if turn == 1:
                                turn_actions = ["Turn Right"]
                            elif turn == 2:
                                turn_actions = ["Turn Right", "Turn Right"]
                            elif turn == 3:
                                turn_actions = ["Turn Left"]
                            # Thêm Move Forward
                            self.actions = turn_actions + ["Move Forward"]
                            break  # Dừng sau khi chọn được action
                else:
                    # Nếu không có neighbor (ít xảy ra), fallback về (0,0)
                    goal = (0, 0)
                    start_state = (x, y, self.direction)
                    self.actions = self.planner.plan(start_state, goal, self.kb_world)

        return self.actions.pop(0)