import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

# Configurações
WIDTH, HEIGHT = 800, 600
FPS = 60

def init():
    pygame.init()
    display = (WIDTH, HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluOrtho2D(0, display[0], display[1], 0)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPointSize(2.0)

def bresenham_line(x0, y0, x1, y1, color=(1,1,1)):
    
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    steep = dy > dx
    
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
    
    dx = x1 - x0
    dy = abs(y1 - y0)
    error = dx // 2
    y_step = 1 if y0 < y1 else -1
    y = y0
    
    for x in range(x0, x1 + 1):
        coord = (y, x) if steep else (x, y)
        points.append(coord)
        error -= dy
        if error < 0:
            y += y_step
            error += dx
    
  
    glColor3f(*color)
    glBegin(GL_POINTS)
    for point in points:
        glVertex2f(*point)
    glEnd()

def bresenham_circle(cx, cy, radius, color=(1,1,1), filled=False):
    
    points = []
    x = radius
    y = 0
    err = 0

    while x >= y:
        points += [
            (cx + x, cy + y), (cx + y, cy + x),
            (cx - y, cy + x), (cx - x, cy + y),
            (cx - x, cy - y), (cx - y, cy - x),
            (cx + y, cy - x), (cx + x, cy - y)
        ]
        y += 1
        err += 1 + 2*y
        if 2*(err - x) + 1 > 0:
            x -= 1
            err += 1 - 2*x
    
    glColor3f(*color)
    glBegin(GL_POINTS)
    for point in points:
        glVertex2f(*point)
    glEnd()
    
    if filled:
        glBegin(GL_LINES)
        for point in points:
            glVertex2f(cx, cy)
            glVertex2f(*point)
        glEnd()

def draw_player(x, y, radius, color, role):
    
    if role == 'goalkeeper':
        # Goleiro - retângulo
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x-radius, y-radius)
        glVertex2f(x+radius, y-radius)
        glVertex2f(x+radius, y+radius)
        glVertex2f(x-radius, y+radius)
        glEnd()
    elif role == 'defender':
        # Defensor - triângulo
        glColor3f(*color)
        glBegin(GL_TRIANGLES)
        glVertex2f(x, y+radius)
        glVertex2f(x-radius, y-radius)
        glVertex2f(x+radius, y-radius)
        glEnd()
    else:
        # Outros - círculo
        bresenham_circle(x, y, radius, color, filled=True)

class Team:
    def __init__(self, color, side, num_players=11):
        self.players = []
        self.color = color
        self.side = side
        # Formação 4-3-3
        self.formation = [
            (0.02, 0.5),   # Goleiro
            (0.15, 0.3), (0.15, 0.5), (0.15, 0.7),  # Zagueiros
            (0.25, 0.2), (0.25, 0.5), (0.25, 0.8),  # Meio-campo
            (0.35, 0.3), (0.35, 0.7),              # Atacantes
            (0.45, 0.4), (0.45, 0.6)               # Pontas
        ]
        
        roles = ['goalkeeper', 'defender', 'defender', 'defender',
                'midfielder', 'midfielder', 'midfielder',
                'forward', 'forward', 'forward', 'forward']
        
        for i in range(num_players):
            x_pos = self.formation[i][0] if side == 'left' else 1 - self.formation[i][0]
            self.players.append({
                'x': x_pos * WIDTH,
                'y': self.formation[i][1] * HEIGHT,
                'radius': 15,
                'color': color,
                'speed': random.uniform(1.5, 2.5),
                'role': roles[i]
            })

    def draw(self):
        for player in self.players:
            draw_player(player['x'], player['y'], 
                       player['radius'], player['color'], player['role'])

    def move_towards_ball(self, ball_pos):
        for player in self.players:
            if player['role'] == 'goalkeeper':
                target_x = player['x']
                target_y = ball_pos[1] if 200 < ball_pos[1] < 400 else 300
                if self.side == 'left':
                    target_x = min(100, ball_pos[0])
                else:
                    target_x = max(700, ball_pos[0])
            else:
                target_x = ball_pos[0] * (0.8 if self.side == 'left' else 1.2)
                target_y = ball_pos[1] * 0.9
            
            dx = target_x - player['x']
            dy = target_y - player['y']
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 5:
                player['x'] += dx/dist * player['speed']
                player['y'] += dy/dist * player['speed']

