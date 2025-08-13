import pygame
import Agent
import World
import Visualize
import sys
import os
import csv

# Frames per second
FPS = 60
# Delay between actions in milliseconds
ACTION_DELAY_MS = 800
# Number of agent actions before Wumpus moves (in moving mode)
WUMPUS_MOVE = 5

def get_valid_input(prompt, min_val, max_val, is_float=False):
    # Function to get valid numeric input from user
    while True:
        try:
            if is_float:
                value = float(input(prompt))
            else:
                value = int(input(prompt))
            
            if min_val <= value <= max_val:
                return value
            print(f"Value must be between [{min_val}, {max_val}]")
        except ValueError:
            print("Please enter a valid number!")

def main():
    # === Get settings from the user ===
    print("\n=== WUMPUS WORLD SETTINGS ===")
    world_size = get_valid_input("Enter map size (4-20): ", 4, 20)
    num_wumpus = get_valid_input(f"Enter number of Wumpus (1-{world_size}): ", 1, world_size)
    p_pit = get_valid_input("Enter probability of Pit appearance (0.0-0.5): ", 0.0, 0.5, True)

    # Select game mode
    print("\n=== SELECT GAME MODE ===")
    print("1: Wumpus does not move")
    print("2: Wumpus moves")
    mode = get_valid_input("Enter desired game mode (1-2): ", 1, 2)

    # Initialize pygame
    pygame.init()
    clock = pygame.time.Clock()

    # Initialize the Wumpus world
    wumpus_world = World.World(world_size, num_wumpus, p_pit)
    agent = Agent.Agent(world_size)
    agent.create_kb_world()
    visualizer = Visualize.Visualize(world_size)

    # Prepare CSV output directory and file
    output_dir = "./TestCases" 
    os.makedirs(output_dir, exist_ok=True)  
    csv_filename = os.path.join(output_dir, f'WumpusWorld_{world_size}x{world_size}.csv')
    with open(csv_filename, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['World Size', 'Num Wumpus', 'P Pit'])
        csv_writer.writerow([world_size, num_wumpus, p_pit])

        # Save world map layout to CSV
        world_map_line = str(wumpus_world).split('\n')
        for i, line in enumerate(world_map_line, 1):
            csv_writer.writerow([f'World Map Line {i}', line.strip()])

        # Header for step-by-step game actions
        csv_writer.writerow(['Step', 'Position', 'Direction', 'Action', 'Percepts'])
    
        # Get initial percepts
        percepts = wumpus_world.get_percepts(agent.current_pos[0], agent.current_pos[1]) + [False]
        last_action = None
        game_result = None

        # Show start screen
        pygame.display.set_caption('WUMPUS GAME - WAITING')
        visualizer.game_display.fill((255, 255, 255))
        visualizer.draw_map(wumpus_world, agent.kb_world)
        visualizer.draw_info(wumpus_world, last_action, percepts if percepts else [False, False, False, False])
        visualizer.draw_inform("PRESS SPACE TO START")
        pygame.display.flip()

        # Wait until the user presses SPACE to start
        waiting_start = True
        while waiting_start:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting_start = False
                        break
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        # Main game loop
        pygame.display.set_caption('WUMPUS GAME - RUNNING')  
        running = True
        count_action = 0

        while running:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if not running: break

            # Move Wumpus after certain number of agent actions (if in moving mode)
            if count_action > 0 and count_action % WUMPUS_MOVE == 0 and mode == 2:
                wumpus_world.move_wumpus()
            
                if wumpus_world.check_wumpus_eat_agent():
                    running = False
                    game_result = "DIED - Agent is eaten by wumpus"
                else:
                    agent.handle_wumpus_move()
                    scream = percepts[3]
                    x, y = wumpus_world.agent_position[0], wumpus_world.agent_position[1]
                    percepts = wumpus_world.get_percepts(x, y) + [scream]

                # Redraw game after Wumpus move
                visualizer.game_display.fill((255, 255, 255))
                visualizer.draw_map(wumpus_world, agent.kb_world)
                visualizer.draw_info(wumpus_world, last_action, percepts if percepts else [False, False, False, False])
                if not running and game_result:
                    visualizer.draw_inform(game_result)
                pygame.display.flip()
                pygame.time.delay(800)

            # Save current position and direction
            position = str(agent.current_pos)
            direction = agent.direction

            # Create a string from current percepts
            percept_str = ""
            percepts_list = [
                ("Stench", percepts[0]), 
                ("Breeze", percepts[1]), 
                ("Glitter", percepts[2]), 
                ("Scream", percepts[3] if len(percepts) > 3 else False)
            ]
            for percept_name, percept_value in percepts_list:
                if percept_value:
                    percept_str += f"{percept_name}, "
            percept_str = percept_str.rstrip(", ") if percept_str else ""  

            # Let agent decide next action
            action = agent.make_decision(percepts)
            
            # Log action to CSV
            csv_writer.writerow([count_action, position, direction, action, percept_str])

            # Handle "Climb" action (exit game)
            if action == "Climb":
                running = False
                if agent.has_gold:
                    game_result = "SUCCESS - Climbed out with gold!"
                else:
                    game_result = "FAIL - Climbed out without gold"
                last_action = 'Climb'
            
            # Execute other actions
            elif running and action:
                last_action = action

                if action == 'Shoot':
                    agent.set_arrow(False)

                agent.agent_update_state(action)
                percepts = wumpus_world.perform_agent_action(action)
                
                if percepts is None:  # Agent died
                    running = False
                    game_result = "DIED - Eaten by Wumpus or fell into a pit"

            # Draw game interface
            visualizer.game_display.fill((255, 255, 255))
            visualizer.draw_map(wumpus_world, agent.kb_world)
            visualizer.draw_info(wumpus_world, last_action, percepts if percepts else [False, False, False, False])
            if not running and game_result:
                visualizer.draw_inform(game_result)
            pygame.display.flip()
            
            clock.tick(FPS)  # Maintain FPS
            pygame.time.delay(ACTION_DELAY_MS)

            count_action += 1

        # Log final game result to CSV
        csv_writer.writerow(['Game Result', game_result if game_result else 'Unknown'])

    # End game loop (wait for quit)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(10)

if __name__ == "__main__":
    main()