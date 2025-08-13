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
import RandomAgent
from World import GOLD
import copy
import csv

SCORE_WIN = 1000
SCORE_LOSE = -1000
COST_MOVE = -1
COST_SHOOT = -10

def run_single_game(agent, world):
    score = 0
    action_count = 0
    
    percepts = world.get_percepts(agent.current_pos[0], agent.current_pos[1]) + [False]

    while True:
        action_count += 1
        
        action = agent.make_decision(percepts)
        
        if action == "Climb":
            if agent.has_gold:
                score += SCORE_WIN
                return {'success': True, 'score': score, 'actions': action_count}
            else:
                score += SCORE_LOSE # Có thể coi việc thoát ra mà không có vàng là một thất bại
                return {'success': False, 'score': score, 'actions': action_count}

        if action in ["Move Forward", "Turn Left", "Turn Right"]:
            score += COST_MOVE
        elif action == "Shoot":
            score += COST_SHOOT
            agent.set_arrow(False)
        
        new_percepts = world.perform_agent_action(action)
        
        agent.agent_update_state(action)

        if new_percepts is None:
            score += SCORE_LOSE
            return {'success': False, 'score': score, 'actions': action_count}
        
        percepts = new_percepts

def run_experiment(sizes, wumpus_counts, pit_densities, num_trials=10):
    res_logic = []
    res_random = []
    
    # Vòng lặp qua các tham số thử nghiệm
    for size in sizes:
        for num_wumpus in wumpus_counts:
            for p_pit in pit_densities:
                print(f"\n--- Bắt đầu thử nghiệm: Size={size}, Wumpus={num_wumpus}, Pit Density={p_pit} ---")
                
                for i in range(num_trials):
                    print(f"  Trial {i + 1}/{num_trials}")
                    
                    # Tạo một thế giới gốc cho mỗi trial
                    original_world = World.World(size, num_wumpus, p_pit)

                    logic_agent_world = copy.deepcopy(original_world) # Tạo bản sao sâu để đảm bảo công bằng
                    logic_agent = Agent.Agent(size)
                    logic_agent.create_kb_world()
                    logic_result = run_single_game(logic_agent, logic_agent_world)
                    
                    logic_result.update({
                        'agent_type': 'Logic', 'size': size, 'wumpus_count': num_wumpus, 'pit_density': p_pit
                    })
                    res_logic.append(logic_result)

                    random_agent_world = copy.deepcopy(original_world) # Tạo bản sao sâu khác
                    random_agent = RandomAgent.RandomAgent(size)
                    random_result = run_single_game(random_agent, random_agent_world)
                    
                    random_result.update({
                        'agent_type': 'Random', 'size': size, 'wumpus_count': num_wumpus, 'pit_density': p_pit
                    })
                    res_random.append(random_result)

    return res_logic, res_random

if __name__ == '__main__':
    # --- CẤU HÌNH THỬ NGHIỆM ---
    # Thay đổi các danh sách này để chạy các thử nghiệm khác nhau
    param_sizes = [15]  # Thử với bản đồ 10x10
    param_wumpus = [1, 2, 3] # Số lượng wumpus từ 1 đến 4
    param_pits = [0.1, 0.2, 0.3] # Mật độ hố
    num_trials_per_setting = 20 # Chạy 20 lần cho mỗi cấu hình để có kết quả ổn định

    res_logic, res_random = run_experiment(param_sizes, param_wumpus, param_pits, num_trials_per_setting)
    fieldnames = res_logic[0].keys()
    with open('logic_result_3.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(res_logic)
    with open('random_result_3.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(res_random)