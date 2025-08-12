# Class to manage a knowledge base for an AI agent.
class KnowledgeBase:
    def __init__(self):
        self.clauses = set()

    def _standardize_clause(self, clause):
        return tuple(sorted(list(set(clause))))

    def add(self, clause):
        if not isinstance(clause, (list, tuple)):
            raise TypeError("Clause must be a list or tuple of literals.")

        standardized_clause = self._standardize_clause(clause)
        if standardized_clause in self.clauses:
            return
        self.clauses.add(standardized_clause)

    def remove(self, clause):
        standardized_clause = self._standardize_clause(clause)
        if standardized_clause not in self.clauses:
            return
        self.clauses.discard(standardized_clause)

    def tell(self, literal):
        self.add([literal])

        # tôi muốn kiểm tra literal đối có trong kb không, nếu có thì xóa thì làm sao
        if literal.startswith('~'):
            # Lấy chuỗi bên trong "Not(...)"
            literal = literal[1:]
        else:
            literal = f"~{literal}"

        self.remove([literal])

    def get_clauses(self):
        return self.clauses

    def __str__(self):
        if not self.clauses:
            return "KB is empty."
        sorted_clauses = sorted(list(self.clauses), key=lambda c: len(c))
        return "Knowledge Base:\n" + "\n".join([f"  - {' v '.join(c)}" for c in sorted_clauses])