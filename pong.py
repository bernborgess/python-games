import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_SIZE = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Initialize game objects
ball = pygame.Rect(
    WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE
)
paddle1 = pygame.Rect(30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(
    WIDTH - 50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT
)

# Game variables
ball_speed_x = 7 * random.choice((1, -1))
ball_speed_y = 7 * random.choice((1, -1))
paddle_speed = 7
score1 = 0
score2 = 0

# Clock to control FPS
clock = pygame.time.Clock()


def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_speed_x *= random.choice((1, -1))
    ball_speed_y *= random.choice((1, -1))


# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move paddles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and paddle1.top > 0:
        paddle1.y -= paddle_speed
    if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
        paddle1.y += paddle_speed
    if keys[pygame.K_UP] and paddle2.top > 0:
        paddle2.y -= paddle_speed
    if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
        paddle2.y += paddle_speed

    # Move ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Ball collision with top/bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1

    # Ball collision with paddles
    if ball.colliderect(paddle1) or ball.colliderect(paddle2):
        ball_speed_x *= -1
        # Add slight vertical speed variation based on paddle impact point
        ball_speed_y += random.uniform(-1, 1)

    # Score points
    if ball.left <= 0:
        score2 += 1
        reset_ball()
    if ball.right >= WIDTH:
        score1 += 1
        reset_ball()

    # Drawing
    screen.fill(BLACK)

    # Draw center line
    for i in range(0, HEIGHT, HEIGHT // 20):
        if i % 2 == 0:
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, i, 4, HEIGHT // 20))

    # Draw paddles and ball
    pygame.draw.rect(screen, WHITE, paddle1)
    pygame.draw.rect(screen, WHITE, paddle2)
    pygame.draw.ellipse(screen, WHITE, ball)

    # Draw scores
    font = pygame.font.Font(None, 74)
    text = font.render(str(score1), True, WHITE)
    screen.blit(text, (WIDTH // 4, 20))
    text = font.render(str(score2), True, WHITE)
    screen.blit(text, (WIDTH * 3 // 4, 20))

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
