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
    draw_text(text, font, (25,25,35), x + 25, y + 12)
    return rect

# -------- Gradient Snake --------
def get_gradient_color(index, total):
    start = (0, 255, 170)
    end = (0, 120, 255)
    ratio = index / max(total, 1)
    r = int(start[0] + (end[0] - start[0]) * ratio)
    g = int(start[1] + (end[1] - start[1]) * ratio)
    b = int(start[2] + (end[2] - start[2]) * ratio)
    return (r, g, b)

def draw_glow_circle(surface, color, pos, radius):
    for i in range(6, 0, -1):
        glow_radius = radius + i * 2
        alpha = max(5, 40 - i * 5)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*color, alpha), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, (pos[0] - glow_radius, pos[1] - glow_radius))

# -------- Particle System --------
particles = []

def spawn_particle(pos):
    particles.append({
        "x": pos[0],
        "y": pos[1],
        "vx": random.uniform(-1, 1),
        "vy": random.uniform(-1, 1),
        "life": random.randint(20, 40),
        "size": random.randint(2, 4)
    })

def update_particles(surface):
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1

        alpha = max(0, p["life"] * 5)
        particle_surface = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (0, 255, 200, alpha),
                           (p["size"], p["size"]), p["size"])
        surface.blit(particle_surface, (p["x"], p["y"]))

        if p["life"] <= 0:
            particles.remove(p)

# -------- Dynamic Background --------
bg_offset = 0

def draw_dynamic_background(surface):
    global bg_offset
    bg_offset += 0.5
    for y in range(0, HEIGHT, 40):
        shift = int((y + bg_offset) % 255)
        color = (20, 20 + shift // 5, 40 + shift // 6)
        pygame.draw.rect(surface, color, (0, y, WIDTH, 40))

# -------- Camera Shake --------
shake_timer = 0

def apply_camera_shake():
    global shake_timer
    if shake_timer > 0:
        shake_timer -= 1
        return random.randint(-5, 5), random.randint(-5, 5)
    return 0, 0

# -------- MENU --------
def main_menu():
    while True:
        screen.fill((25,25,35))
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

# -------- GAME LOOP --------
def game_loop():
    global shake_timer

    snake = [(WIDTH // 2, HEIGHT // 2)]
    dx, dy = BLOCK, 0

    food = (
        random.randint(0, (WIDTH - BLOCK) // BLOCK) * BLOCK,
        random.randint(0, (HEIGHT - BLOCK) // BLOCK) * BLOCK
    )

    score = 0
    speed = 5   # 👈 START SPEED
    paused = False
    high_score = load_high_score()

    while True:
        offset_x, offset_y = apply_camera_shake()
        temp_surface = pygame.Surface((WIDTH, HEIGHT))

        draw_dynamic_background(temp_surface)

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

        head = (snake[0][0] + dx, snake[0][1] + dy)

        if (head[0] < 0 or head[0] >= WIDTH or
            head[1] < 0 or head[1] >= HEIGHT or
            head in snake):

            shake_timer = 20

            if score > high_score:
                save_high_score(score)

            return game_over(score)

        snake.insert(0, head)

        snake_rect = pygame.Rect(head[0], head[1], BLOCK, BLOCK)
        food_rect = pygame.Rect(food[0], food[1], BLOCK, BLOCK)

        if snake_rect.colliderect(food_rect):
            score += 1
            speed += 0.3
            food = (
                random.randint(0, (WIDTH - BLOCK) // BLOCK) * BLOCK,
                random.randint(0, (HEIGHT - BLOCK) // BLOCK) * BLOCK
            )
        else:
            snake.pop()

        pygame.draw.rect(temp_surface, (255, 80, 80), (*food, BLOCK, BLOCK), border_radius=6)

        # Draw snake
        for i, s in enumerate(snake):
            color = get_gradient_color(i, len(snake))
            center = (s[0] + BLOCK // 2, s[1] + BLOCK // 2)

            if i == 0:
                draw_glow_circle(temp_surface, color, center, BLOCK // 2)
                spawn_particle(center)

            pygame.draw.circle(temp_surface, color, center, BLOCK // 2)

        update_particles(temp_surface)

        draw_text(f"Score: {score}", font, WHITE, 10, 10)
        draw_text(f"High Score: {high_score}", font, WHITE, 10, 35)

        screen.blit(temp_surface, (offset_x, offset_y))
        pygame.display.flip()
        clock.tick(speed)

# -------- GAME OVER --------
def game_over(score):
    while True:
        screen.fill((25,25,35))
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

# -------- START --------
main_menu()