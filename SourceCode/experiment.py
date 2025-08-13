# chạy 10 lần
# random 1 map
# cho 2 agent thực hiện
# test số lần thành công và số lần fail
# tăng N (sau 10 lần đổi kích cỡ map?), tăng wumpus (bắt đầu 1 con đến N con), tăng mật độ (từ 0 đến 0.5, mỗi lần + 0.1)
# viết dữ liệu ra file CSV
# xài Matplotlib để vẽ biểu đồ (ncl vẽ biểu đồ)

import matplotlib as plt 
import pandas as pd
import seaborn as sns
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

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def load_and_combine_results(logic_file, random_file):
    """
    Đọc dữ liệu từ hai file CSV và kết hợp chúng thành một DataFrame duy nhất.
    """
    try:
        # Đọc file của Logic Agent
        df_logic = pd.read_csv(logic_file)
        print(f"Đã đọc thành công file '{logic_file}' với {len(df_logic)} dòng.")
        
        # Đọc file của Random Agent
        df_random = pd.read_csv(random_file)
        print(f"Đã đọc thành công file '{random_file}' với {len(df_random)} dòng.")

    except FileNotFoundError as e:
        print(f"Lỗi: Không tìm thấy file. Hãy chắc chắn rằng file '{e.filename}' tồn tại trong cùng thư mục.")
        return None

    # Kết hợp hai DataFrame lại với nhau
    combined_df = pd.concat([df_logic, df_random], ignore_index=True)
    print(f"Đã kết hợp thành công. Dữ liệu tổng cộng có {len(combined_df)} dòng.")
    
    return combined_df


def plot_comparison_charts(df):
    """
    Vẽ biểu đồ phân tích kết quả từ một DataFrame đã được kết hợp.
    LƯU Ý: Hàm này gần như giống hệt hàm plot_results trước đây,
    nhưng nó trực tiếp nhận vào DataFrame đã được xử lý.
    """
    if df is None or df.empty:
        print("DataFrame trống, không có gì để vẽ.")
        return

    # ---- Biểu đồ 1: Tổng quan Tỉ lệ thành công ----
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Tính tỉ lệ thành công trung bình cho mỗi loại agent
    success_rate = df.groupby('agent_type')['success'].mean().sort_values(ascending=False)
    
    success_rate.plot(kind='bar', ax=ax, color=['#4a78a7', '#f28e2b'])
    
    ax.set_title('Average Success Rate: Logic Agent vs. Random Agent', fontsize=16, fontweight='bold')
    ax.set_xlabel('Agent Type', fontsize=12)
    ax.set_ylabel('Success rate', fontsize=12)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    
    for i, v in enumerate(success_rate):
        ax.text(i, v + 0.01, f"{v:.1%}", ha='center', fontweight='bold')
        
    plt.tight_layout()
    plt.show()

    # ---- Biểu đồ 2: Heatmap so sánh tỉ lệ thành công ----
    fig, axes = plt.subplots(1, 2, figsize=(18, 8), sharey=True, gridspec_kw={'width_ratios': [1, 1]})
    fig.suptitle('Heatmap Success Rate by Map Configuration', fontsize=20, fontweight='bold')
    
    agent_types = ['Logic', 'Random']
    for i, agent_type in enumerate(agent_types):
        ax = axes[i]
        
        agent_df = df[df['agent_type'] == agent_type]
        
        # Tạo pivot table, sử dụng fill_value=0 nếu có cấu hình nào đó không có dữ liệu
        pivot_data = agent_df.groupby(['wumpus_count', 'pit_density'])['success'].mean().unstack(fill_value=0)
        
        sns.heatmap(
            pivot_data, 
            ax=ax,
            annot=True,
            fmt=".1%",
            linewidths=.5,
            cmap='viridis',
            vmin=0, vmax=1 # Giữ thang màu (0% đến 100%) để so sánh công bằng
        )
        
        ax.set_title(f'{agent_type} Agent', fontsize=14)
        ax.set_xlabel('Pit density')
        ax.set_ylabel('Number of wumpus' if i == 0 else '')
        
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

