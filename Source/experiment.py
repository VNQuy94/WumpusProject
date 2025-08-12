# chạy 10 lần
# random 1 map
# cho 2 agent thực hiện
# test số lần thành công và số lần fail
# tăng N (sau 10 lần đổi kích cỡ map?), tăng wumpus (bắt đầu 1 con đến N con), tăng mật độ (từ 0 đến 0.5, mỗi lần + 0.1)
# viết dữ liệu ra file CSV
# xài Matplotlib để vẽ biểu đồ (ncl vẽ biểu đồ)

import Agent
import World
import GameCoords
from World import GOLD

if __name__ == '__main__':
    action_counts = []
    random_action_counts = []
    success_count = 0
    random_success_count = 0
    fail_count = 0
    random_fail_count = 0
    scores = []
    random_scores = []
    results = []
    random_results = []
    size = 10
    num_wumpus = 3
    p_pit = 0.5
    
    for _ in range(0, 50):
        print(f"Lần chơi thứ {_ + 1}")
        score = 0
        random_score = 0
        action_count = 0
        random_action_count = 0
        wumpus_world = World.World(size, num_wumpus, p_pit)
        wumpus_world_second = wumpus_world
        agent = Agent.Agent(size)
        agent.create_kb_world()
        random_agent = Agent.Agent(size)
        percepts = wumpus_world.get_percepts(agent.current_pos[0], agent.current_pos[1]) + [False]
        print("Map test: ")
        print(wumpus_world)
        print("Lần chơi của Agent thường")
        running = True
        running_random = True
        while running:
            action = agent.make_decision(percepts)
            print(f"Action: {action}")
            
            if action == "Climb":
                action_count += 1
                if agent.has_gold:
                    score += 1000
                    success_count += 1
                    results.append(True)
                else:
                    fail_count += 1
                    results.append(False)
                scores.append(score)
                action_counts.append(action_count)
                running = False
                action = None
            
            if action:
                action_count += 1
                if action in ["Move Forward", "Turn Left", "Turn Right"]:
                    score -= 1
                if action == "Shoot":
                    score -= 10
                if action == "Grab":
                    score += 10
                agent.agent_update_state(action)
                percepts = wumpus_world.perform_agent_action(action)
 
                if percepts is None:  # Agent died
                    print("Agent đã chết!")
                    score -= 1000
                    fail_count += 1
                    scores.append(score)
                    action_counts.append(action_count)
                    results.append(False)
                    running = False
                
        print("Lần chơi của Agent random")
        
        while running_random:
            # if random_action_count == 100:
            #     random_fail_count += 1
            #     random_results.append(False)
            #     random_scores.append(random_score)
            #     random_action_counts.append(random_action_count)
            #     break
            
            action = random_agent.random_action()
            print(f"Action: {action}")
            
            if action == "Climb":
                random_action_count += 1
                if (random_agent.current_pos[0], random_agent.current_pos[1]) == (0, 0) and random_agent.has_gold is True: # nếu climb là nước hợp lệ
                        print("Agent đã thoát thành công với vàng!")
                        random_score += 1000
                        random_success_count += 1
                        random_results.append(True)
                        random_scores.append(random_score)
                        random_action_counts.append(random_action_count)
                        running_random = False
                        action = None
                        
                elif (random_agent.current_pos[0], random_agent.current_pos[1]) == (0, 0) and random_agent.has_gold is False:
                        print("Agent đã thoát thành công nhưng không có vàng!")
                        random_fail_count +=1
                        random_results.append(False)
                        random_scores.append(random_score)
                        random_action_counts.append(random_action_count)
                        running_random = False
                        action = None
                        
            
            if action:
                random_action_count += 1
                
                if action == ["Move Forward", "Turn Left", "Turn Right"]:
                    random_score -= 1
                    
                if action == "Shoot":
                    random_score -= 10
                    
                if action == "Grab" and random_agent.has_gold is False:
                    x, y = wumpus_world_second.agent_position
                    row, col = GameCoords.game_to_array_coords(x, y, wumpus_world_second.size)
                    if GOLD in wumpus_world_second.world[row][col]:
                        random_score += 10
                        print(f"Agent đã nhặt vàng tại ({x}, {y})")
                        
                if action in ["Move Forward", "Turn Left", "Turn Right", "Shoot", "Grab", "Shoot"]:
                    random_agent.agent_update_state(action)
                    res = wumpus_world_second.perform_agent_random(action, random_agent)
    
                if res is False:  # Agent died
                    random_score -= 1000
                    random_fail_count += 1
                    random_results.append(False)
                    random_scores.append(random_score)
                    random_action_counts.append(random_action_count)
                    running_random = False
    
    print(f"Action count list: {action_counts}")
    print(f"Random action count list: {random_action_counts}")
    print(f"Success count: {success_count}")
    print(f"Random success count: {random_success_count}")
    print(f"Fail count: {fail_count}")
    print(f"Random fail count: {random_fail_count}")
    print(f"Scores: {scores}")
    print(f"Random Scores: {random_scores}")
    print(f"Results: {results}")
    print(f"Random results: {random_results}")
    print(f"Average score: {sum(scores) / len(scores)}")
    print(f"Random average score: {sum(random_scores) / len(random_scores)}")