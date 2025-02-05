import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# ----- Configuration -----
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Define building floors.
# In this simple version there are three floors.
# For each floor we specify a “floor line” (y coordinate) and a list of door rectangles.
# (Door rectangles are used for both descending via an elevator and, on the bottom floor, as the exit.)
DOOR_WIDTH = 50
DOOR_HEIGHT = 80
floors = [
    {  # Floor 0 (top)
        "y": 100,
        "doors": [
            pygame.Rect(50, 100 - DOOR_HEIGHT // 2, DOOR_WIDTH, DOOR_HEIGHT),
            pygame.Rect(700, 100 - DOOR_HEIGHT // 2, DOOR_WIDTH, DOOR_HEIGHT),
        ],
    },
    {  # Floor 1 (middle)
        "y": 300,
        "doors": [pygame.Rect(375, 300 - DOOR_HEIGHT // 2, DOOR_WIDTH, DOOR_HEIGHT)],
    },
    {  # Floor 2 (ground/exit floor)
        "y": 500,
        "doors": [
            pygame.Rect(
                375, 500 - DOOR_HEIGHT // 2, DOOR_WIDTH, DOOR_HEIGHT
            )  # exit door
        ],
    },
]

# Document is placed on floor 1.
document_rect = pygame.Rect(100, floors[1]["y"] - 15, 30, 30)
document_collected = False


# ----- Game Object Classes -----
class Player:
    WIDTH = 30
    HEIGHT = 40
    SPEED = 5

    def __init__(self, x, y, floor_index):
        self.rect = pygame.Rect(x, y, Player.WIDTH, Player.HEIGHT)
        self.floor = floor_index
        self.direction = 1  # 1 = facing right; -1 = facing left

    def update(self, keys):
        # Move left/right
        if keys[pygame.K_LEFT]:
            self.rect.x -= Player.SPEED
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.rect.x += Player.SPEED
            self.direction = 1

        # Keep within screen horizontally.
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def try_descend(self):
        """
        If the player is overlapping any door on the current floor,
        and there is a lower floor, move the player to the lower floor.
        """
        global document_collected
        if self.floor < len(floors) - 1:
            for door in floors[self.floor]["doors"]:
                if self.rect.colliderect(door):
                    # Descend to the next floor.
                    self.floor += 1
                    # Update the vertical position so that the player's feet
                    # are near the floor line (we center vertically relative to floor).
                    self.rect.y = floors[self.floor]["y"] - self.rect.height // 2
                    break

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)
        # Optional: Draw a simple "gun" to indicate facing.
        gun_tip = (self.rect.centerx + self.direction * 10, self.rect.centery)
        pygame.draw.circle(surface, RED, gun_tip, 4)


class Bullet:
    WIDTH = 6
    HEIGHT = 4
    SPEED = 10

    def __init__(self, x, y, direction, floor):
        self.rect = pygame.Rect(x, y, Bullet.WIDTH, Bullet.HEIGHT)
        self.direction = direction
        self.floor = floor

    def update(self):
        self.rect.x += self.direction * Bullet.SPEED

    def draw(self, surface):
        pygame.draw.rect(surface, CYAN, self.rect)


class Enemy:
    WIDTH = 30
    HEIGHT = 40
    SPEED = 2

    def __init__(self, x, y, floor):
        self.rect = pygame.Rect(x, y, Enemy.WIDTH, Enemy.HEIGHT)
        self.floor = floor
        self.direction = random.choice([-1, 1])

    def update(self):
        self.rect.x += self.direction * Enemy.SPEED
        # Reverse direction if hitting screen boundaries.
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)


# ----- Utility Functions -----
def draw_floors(surface):
    # Draw horizontal floor lines and doors.
    for floor in floors:
        y = floor["y"]
        # Draw the floor line.
        pygame.draw.line(surface, WHITE, (0, y), (SCREEN_WIDTH, y), 2)
        # Draw each door.
        for door in floor["doors"]:
            pygame.draw.rect(surface, BLUE, door, 2)


def draw_document(surface):
    if not document_collected:
        pygame.draw.rect(surface, GREEN, document_rect)


def draw_text(surface, text, size, color, center):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, rect)


# ----- Game Over / Win Screens -----
def show_end_screen(message):
    while True:
        screen.fill(BLACK)
        draw_text(
            screen, message, 64, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
        )
        draw_text(
            screen,
            "Press R to Restart or Q to Quit",
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
                    return  # restart the game
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(15)


# ----- Main Game Function -----
def run_game():
    global document_collected
    # Initialize player on the top floor (floor 0) at roughly center.
    player = Player(SCREEN_WIDTH // 2, floors[0]["y"] - Player.HEIGHT // 2, 0)
    bullets = []
    enemies = []
    enemy_spawn_timer = 0
    document_collected = False

    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        # ----- Event Handling -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Shooting a bullet.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Create a bullet from the player’s center.
                    bullet_x = player.rect.centerx
                    bullet_y = player.rect.centery
                    bullets.append(
                        Bullet(bullet_x, bullet_y, player.direction, player.floor)
                    )
                # Try to descend when DOWN is pressed.
                if event.key == pygame.K_DOWN:
                    player.try_descend()

        # ----- Update Game Objects -----
        player.update(keys)

        # Update bullets.
        for bullet in bullets:
            bullet.update()
        # Remove bullets that have left the screen.
        bullets = [b for b in bullets if 0 <= b.rect.x <= SCREEN_WIDTH]

        # Spawn an enemy on the same floor as the player every few seconds.
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= FPS * 3:  # every 3 seconds
            enemy_spawn_timer = 0
            # Choose a spawn x position near one of the doors on the player's floor, if any.
            door_list = floors[player.floor]["doors"]
            if door_list:
                door = random.choice(door_list)
                spawn_x = door.x + door.width // 2 - Enemy.WIDTH // 2
                spawn_y = floors[player.floor]["y"] - Enemy.HEIGHT // 2
                enemies.append(Enemy(spawn_x, spawn_y, player.floor))
            else:
                # Otherwise, spawn somewhere randomly.
                spawn_x = random.randint(0, SCREEN_WIDTH - Enemy.WIDTH)
                spawn_y = floors[player.floor]["y"] - Enemy.HEIGHT // 2
                enemies.append(Enemy(spawn_x, spawn_y, player.floor))

        # Update enemies.
        for enemy in enemies:
            # Only update enemies on the same floor as the player.
            if enemy.floor == player.floor:
                enemy.update()

        # Check bullet/enemy collisions.
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.floor == enemy.floor and bullet.rect.colliderect(enemy.rect):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    break

        # Check enemy/player collisions (only if on the same floor).
        for enemy in enemies:
            if enemy.floor == player.floor and player.rect.colliderect(enemy.rect):
                show_end_screen("GAME OVER!")
                return

        # Check document collection.
        if (
            (not document_collected)
            and player.floor == 1
            and player.rect.colliderect(document_rect)
        ):
            document_collected = True

        # Check win condition:
        # If the player is on floor 2 (the exit floor), inside the exit door,
        # and has already collected the document, then the player wins.
        if player.floor == 2:
            for door in floors[2]["doors"]:
                if player.rect.colliderect(door) and document_collected:
                    show_end_screen("YOU WIN!")
                    return

        # ----- Draw Everything -----
        screen.fill(BLACK)
        # Draw floors and elevator doors.
        draw_floors(screen)
        # Draw document if not yet collected.
        draw_document(screen)
        # Draw player.
        player.draw(screen)
        # Draw bullets.
        for bullet in bullets:
            bullet.draw(screen)
        # Draw enemies.
        for enemy in enemies:
            enemy.draw(screen)
        # Optionally, display the current floor and document status.
        status_text = f"Floor: {player.floor}    Document: {'Yes' if document_collected else 'No'}"
        draw_text(screen, status_text, 24, WHITE, (SCREEN_WIDTH // 2, 20))

        pygame.display.flip()


# ----- Main Loop -----
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Elevator Action")


def main():
    while True:
        run_game()


if __name__ == "__main__":
    main()
