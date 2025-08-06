# This class is responsible for resolving logical clauses using resolution.
class ResolutionEngine:
    # Negation of a literal.
    def _negate_literal(self, literal):
        if literal.startswith('~'):
            return literal[1:]
        else:
            return f'~{literal}'
    
    # Negation of a clause.
    def _negate_clause(self, clause):
        negated_clauses = []
        for literal in clause:
            negated_literal = self._negate_literal(literal)
            negated_clauses.append((negated_literal,))
        return negated_clauses

    # Resolves two clauses and returns the resolvents.
    def _resolve(self, c1, c2):
        resolvents = set()
        
        clause1_set = set(c1)
        clause2_set = set(c2)
        
        for literal in clause1_set:
            negated_literal = self._negate_literal(literal)
            
            if negated_literal in clause2_set:
                new_clause = (clause1_set - {literal}) | (clause2_set - {negated_literal})
                
                if not self._is_tautology(new_clause):
                    resolvents.add(tuple(sorted(new_clause)))
        
        return resolvents
    
    # Checks if a clause is a tautology.
    def _is_tautology(self, clause_set):
        for literal in clause_set:
            negated = self._negate_literal(literal)
            if negated in clause_set:
                return True
        return False

    def ask(self, kb, query):
        if isinstance(query, str):
            query = (query,)
 
        clauses = set(kb.get_clauses())

        negated_query_clauses = self._negate_clause(query)

        for neg_clause in negated_query_clauses:
            clauses.add(neg_clause)
        
        while True:
            new_clauses = set()
            clauses_list = list(clauses)
            
            for i in range(len(clauses_list)):
                for j in range(i + 1, len(clauses_list)):
                    resolvents = self._resolve(clauses_list[i], clauses_list[j])

                    for resolvent in resolvents:
                        if len(resolvent) == 0:
                            print("True")
                            return True 
                        
                        new_clauses.add(resolvent)
            
            if new_clauses.issubset(clauses):
                print("False")
                return False 
            
            clauses.update(new_clauses)