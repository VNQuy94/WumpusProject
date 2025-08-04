from collections import defaultdict, deque

from KnowledgeBase import KnowledgeBase, Clause

class InferenceEngine:
    """
    Bộ não suy luận, sử dụng thuật toán Forward Chaining.
    """
    def ask(self, kb, query):
        """
        Kiểm tra xem một query (symbol) có thể được suy ra từ KB hay không.
        
        kb: một đối tượng KnowledgeBase
        query: một chuỗi symbol, ví dụ 'OK12'
        """
        # Đây chính là hàm pl_fc_entails của bạn, được tích hợp vào class
        
        clauses_from_kb = kb.get_clauses()
        count = {}  
        inferred = defaultdict(bool)
        agenda = deque()

        # B1: Khởi tạo
        for clause in clauses_from_kb:
            count[clause] = len(clause.premise)
            if len(clause.premise) == 0:
                # Nếu là một sự thật, thêm ngay vào hàng đợi
                if not inferred[clause.conclusion]:
                    agenda.append(clause.conclusion)
                    inferred[clause.conclusion] = True
        
        # B2: Vòng lặp Forward Chaining
        while agenda:
            p = agenda.popleft()

            if p == query:
                return True

            # Tìm tất cả các quy tắc mà p là một phần của tiền đề
            for clause in clauses_from_kb:
                if p in clause.premise:
                    count[clause] -= 1
                    if count[clause] == 0:
                        # Quy tắc được "kích hoạt", thêm kết luận vào agenda nếu nó là mới
                        if not inferred[clause.conclusion]:
                            agenda.append(clause.conclusion)
                            inferred[clause.conclusion] = True
        
        return False