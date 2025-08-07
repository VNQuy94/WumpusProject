from ResolutionEngine import ResolutionEngine
from KnowledgeBase import KnowledgeBase
from Planner import Planner
from Cells import Cell

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
        return abs(self.current_pos[0] - x) + abs(self.current_pos[1] - y)
    
    def create_kb_world(self):
        self.kb_world = [[Cell(i, j) for j in range(self.size)] for i in range(self.size)]
        self.kb_world[self.size - 1][0].is_safe = True
        self.kb_world[self.size - 1][0].is_visited = True
        self.kb.tell(Not(P(0, 0)))
        self.kb.tell(Not(W(0, 0)))

    def _get_neighbors(self, x, y):
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors

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

    def agent_update_state(self, action, percepts):
        x, y = self.current_pos

        directions = ["East", "South", "West", "North"]
        agent_direction_index = directions.index(self.direction)

        if action == "Turn left":
            self.direction = directions[(agent_direction_index - 1) % 4]
            
        if action == "Turn right":
            self.direction = directions[(agent_direction_index + 1) % 4]

        if action == "Move Forward":
            if self.direction == "East":
                y += 1

            elif self.direction == "West":
                y -= 1

            elif self.direction == "South":
                x -= 1

            elif self.direction == "North":
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
            
    def make_decision(self, percepts):
        x, y = self.current_pos

        # Cập nhật percepts vào knowledge base
        self.perceive_and_update(percepts)

        # Kiểm tra và nhặt vàng nếu có
        if percepts[2]:  # Glitter = True
            self.has_gold = True
            self.actions = []  # Xóa danh sách hành động để lập kế hoạch mới
            return "Grab"

        # Kiểm tra nếu ở (0,0) và có vàng thì leo ra
        if self.has_gold and self.current_pos == (0, 0):
            print("Agent leo ra tại (0,0) với vàng!")
            return "Climb"

        action = None
        # Nếu danh sách hành động của agent không rỗng    
        if len(self.actions):
            action = self.actions.pop(0)
        
        # Nếu danh sách hành động của agent là rỗng
        else:
            neighbors = self._get_neighbors(x, y) # Tìm kiếm các ô xung quanh

            # Kiểm tra các ô xung quanh có an toàn hay không
            for nx, ny in neighbors:
                is_safe_pit = self.engine.ask(self.kb, Not(P(nx, ny)))
                is_safe_wumpus = self.engine.ask(self.kb, Not(W(nx, ny)))

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
            
            # Nếu danh sách hành động trả về là rỗng
            else:
                # Nếu vẫn chưa sử dụng mũi tên, bắn mũi tên theo vị trí và hướng đứng hiện tại
                if self.has_arrow:
                    self.has_arrow = False
                    action = "Shoot"

                # Trường hợp nếu không có cung tên
        return action