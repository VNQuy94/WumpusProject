from Solution import InferenceEngine
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
        self.engine = InferenceEngine()
        self.planner = Planner(size)
        self.current_pos = (0, 0)
        self.direction = "East"
        self.has_arrow = True
        self.has_gold = False
        self.action_count = 0

    def create_kb_world(self):
        self.kb_world = [[Cell(i, j) for j in range(self.size)] for i in range(self.size)]
        self.kb_world[0][0].is_safe = True
        self.kb_world[0][0].is_visited = True


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
        if percepts.get('stench'):
            self.kb.tell(S(x, y))
            self.add_wumpus_rules(x, y)
        else:
            self.kb.tell(Not(S(x, y)))
            neighbors = self._get_neighbors(x, y)
            for nx, ny in self._get_neighbors(x, y):
                self.kb.tell(Not(W(nx, ny)))
            
        if percepts.get('breeze'):
            self.kb.tell(B(x, y))
            self.add_pit_rules(x, y)
        else:
            self.kb.tell(Not(B(x, y)))
            neighbors = self._get_neighbors(x, y)
            for nx, ny in self._get_neighbors(x, y):
                self.kb.tell(Not(P(nx, ny)))

        if percepts.get('glitter'):
            self.kb.tell(Glitter(x, y))
            self.add_gold_rules(x, y)

    def mark_visited(self):
        """Đánh dấu ô hiện tại là đã thăm."""
        self.kb_world[self.current_pos[0]][self.current_pos[1]].set_is_visited(True)
        self.self.kb_world[self.current_pos[0]][self.current_pos[1]].set_is_safe(True)
        self.kb.tell(Not(P(self.current_pos[0], self.current_pos[1])))
        self.kb.tell(Not(W(self.current_pos[0], self.current_pos[1])))

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

# x, y = self.current_pos
#     neighbors = self._get_neighbors(x, y)
# for nx, ny in neighbors:
#         # Chỉ     xem xét các ô chưa thăm
#             is_safe_1 = self.engine.ask(self.kb, Not(P(nx, ny)))
#             is_safe_2 = self.engine.ask(self.kb, Not(W(nx, ny)))
#             if is_safe_1 and is_safe_2:
#                 safe_moves.append((nx, ny))
#                 self.kb_world[nx][ny].set_is_safe(True)