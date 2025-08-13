# Class to manage a knowledge base for an AI agent.
class KnowledgeBase:
    def __init__(self):
        # A set to store clauses, each clause is represented as a tuple of literals.
        self.clauses = set()

    def _standardize_clause(self, clause):
        """
        Convert a clause (list/tuple of literals) into a sorted tuple without duplicates.
        This ensures that clauses are stored in a consistent format so they can be compared easily.
        """
        return tuple(sorted(list(set(clause))))

    def add(self, clause):
        """
        Add a clause to the knowledge base.
        clause: list or tuple of literals (e.g., ['P1', '~W2'])
        """
        if not isinstance(clause, (list, tuple)):
            raise TypeError("Clause must be a list or tuple of literals.")

        standardized_clause = self._standardize_clause(clause)
        if standardized_clause in self.clauses:
            return  # Clause already exists, do nothing
        self.clauses.add(standardized_clause)

    def remove(self, clause):
        """
        Remove a clause from the knowledge base if it exists.
        """
        standardized_clause = self._standardize_clause(clause)
        if standardized_clause not in self.clauses:
            return  # Clause not found, do nothing
        self.clauses.discard(standardized_clause)

    def tell(self, literal):
        """
        Add a single literal to the knowledge base as a new clause.
        Also removes its opposite literal (negation) if it exists in the KB.
        
        literal: string representing a fact (e.g., 'P1') or its negation (e.g., '~P1')
        """
        # Add the literal as a new clause
        self.add([literal])

        # If literal is negative, strip '~' to get positive version
        # Otherwise, create the negative version
        if literal.startswith('~'):
            literal = literal[1:]  # Remove '~' prefix
        else:
            literal = f"~{literal}"  # Add '~' prefix

        # Remove the opposite literal if present
        self.remove([literal])

    def get_clauses(self):
        """
        Return all clauses currently stored in the knowledge base.
        """
        return self.clauses

    def __str__(self):
        """
        Return a formatted string representation of the knowledge base.
        Clauses are sorted by length for readability.
        """
        if not self.clauses:
            return "KB is empty."
        sorted_clauses = sorted(list(self.clauses), key=lambda c: len(c))
        return "Knowledge Base:\n" + "\n".join([f"  - {' v '.join(c)}" for c in sorted_clauses])