def plot_score_comparison(df):
    """
    Tạo 2 biểu đồ so sánh ĐIỂM SỐ: Biểu đồ hộp và Biểu đồ cột trung bình.
    """
    if df is None or df.empty:
        return

    # Tạo một figure chứa 2 biểu đồ con (1 hàng, 2 cột)
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Compare Scores', fontsize=18, fontweight='bold')

    # --- Biểu đồ 1: Phân bổ Điểm số (Box Plot) ---
    sns.boxplot(ax=axes[0], x='agent_type', y='score', data=df, palette="colorblind")
    axes[0].set_title('Score Distribution', fontsize=14)
    axes[0].set_xlabel('Agent Type', fontsize=12)
    axes[0].set_ylabel('Score', fontsize=12)
    
    # --- Biểu đồ 2: Điểm số Trung bình (Bar Plot) ---
    # Seaborn tự động tính giá trị trung bình cho chiều cao của cột
    sns.barplot(ax=axes[1], x='agent_type', y='score', data=df, palette="colorblind", ci=None)
    axes[1].set_title('Average Score', fontsize=14)
    axes[1].set_xlabel('Agent Type', fontsize=12)
    axes[1].set_ylabel('Average Score', fontsize=12)

    # Thêm nhãn giá trị trung bình lên trên mỗi cột để rõ ràng hơn
    # Tính toán giá trị trung bình
    avg_scores = df.groupby('agent_type')['score'].mean()
    for i, agent_type in enumerate(avg_scores.index):
        score_val = avg_scores[agent_type]
        axes[1].text(i, score_val, f'{score_val:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.show()


def plot_action_comparison(df):
    """
    Tạo 2 biểu đồ so sánh SỐ HÀNH ĐỘNG: Biểu đồ hộp và Biểu đồ cột trung bình.
    """
    if df is None or df.empty:
        return

    # Tạo một figure chứa 2 biểu đồ con (1 hàng, 2 cột)
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Performance Comparison in Actions', fontsize=18, fontweight='bold')

    # --- Biểu đồ 1: Phân bổ Số hành động (Box Plot) ---
    sns.boxplot(ax=axes[0], x='agent_type', y='actions', data=df, palette="viridis")
    axes[0].set_title('Allocation of Action Number', fontsize=14)
    axes[0].set_xlabel('Agent Type', fontsize=12)
    axes[0].set_ylabel('Number of actions', fontsize=12)

    # --- Biểu đồ 2: Số hành động Trung bình (Bar Plot) ---
    sns.barplot(ax=axes[1], x='agent_type', y='actions', data=df, palette="viridis", ci=None)
    axes[1].set_title('Average Actions', fontsize=14)
    axes[1].set_xlabel('Agent Type', fontsize=12)
    axes[1].set_ylabel('Average Actions', fontsize=12)

    # Thêm nhãn giá trị trung bình lên trên mỗi cột
    avg_actions = df.groupby('agent_type')['actions'].mean()
    for i, agent_type in enumerate(avg_actions.index):
        action_val = avg_actions[agent_type]
        axes[1].text(i, action_val, f'{action_val:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.show()


# --- Điểm bắt đầu của script phân tích ---
if __name__ == "__main__":
    # Đặt tên file kết quả của bạn ở đây
    LOGIC_AGENT_FILE = "logic_result.csv"
    RANDOM_AGENT_FILE = "random_result.csv" # Giả sử tên file của random agent là đây

    # 1. Tải và kết hợp dữ liệu
    combined_data = load_and_combine_results(LOGIC_AGENT_FILE, RANDOM_AGENT_FILE)

    # 2. Vẽ biểu đồ nếu dữ liệu được tải thành công
    if combined_data is not None:
        plot_score_comparison(combined_data)
        plot_action_comparison(combined_data)