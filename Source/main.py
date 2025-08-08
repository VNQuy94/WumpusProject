import Agent
import World

if __name__ == "__main__":
    
    # Khởi tạo thế giới Wumpus
    world_size = 4  # Kích thước của thế giới
    num_wumpus = 1  # Số lượng Wumpus
    p_pit = 0.1  # Xác suất có Pit

    wumpus_world = World.World(world_size, num_wumpus, p_pit)
    
    # Khởi tạo agent
    agent = Agent.Agent(world_size)
    agent.create_kb_world()
    percepts = wumpus_world.get_percepts(agent.current_pos[0], agent.current_pos[1])

    print("Initial Percepts:", percepts)

    print(wumpus_world)

    count = 0
    # Vòng lặp chính của trò chơi
    while count < 100:
        action = agent.make_decision(percepts)
        print(f"Action: {action}")
        
        if action == "Climb":
            print("Agent đã leo ra khỏi hố!")
            break
        
        if action:
            agent.agent_update_state(action)
            percepts = wumpus_world.perform_agent_action(action)
            print("Updated Percepts:", percepts)

            if percepts is None:
                break
        
        count += 1