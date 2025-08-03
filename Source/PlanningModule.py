import Agent
import World
import time
import tracemalloc
from queue import PriorityQueue
from collections import deque

# UCS algorithm from the previous PJ1 (can be upgraded to A* later)

def ucs_algorithm(game_board: World):
    #Start memory tracing
    tracemalloc.start()
    
    # Start calculating the time
    start = time.time()
    
    # Number of expanded nodes
    expanded_nodes = 0
    
    # Initialize the priority queue
    frontier = PriorityQueue()

    node_counter = 0 # Used to break ties in priority queue

    # Keep track of visited states to avoid cycles
    visited = {}
    
    # Push the initial state into the priority queue with cost 0
    frontier.put((0, node_counter, game_board))
    visited[game_board] = (0, game_board)
    
    while not frontier.empty():
        # Get the state with the lowest cost
        current_cost, _, current_board = frontier.get()

        if current_board in visited and current_cost > visited[current_board][0]:
            continue
        
        expanded_nodes += 1
        
        # If we reach the goal state i.e. solved, return the path
        if current_board.has_solved():
            # Final statistics for running time and peak memory usage
            end = time.time()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return end-start, peak, expanded_nodes, len(path), current_cost
        
        # Generate successors and their costs
        # Generate successors
        for new_moves in current_board.check_for_moves():
            new_game_board = World(game_board, N=8, num_wumpus=2, p_pit=0.2)
            
            # calculate new cost
            new_cost = current_cost
            for moves in new_moves:
                if moves not in current_board.moves:
                    new_cost += moves.length
                    break

            # Check if this state is new or has better priority than previous visit
            if new_game_board not in visited or new_cost < visited[new_game_board][0]:
                node_counter += 1
                frontier.put((new_cost, node_counter, new_game_board))
                visited[new_game_board] = (new_cost, new_game_board, current_board)
    
    # Statistics: If no solution is found
    
    # Final statistics for running time and peak memory usage
    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    
    tracemalloc.stop()
    # If no solution is found, return None
    return None, end-start, peak, expanded_nodes, None, None
