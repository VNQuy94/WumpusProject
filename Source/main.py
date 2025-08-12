import pygame
import Agent
import World
import Visualize
import sys

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

        action = agent.make_decision(percepts)
        print(f"Action: {action}")
        
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
        pygame.time.delay(1500)

        count_action += 1

    # Kết thúc game
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(10)

if __name__ == "__main__":
    main()