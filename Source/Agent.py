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
        self.bump = False
        self.action_count = 0

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
        if not percepts[0]:
            self.kb.tell(S(x, y))
            self.add_wumpus_rules(x, y)
        else:
            self.kb.tell(Not(S(x, y)))
            neighbors = self._get_neighbors(x, y)
            for nx, ny in neighbors:
                self.kb.tell(Not(W(nx, ny)))
            
        if not percepts[1]:
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

    def agent_update_position(self, action):
        x, y = self.current_pos

        if action == "Turn left":
            if self.direction == "East":
                self.direction = "North"
            elif self.direction == "North":
                self.direction = "West"
            elif self.direction == "West":
                self.direction = "South"
            elif self.direction == "South":
                self.direction = "East"
            
        if action == "Turn right":
            if self.direction == "East":
                self.direction = "South"
            elif self.direction == "South":
                self.direction = "West"
            elif self.direction == "West":
                self.direction = "North"
            elif self.direction == "North":
                self.direction = "East"

        if action == "Move Forward":
            if self.direction == "East":
                x += 1
                if x == 0 or x == self.size - 1:
                    self.bump = True
                    x -= 1

            elif self.direction == "West":
                x -= 1
                if x == 0 or x == self.size - 1:
                    self.bump = True
                    x += 1

            elif self.direction == "South":
                y -= 1
                if y == 0 or y == self.size - 1:
                    self.bump = True
                    y += 1

            elif self.direction == "North":
                y += 1
                if y == 0 or y == self.size - 1:
                    self.bump = True
                    y -= 1

        return x, y

    def make_decision(self, wumpus_world):
        still_alive = True

        while(still_alive):
            x, y = self.current_pos
            percepts = wumpus_world.get_percepts(x, y)

            self.perceive_and_update(percepts)

            # Nếu danh sách hành động của agent không rỗng    
            if len(self.actions):
                action = self.actions.pop(0)

                # Cập nhật vị trí hoặc hướng của agent qua hành động vừa lấy ra khỏi danh sách
                new_x, new_y = self.agent_update_position(action)
                self.action_count += 1

                # Nếu agent di chuyển chạm tường
                if self.bump:
                    print(f"Đụng tường tại ({new_x}, {new_y})")
                    self.bump = False
                    continue
                
                if not self.current_pos == (new_x, new_y):
                    # Cập nhật vị trí mới
                    self.current_pos = (new_x, new_y)
                    self.kb_world[new_x][new_y].is_visited = True

                    # Kiểm tra vị trí mới
                    if not wumpus_world.check_agent_action(x, y):
                        print("Agent đã chết (gặp Wumpus hoặc hố)!")
                        still_alive = False
                        return False
                
                # Kiểm tra và nhặt vàng nếu có
                if percepts[2]:  # Glitter = True
                    self.has_gold = True
                    action = "Grab"
                    grab_gold = wumpus_world.check_agent_action(new_x, new_y, self.direction, action)
                    if grab_gold:
                        print(f"Agent nhặt vàng tại ({new_x}, {new_y})")
                        self.actions = []  # Xóa danh sách hành động để lập kế hoạch mới

                # Kiểm tra nếu ở (0,0) và có vàng thì leo ra
                if self.has_gold and (new_x, new_y) == (0, 0):
                    print("Agent leo ra tại (0,0) với vàng!")
                    return True
            
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
                start_state = (x, y, self.direction, self. has_gold, self.action_count)
                actions = self.planner.plan(start_state, self.kb_world)

                # Nếu danh sách hành động không rỗng thì thêm nó vào danh sách hành động của agent
                if actions:
                    for action in actions:
                        self.actions.append(action)
                
                # Nếu danh sách hành động trả về là rỗng
                else:
                    # Nếu vẫn chưa sử dụng mũi tên, bắn mũi tên theo vị trí và hướng đứng hiện tại
                    if self.has_arrow:
                        self.has_arrow = False
                        action = "Shoot"
                        kill_wumpus = wumpus_world.check_agent_action(x, y, self.direction, action)
                        if kill_wumpus:
                            print("Agent đã hạ gục Wumpus")

                    # Trường hợp nếu không có cung tên

        return False