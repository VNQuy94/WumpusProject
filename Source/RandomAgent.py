import Agent
import World
import Action
import time
import tracemalloc
from queue import PriorityQueue
from collections import deque

# BFS algorithm (from the old PJ1)
def bfs_algorithm(gameboard: World):
    #Start memory tracing
    tracemalloc.start()

    # Get start time currently
    start = time.time()

    # Number of expanded nodes
    expanded_nodes = 0
    # Initialize the queue for BFS
    queue = deque()
    # Keep track of visited states to avoid cycles
    visited = {}

    # Add the start state to the queue and mark it as visited
    queue.append(gameboard)
    visited[gameboard] = (gameboard, None)

    # While there are states to explore in the queue
    while queue:
        # Get the current state from the queue and increase the expanded nodes count
        current_gameboard = queue.popleft()
        expanded_nodes += 1

        # Get the successors of the current state
        for new_movess in current_gameboard.check_for_moves():
            next_gameboard = World(gameboard, N=8, num_wumpus=2, p_pit=0.2)
            # If the next state has not been visited yet
            if next_gameboard not in visited:
                # Check if the next state has solved the game
                if next_gameboard.has_solved():
                    end = time.time()
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()

                    path = helpFunctions.trace_back_solution(visited, gameboard, current_gameboard)
                    path.append(next_gameboard)

                    return path, end-start, peak, expanded_nodes, len(path), None
                
                # If not solved, add the next state to the queue and mark it as visited
                queue.append(next_gameboard)
                visited[next_gameboard] = (next_gameboard, current_gameboard)

    # If no solution is found, return None and print statistics
    end = time.time()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return None, end-start, peak, expanded_nodes, None, None