def draw_text(text, x, y, size=30, color=(1,1,1)):
    
    font = pygame.font.SysFont('Arial', size, bold=True)
    text_surface = font.render(text, True, (color[0]*255, color[1]*255, color[2]*255, 255))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(),
                GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def draw_field():
    
    # Gramado
    glColor3f(0.1, 0.5, 0.1)
    glBegin(GL_QUADS)
    glVertex2f(50, 50)
    glVertex2f(750, 50)
    glVertex2f(750, 550)
    glVertex2f(50, 550)
    glEnd()
    
    # Linhas do campo
    glColor3f(1, 1, 1)
    bresenham_line(50, 50, 750, 50)   # Superior
    bresenham_line(50, 550, 750, 550) # Inferior
    bresenham_line(50, 50, 50, 550)   # Esquerda
    bresenham_line(750, 50, 750, 550) # Direita
    bresenham_line(400, 50, 400, 550) # Central
    
    # Círculo central
    bresenham_circle(400, 300, 50, filled=False)
    
    # Áreas
    bresenham_line(50, 200, 150, 200)  # Área esquerda superior
    bresenham_line(150, 200, 150, 400) # Área esquerda lateral
    bresenham_line(50, 400, 150, 400)  # Área esquerda inferior
    
    bresenham_line(750, 200, 650, 200)  # Área direita superior
    bresenham_line(650, 200, 650, 400)  # Área direita lateral
    bresenham_line(750, 400, 650, 400)  # Área direita inferior
    
    # Gols
    glColor3f(1, 1, 0)
    bresenham_line(0, 200, 20, 200)    # Gol esquerdo trave superior
    bresenham_line(0, 400, 20, 400)    # Gol esquerdo trave inferior
    bresenham_line(10, 200, 10, 400)   # Gol esquerdo trave traseira
    
    bresenham_line(780, 200, 800, 200)  # Gol direito trave superior
    bresenham_line(780, 400, 800, 400)  # Gol direito trave inferior
    bresenham_line(790, 200, 790, 400)  # Gol direito trave traseira

def main():
    init()
    clock = pygame.time.Clock()
    
    # Configurações do jogo
    ball_pos = [WIDTH//2, HEIGHT//2]
    ball_vel = [0, 0]
    ball_radius = 12
    score = [0, 0]  # [Azul, Vermelho]
    
    # Times
    team_blue = Team((0, 0, 1), 'left')    # Time azul
    team_red = Team((1, 0, 0), 'right')    # Time vermelho
    
    # Gols
    goals = [
        {"x": 0, "y": 200, "width": 20, "height": 200, "team": "red"},
        {"x": WIDTH-20, "y": 200, "width": 20, "height": 200, "team": "blue"}
    ]

    while True:
        dt = clock.tick(FPS)/1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Controles da bola
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]: ball_vel[0] = max(-15, ball_vel[0] - 0.7)
        if keys[K_RIGHT]: ball_vel[0] = min(15, ball_vel[0] + 0.7)
        if keys[K_UP]: ball_vel[1] = max(-15, ball_vel[1] - 0.7)
        if keys[K_DOWN]: ball_vel[1] = min(15, ball_vel[1] + 0.7)
        
        # Movimento da bola
        ball_pos[0] += ball_vel[0]
        ball_pos[1] += ball_vel[1]
        ball_vel[0] *= 0.96
        ball_vel[1] *= 0.96
        
        # Colisão com bordas
        if ball_pos[1] - ball_radius < 50:
            ball_pos[1] = 50 + ball_radius
            ball_vel[1] *= -0.8
        elif ball_pos[1] + ball_radius > 550:
            ball_pos[1] = 550 - ball_radius
            ball_vel[1] *= -0.8
            
        # Verificação de Gol
        for goal in goals:
            if ((goal["x"] < ball_pos[0] < goal["x"] + goal["width"]) and 
                (goal["y"] < ball_pos[1] < goal["y"] + goal["height"])):
                
                if goal["team"] == "blue":
                    score[0] += 1
                else:
                    score[1] += 1
                
                # Reset da bola
                ball_pos = [WIDTH//2, HEIGHT//2]
                ball_vel = [random.choice([-4,4]), random.uniform(-3,3)]
                break
        
        # Colisão lateral (exceto área dos gols)
        if not (200 < ball_pos[1] < 400):
            if ball_pos[0] - ball_radius < 50:
                ball_pos[0] = 50 + ball_radius
                ball_vel[0] *= -0.8
            elif ball_pos[0] + ball_radius > 750:
                ball_pos[0] = 750 - ball_radius
                ball_vel[0] *= -0.8
        
        # Movimento dos times
        team_blue.move_towards_ball(ball_pos)
        team_red.move_towards_ball(ball_pos)
        
        # Colisão com jogadores
        for team in [team_blue, team_red]:
            for player in team.players:
                dx = ball_pos[0] - player['x']
                dy = ball_pos[1] - player['y']
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < ball_radius + player['radius']:
                    angle = math.atan2(dy, dx)
                    min_dist = ball_radius + player['radius']
                    ball_pos[0] = player['x'] + math.cos(angle) * min_dist
                    ball_pos[1] = player['y'] + math.sin(angle) * min_dist
                    speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2) * 1.2
                    ball_vel[0] = math.cos(angle) * speed
                    ball_vel[1] = math.sin(angle) * speed
        
        # Renderização
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Desenha o campo
        draw_field()
        
        # Desenha os times
        team_blue.draw()
        team_red.draw()
        
        # Desenha a bola
        bresenham_circle(int(ball_pos[0]), int(ball_pos[1]), ball_radius, (1,1,1), True)
        
        # Desenha o placar
        draw_text(f"AZUL {score[0]} x {score[1]} VERMELHO", WIDTH//2-100, 20, 40)
        
        pygame.display.flip()

if __name__ == "__main__":
    main()