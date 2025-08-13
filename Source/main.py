import pygame
import Agent
import World
import Visualize
import sys
import os
import csv

FPS = 60
ACTION_DELAY_MS = 800
WUMPUS_MOVE = 5

def get_valid_input(prompt, min_val, max_val, is_float=False):
    while True:
        try:
            if is_float:
                value = float(input(prompt))
            else:
                value = int(input(prompt))
            
            if min_val <= value <= max_val:
                return value
            print(f"Giá trị phải nằm trong khoảng [{min_val}, {max_val}]")
        except ValueError:
            print("Vui lòng nhập số hợp lệ!")

def main():
    # Nhập các thông số từ người dùng
    print("\n=== WUMPUS WORLD SETTINGS ===")
    world_size = get_valid_input("Nhập kích thước map (4-20): ", 4, 20)
    num_wumpus = get_valid_input(f"Nhập số lượng Wumpus (1-{world_size}): ", 1, world_size)
    p_pit = get_valid_input("Nhập xác suất xuất hiện Pit (0.0-0.5): ", 0.0, 0.5, True)

    print("\n===CHỌN MODE CHƠI===")
    print("1: Wumpus không di chuyển")
    print("2: Wumpus di chuyển")
    mode = get_valid_input("Nhập mode chơi mong muốn (1-2): ", 1, 2)

    # Khởi tạo pygame
    pygame.init()
    clock = pygame.time.Clock()

    # Khởi tạo thế giới Wumpus
    wumpus_world = World.World(world_size, num_wumpus, p_pit)
    agent = Agent.Agent(world_size)
    agent.create_kb_world()
    visualizer = Visualize.Visualize(world_size)

    output_dir = "./TestCases" 
    os.makedirs(output_dir, exist_ok=True)  
    csv_filename = os.path.join(output_dir, f'WumpusWorld_15x15.csv')
    with open(csv_filename, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['World Size', 'Num Wumpus', 'P Pit'])
        csv_writer.writerow([world_size, num_wumpus, p_pit])

        world_map_line = str(wumpus_world).split('\n')
        for i, line in enumerate(world_map_line, 1):
            csv_writer.writerow([f'World Map Line {i}', line.strip()])

        csv_writer.writerow(['Step', 'Position', 'Direction', 'Action', 'Percepts'])
    
        # Lấy percepts ban đầu
        percepts = wumpus_world.get_percepts(agent.current_pos[0], agent.current_pos[1]) + [False]
        last_action = None
        game_result = None

        pygame.display.set_caption('WUMPUS GAME - WAITING')
        visualizer.game_display.fill((255, 255, 255))
        visualizer.draw_map(wumpus_world, agent.kb_world)
        visualizer.draw_info(wumpus_world, last_action, percepts if percepts else [False, False, False, False])
        visualizer.draw_inform("PRESS SPACE TO START")
        pygame.display.flip()

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

        pygame.display.set_caption('WUMPUS GAME - RUNNING')  
        # Vòng lặp chính
        running = True
        count_action = 0

        while running:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if not running: break

            if count_action > 0 and count_action % WUMPUS_MOVE == 0 and mode == 2:
                wumpus_world.move_wumpus()
            
                if wumpus_world.check_wumpus_eat_agent():
                    running = False
                    game_result = "DIED - Agent is eaten by wumpus"

                else:
                    agent.handle_wumpus_move()
                    scream = percepts[3]
                    x, y = wumpus_world.agent_position[0], wumpus_world.agent_position[1]
                    print(x, y)
                    percepts = wumpus_world.get_percepts(x, y) + [scream]

                visualizer.game_display.fill((255, 255, 255))
                visualizer.draw_map(wumpus_world, agent.kb_world)
                visualizer.draw_info(wumpus_world, last_action, percepts if percepts else [False, False, False, False])
                if not running and game_result:
                    visualizer.draw_inform(game_result)
                pygame.display.flip()
                pygame.time.delay(800)

            position = str(agent.current_pos)
            direction = agent.direction

            percept_str = ""
            percepts_list = [("Stench", percepts[0]), ("Breeze", percepts[1]), 
                            ("Glitter", percepts[2]), ("Scream", percepts[3] if len(percepts) > 3 else False)]
            for percept_name, percept_value in percepts_list:
                if percept_value:
                    percept_str += f"{percept_name}, "
            percept_str = percept_str.rstrip(", ") if percept_str else ""  

            action = agent.make_decision(percepts)
            print(f"Action: {action}")
            
            csv_writer.writerow([count_action, position, direction, action, percept_str])

            if action == "Climb":
                running = False
                if agent.has_gold:
                    print("Agent đã thoát thành công với vàng!")
                    game_result = "SUCCESS - Climbed out with gold!"
                else:
                    print("Agent đã thoát nhưng không có vàng!")
                    game_result = "FAIL - Climbed out without gold"
                last_action = 'Climb'
            
            elif running and action:
                last_action = action

                if action == 'Shoot':
                    agent.set_arrow(False)

                agent.agent_update_state(action)
                percepts = wumpus_world.perform_agent_action(action)
                print(percepts)
                
                if percepts is None:  # Agent died
                    print("Agent đã chết!")
                    running = False
                    game_result = "DIED - Eaten by Wumpus or fell into a pit"

            # Vẽ game
            visualizer.game_display.fill((255, 255, 255))
            visualizer.draw_map(wumpus_world, agent.kb_world)
            visualizer.draw_info(wumpus_world, last_action, percepts if percepts else [False, False, False, False])
            if not running and game_result:
                visualizer.draw_inform(game_result)
            pygame.display.flip()
            
            clock.tick(FPS)  # FPS = 60
            pygame.time.delay(ACTION_DELAY_MS)

            count_action += 1

        csv_writer.writerow(['Game Result', game_result if game_result else 'Unknown'])

    # Kết thúc game
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(10)

if __name__ == "__main__":
    main()