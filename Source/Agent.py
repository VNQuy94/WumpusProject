from Solution import InferenceEngine
from KnowledgeBase import KnowledgeBase, Clause
from Planner import Planner
from Cells import Cell

def P(x, y):
    """Tạo literal 'Có Hố' tại (x,y)"""
    return f"P{x}{y}"

def W(x, y):
    """Tạo literal 'Có Wumpus' tại (x,y)"""
    return f"W{x}{y}"

def S(x, y):
    """Tạo literal 'Có Mùi hôi' tại (x,y)"""
    return f"S{x}{y}"

def B(x, y):
    """Tạo literal 'Có Gió' tại (x,y)"""
    return f"B{x}{y}"

def OK(x, y):
    """Tạo literal 'Ô an toàn' tại (x,y)"""
    return f"OK{x}{y}"

def Not(literal):
    """Tạo literal PHỦ ĐỊNH"""
    if literal.startswith('~'):
        return literal[1:]  # Phủ định hai lần thì về ban đầu
    return f"~{literal}"

class Agent:
    def __init__(self, size):
        self.size = size
        self.kb_world = None
        self.kb = KnowledgeBase()
        self.engine = InferenceEngine()
        self.planner = Planner(size)
        self.current_pos = (0, 0)
        self.direction = "East"
        self.has_arrow = True
        self.has_gold = False
        self.action_count = 0
        self.kb.tell(f'OK00')   # Ô (0,0) an toàn

    def create_kb_world(self):
        self.kb_world = [[Cell(i, j) for j in range(self.size)] for i in range(self.size)]
        self.kb_world[0][0].is_safe = True
        self.kb_world[0][0].is_visited = True


    def _get_neighbors(self, x, y):
        """Lấy các ô hàng xóm hợp lệ."""
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors

    def add_wumpus_rules(self, x, y):
        neighbors = self._get_neighbors(x, y)
        for nx, ny in neighbors:
            rule = Clause([S(x, y)], W(nx, ny))
            self.kb.add(rule)

    def add_pit_rules(self, x, y):
        neighbors = self._get_neighbors(x, y)
        for nx, ny in neighbors:
            rule = Clause([B(x, y)], P(nx, ny))
            self.kb.add(rule)
    
    def add_safe_rules(self, x, y):
        neighbors = self._get_neighbors(x, y)
        for nx, ny in neighbors:
            rule = Clause([Not(S(x, y)), Not(B(x, y))], OK(nx, ny))
            self.kb.add(rule)

    def perceive_and_update(self, percepts):
        x, y = self.current_pos
        # Dịch cảm nhận thành các symbol khẳng định
        if percepts.get('stench'):
            self.kb.tell(S(x, y))
            self.add_wumpus_rules(x, y)
        else:
            self.kb.tell(Not(S(x, y)))
            
        if percepts.get('breeze'):
            self.kb.tell(B(x, y))
            self.add_pit_rules(x, y)
        else:
            self.kb.tell(Not(B(x, y)))
        
        # Nếu không có mùi, không có gió, ô này chắc chắn an toàn
        if not percepts.get('stench') and not percepts.get('breeze'):
            self.kb.tell(OK(x, y))
            self.add_safe_rules(x, y)

    def make_decision(self):
        """Sử dụng A* để lập kế hoạch hành động."""
        x, y = self.current_pos
        state = (x, y, self.direction, self.has_arrow, self.has_gold, self.action_count)
        action = self.planner.plan(state, self.kb_world)

        if not action:
            print("No safe plan found. Agent may need to backtrack or take a risk.")
            return None

        # Thực hiện hành động trong kế hoạch
        print(f"Decision: {action}")
        self.action_count += 1

        if action == "Move Forward":
            if self.direction == "East":
                self.current_pos = (x + 1, y)
                self.kb_world[x + 1][y].is_visited = True

            elif self.direction == "West":
                self.current_pos = (x - 1, y)
                self.kb_world[x - 1][y].is_visited = True

            elif self.direction == "North":
                self.current_pos = (x, y + 1)
                self.kb_world[x][y + 1].is_visited = True

            elif self.direction == "South":
                self.current_pos = (x, y - 1)
                self.kb_world[x][y - 1].is_visited = True

        elif action == "Turn Left":
            dir_idx = self.planner.directions.index(self.direction)
            self.direction = self.planner.directions[(dir_idx - 1) % 4]

        elif action == "Turn Right":
            dir_idx = self.planner.directions.index(self.direction)
            self.direction = self.planner.directions[(dir_idx + 1) % 4]

        elif action == "Grab":
            self.has_gold = True
            self.kb_world[x][y].remove_content('GOLD')

        elif action == "Shoot":
            self.has_arrow = False
            # Giả sử World xử lý việc bắn và phát ra scream

        elif action == "Climb":
            if x == 0 and y == 0 and self.has_gold:
                print("Agent climbs out with gold. Game over!")