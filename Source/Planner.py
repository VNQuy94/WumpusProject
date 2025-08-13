from heapq import heappush, heappop
from collections import defaultdict

class Planner:
    def __init__(self, size):
        self.size = size
        # Directions are ordered clockwise for easy turn calculations
        self.directions = ["East", "South", "West", "North"]

    def manhattan_distance(self, x1, y1, x2, y2):
        """
        Calculate the Manhattan distance between two coordinates.
        This is used as a heuristic for the A* algorithm.
        """
        return abs(x1 - x2) + abs(y1 - y2)

    def get_neighbors(self, state, kb_world):
        """
        Get valid neighboring states from the current state.
        
        state: (x, y, direction)
        kb_world: Knowledge Base world (contains safety information)
        
        Returns: list of tuples -> (next_state, action, cost)
        """
        x, y, direction = state
        neighbors = []
        dir_idx = self.directions.index(direction)

        # Move Forward (only into safe cells)
        if direction == "East" and y < self.size - 1:
            if kb_world[x][y + 1].is_safe:
                neighbors.append(((x, y + 1, direction), "Move Forward", 1))
        elif direction == "West" and y > 0:
            if kb_world[x][y - 1].is_safe:
                neighbors.append(((x, y - 1, direction), "Move Forward", 1))
        elif direction == "North" and x < self.size - 1:
            if kb_world[x + 1][y].is_safe:
                neighbors.append(((x + 1, y, direction), "Move Forward", 1))
        elif direction == "South" and x > 0:
            if kb_world[x - 1][y].is_safe:
                neighbors.append(((x - 1, y, direction), "Move Forward", 1))

        # Turn Left (cost 1)
        new_dir = self.directions[(dir_idx - 1) % 4]
        neighbors.append(((x, y, new_dir), "Turn Left", 1))

        # Turn Right (cost 1)
        new_dir = self.directions[(dir_idx + 1) % 4]
        neighbors.append(((x, y, new_dir), "Turn Right", 1))

        return neighbors

    def plan(self, start_state, goal_position, kb_world):
        """
        A* Search Algorithm to find an optimal path based on the knowledge base.
        
        start_state: (x, y, direction) - starting coordinates and facing direction
        goal_position: (x, y) - target coordinates
        kb_world: Knowledge Base world (contains safety information)
        
        Returns: list of actions that form the plan
        """
        # Priority queue (min-heap) of states to explore: (f_score, state, actions_taken)
        open_list = [(0, start_state, [])]
        visited_states = set()

        # Cost from start to each state
        g_score = defaultdict(lambda: float('inf'))
        g_score[start_state] = 0

        # Estimated total cost (g + h)
        f_score = defaultdict(lambda: float('inf'))
        f_score[start_state] = self.manhattan_distance(start_state[0], start_state[1], goal_position[0], goal_position[1])

        while open_list:
            # Get the state with the lowest f_score
            _, current_state, actions = heappop(open_list)
            x, y, _ = current_state

            # Goal check
            if (x, y) == goal_position:
                return [action for action in actions]

            # Skip already visited states
            if current_state in visited_states:
                continue
            visited_states.add(current_state)

            # Explore neighbors
            for next_state, action, cost in self.get_neighbors(current_state, kb_world):
                if next_state in visited_states:
                    continue

                tentative_g_score = g_score[current_state] + cost

                # Found a better path to this state
                if tentative_g_score < g_score[next_state]:
                    g_score[next_state] = tentative_g_score
                    h_score = self.manhattan_distance(next_state[0], next_state[1], goal_position[0], goal_position[1])
                    f_score[next_state] = tentative_g_score + h_score
                    # Push new path into open list
                    heappush(open_list, (f_score[next_state], next_state, actions + [action]))

        # Return empty if no path found
        return []
