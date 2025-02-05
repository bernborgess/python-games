import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# ----- Configuration -----
TILE_SIZE = 24
FPS = 10  # Lower FPS for grid-based feel (you can increase for smoother movement)

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
PINK = (255, 100, 150)

# Screen size will depend on the maze size.
# Define a simple maze using a list of strings.
# Legend:
#   '#' - wall
#   '.' - pellet
#   ' ' - empty space
#   'P' - Pac-Man starting position
#   'G' - Ghost starting position
maze_layout = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #................#     ",
    "     #.##### ## #####.#     ",
    "######.##### ## #####.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "############################",
]

# Compute maze dimensions
MAZE_ROWS = len(maze_layout)
MAZE_COLS = len(maze_layout[0])
SCREEN_WIDTH = MAZE_COLS * TILE_SIZE
SCREEN_HEIGHT = MAZE_ROWS * TILE_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Pac-Man")
clock = pygame.time.Clock()


# ----- Helper Functions -----
def draw_text(surface, text, size, color, center):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, rect)


# ----- Game Classes -----
class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.wall_rects = []  # List of pygame.Rect for walls
        self.pellets = []  # List of pellets as rects (or centers)
        self.pacman_start = None
        self.ghost_start = None
        self.parse_layout()

    def parse_layout(self):
        for row_idx, row in enumerate(self.layout):
            for col_idx, char in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                if char == "#":
                    self.wall_rects.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif char == ".":
                    # Place a pellet in the center of the tile.
                    pellet_rect = pygame.Rect(0, 0, 6, 6)
                    pellet_rect.center = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                    self.pellets.append(pellet_rect)
                elif char == "P":
                    self.pacman_start = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                elif char == "G":
                    self.ghost_start = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                # If the tile is empty " " do nothing.

    def draw(self, surface):
        # Draw walls
        for wall in self.wall_rects:
            pygame.draw.rect(surface, BLUE, wall)
        # Draw pellets
        for pellet in self.pellets:
            pygame.draw.circle(surface, WHITE, pellet.center, pellet.width // 2)


class Pacman:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = TILE_SIZE // 2 - 2
        self.speed = TILE_SIZE  # Moves one tile per update
        # Direction vector: (dx, dy). Initially stationary.
        self.direction = pygame.Vector2(0, 0)

    def update(self, maze):
        # Save current position
        old_pos = self.pos.copy()
        # Update position based on direction
        self.pos += self.direction * self.speed

        # Create a rect for collision detection
        pac_rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        pac_rect.center = self.pos

        # Check collision with walls: if colliding, revert movement.
        for wall in maze.wall_rects:
            if pac_rect.colliderect(wall):
                self.pos = old_pos
                break

        # Eat any pellet that collides with Pac-Man.
        # We use a copy of the list so we can remove items while iterating.
        for pellet in maze.pellets[:]:
            if pac_rect.colliderect(pellet):
                maze.pellets.remove(pellet)

    def draw(self, surface):
        # Draw Pac-Man as a yellow circle.
        pygame.draw.circle(
            surface, YELLOW, (int(self.pos.x), int(self.pos.y)), self.radius
        )
        # For a simple "mouth", you could draw a black triangle overlay.
        # (Optional enhancement)


class Ghost:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = TILE_SIZE // 2 - 2
        self.speed = TILE_SIZE  # Moves one tile per update
        # Start with a random direction among the four cardinal directions.
        self.direction = random.choice(
            [
                pygame.Vector2(1, 0),
                pygame.Vector2(-1, 0),
                pygame.Vector2(0, 1),
                pygame.Vector2(0, -1),
            ]
        )

    def update(self, maze):
        old_pos = self.pos.copy()
        self.pos += self.direction * self.speed

        ghost_rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        ghost_rect.center = self.pos

        collided = False
        for wall in maze.wall_rects:
            if ghost_rect.colliderect(wall):
                collided = True
                break
        if collided:
            # Revert position and choose a new random valid direction.
            self.pos = old_pos
            self.choose_new_direction(maze)
        else:
            # At intersections, randomly change direction.
            if random.random() < 0.2:
                self.choose_new_direction(maze)

    def choose_new_direction(self, maze):
        # Try all four directions and choose one that is not blocked.
        possible_dirs = [
            pygame.Vector2(1, 0),
            pygame.Vector2(-1, 0),
            pygame.Vector2(0, 1),
            pygame.Vector2(0, -1),
        ]
        valid_dirs = []
        ghost_rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        for d in possible_dirs:
            test_pos = self.pos + d * self.speed
            ghost_rect.center = test_pos
            if not any(ghost_rect.colliderect(wall) for wall in maze.wall_rects):
                valid_dirs.append(d)
        if valid_dirs:
            self.direction = random.choice(valid_dirs)

    def draw(self, surface):
        pygame.draw.circle(
            surface, PINK, (int(self.pos.x), int(self.pos.y)), self.radius
        )


# ----- Game Over / Win Screens -----
def show_end_screen(message):
    """Display a screen with the given message and wait for player to press R to restart or Q to quit."""
    while True:
        screen.fill(BLACK)
        draw_text(
            screen, message, 48, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
        )
        draw_text(
            screen,
            "Press R to Restart, Q to Quit",
            32,
            WHITE,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30),
        )
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return  # restart
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(15)


# ----- Main Game Function -----
def run_game():
    # Build the maze and identify starting positions.
    maze = Maze(maze_layout)
    # If the maze layout contains explicit starting positions, use them.
    # Otherwise, use default positions.
    pacman_start = (
        maze.pacman_start
        if maze.pacman_start
        else (TILE_SIZE + TILE_SIZE // 2, TILE_SIZE + TILE_SIZE // 2)
    )
    ghost_start = (
        maze.ghost_start
        if maze.ghost_start
        else (SCREEN_WIDTH - TILE_SIZE, SCREEN_HEIGHT - TILE_SIZE)
    )

    pacman = Pacman(pacman_start)
    ghost = Ghost(ghost_start)

    running = True
    while running:
        clock.tick(FPS)

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Set Pac-Man's direction based on arrow key input.
                if event.key == pygame.K_LEFT:
                    pacman.direction = pygame.Vector2(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    pacman.direction = pygame.Vector2(1, 0)
                elif event.key == pygame.K_UP:
                    pacman.direction = pygame.Vector2(0, -1)
                elif event.key == pygame.K_DOWN:
                    pacman.direction = pygame.Vector2(0, 1)

        # --- Update Game Objects ---
        pacman.update(maze)
        ghost.update(maze)

        # Check for collisions between Pac-Man and the ghost.
        pac_rect = pygame.Rect(0, 0, pacman.radius * 2, pacman.radius * 2)
        pac_rect.center = pacman.pos
        ghost_rect = pygame.Rect(0, 0, ghost.radius * 2, ghost.radius * 2)
        ghost_rect.center = ghost.pos
        if pac_rect.colliderect(ghost_rect):
            show_end_screen("Game Over!")
            return

        # Check win condition: no more pellets.
        if not maze.pellets:
            show_end_screen("You Win!")
            return

        # --- Draw Everything ---
        screen.fill(BLACK)
        maze.draw(screen)
        pacman.draw(screen)
        ghost.draw(screen)
        pygame.display.flip()


# ----- Main Loop -----
def main():
    while True:
        run_game()


if __name__ == "__main__":
    main()
