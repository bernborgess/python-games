import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Asteroids Game")
clock = pygame.time.Clock()

# Set up fonts
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)


# Spaceship class
class Spaceship:
    def __init__(self):
        self.position = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.velocity = pygame.Vector2(0, 0)
        self.angle = 0  # In degrees; 0 points to the right
        self.rotation_speed = 5  # degrees per frame
        self.acceleration = 0.2
        self.radius = 10  # For collision detection

    def update(self):
        keys = pygame.key.get_pressed()
        # Rotate the ship
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed

        # Accelerate in the facing direction
        if keys[pygame.K_UP]:
            rad = math.radians(self.angle)
            force = pygame.Vector2(math.cos(rad), -math.sin(rad))
            self.velocity += force * self.acceleration

        self.position += self.velocity

        # Wrap around the screen edges
        self.position.x %= WIDTH
        self.position.y %= HEIGHT

    def draw(self, surface):
        # Draw the ship as a triangle.
        rad = math.radians(self.angle)
        tip = self.position + pygame.Vector2(math.cos(rad), -math.sin(rad)) * 20
        left = (
            self.position
            + pygame.Vector2(
                math.cos(rad + math.radians(140)), -math.sin(rad + math.radians(140))
            )
            * 20
        )
        right = (
            self.position
            + pygame.Vector2(
                math.cos(rad - math.radians(140)), -math.sin(rad - math.radians(140))
            )
            * 20
        )
        pygame.draw.polygon(surface, WHITE, [tip, left, right])


# Asteroid class
class Asteroid:
    def __init__(self, position=None, size=3):
        """
        size: 3 for large, 2 for medium, 1 for small.
        """
        self.size = size
        if position is None:
            self.position = pygame.Vector2(
                random.randrange(WIDTH), random.randrange(HEIGHT)
            )
        else:
            self.position = pygame.Vector2(position)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        self.velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
        self.radius = size * 15  # Larger asteroids have a larger radius

    def update(self):
        self.position += self.velocity
        self.position.x %= WIDTH
        self.position.y %= HEIGHT

    def draw(self, surface):
        pygame.draw.circle(
            surface, GRAY, (int(self.position.x), int(self.position.y)), self.radius, 2
        )


# Bullet class
class Bullet:
    def __init__(self, position, angle):
        self.position = pygame.Vector2(position)
        rad = math.radians(angle)
        self.velocity = pygame.Vector2(math.cos(rad), -math.sin(rad)) * 8
        self.radius = 2
        self.lifetime = 60  # Frames

    def update(self):
        self.position += self.velocity
        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        self.lifetime -= 1

    def draw(self, surface):
        pygame.draw.circle(
            surface, WHITE, (int(self.position.x), int(self.position.y)), self.radius
        )


def show_game_over_screen():
    """Display the game over screen until the player presses R to restart or quits."""
    while True:
        screen.fill(BLACK)
        # Render game over messages
        game_over_text = font.render("GAME OVER", True, WHITE)
        restart_text = small_font.render("Press R to Restart", True, WHITE)
        quit_text = small_font.render("Press Q or close window to Quit", True, WHITE)

        # Position texts at the center of the screen
        screen.blit(
            game_over_text, game_over_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
        )
        screen.blit(restart_text, restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2)))
        screen.blit(quit_text, quit_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50)))
        pygame.display.flip()

        # Wait for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return  # Exit this loop and restart the game
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()

        clock.tick(60)


def run_game():
    spaceship = Spaceship()
    asteroids = [Asteroid(size=3) for _ in range(5)]
    bullets = []
    running = True

    while running:
        clock.tick(60)  # 60 FPS

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Fire bullet when space is pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(spaceship.position, spaceship.angle)
                    bullets.append(bullet)

        # Update game objects
        spaceship.update()
        for asteroid in asteroids:
            asteroid.update()
        for bullet in bullets:
            bullet.update()

        # Remove bullets that have expired
        bullets = [b for b in bullets if b.lifetime > 0]

        # Check collisions between bullets and asteroids
        new_asteroids = []
        for asteroid in asteroids:
            hit = False
            for bullet in bullets:
                if asteroid.position.distance_to(bullet.position) < asteroid.radius:
                    hit = True
                    # If the asteroid is not the smallest, split it into two smaller asteroids
                    if asteroid.size > 1:
                        for _ in range(2):
                            new_asteroids.append(
                                Asteroid(
                                    position=asteroid.position, size=asteroid.size - 1
                                )
                            )
                    break
            if not hit:
                new_asteroids.append(asteroid)
        asteroids = new_asteroids

        # Check collision between the spaceship and asteroids
        for asteroid in asteroids:
            if (
                spaceship.position.distance_to(asteroid.position)
                < asteroid.radius + spaceship.radius
            ):
                running = False  # End game loop if collision occurs

        # Drawing
        screen.fill(BLACK)
        spaceship.draw(screen)
        for asteroid in asteroids:
            asteroid.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        pygame.display.flip()


def main():
    while True:
        run_game()
        # When run_game() returns, a collision has occurred.
        show_game_over_screen()


if __name__ == "__main__":
    main()
