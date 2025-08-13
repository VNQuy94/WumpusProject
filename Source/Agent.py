from ResolutionEngine import ResolutionEngine
from KnowledgeBase import KnowledgeBase
from Planner import Planner
from Cells import Cell
import random

# Helper functions to create propositional logic symbols for the Wumpus World
def P(x, y): 
    return f"P{x}{y}"  # Pit at coordinates (x, y)

def W(x, y): 
    return f"W{x}{y}"  # Wumpus at coordinates (x, y)

def S(x, y): 
    return f"S{x}{y}"  # Stench at coordinates (x, y)

def B(x, y): 
    return f"B{x}{y}"  # Breeze at coordinates (x, y)

def Not(literal):
    # Negates a literal: if not already negated, prepend '~'; if negated, remove '~'
    return f"~{literal}" if not literal.startswith('~') else literal[1:]

# Agent class representing the Wumpus World AI player
class Agent:
    def __init__(self, size):
        self.size = size  # Grid size of the world
        self.kb_world = [[Cell(x, y) for y in range(self.size)] for x in range(self.size)]  # Internal map representation
        self.kb = KnowledgeBase()  # Knowledge Base storing facts and rules
        self.engine = ResolutionEngine()  # Logical reasoning engine
        self.planner = Planner(size)  # Path planner for movement
        self.actions = []  # Queue of planned actions to execute
        self.current_pos = (0, 0)  # Agent starts at (0, 0)
        self.direction = "East"  # Initial facing direction
        self.has_arrow = True  # Whether the agent still has an arrow
        self.has_gold = False  # Whether the agent has collected the gold
        self.action_count = 0  # Number of actions taken so far
        self.shooting_plan = None  # Planned position and direction to shoot Wumpus

    def set_arrow(self, value):
        # Update whether the agent has an arrow
        self.has_arrow = value
        
    def manhattan_distance(self, x, y):
        # Compute Manhattan distance from current position to (x, y)
        return abs(x - self.current_pos[0]) + abs(y - self.current_pos[1])
    
    def create_kb_world(self):
        # Reset internal world representation and mark starting cell as safe & visited
        self.kb_world = [[Cell(i, j) for j in range(self.size)] for i in range(self.size)]
        self.kb_world[0][0].is_safe = True
        self.kb_world[0][0].is_visited = True
        self.kb.tell(Not(P(0, 0)))  # No pit at start
        self.kb.tell(Not(W(0, 0)))  # No Wumpus at start

    def _get_neighbors(self, x, y):
        # Return list of adjacent valid cell coordinates
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors

    def get_direction_to_neighbor(self, nx, ny):
        """Return direction from current_pos to given neighbor cell."""
        x, y = self.current_pos
        if nx == x and ny == y + 1:
            return "East"
        elif nx == x and ny == y - 1:
            return "West"
        elif nx == x + 1 and ny == y:
            return "North"
        elif nx == x - 1 and ny == y:
            return "South"
        return None  # Not a valid adjacent cell

    def add_wumpus_rules(self, x, y):
        # Add logical constraints related to Wumpus based on Stench perception at (x, y)
        neighbors = self._get_neighbors(x, y)
        if not neighbors:
            return
    
        literals = [W(nx, ny) for nx, ny in neighbors]
        self.kb.add([Not(S(x,y))] + literals)  # If no Stench, no Wumpus in neighbors
        for nx, ny in neighbors:
            self.kb.add([Not(W(nx, ny)), S(x, y)])  # If Wumpus absent, Stench still possible

    def add_pit_rules(self, x, y):
        # Add logical constraints related to Pits based on Breeze perception at (x, y)
        neighbors = self._get_neighbors(x, y)
        if not neighbors:
            return
        
        literals = [P(nx, ny) for nx, ny in neighbors]
        self.kb.add([Not(B(x,y))] + literals)  # If no Breeze, no Pit in neighbors
        for nx, ny in neighbors:
            self.kb.add([Not(P(nx, ny)), B(x, y)])  # If Pit absent, Breeze still possible

    def remove_rules_for_cell(self, x, y):
        # Remove all hazard rules involving this cell and its neighbors
        neighbors = self._get_neighbors(x, y)

        # Remove Wumpus rules
        if neighbors:
            wumpus_literals = [W(nx, ny) for nx, ny in neighbors]
            self.kb.remove([Not(S(x,y))] + wumpus_literals)
            for nx, ny in neighbors:
                self.kb.remove([Not(W(nx, ny)), S(x, y)])
                
        # Remove Pit rules
        if neighbors:
            pit_literals = [P(nx, ny) for nx, ny in neighbors]
            self.kb.remove([Not(B(x,y))] + pit_literals)
            for nx, ny in neighbors:
                self.kb.remove([Not(P(nx, ny)), B(x, y)])

    def infer_local_hazards(self, x, y):
        """
        Deduce certain hazards immediately:
        - If Stench present and only one unknown neighbor remains, it's Wumpus.
        - If Breeze present and only one unknown neighbor remains, it's a Pit.
        Updates both KB and kb_world directly.
        """
        neighbors = self._get_neighbors(x, y)
        if not neighbors:
            return

        # Wumpus deduction
        if self.engine.ask(self.kb, S(x, y)):
            unknown_wumpus_candidates = [
                (nx, ny) for nx, ny in neighbors
                if not self.engine.ask(self.kb, Not(W(nx, ny)))
            ]
            if len(unknown_wumpus_candidates) == 1:
                wx, wy = unknown_wumpus_candidates[0]
                if not self.engine.ask(self.kb, W(wx, wy)):
                    self.kb.tell(W(wx, wy))
                self.kb_world[wx][wy].set_has_wumpus(True)
                for nx, ny in neighbors:
                    if (nx, ny) != (wx, wy):
                        self.kb.tell(Not(W(nx, ny))))

        # Pit deduction
        if self.engine.ask(self.kb, B(x, y)):
            unknown_pit_candidates = [
                (nx, ny) for nx, ny in neighbors
                if not self.engine.ask(self.kb, Not(P(nx, ny)))
            ]
            if len(unknown_pit_candidates) == 1:
                px, py = unknown_pit_candidates[0]
                if not self.engine.ask(self.kb, P(px, py)):
                    self.kb.tell(P(px, py))
                self.kb_world[px][py].set_has_pit(True)
                for nx, ny in neighbors:
                    if (nx, ny) != (px, py):
                        self.kb.tell(Not(P(nx, ny))))

    def perceive_and_update(self, percepts):
        """
        Update KB based on percepts received:
        percepts = [Stench, Breeze, Glitter, Bump, Scream]
        """
        x, y = self.current_pos

        # Process Stench
        if percepts[0]:
            self.kb.tell(S(x, y))
            self.add_wumpus_rules(x, y)
        else:
            self.kb.tell(Not(S(x, y)))
            for nx, ny in self._get_neighbors(x, y):
                self.kb.tell(Not(W(nx, ny)))
        
        # Process Breeze
        if percepts[1]:
            self.kb.tell(B(x, y))
            self.add_pit_rules(x, y)
        else:
            self.kb.tell(Not(B(x, y)))
            for nx, ny in self._get_neighbors(x, y):
                self.kb.tell(Not(P(nx, ny)))

        # Process Scream — if Wumpus killed, mark all cells in that direction as safe
        if percepts[3]:
            dx, dy = 0, 0
            if self.direction == 'East': dy = 1
            elif self.direction == 'West': dy = -1
            elif self.direction == 'North': dx = 1                 
            elif self.direction == 'South': dx = -1
            current_x, current_y = x + dx, y + dy
            while 0 <= current_x < self.size and 0 <= current_y < self.size:
                if not self.kb_world[current_x][current_y].is_visited:
                    self.kb.tell(Not(W(current_x, current_y)))
                    self.kb.remove(W(current_x, current_y))
                    self.kb_world[current_x][current_y].set_has_wumpus(False)
                    self.kb_world[current_x][current_y].set_is_safe(True)
                current_x += dx
                current_y += dy

        # Attempt immediate hazard inference
        self.infer_local_hazards(x, y)

    def agent_update_state(self, action):
        # Extract current position coordinates (x: row, y: column)
        x, y = self.current_pos

        # Define the order of directions (clockwise order)
        directions = ["East", "South", "West", "North"]
        # Get the current facing direction index
        agent_direction_index = directions.index(self.direction)

        # If the action is to turn left, update direction counterclockwise
        if action == "Turn Left":
            self.direction = directions[(agent_direction_index - 1) % 4]
            
        # If the action is to turn right, update direction clockwise
        if action == "Turn Right":
            self.direction = directions[(agent_direction_index + 1) % 4]

        # If the action is to move forward, update position based on direction
        if action == "Move Forward":
            # Remove rules associated with the current cell (e.g., hazards)
            self.remove_rules_for_cell(x, y)
            # Move east (increase column) if not at the right boundary
            if self.direction == "East":
                if y < self.size - 1:
                    y += 1
            # Move west (decrease column) if not at the left boundary
            elif self.direction == "West":
                if y > 0:
                    y -= 1
            # Move south (decrease row index) if not at the bottom boundary
            elif self.direction == "South":
                if x > 0:
                    x -= 1
            # Move north (increase row index) if not at the top boundary
            elif self.direction == "North":
                if x < self.size - 1:
                    x += 1

        # Update the agent's current position
        self.current_pos = (x, y)
        # Mark the current cell as visited and safe
        self.kb_world[x][y].set_is_visited(True)
        self.kb_world[x][y].set_is_safe(True)
        # Store the turn number when this cell was visited
        self.kb_world[x][y].set_turn_visited(self.action_count)

    def find_goal(self):
        # If the agent already has the gold, the goal is the start cell (0,0)
        if self.has_gold:
            return (0, 0)
        
        # Find all safe but unvisited cells
        safe_unvisited = [(x, y) for x in range(self.size) for y in range(self.size)
                          if self.kb_world[x][y].is_safe and not self.kb_world[x][y].is_visited]
        
        # Sort them by Manhattan distance from the current position
        if safe_unvisited:
            safe_unvisited.sort(key=lambda p: self.manhattan_distance(p[0], p[1]))

            # Prioritize a safe cell directly in front of the agent
            x, y = self.current_pos
            if self.direction == "East":
                if (x, y + 1) in safe_unvisited:
                    return (x, y + 1)
            elif self.direction == "West":
                if (x, y - 1) in safe_unvisited:
                    return (x, y - 1)
            elif self.direction == "South":
                if (x - 1, y) in safe_unvisited:
                    return (x - 1, y)
            elif self.direction == "North":
                if (x + 1, y) in safe_unvisited:
                    return (x + 1, y)
            
            # Otherwise, return the nearest safe cell
            return safe_unvisited[0]
        
        # No safe cells left
        return None

    def find_shooting_position(self):
        """
        Find the nearest safe position in the same row or column
        as a known Wumpus location. Return (shooting_position, shooting_direction)
        or None if no suitable position exists.
        """
        # Find all known Wumpus positions
        wumpus_positions = [
            (i, j) 
            for i in range(self.size) 
            for j in range(self.size) 
            if self.kb_world[i][j].has_wumpus
        ]
        if not wumpus_positions:
            return None

        candidate_positions = []
        for wx, wy in wumpus_positions:
            # Safe positions in the same row
            for y_pos in range(self.size):
                if self.kb_world[wx][y_pos].is_safe and (wx, y_pos) != (wx, wy):
                    candidate_positions.append(((wx, y_pos), wx, wy))
            # Safe positions in the same column
            for x_pos in range(self.size):
                if self.kb_world[x_pos][wy].is_safe and (x_pos, wy) != (wx, wy):
                    candidate_positions.append(((x_pos, wy), wx, wy))

        # If no safe shooting positions found
        if not candidate_positions:
            return None

        # Remove duplicates by position
        seen = {}
        for shoot_pos, wx, wy in candidate_positions:
            seen[shoot_pos] = (wx, wy)
        candidate_positions = [(pos, seen[pos][0], seen[pos][1]) for pos in seen]

        # Sort by Manhattan distance from the agent's position
        candidate_positions.sort(
            key=lambda item: self.manhattan_distance(item[0][0], item[0][1])
        )

        # Select the nearest shooting position
        shoot_pos, wx, wy = candidate_positions[0]

        # Determine shooting direction
        if shoot_pos[0] == wx:
            shoot_dir = "East" if wy > shoot_pos[1] else "West"
        elif shoot_pos[1] == wy:
            shoot_dir = "South" if wx < shoot_pos[0] else "North"

        return shoot_pos, shoot_dir

    def handle_wumpus_move(self):
        # Keep only clauses not related to Wumpus or Stench
        clause_to_keep = []
        all_clauses = self.kb.get_clauses()
        for clause in all_clauses:
            is_wumpus_stench_related = False
            for literal in clause:
                if 'W' in literal or 'S' in literal:
                    is_wumpus_stench_related = True
                    break
            if not is_wumpus_stench_related:
                clause_to_keep.append(clause)

        # Update KB clauses
        self.kb.clauses = set(clause_to_keep)

        # Update Wumpus-related knowledge in the grid
        for row in range(self.size):
            for col in range(self.size):
                if self.kb_world[row][col].is_visited and self.action_count - self.kb_world[row][col].turn_visited <= 5 and S(row, col) not in all_clauses:
                    self.kb.tell(Not(W(row, col)))
                else:
                    self.kb_world[row][col].set_has_wumpus(False)
                    self.kb_world[row][col].set_is_safe(False)
                    self.kb_world[row][col].set_is_visited(False)

        # Reset planned actions and shooting plan
        self.actions = []
        self.shooting_plan = None

    def make_decision(self, percepts):
        # Order of directions
        directions = ["East", "South", "West", "North"]

        # Current coordinates
        x, y = self.current_pos

        # Update KB with percepts
        self.perceive_and_update(percepts)

        # If gold detected (Glitter = True) and not yet collected → Grab
        if percepts[2] and not self.has_gold:
            self.has_gold = True
            return "Grab"
        
        # If already have gold and at start → Climb out immediately
        if self.has_gold and self.current_pos == (0, 0):
            return "Climb"
        
        # If there are pre-planned actions, execute next one
        if self.actions:
            return self.actions.pop(0)
        
        # If gold obtained → plan a route back to start
        if self.has_gold:
            if self.kb_world[0][0].is_safe:
                print("Gold acquired, planning route back to start.")
                start_state = (self.current_pos[0], self.current_pos[1], self.direction)
                self.actions = self.planner.plan(start_state, (0, 0), self.kb_world)
                print(self.actions)
                return self.actions.pop(0)

        # If at shooting position → aim and shoot
        if self.shooting_plan and self.current_pos == self.shooting_plan['target_pos']:
            target_dir = self.shooting_plan['target_dir']

            # Calculate turning actions to face target
            turn_actions = []
            current_idx = directions.index(self.direction)
            target_idx = directions.index(target_dir)
            turn = (target_idx - current_idx) % 4
            if turn == 1:
                turn_actions = ["Turn Right"]
            elif turn == 2:
                turn_actions = ["Turn Right", "Turn Right"]
            elif turn == 3:
                turn_actions = ["Turn Left"]
            self.actions = turn_actions + ["Shoot"]
            self.shooting_plan = None
            return self.actions.pop(0)      
        
        # If no actions queued → analyze neighbors
        if not self.actions:
            neighbors = self._get_neighbors(x, y) # Get adjacent cells

            # Check each neighbor's safety using KB
            for nx, ny in neighbors:
                is_safe_pit = self.engine.ask(self.kb, Not(P(nx, ny)))
                is_safe_wumpus = self.engine.ask(self.kb, Not(W(nx, ny)))

                # Update KB world safety info
                if is_safe_pit and is_safe_wumpus:
                    self.kb_world[nx][ny].set_is_safe(True)
                else:
                    has_wumpus = self.engine.ask(self.kb, W(nx, ny))
                    has_pit = self.engine.ask(self.kb, P(nx, ny))

                    if has_wumpus:
                        print(f"Wumpus found at ({nx}, {ny})")
                        self.kb.tell(W(nx, ny))
                        self.kb_world[nx][ny].set_has_wumpus(True)
                    if has_pit:
                        self.kb.tell(P(nx, ny))
                        self.kb_world[nx][ny].set_has_pit(True)

            # Search for a safe goal
            goal = self.find_goal()
            print(goal)
            if goal is not None:
                start_state = (x, y, self.direction)
                self.actions = self.planner.plan(start_state, goal, self.kb_world)
            else:
                # No safe cells left
                print("No safe cells remaining")
                if self.has_arrow:
                    # Try to find a shooting position
                    shoot_info = self.find_shooting_position()
                    print(shoot_info)
                    if shoot_info:
                        shoot_pos, shoot_dir = shoot_info
                        if shoot_pos and shoot_dir:
                            self.shooting_plan = {'target_pos': shoot_pos, 'target_dir': shoot_dir}
                            start_state = (x, y, self.direction)
                            self.actions = self.planner.plan(start_state, shoot_pos, self.kb_world)

            # If still no actions → move randomly to unvisited neighbor
            if not self.actions:
                neighbors = self._get_neighbors(x, y)
                unvisited_neighbors = [(nx, ny) for nx, ny in neighbors if not self.kb_world[nx][ny].is_visited]
                if unvisited_neighbors:
                    random.shuffle(unvisited_neighbors)  # Shuffle for randomness
                    for nx, ny in unvisited_neighbors:
                        target_dir = self.get_direction_to_neighbor(nx, ny)
                        if target_dir:
                            current_idx = directions.index(self.direction)
                            target_idx = directions.index(target_dir)
                            turn = (target_idx - current_idx) % 4
                            turn_actions = []
                            if turn == 1:
                                turn_actions = ["Turn Right"]
                            elif turn == 2:
                                turn_actions = ["Turn Right", "Turn Right"]
                            elif turn == 3:
                                turn_actions = ["Turn Left"]
                            self.actions = turn_actions + ["Move Forward"]
                            break
                else:
                    # If trapped → fallback to start and climb out
                    goal = (0, 0)
                    start_state = (x, y, self.direction)
                    self.actions = self.planner.plan(start_state, goal, self.kb_world)
                    self.actions.append("Climb")

        # Execute the next planned action
        return self.actions.pop(0)
