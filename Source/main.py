import pygame
import Agent
import World
import Visualize
import sys
import win32gui
import time
pygame.init()
clock = pygame.time.Clock()

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

    # Khởi tạo pygame

    # Khởi tạo thế giới Wumpus
    wumpus_world = World.World(world_size, num_wumpus, p_pit)
    
    # Khởi tạo agent
    agent = Agent.Agent(world_size)
    agent.create_kb_world()

    # Khởi tạo visualizer
    visualizer = Visualize.Visualize(world_size)
    
    # Lấy percepts ban đầu
    percepts = wumpus_world.get_percepts(agent.current_pos[0], agent.current_pos[1]) + [False]
    last_action = None

    pygame.display.set_caption('WUMPUS GAME')
    visualizer.game_display.fill((255, 255, 255))
    visualizer.draw_map(wumpus_world, agent.kb_world)
    visualizer.draw_info(wumpus_world, last_action, percepts if percepts else [False, False, False, False])
    visualizer.draw_inform("PRESS SPACE TO START")
    pygame.display.flip()


    print("\n=== GAME START ===")
    start = False
    while not start:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = True
                    break
            if event.type == pygame.QUIT:
                return
                    
    # Vòng lặp chính
    running = True
    while running:
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        action = agent.make_decision(percepts)
        print(f"Action: {action}")
        
        if action == "Climb":
            if agent.has_gold:
                print("Agent đã thoát thành công với vàng!")
            else:
                print("Agent đã thoát nhưng không có vàng!")
            
            running = False
            action = None
        
        if action:
            last_action = action
            agent.agent_update_state(action)
            percepts = wumpus_world.perform_agent_action(action)
            
            if percepts is None:  # Agent died
                print("Agent đã chết!")
                running = False

        # Vẽ game
        visualizer.game_display.fill((255, 255, 255))
        visualizer.draw_map(wumpus_world, agent.kb_world)
        visualizer.draw_info(wumpus_world, last_action, percepts if percepts else [False, False, False, False])
        if percepts is None:
            visualizer.draw_inform("AGENT IS DIED")
        if action is None:
            visualizer.draw_inform("SUCCESS")
        pygame.display.flip()
        
        clock.tick(60)  # FPS = 60
        pygame.time.delay(800)

    # Kết thúc game
    pygame.time.delay(1000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()