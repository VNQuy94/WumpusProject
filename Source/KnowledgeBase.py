class Clause:
    # Biểu diễn một mệnh đề xác định (definite clause).
    # Dạng: (P1 ^ P2 ^ ...) => C

    def __init__(self, premise, conclusion):
        # premise: một list các symbol, ví dụ ['S11', 'Clear12']
        self.premise = sorted(premise)
        # conclusion: một symbol duy nhất, ví dụ 'W12'
        self.conclusion = conclusion

    def __repr__(self):
        if not self.premise:
            return f"Fact: {self.conclusion}"
        return f"{' & '.join(self.premise)} => {self.conclusion}"

    # Các hàm sau cần thiết để có thể thêm Clause vào set hoặc dùng làm key trong dict
    def __eq__(self, other):
        return self.premise == other.premise and self.conclusion == other.conclusion

    def __hash__(self):
        return hash((tuple(self.premise), self.conclusion))


class KnowledgeBase:
    # Lưu trữ kiến thức của Agent dưới dạng các đối tượng Clause.

    def __init__(self):
        self.clauses = set() # Dùng set để tránh các quy tắc/sự thật trùng lặp

    def add(self, clause):
        # Thêm một đối tượng Clause vào KB.
        self.clauses.add(clause)

    def tell(self, fact_symbol):
        # Một cách tiện lợi để thêm một sự thật (fact) vào KB.
        self.add(Clause(premise=[], conclusion=fact_symbol))

    def get_clauses(self):
        # Lấy ra toàn bộ kiến thức hiện có.
        return list(self.clauses)

    def __str__(self):
        if not self.clauses:
            return "KB is empty."
        return "Knowledge Base:\n" + "\n".join([f"  - {c}" for c in sorted(list(self.clauses), key=lambda x: x.conclusion)])
