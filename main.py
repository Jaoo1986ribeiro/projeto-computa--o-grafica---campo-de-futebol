import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

def init():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluOrtho2D(0, display[0], display[1], 0)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def draw_circle(cx, cy, radius, filled=True):
    glBegin(GL_TRIANGLE_FAN if filled else GL_LINE_LOOP)
    for i in range(360):
        angle = math.radians(i)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        glVertex2f(x, y)
    glEnd()

def draw_rect(x, y, width, height, filled=False):
    if filled:
        glBegin(GL_QUADS)
    else:
        glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

def draw_text(text, x, y, size=30):
    font = pygame.font.SysFont('Arial', size, bold=True)
    text_surface = font.render(text, True, (255, 255, 255, 255))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(),
                GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def main():
    init()
    clock = pygame.time.Clock()
    
    # Configurações
    ball_pos = [400, 300]
    ball_vel = [0, 0]
    ball_radius = 12
    score = [0, 0]  # [Azul, Vermelho]
    
    # Gols visíveis (traves amarelas)
    goals = [
        {"x": 0, "y": 200, "width": 20, "height": 200, "team": "red"},    # Gol esquerdo
        {"x": 780, "y": 200, "width": 20, "height": 200, "team": "blue"}  # Gol direito
    ]
    
    # Campo principal
    field_left = 50
    field_right = 750
    field_top = 50
    field_bottom = 550
    
    # Jogadores
    players = [
        {"x": 200, "y": 300, "radius": 25, "color": (0, 0, 1)},
        {"x": 600, "y": 300, "radius": 25, "color": (1, 0, 0)}
    ]

    while True:
        dt = 0.016  # Delta time para 60FPS
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Controles
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]: ball_vel[0] = max(-15, ball_vel[0] - 0.7)
        if keys[K_RIGHT]: ball_vel[0] = min(15, ball_vel[0] + 0.7)
        if keys[K_UP]: ball_vel[1] = max(-15, ball_vel[1] - 0.7)
        if keys[K_DOWN]: ball_vel[1] = min(15, ball_vel[1] + 0.7)
        
        # Movimento
        ball_pos[0] += ball_vel[0]
        ball_pos[1] += ball_vel[1]
        ball_vel[0] *= 0.96
        ball_vel[1] *= 0.96
        
        # Colisão com bordas do campo
        if ball_pos[1] - ball_radius < field_top:  # Topo
            ball_pos[1] = field_top + ball_radius
            ball_vel[1] *= -0.8
        elif ball_pos[1] + ball_radius > field_bottom:  # Base
            ball_pos[1] = field_bottom - ball_radius
            ball_vel[1] *= -0.8
            
        # Verificação de GOL
        for goal in goals:
            if ((goal["x"] < ball_pos[0] < goal["x"] + goal["width"]) and 
                (goal["y"] < ball_pos[1] < goal["y"] + goal["height"])):
                
                if goal["team"] == "blue":
                    score[0] += 1
                else:
                    score[1] += 1
                
                # Reset com efeito
                ball_pos = [400, 300]
                ball_vel = [random.choice([-4,4]), random.uniform(-3,3)]
                break
        
        # Colisão lateral (exceto na área dos gols)
        if not (200 < ball_pos[1] < 400):  # Só colide fora da altura dos gols
            if ball_pos[0] - ball_radius < field_left:  # Esquerda
                ball_pos[0] = field_left + ball_radius
                ball_vel[0] *= -0.8
            elif ball_pos[0] + ball_radius > field_right:  # Direita
                ball_pos[0] = field_right - ball_radius
                ball_vel[0] *= -0.8
        
        # Colisão com jogadores
        for player in players:
            dx = ball_pos[0] - player["x"]
            dy = ball_pos[1] - player["y"]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < ball_radius + player["radius"]:
                angle = math.atan2(dy, dx)
                min_dist = ball_radius + player["radius"]
                ball_pos[0] = player["x"] + math.cos(angle) * min_dist
                ball_pos[1] = player["y"] + math.sin(angle) * min_dist
                speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2) * 1.2
                ball_vel[0] = math.cos(angle) * speed
                ball_vel[1] = math.sin(angle) * speed
        
        # Renderização
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Fundo
        glColor3f(0.2, 0.2, 0.2)
        draw_rect(0, 0, 800, 600, True)
        
        # Campo principal (gramado)
        glColor3f(0.1, 0.5, 0.1)
        draw_rect(field_left, field_top, field_right-field_left, field_bottom-field_top, True)
        
        # Linhas do campo
        glColor3f(1, 1, 1)
        draw_rect(field_left, field_top, field_right-field_left, field_bottom-field_top, False)
        glBegin(GL_LINES)
        glVertex2f(400, field_top)
        glVertex2f(400, field_bottom)
        glEnd()
        draw_circle(400, 300, 50, False)
        
        # Gols (traves amarelas - agora visíveis)
        glColor3f(1, 1, 0)
        for goal in goals:
            draw_rect(goal["x"], goal["y"], goal["width"], goal["height"], False)
        
        # Jogadores
        for player in players:
            glColor3fv(player["color"])
            draw_circle(player["x"], player["y"], player["radius"], True)
        
        # Bola
        glColor3f(1, 1, 1)
        draw_circle(ball_pos[0], ball_pos[1], ball_radius, True)
        
        # Placar corrigido (sem "AZULO")
        draw_text(f"AZUL {score[0]} x {score[1]} VERMELHO", 250, 20, 40)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()