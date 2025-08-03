class KnowledgeBase:
    def __init__(self, size):
        self.size = size
        # Lưu trạng thái ô: { (x,y): { "safe": True/False/None, "wumpus": True/False/None, "pit": True/False/None, "visited": True/False } }
        self.kb = {(x, y): {"safe": None, "wumpus": None, "pit": None, "visited": False}
                   for x in range(size) for y in range(size)}
        self.kb[(0, 0)] = {"safe": True, "wumpus": False, "pit": False, "visited": True}
        self.rules = []  # Danh sách quy tắc logic

    def update(self, x, y, percepts):
        """Cập nhật KB dựa trên percepts tại ô (x,y)"""
        self.kb[(x, y)]["visited"] = True
        if percepts["glitter"]:
            self.kb[(x, y)]["safe"] = True
            self.kb[(x, y)]["wumpus"] = False
            self.kb[(x, y)]["pit"] = False
        if not percepts["stench"] and not percepts["breeze"]:
            self.kb[(x, y)]["safe"] = True
            self.kb[(x, y)]["wumpus"] = False
            self.kb[(x, y)]["pit"] = False
            # Suy ra các ô lân cận an toàn
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    self.kb[(nx, ny)]["wumpus"] = False
                    self.kb[(nx, ny)]["pit"] = False
                    self.kb[(nx, ny)]["safe"] = True
        if percepts["stench"]:
            # Thêm quy tắc: Wumpus ở một ô lân cận
            neighbors = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                         if 0 <= x + dx < self.size and 0 <= y + dy < self.size]
            self.rules.append(("stench", (x, y), neighbors))
        if percepts["breeze"]:
            # Thêm quy tắc: Pit ở một ô lân cận
            neighbors = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                         if 0 <= x + dx < self.size and 0 <= y + dy < self.size]
            self.rules.append(("breeze", (x, y), neighbors))

    def infer(self):
        """Suy luận dựa trên quy tắc và KB hiện tại"""
        # Ví dụ: Forward chaining
        for rule_type, (x, y), neighbors in self.rules:
            if rule_type == "stench":
                # Kiểm tra nếu chỉ còn một ô lân cận có thể chứa Wumpus
                unknown_neighbors = [n for n in neighbors if self.kb[n]["wumpus"] is None]
                if len(unknown_neighbors) == 1:
                    self.kb[unknown_neighbors[0]]["wumpus"] = True
                    self.kb[unknown_neighbors[0]]["safe"] = False
            elif rule_type == "breeze":
                # Tương tự cho pit
                unknown_neighbors = [n for n in neighbors if self.kb[n]["pit"] is None]
                if len(unknown_neighbors) == 1:
                    self.kb[unknown_neighbors[0]]["pit"] = True
                    self.kb[unknown_neighbors[0]]["safe"] = False

    def is_safe(self, x, y):
        """Kiểm tra ô (x,y) có an toàn không"""
        return self.kb[(x, y)]["safe"] == True