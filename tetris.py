import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
WIDTH = BLOCK_SIZE * GRID_WIDTH + 150
HEIGHT = BLOCK_SIZE * GRID_HEIGHT
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (50, 50, 50)  # Grey background
COLORS = [
    (0, 255, 255),    # Cyan (I)
    (255, 165, 0),    # Orange (L)
    (0, 0, 255),      # Blue (J)
    (255, 255, 0),    # Yellow (O)
    (0, 255, 0),      # Green (S)
    (255, 0, 0),      # Red (Z)
    (128, 0, 128)     # Purple (T)
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # J
    [[1, 1, 1], [0, 0, 1]],  # L
    [[1, 1], [1, 1]],        # O
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]
        self.rotation = 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.paused = False  # Pause state
        self.fall_speed = 500
        self.last_fall = pygame.time.get_ticks()

    def new_piece(self):
        shape = random.choice(SHAPES)
        return Tetromino(GRID_WIDTH // 2 - len(shape[0]) // 2, 0, shape)

    def valid_move(self, piece, x, y, rotation):
        current_shape = piece.shape
        if rotation != 0:
            current_shape = self.rotate_piece(piece, rotation)
        
        for i, row in enumerate(current_shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = x + j
                    new_y = y + i
                    if (new_x < 0 or new_x >= GRID_WIDTH or
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True

    def rotate_piece(self, piece, rotation):
        return [list(row) for row in zip(*piece.shape[::-1])]

    def lock_piece(self, piece):
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    if piece.y + i < 0:
                        self.game_over = True
                        return
                    self.grid[piece.y + i][piece.x + j] = piece.color
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

    def clear_lines(self):
        lines_cleared = 0
        for i, row in enumerate(self.grid):
            if all(cell != 0 for cell in row):
                self.grid.pop(i)
                self.grid.insert(0, [0] * GRID_WIDTH)
                lines_cleared += 1
        if lines_cleared:
            self.score += lines_cleared * 100

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = GREY if self.grid[y][x] == 0 else self.grid[y][x]
                rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, 
                                 BLOCK_SIZE -1, BLOCK_SIZE -1)
                pygame.draw.rect(self.screen, color, rect)

    def draw_piece(self, piece):
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    x = (piece.x + j) * BLOCK_SIZE
                    y = (piece.y + i) * BLOCK_SIZE
                    rect = pygame.Rect(x, y, BLOCK_SIZE -1, BLOCK_SIZE -1)
                    pygame.draw.rect(self.screen, piece.color, rect)

    def draw_next_piece(self):
        font = pygame.font.Font(None, 36)
        text = font.render("Next:", True, WHITE)
        self.screen.blit(text, (GRID_WIDTH * BLOCK_SIZE + 10, 50))
        
        for i, row in enumerate(self.next_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    x = GRID_WIDTH * BLOCK_SIZE + 50 + j * BLOCK_SIZE
                    y = 100 + i * BLOCK_SIZE
                    rect = pygame.Rect(x, y, BLOCK_SIZE -1, BLOCK_SIZE -1)
                    pygame.draw.rect(self.screen, self.next_piece.color, rect)

    def draw_score(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (GRID_WIDTH * BLOCK_SIZE + 10, 200))

    def draw_pause(self):
        font = pygame.font.Font(None, 48)
        text = font.render("Paused", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(text, text_rect)

    def draw_game_over(self):
        font = pygame.font.Font(None, 48)
        text = font.render("Game Over!", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(text, text_rect)

    def run(self):
        while not self.game_over:
            self.screen.fill(BLACK)
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Pause on 'P' key
                        self.paused = not self.paused
                    if not self.paused:
                        if event.key == pygame.K_LEFT:
                            if self.valid_move(self.current_piece, self.current_piece.x -1, self.current_piece.y, 0):
                                self.current_piece.x -= 1
                        if event.key == pygame.K_RIGHT:
                            if self.valid_move(self.current_piece, self.current_piece.x +1, self.current_piece.y, 0):
                                self.current_piece.x += 1
                        if event.key == pygame.K_DOWN:
                            if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y +1, 0):
                                self.current_piece.y += 1
                        if event.key == pygame.K_UP:
                            if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y, 1):
                                self.current_piece.shape = self.rotate_piece(self.current_piece, 1)
                        if event.key == pygame.K_SPACE:
                            while self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y +1, 0):
                                self.current_piece.y += 1
                            self.lock_piece(self.current_piece)

            if not self.paused:
                # Automatic falling
                if current_time - self.last_fall > self.fall_speed:
                    if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y +1, 0):
                        self.current_piece.y += 1
                        self.last_fall = current_time
                    else:
                        self.lock_piece(self.current_piece)
                        self.last_fall = current_time

            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_next_piece()
            self.draw_score()
            
            if self.paused:
                self.draw_pause()
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        # Wait for quit after game over
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()