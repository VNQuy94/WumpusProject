from ResolutionEngine import ResolutionEngine
from KnowledgeBase import KnowledgeBase
from Planner import Planner
from Cells import Cell
import random
import GameCoords

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
    
    def add_gold_rules(self, x, y):
        neighbors = self._get_neighbors(x, y)
        if not neighbors:
            return 
        
        literals = [Gold(nx, ny) for nx, ny in neighbors]
        self.kb.add([Not(Glitter(x,y))] + literals)

        for nx, ny in neighbors:
            self.kb.add([Not(Gold(nx, ny)), Glitter(x, y)])

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

        if percepts[2]:
            self.kb.tell(Glitter(x, y))
            self.add_gold_rules(x, y)

    # Làm sao để khi tôi đi ra khỏi ô đó không cần những rule đó nữa thì agent sẽ xóa bớt đi những rules đó vì không cần dùng tới
    def remove_rules_for_cell(self, x, y):
        self.kb.remove([S(x, y)])
        self.kb.remove([B(x, y)])
        self.kb.remove([Glitter(x, y)])
        self.kb.remove([W(x, y)])
        self.kb.remove([P(x, y)])

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
        """Kiểm tra xem có Wumpus trên hàng ngang hoặc cột dọc theo hướng mặt hiện tại không."""
        x, y = self.current_pos
        if self.direction in ["East", "West"]:  # Hàng ngang (horizontal)
            for ny in range(self.size):
                if self.kb_world[x][ny].has_wumpus:
                    return True
        elif self.direction in ["North", "South"]:  # Cột dọc (vertical)
            for nx in range(self.size):
                if self.kb_world[nx][y].has_wumpus:
                    return True
        return False

    def find_shooting_position(self):
        """Tìm vị trí an toàn gần nhất trên cùng hàng/cột với một Wumpus đã biết để di chuyển đến và bắn."""
        wumpus_positions = [(i, j) for i in range(self.size) for j in range(self.size) if self.kb_world[i][j].has_wumpus]
        if not wumpus_positions:
            return None

        candidate_positions = []
        for wx, wy in wumpus_positions:
            # Vị trí an toàn trên cùng hàng (row)
            for y_pos in range(self.size):
                if self.kb_world[wx][y_pos].is_safe and (wx, y_pos) != (wx, wy):  # Không phải vị trí Wumpus
                    candidate_positions.append((wx, y_pos))
            # Vị trí an toàn trên cùng cột (column)
            for x_pos in range(self.size):
                if self.kb_world[x_pos][wy].is_safe and (x_pos, wy) != (wx, wy):
                    candidate_positions.append((x_pos, wy))

        if not candidate_positions:
            return None

        # Sắp xếp theo khoảng cách Manhattan gần nhất từ vị trí hiện tại
        candidate_positions = list(set(candidate_positions))  # Loại trùng lặp
        candidate_positions.sort(key=lambda p: self.manhattan_distance(p[0], p[1]))
        return candidate_positions[0]  # Trả về vị trí gần nhất

    def make_decision(self, percepts):
        x, y = self.current_pos

        # Cập nhật percepts vào knowledge base
        self.perceive_and_update(percepts)

        # Kiểm tra và nhặt vàng nếu có
        if percepts[2] and not self.has_gold:  # Glitter = True
            self.has_gold = True
            self.actions = []  # Xóa danh sách hành động để lập kế hoạch mới
            return "Grab"

        # Kiểm tra nếu ở (0,0) và có vàng thì leo ra
        if self.has_gold and self.current_pos == (0, 0):
            print("Agent leo ra tại (0,0) với vàng!")
            return "Climb"
        
        if self.has_gold and self.current_pos != (0, 0):
            start_state = (x, y, self.direction)
            self.actions = self.planner.plan(start_state, (0, 0), self.kb_world)

            if self.actions:
                action = self.actions.pop(0)
                return action

        action = None
        # Nếu danh sách hành động của agent không rỗng    
        if len(self.actions):
            action = self.actions.pop(0)
        
        # Nếu danh sách hành động của agent là rỗng
        else:
            neighbors = self._get_neighbors(x, y) # Tìm kiếm các ô xung quanh

            # Kiểm tra các ô xung quanh có an toàn hay không
            for nx, ny in neighbors:
                # hãy tạo thành một list query truyền vào 1 lần thôi
                is_safe_pit = self.engine.ask(self.kb, Not(P(nx, ny)))
                is_safe_wumpus = self.engine.ask(self.kb, Not(W(nx, ny)))
                has_wumpus = self.engine.ask(self.kb, W(nx, ny))

                if has_wumpus:
                    print(f"Wumpus found at ({nx}, {ny})")
                    self.kb_world[nx][ny].set_has_wumpus(True)

                # Cập nhật kb_world dựa trên kb
                if is_safe_pit and is_safe_wumpus:
                     self.kb_world[nx][ny].is_safe = True
                    
            # Tìm kiếm danh sách các hành động mới
            goal = self.find_goal()
            if goal is not None:
                start_state = (x, y, self.direction)
                self.actions = self.planner.plan(start_state, goal, self.kb_world)

                if self.actions:
                    action = self.actions.pop(0)
            
            # Nếu không có goal an toàn (danh sách hành động rỗng)
            else:
                print("Không còn ô an toàn")
                if self.has_arrow:
                    # Kiểm tra có thể bắn trực tiếp từ vị trí hiện tại không
                    if self.find_wumpus_on_line():
                        self.has_arrow = False  # Bắn rồi thì hết arrow
                        return "Shoot"  # Bắn ngay
                    
                    else:
                        # Tìm vị trí để di chuyển đến để bắn
                        shooting_pos = self.find_shooting_position()
                        
                        print(shooting_pos)

                        if shooting_pos:
                            start_state = (x, y, self.direction)
                            self.actions = self.planner.plan(start_state, shooting_pos, self.kb_world)
                            if self.actions:
                                action = self.actions.pop(0)

                # Nếu không có action từ trên và không còn arrow, random di chuyển
            if action is None:
                neighbors = self._get_neighbors(x, y)
                if neighbors:  # Nếu có ô lân cận
                    unvisited_neighbors = [(nx, ny) for nx, ny in neighbors if not self.kb_world[nx][ny].is_visited]
                    random.shuffle(unvisited_neighbors)  # Xáo trộn để random
                    for nx, ny in unvisited_neighbors:
                        target_dir = self.get_direction_to_neighbor(nx, ny)
                        if target_dir:  # Nếu là ô lân cận hợp lệ
                            directions = ["East", "South", "West", "North"]

                            current_idx = directions.index(self.direction)
                            target_idx = directions.index(target_dir)

                            turns = (target_idx - current_idx) % 4
                            turn_actions = []
                            if turns == 1:
                                turn_actions = ["Turn Right"]
                            elif turns == 2:
                                turn_actions = ["Turn Right", "Turn Right"]
                            elif turns == 3:
                                turn_actions = ["Turn Left"]
                            # Thêm Move Forward
                            self.actions = turn_actions + ["Move Forward"]
                            action = self.actions.pop(0)  # Thực hiện hành động đầu tiên
                            break  # Dừng sau khi chọn được action
                else:
                    # Nếu không có neighbor (ít xảy ra), fallback về (0,0)
                    goal = (0, 0)
                    start_state = (x, y, self.direction)
                    self.actions = self.planner.plan(start_state, goal, self.kb_world)
                    if self.actions:
                        action = self.actions.pop(0)

        return action