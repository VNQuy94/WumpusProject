import pygame
import Agent
import GameCoords

class Visualize:
    def __init__(self, world_size):
        # Set display dimensions
        self.width, self.height = 1000, 600
        self.map_width = 600        # Width of the map section
        self.info_width = 400       # Width of the information panel
        self.game_display = pygame.display.set_mode((self.width, self.height))  # Main game window

        self.world_size = world_size
        self.cell_size = self.map_width // world_size  # Size of each cell in the map grid

        # Load and scale agent images for all directions
        self.agent_images_up = pygame.transform.scale(pygame.image.load("assets/agent_up.png"), (self.cell_size, self.cell_size))
        self.agent_images_down = pygame.transform.scale(pygame.image.load("assets/agent_down.png"), (self.cell_size, self.cell_size))
        self.agent_images_left = pygame.transform.scale(pygame.image.load("assets/agent_left.png"), (self.cell_size, self.cell_size))
        self.agent_images_right = pygame.transform.scale(pygame.image.load("assets/agent_right.png"), (self.cell_size, self.cell_size))

        # Load and scale images for game objects
        self.wumpus_image = pygame.transform.scale(pygame.image.load("assets/wumpus.png"), (self.cell_size, self.cell_size))
        self.gold_image = pygame.transform.scale(pygame.image.load("assets/gold.png"), (self.cell_size, self.cell_size))
        self.pit_image = pygame.transform.scale(pygame.image.load("assets/pit.png"), (self.cell_size, self.cell_size))

        # Colors
        self.DARK_GRAY = (50, 50, 50)
        self.LIGHT_GRAY = (169, 169, 169)

        # Fonts for different UI sections
        self.PERCEPT_FONT = pygame.font.SysFont('sans', self.cell_size // 4, bold=True)  # Small text inside cells
        self.INFO_FONT = pygame.font.SysFont('sans', 22)  # Information panel font
        self.TITLE_FONT = pygame.font.SysFont('sans', 28, bold=True)  # Panel title font

    def draw_map(self, world, kb_world):
        """
        Draw the game map grid including visited cells, objects (Wumpus, Gold, Pit),
        percepts (Breeze, Stench), and the agent in its current position and direction.
        """
        # Convert agent's position to array coordinates
        x_agent, y_agent = GameCoords.game_to_array_coords(world.agent_position[0], world.agent_position[1], self.world_size)
        agent_direction = world.agent_direction

        for row in range(self.world_size):
            for col in range(self.world_size):
                # Draw cell background
                rect = pygame.Rect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                x_game, y_game = GameCoords.array_to_game_coords(row, col, self.world_size)

                # Color cell based on visit status
                if kb_world[x_game][y_game].is_visited:
                    pygame.draw.rect(self.game_display, self.LIGHT_GRAY, rect)  # Visited
                else:
                    pygame.draw.rect(self.game_display, self.DARK_GRAY, rect)   # Not visited

                # Draw objects in the cell
                if 'W' in world.world[row][col]:
                    self.game_display.blit(self.wumpus_image, rect)
                if 'G' in world.world[row][col]:
                    self.game_display.blit(self.gold_image, rect)
                if 'P' in world.world[row][col]:
                    self.game_display.blit(self.pit_image, rect)

                # Draw percept letters: Breeze (B) and Stench (S)
                if 'B' in world.world[row][col]:
                    text_surface = self.PERCEPT_FONT.render('B', True, (255, 0, 0))  # Red for Breeze
                    text_rect = text_surface.get_rect()
                    text_rect.topright = ((col + 1) * self.cell_size - 5, row * self.cell_size + 5)
                    self.game_display.blit(text_surface, text_rect)

                if 'S' in world.world[row][col]:
                    text_surface = self.PERCEPT_FONT.render('S', True, (0, 255, 0))  # Green for Stench
                    text_rect = text_surface.get_rect()
                    text_rect.topright = ((col + 1) * self.cell_size - 5, row * self.cell_size + 20)
                    self.game_display.blit(text_surface, text_rect)
                
                # Draw grid border
                pygame.draw.rect(self.game_display, (0, 0, 0), rect, 1)

                # Draw the agent if this is its position
                if row == x_agent and col == y_agent:
                    if agent_direction == 'East':
                        self.game_display.blit(self.agent_images_right, rect)
                    if agent_direction == 'South':
                        self.game_display.blit(self.agent_images_down, rect)
                    if agent_direction == 'North':
                        self.game_display.blit(self.agent_images_up, rect)
                    if agent_direction == 'West':
                        self.game_display.blit(self.agent_images_left, rect)
    
    def draw_info(self, world, action, percepts):
        """
        Draws the information panel on the right side of the screen,
        showing agent's position, direction, last action, and current percepts.
        """
        info_x, info_y = self.map_width, 0
        info_width, info_height = self.info_width, self.height

        # Draw background for info panel
        pygame.draw.rect(self.game_display, (230, 230, 230), (info_x, info_y, info_width, info_height))
        self.game_display.blit(self.TITLE_FONT.render("Agent Info", True, (0, 0, 0)), (info_x + 20, info_y + 20))
        self.game_display.blit(self.INFO_FONT.render(f"Position: {world.agent_position}", True, (0,0,0)), (info_x + 20, info_y + 60))
        self.game_display.blit(self.INFO_FONT.render(f"Direction: {world.agent_direction}", True, (0, 0, 0)), (info_x + 20, info_y + 90))
        self.game_display.blit(self.INFO_FONT.render(f"Last action: {action}", True, (0, 0, 0)), (info_x + 20, info_y + 120))
        
        # Build percept text string
        text_percept = ""
        if percepts[0]:
            text_percept += "Stench"
        if percepts[1]:
            text_percept += ", Breeze"
        if percepts[2]:
            text_percept += ", Glitter"
        if percepts[3]:
            text_percept += ", Scream"
        
        # Display percepts
        self.game_display.blit(self.INFO_FONT.render(f"Percepts: {text_percept}", True, (0, 0, 0)), (info_x + 20, info_y + 150))

    def draw_inform(self, inform):
        """
        Draws a semi-transparent overlay on the screen with a central message.
        Used to display notifications like game over or win/lose messages.
        """
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.set_alpha(150)  # Transparency level
        overlay.fill((0, 0, 0))  # Black overlay

        # Draw overlay over the entire screen
        self.game_display.blit(overlay, (0, 0))

        # Draw centered text
        font_inform = pygame.font.SysFont('sans', 30, bold=True)
        text_surface = font_inform.render(inform, True, (239, 239, 200))  # Light yellow text
        
        # Position text in the center of the screen
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.game_display.blit(text_surface, text_rect)