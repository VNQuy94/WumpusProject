# Run 10 times
# Randomly generate 1 map
# Let 2 agents execute
# Test the number of successes and failures
# Increase N (after 10 runs change map size)
# Increase number of Wumpus (starting from 1 up to N)
# Increase pit density (from 0 to 0.5, increment by 0.1 each time)
# Write data to CSV file
# Use Matplotlib to plot charts

import Agent
import World
import GameCoords
import RandomAgent
from World import GOLD
import copy
import csv
import os
import sys

# Scoring constants
SCORE_WIN = 1000   # Score when agent wins
SCORE_LOSE = -1000 # Score when agent loses
COST_MOVE = -1     # Cost for moving
COST_SHOOT = -10   # Cost for shooting

def run_single_game(agent, world):
    # Run a single game and return result statistics
    score = 0
    action_count = 0
    
    # Get initial percepts for the agent
    percepts = world.get_percepts(agent.current_pos[0], agent.current_pos[1]) + [False]

    while True:
        action_count += 1
        
        # Agent decides an action based on current percepts
        action = agent.make_decision(percepts)
        
        # If agent decides to climb out
        if action == "Climb":
            if agent.has_gold:
                score += SCORE_WIN
                return {'success': True, 'score': score, 'actions': action_count}
            else:
                # Exiting without gold is considered a failure
                score += SCORE_LOSE
                return {'success': False, 'score': score, 'actions': action_count}

        # Update score based on action type
        if action in ["Move Forward", "Turn Left", "Turn Right"]:
            score += COST_MOVE
        elif action == "Shoot":
            score += COST_SHOOT
            agent.set_arrow(False)
        
        # Perform action in the world
        new_percepts = world.perform_agent_action(action)
        
        # Update the agent's internal state
        agent.agent_update_state(action)

        # If percepts is None, the agent died
        if new_percepts is None:
            score += SCORE_LOSE
            return {'success': False, 'score': score, 'actions': action_count}
        
        percepts = new_percepts

def run_experiment(sizes, wumpus_counts, pit_densities, num_trials=10):
    # Run multiple experiments and collect results for logic agent and random agent
    res_logic = []
    res_random = []
    
    # Loop through experimental parameters
    for size in sizes:
        for num_wumpus in wumpus_counts:
            for p_pit in pit_densities:
                print(f"\n--- Starting experiment: Size={size}, Wumpus={num_wumpus}, Pit Density={p_pit} ---")
                
                for i in range(num_trials):
                    print(f"  Trial {i + 1}/{num_trials}")
                    
                    # Create an original world for each trial
                    original_world = World.World(size, num_wumpus, p_pit)

                    # Logic agent test
                    logic_agent_world = copy.deepcopy(original_world) # Deep copy to ensure fairness
                    logic_agent = Agent.Agent(size)
                    logic_agent.create_kb_world()
                    logic_result = run_single_game(logic_agent, logic_agent_world)
                    
                    logic_result.update({
                        'agent_type': 'Logic', 
                        'size': size, 
                        'wumpus_count': num_wumpus, 
                        'pit_density': p_pit
                    })
                    res_logic.append(logic_result)

                    # Random agent test
                    random_agent_world = copy.deepcopy(original_world) # Another deep copy
                    random_agent = RandomAgent.RandomAgent(size)
                    random_result = run_single_game(random_agent, random_agent_world)
                    
                    random_result.update({
                        'agent_type': 'Random', 
                        'size': size, 
                        'wumpus_count': num_wumpus, 
                        'pit_density': p_pit
                    })
                    res_random.append(random_result)

    return res_logic, res_random

if __name__ == '__main__':
    # --- EXPERIMENT CONFIGURATION ---
    # Change these lists to run different experiments
    param_sizes = [5]  # Test with a 15x15 map
    param_wumpus = [1, 2, 3] # Number of wumpus from 1 to 3
    param_pits = [0.1, 0.2, 0.3] # Pit density
    num_trials_per_setting = 20 # Run 20 times per configuration for stable results

    # Run the experiment
    res_logic, res_random = run_experiment(param_sizes, param_wumpus, param_pits, 10)
    # Prepare CSV output directory and file
    output_dir = "./Experiments" 
    os.makedirs(output_dir, exist_ok=True)  
    csv_filename = os.path.join(output_dir, f'logic_result_test.csv')
    csv_filename_2 = os.path.join(output_dir, f'random_result_test.csv')
    
    # Save logic agent results to CSV
    fieldnames = res_logic[0].keys()
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(res_logic)
    
    # Save random agent results to CSV
    with open(csv_filename_2, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(res_random)
