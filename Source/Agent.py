from Solution import InferenceEngine
from KnowledgeBase import KnowledgeBase, Clause

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
        self.kb = KnowledgeBase()
        self.engine = InferenceEngine()
        
        self.current_pos = (0, 0)
        self.visited_cells = set()
        
        # # Thêm sự thật ban đầu
        # # Thay vì ~P00, ~W00, chúng ta tạo ra các sự thật khẳng định
        # self.kb.tell(f'OK00') # Ô (0,0) an toàn

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

    def mark_visited(self):
        """Đánh dấu ô hiện tại là đã thăm."""
        self.visited_cells.add(self.current_pos)

    def make_decision(self):
        """
        Sử dụng bộ não để tìm các ô an toàn và quyết định nước đi tiếp theo.
        """
        x, y = self.current_pos
        
        neighbors = self._get_neighbors(x, y)

        safe_moves = []

        for nx, ny in neighbors:
            # Chỉ xem xét các ô chưa thăm
            if (nx, ny) not in self.visited_cells:
                # Hỏi bộ não: "Liệu ô (nx,ny) có an toàn không?"
                is_safe = self.engine.ask(self.kb, OK(nx, ny))
                if is_safe:
                    safe_moves.append((nx, ny))
                        
        print(f"Inferred safe and unvisited cells: {safe_moves}")
        
        if not safe_moves:
            print("Decision: No provably safe moves. Agent should consider backtracking or taking a risk.")
            return None
        else:
            # Logic đơn giản: chọn ô an toàn gần nhất để đi
            # (Ở đây bạn sẽ tích hợp thuật toán A*)
            next_move = safe_moves[0]
            print(f"Decision: Plan to move to the safe cell {next_move}.")
            self.current_pos = next_move
            self.mark_visited()
        
# --- Main Execution ---
if __name__ == "__main__":
    # Kịch bản giả lập
    # Agent bắt đầu ở (0,0), không cảm thấy gì.
    my_agent = Agent(size=4)
    
    # Lượt 1: Tại (0,0)
    print("--- TURN 1 ---")
    print(f"Current position: {my_agent.current_pos}")
    percepts_at_00 = {} # Không có gì
    my_agent.perceive_and_update(percepts_at_00)
    print(my_agent.kb)
    my_agent.make_decision() # Sẽ suy ra (0,1) và (1,0) là an toàn

    # Lượt 2: Agent di chuyển đến (1,0)
    # Giả sử tại (1,0) có gió mát
    print("\n--- TURN 2 ---")
    # my_agent.current_pos = (1,0)
    print(f"Current position: {my_agent.current_pos}")
    percepts_at_01 = {'breeze': True}
    my_agent.perceive_and_update(percepts_at_01)
    print(my_agent.kb)
    my_agent.make_decision() # Lần này sẽ không thể chứng minh (2,0) hay (1,1) an toàn
                             # chỉ dựa trên quy tắc đơn giản.
    
    my_agent.make_decision()  # Agent sẽ quyết định di chuyển đến (0,1) hoặc (1,1) nếu có quy tắc an toàn
    print(f"Current position: {my_agent.current_pos}")

    # Lượt 3: Giả sử tại (1,0) có mùi hôi
    print("\n--- TURN 3 ---")
    print(f"Current position: {my_agent.current_pos}")
    percepts_at_01 = {'stench': True}
    my_agent.perceive_and_update(percepts_at_01)
    print(my_agent.kb)
    my_agent.make_decision() # Lần này sẽ không thể chứng minh (2,0) hay (1,1) an toàn
                            # chỉ dựa trên quy tắc đơn giản.