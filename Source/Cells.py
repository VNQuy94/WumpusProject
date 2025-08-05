# Constants
NUM_GOLD = 1
NUM_ARROW = 1
PIT = 'P'
WUMPUS = 'W'
GOLD = 'G'
STENCH = 'S'
BREEZE = 'B'
EMPTY = '.'

class Cell:
    def __init__(self, x, y):
        self.x = x  # Tọa độ x
        self.y = y  # Tọa độ y
        self.has_wumpus = False  # Có Wumpus không
        self.has_pit = False     # Có hố không
        self.has_gold = False    # Có vàng không
        self.has_stench = False  # Có mùi hôi (stench) không
        self.has_breeze = False  # Có gió (breeze) không
        self.has_glitter = False # Có lấp lánh (glitter) không
        self.is_visited = False  # Ô đã được thăm chưa
        self.is_safe = None      # Trạng thái an toàn (True/False/None cho không chắc chắn)

    def add_content(self, content):
        """Thêm nội dung vào ô (Wumpus, pit, gold)"""
        if content == WUMPUS:
            self.has_wumpus = True
        elif content == PIT:
            self.has_pit = True
        elif content == GOLD:
            self.has_gold = True
            self.has_glitter = True  # Ô có vàng thì có glitter

    def add_effect(self, effect):
        """Thêm hiệu ứng (stench, breeze)"""
        if effect == STENCH:
            self.has_stench = True
        elif effect == BREEZE:
            self.has_breeze = True

    def remove_content(self, content):
        """Xóa nội dung (ví dụ: khi Wumpus chết hoặc vàng bị nhặt)"""
        if content == WUMPUS:
            self.has_wumpus = False
            self.has_stench = False  # Xóa stench nếu Wumpus chết
        elif content == GOLD:
            self.has_gold = False
            self.has_glitter = False  # Xóa glitter nếu vàng bị nhặt

    def get_percepts(self):
        """Trả về các percepts hiện tại của ô"""
        return {
            "stench": self.has_stench,
            "breeze": self.has_breeze,
            "glitter": self.has_glitter,
            "bump": False,  # Bump sẽ được xử lý trong World
            "scream": False  # Scream sẽ được xử lý trong World khi Wumpus chết
        }

    def __str__(self):
        """Hiển thị trạng thái ô cho visualization"""
        if self.has_wumpus:
            return WUMPUS
        
        elif self.has_pit:
            return PIT
        
        elif self.has_gold:
            return GOLD
        
        elif self.has_stench and self.has_breeze:
            return f"{STENCH},{BREEZE}"
        
        elif self.has_stench:
            return STENCH
        
        elif self.has_breeze:
            return BREEZE
        
        return EMPTY