import pygame
import random
import sys
import os

pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 500
BLOCK = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game Pro")

clock = pygame.time.Clock()

# Colors
BG = (25, 25, 35)
GRID = (40, 40, 55)
SNAKE = (0, 220, 120)
FOOD = (255, 80, 80)
WHITE = (255, 255, 255)
ACCENT = (255, 200, 0)

font = pygame.font.SysFont("Segoe UI", 24)
big_font = pygame.font.SysFont("Segoe UI", 50)

# High score file
HS_FILE = "highscore.txt"

def load_high_score():
    try:
        if not os.path.exists(HS_FILE):
            with open(HS_FILE, "w") as f:
                f.write("0")
        with open(HS_FILE, "r") as f:
            data = f.read().strip()
            return int(data) if data else 0
    except:
        return 0

def save_high_score(score):
    with open(HS_FILE, "w") as f:
        f.write(str(score))

def draw_text(text, f, color, x, y):
    screen.blit(f.render(text, True, color), (x, y))

def draw_button(text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, ACCENT, rect, border_radius=8)
    draw_text(text, font, BG, x + 25, y + 12)
    return rect

def draw_grid():
    for x in range(0, WIDTH, BLOCK):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))

# ---------- MENU ----------
def main_menu():
    while True:
        screen.fill(BG)
        draw_text("SNAKE GAME PRO", big_font, WHITE, WIDTH // 3, 120)

        start_btn = draw_button("Start Game", WIDTH // 2 - 100, 250, 200, 50)
        quit_btn = draw_button("Quit", WIDTH // 2 - 100, 320, 200, 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    return game_loop()
                if quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# ---------- GAME LOOP ----------
def game_loop():
    snake = [(WIDTH // 2, HEIGHT // 2)]
    dx, dy = BLOCK, 0

    food = (
        random.randint(0, (WIDTH - BLOCK) // BLOCK) * BLOCK,
        random.randint(0, (HEIGHT - BLOCK) // BLOCK) * BLOCK
    )

    score = 0
    speed = 4
    paused = False
    high_score = load_high_score()

    while True:
        screen.fill(BG)
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

                if not paused:
                    if event.key == pygame.K_LEFT and dx == 0:
                        dx, dy = -BLOCK, 0
                    elif event.key == pygame.K_RIGHT and dx == 0:
                        dx, dy = BLOCK, 0
                    elif event.key == pygame.K_UP and dy == 0:
                        dx, dy = 0, -BLOCK
                    elif event.key == pygame.K_DOWN and dy == 0:
                        dx, dy = 0, BLOCK

        if paused:
            draw_text("PAUSED", big_font, WHITE, WIDTH // 2 - 80, HEIGHT // 2)
            pygame.display.flip()
            continue

        # Move snake
        head = (snake[0][0] + dx, snake[0][1] + dy)

        # Collision with wall or self
        if (head[0] < 0 or head[0] >= WIDTH or
            head[1] < 0 or head[1] >= HEIGHT or
            head in snake):

            if score > high_score:
                save_high_score(score)

            return game_over(score)

        snake.insert(0, head)

        # Rect collision detection
        snake_rect = pygame.Rect(head[0], head[1], BLOCK, BLOCK)
        food_rect = pygame.Rect(food[0], food[1], BLOCK, BLOCK)

        if snake_rect.colliderect(food_rect):
            score += 1
            speed += 0.4

            food = (
                random.randint(0, (WIDTH - BLOCK) // BLOCK) * BLOCK,
                random.randint(0, (HEIGHT - BLOCK) // BLOCK) * BLOCK
            )
        else:
            snake.pop()

        # Draw food
        pygame.draw.rect(screen, FOOD, (*food, BLOCK, BLOCK), border_radius=6)

        # Draw snake
        for s in snake:
            pygame.draw.rect(screen, SNAKE, (*s, BLOCK, BLOCK), border_radius=6)

        draw_text(f"Score: {score}", font, WHITE, 10, 10)
        draw_text(f"High Score: {high_score}", font, WHITE, 10, 35)

        pygame.display.flip()
        clock.tick(speed)

# ---------- GAME OVER ----------
def game_over(score):
    while True:
        screen.fill(BG)
        draw_text("GAME OVER", big_font, WHITE, WIDTH // 3, 150)
        draw_text(f"Score: {score}", font, ACCENT, WIDTH // 2 - 40, 230)
        draw_text("Press R to Restart or M for Menu", font, WHITE, WIDTH // 3, 280)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return game_loop()
                if event.key == pygame.K_m:
                    return main_menu()

# ---------- START ----------
main_menu()