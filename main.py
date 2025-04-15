import pygame
import sys
import math
import random
from pygame.locals import *
pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Futebol 2D Aprimorado')

WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Campo
FIELD_WIDTH, FIELD_HEIGHT = 700, 500
FIELD_X, FIELD_Y = (WIDTH - FIELD_WIDTH) // 2, (HEIGHT - FIELD_HEIGHT) // 2
GOAL_WIDTH = 200
GOAL_DEPTH = 20
CENTER_CIRCLE_RADIUS = 50

# Bola
ball_radius = 15
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = 0
ball_speed_y = 0
max_speed = 10
friction = 0.98
elasticity = 0.8


score_blue = 0 # Placar e estatísticas
score_red = 0
crossbar_hits = 0
font = pygame.font.SysFont('Arial', 36)
small_font = pygame.font.SysFont('Arial', 18)


players = [
    {"x": FIELD_X + FIELD_WIDTH // 4, "y": FIELD_Y + FIELD_HEIGHT // 2, "color": BLUE, "team": "blue", "speed": 3}, # Jogadores
    {"x": FIELD_X + 3 * FIELD_WIDTH // 4, "y": FIELD_Y + FIELD_HEIGHT // 2, "color": RED, "team": "red", "speed": 3},
    {"x": FIELD_X + FIELD_WIDTH // 4, "y": FIELD_Y + FIELD_HEIGHT // 3, "color": BLUE, "team": "blue", "speed": 3},
    {"x": FIELD_X + 3 * FIELD_WIDTH // 4, "y": FIELD_Y + 2 * FIELD_HEIGHT // 3, "color": RED, "team": "red", "speed": 3}
]

def draw_line_bresenham(surface, color, start, end, width=1):
    x1, y1 = start
    x2, y2 = end

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    steep = dy > dx
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    error = dx // 2
    y_step = 1 if y1 < y2 else -1
    y = y1
    for x in range(x1, x2 + 1):
        coord = (y, x) if steep else (x, y)
        for w in range(width):
            if 0 <= coord[0] < WIDTH and 0 <= coord[1] + w < HEIGHT:
                surface.set_at((coord[0], coord[1] + w), color)
            if 0 <= coord[0] + w < WIDTH and 0 <= coord[1] < HEIGHT:
                surface.set_at((coord[0] + w, coord[1]), color)
        error -= dy
        if error < 0:
            y += y_step
            error += dx

def draw_field():
    pygame.draw.rect(screen, GREEN, (FIELD_X, FIELD_Y, FIELD_WIDTH, FIELD_HEIGHT))
    draw_line_bresenham(screen, WHITE, (FIELD_X, FIELD_Y), (FIELD_X + FIELD_WIDTH, FIELD_Y), 2)
    draw_line_bresenham(screen, WHITE, (FIELD_X, FIELD_Y + FIELD_HEIGHT), (FIELD_X + FIELD_WIDTH, FIELD_Y + FIELD_HEIGHT), 2)
    draw_line_bresenham(screen, WHITE, (FIELD_X, FIELD_Y), (FIELD_X, FIELD_Y + FIELD_HEIGHT), 2)
    draw_line_bresenham(screen, WHITE, (FIELD_X + FIELD_WIDTH, FIELD_Y), (FIELD_X + FIELD_WIDTH, FIELD_Y + FIELD_HEIGHT), 2)
    draw_line_bresenham(screen, WHITE, (FIELD_X + FIELD_WIDTH // 2, FIELD_Y), (FIELD_X + FIELD_WIDTH // 2, FIELD_Y + FIELD_HEIGHT), 2)
    pygame.draw.circle(screen, WHITE, (WIDTH // 2, HEIGHT // 2), CENTER_CIRCLE_RADIUS, 2)

    pygame.draw.rect(screen, WHITE, (FIELD_X, FIELD_Y + FIELD_HEIGHT // 2 - 50, 50, 100), 2)
    pygame.draw.rect(screen, WHITE, (FIELD_X, FIELD_Y + FIELD_HEIGHT // 2 - 100, 100, 200), 2)
    pygame.draw.rect(screen, WHITE, (FIELD_X + FIELD_WIDTH - 50, FIELD_Y + FIELD_HEIGHT // 2 - 50, 50, 100), 2)
    pygame.draw.rect(screen, WHITE, (FIELD_X + FIELD_WIDTH - 100, FIELD_Y + FIELD_HEIGHT // 2 - 100, 100, 200), 2)

   
    pygame.draw.rect(screen, YELLOW, (FIELD_X - GOAL_DEPTH, FIELD_Y + FIELD_HEIGHT // 2 - GOAL_WIDTH // 2, GOAL_DEPTH, GOAL_WIDTH), 3)
    pygame.draw.rect(screen, YELLOW, (FIELD_X + FIELD_WIDTH, FIELD_Y + FIELD_HEIGHT // 2 - GOAL_WIDTH // 2, GOAL_DEPTH, GOAL_WIDTH), 3)

def draw_players():
    for i, player in enumerate(players):
        pygame.draw.circle(screen, player["color"], (int(player["x"]), int(player["y"])), 20)
        text = small_font.render(str(i + 1), True, WHITE)
        screen.blit(text, (int(player["x"]) - 5, int(player["y"]) - 5))

def move_players():
    keys = pygame.key.get_pressed()
    if keys[K_w]: players[0]["y"] -= players[0]["speed"]
    if keys[K_s]: players[0]["y"] += players[0]["speed"]
    if keys[K_a]: players[0]["x"] -= players[0]["speed"]
    if keys[K_d]: players[0]["x"] += players[0]["speed"]

    if keys[K_UP]: players[1]["y"] -= players[1]["speed"]
    if keys[K_DOWN]: players[1]["y"] += players[1]["speed"]
    if keys[K_LEFT]: players[1]["x"] -= players[1]["speed"]
    if keys[K_RIGHT]: players[1]["x"] += players[1]["speed"]

    for player in players:
        player["x"] = max(FIELD_X + 20, min(FIELD_X + FIELD_WIDTH - 20, player["x"]))
        player["y"] = max(FIELD_Y + 20, min(FIELD_Y + FIELD_HEIGHT - 20, player["y"]))

def update_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y
    ball_speed_x *= friction
    ball_speed_y *= friction
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    if ball_x - ball_radius < FIELD_X or ball_x + ball_radius > FIELD_X + FIELD_WIDTH:
        ball_speed_x *= -elasticity
        ball_x = max(FIELD_X + ball_radius, min(FIELD_X + FIELD_WIDTH - ball_radius, ball_x))
    if ball_y - ball_radius < FIELD_Y or ball_y + ball_radius > FIELD_Y + FIELD_HEIGHT:
        ball_speed_y *= -elasticity
        ball_y = max(FIELD_Y + ball_radius, min(FIELD_Y + FIELD_HEIGHT - ball_radius, ball_y))

    for player in players:
        dx = ball_x - player["x"]
        dy = ball_y - player["y"]
        distance = math.hypot(dx, dy)
        if distance < ball_radius + 20:
            if distance > 0:
                dx /= distance
                dy /= distance
            overlap = (ball_radius + 20) - distance
            ball_x += dx * overlap * 0.5
            ball_y += dy * overlap * 0.5
            impact = math.sqrt(ball_speed_x**2 + ball_speed_y**2)
            ball_speed_x = dx * (impact + player["speed"] * 0.5)
            ball_speed_y = dy * (impact + player["speed"] * 0.5)
            speed = math.sqrt(ball_speed_x**2 + ball_speed_y**2)
            if speed > max_speed:
                ball_speed_x = (ball_speed_x / speed) * max_speed
                ball_speed_y = (ball_speed_y / speed) * max_speed

def check_goals_and_crossbar():
    global score_blue, score_red, crossbar_hits, ball_x, ball_y, ball_speed_x, ball_speed_y

    
    left_goal_line = FIELD_X - GOAL_DEPTH
    right_goal_line = FIELD_X + FIELD_WIDTH + GOAL_DEPTH
    goal_top = FIELD_Y + (FIELD_HEIGHT - GOAL_WIDTH) // 2
    goal_bottom = FIELD_Y + (FIELD_HEIGHT + GOAL_WIDTH) // 2

    
    if ball_x - ball_radius <= left_goal_line: # Verificação do gol esquerdo (time vermelho)
        if goal_top <= ball_y <= goal_bottom:
            score_red += 1
            show_goal_animation("RED")
            reset_ball()
        else:
            
            crossbar_hits += 1
            ball_x = left_goal_line + ball_radius
            ball_speed_x *= -0.7
            ball_speed_y += random.uniform(-2, 2)

    
    elif ball_x + ball_radius >= right_goal_line: # Verificação do gol direito (time azul)
        if goal_top <= ball_y <= goal_bottom:
            score_blue += 1
            show_goal_animation("BLUE")
            reset_ball()
        else:
            
            crossbar_hits += 1
            ball_x = right_goal_line - ball_radius
            ball_speed_x *= -0.7
            ball_speed_y += random.uniform(-2, 2)

def update_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y
    
    
    ball_speed_x *= friction # Aplica atrito
    ball_speed_y *= friction
    
    
    ball_x += ball_speed_x # Atualiza posição
    ball_y += ball_speed_y
    

    if ball_y - ball_radius < FIELD_Y or ball_y + ball_radius > FIELD_Y + FIELD_HEIGHT: # Colisão com as bordas do campo
        ball_speed_y *= -elasticity
        ball_y = max(FIELD_Y + ball_radius, min(FIELD_Y + FIELD_HEIGHT - ball_radius, ball_y))
    
    
    for player in players: # Colisão com os jogadores
        dx = ball_x - player["x"]
        dy = ball_y - player["y"]
        distance = math.hypot(dx, dy)
        
        if distance < ball_radius + 20:  # 20 é o raio do jogador
            
            angle = math.atan2(dy, dx) # Calcula ângulo de colisão
            
           
            overlap = (ball_radius + 20) - distance   # Ajusta posição para evitar sobreposição
            ball_x += math.cos(angle) * overlap * 0.5
            ball_y += math.sin(angle) * overlap * 0.5
            
            
            player_speed = math.hypot(players[0]["speed"], players[1]["speed"])# Calcula força do chute baseada na velocidade do jogador e direção
            kick_power = 0.5 + player_speed * 0.3
            
           
            ball_speed_x = math.cos(angle) * kick_power * max_speed # Aplica nova velocidade com direção do chute
            ball_speed_y = math.sin(angle) * kick_power * max_speed
            
            
            speed = math.hypot(ball_speed_x, ball_speed_y) # Limita velocidade máxima
            if speed > max_speed:
                ball_speed_x = (ball_speed_x / speed) * max_speed
                ball_speed_y = (ball_speed_y / speed) * max_speed
            
def reset_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_speed_x = random.choice([-1, 1]) * 2
    ball_speed_y = random.uniform(-1, 1) * 2
    pygame.time.delay(800)

def show_goal_animation(team):
    font_large = pygame.font.SysFont('Arial', 72, bold=True)
    screen_rect = screen.get_rect()
    color = BLUE if team == "BLUE" else RED
    text = font_large.render(f"GOOOOL DO {team}!", True, color)
    text_rect = text.get_rect(center=screen_rect.center)
    overlay = pygame.Surface((text_rect.width + 40, text_rect.height + 40), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (text_rect.x - 20, text_rect.y - 20))
    screen.blit(text, text_rect)
    pygame.display.update()
    pygame.time.delay(1500)


clock = pygame.time.Clock() # Loop principal
running = True
while running:
    screen.fill(BLACK)
    draw_field()
    move_players()
    update_ball()
    check_goals_and_crossbar()
    draw_players()
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)

    score_text = font.render(f"{score_blue} - {score_red}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

    crossbar_text = small_font.render(f"Traves: {crossbar_hits}", True, YELLOW)
    screen.blit(crossbar_text, (10, HEIGHT - 30))

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()