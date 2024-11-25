import pygame
import sys
import random
from pygame.locals import *

# Inicialización de Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 1024, 768
player_speed = 5
bullet_speed = 7
enemy_speed = 2
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Constantes de márgenes
MARGIN_TOP = 80
MARGIN_SIDE = 20
MARGIN_BOTTOM = 20

# Configuración de la pantalla
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Invaders')

# Cargar imágenes PNG con canal Alpha
player_img = pygame.image.load('player.png').convert_alpha()
enemy_img = pygame.image.load('enemy.png').convert_alpha()

# Verificar si las imágenes tienen canal Alpha
if player_img.get_alpha() is None:
    print("Advertencia: La imagen del jugador no tiene canal Alpha.")
if enemy_img.get_alpha() is None:
    print("Advertencia: La imagen del enemigo no tiene canal Alpha.")

# Posiciones iniciales
player_pos = [WIDTH // 2, HEIGHT - MARGIN_BOTTOM - 128]
bullet_list = []
enemy_list = []

# Variables de juego
runing = False
lives = 3
score = 0

# Variables de movimiento de enemigos
enemy_direction = 1
enemy_drop = 10

# Lista de disparos enemigos
enemy_bullet_list = []
enemy_bullet_speed = 5
enemy_shoot_event = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_shoot_event, 2000)

# Inicializar enemigos en formación
def initialize_enemies():
    """
    Inicializa los enemigos en una formación de 5 filas por 8 columnas.
    """
    for row in range(4):
        for col in range(8):
            x = MARGIN_SIDE + col * (enemy_img.get_width() * 1.5)
            y = MARGIN_TOP + row * (enemy_img.get_height() * 1.5)
            enemy_list.append([x, y])

def handle_events():
    """
    Maneja los eventos de entrada del usuario.
    """
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                if len(bullet_list) < 2:
                    bullet_list.append([player_pos[0] + player_img.get_width() // 2, player_pos[1]])
        if event.type == enemy_shoot_event:
            if enemy_list:
                shooter = random.choice(enemy_list)
                enemy_bullet_list.append([shooter[0] + enemy_img.get_width() // 2, shooter[1] + enemy_img.get_height()])

def move_bullets():
    """
    Mueve las balas hacia arriba y las elimina si salen de la pantalla.
    """
    for bullet in bullet_list[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullet_list.remove(bullet)

def move_enemy_bullets():
    """
    Mueve las balas enemigas hacia abajo y las elimina si salen de la pantalla.
    """
    for bullet in enemy_bullet_list[:]:
        bullet[1] += enemy_bullet_speed
        if bullet[1] > HEIGHT:
            enemy_bullet_list.remove(bullet)

def move_player():
    """
    Mueve al jugador a la izquierda o derecha según la entrada del usuario.
    """
    keys = pygame.key.get_pressed()
    if keys[K_LEFT] and player_pos[0] > MARGIN_SIDE:
        player_pos[0] -= player_speed
    if keys[K_RIGHT] and player_pos[0] < WIDTH - MARGIN_SIDE - player_img.get_width():
        player_pos[0] += player_speed

def move_enemies():
    """
    Mueve a los enemigos lateralmente y los hace descender cuando alcanzan un borde.
    """
    global enemy_direction
    edge_reached = False
    for enemy in enemy_list:
        enemy[0] += enemy_speed * enemy_direction
        if enemy[0] <= MARGIN_SIDE or enemy[0] >= WIDTH - MARGIN_SIDE - enemy_img.get_width():
            edge_reached = True

    if edge_reached:
        enemy_direction *= -1
        for enemy in enemy_list:
            enemy[1] += enemy_drop

def reset_enemies():
    """
    Reinicia la posición de los enemigos.
    """
    enemy_list.clear()
    initialize_enemies()

def check_collisions():
    """
    Verifica las colisiones entre balas y enemigos, y entre enemigos y el jugador.
    """
    global score, lives
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_img.get_width(), player_img.get_height())
    for bullet in bullet_list[:]:
        bullet_rect = pygame.Rect(bullet[0], bullet[1], 5, 10)
        for enemy in enemy_list[:]:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_img.get_width(), enemy_img.get_height())
            if bullet_rect.colliderect(enemy_rect):
                bullet_list.remove(bullet)
                enemy_list.remove(enemy)
                score += 25
                break
    for enemy in enemy_list[:]:
        enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_img.get_width(), enemy_img.get_height())
        if enemy_rect.colliderect(player_rect):
            lives -= 1
            reset_enemies()
            if lives <= 0:
                game_over()
    for bullet in enemy_bullet_list[:]:
        bullet_rect = pygame.Rect(bullet[0], bullet[1], 5, 10)
        if bullet_rect.colliderect(player_rect):
            enemy_bullet_list.remove(bullet)
            lives -= 1
            if lives <= 0:
                game_over()
    if not enemy_list:
        level_complete()

def level_complete():
    """
    Muestra el mensaje de nivel completado y espera a que el usuario presione Enter para continuar.
    """
    font = pygame.font.Font(None, 74)
    level_complete_text = font.render('¡Nivel Completado!', True, WHITE)
    continue_text = font.render('Presiona Enter para continuar', True, WHITE)
    screen.blit(level_complete_text, (WIDTH // 2 - level_complete_text.get_width() // 2, HEIGHT // 2 - level_complete_text.get_height() // 2))
    screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    wait_for_continue()

def wait_for_continue():
    """
    Espera a que el usuario presione Enter para continuar al siguiente nivel.
    """
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:
                reset_enemies()
                return

def game_over():
    """
    Muestra el mensaje de "GAME OVER" y espera a que el usuario presione 'R' para reiniciar.
    """
    global runing
    runing = False
    font = pygame.font.Font(None, 74)
    game_over_text = font.render('GAME OVER', True, WHITE)
    restart_text = font.render('Press R to Restart', True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    wait_for_restart()

def wait_for_restart():
    """
    Espera a que el usuario presione 'R' para reiniciar el juego.
    """
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_r:
                reset_game()
                return

def reset_game():
    """
    Reinicia el juego estableciendo las variables y listas a sus valores iniciales.
    """
    global lives, score, player_pos, bullet_list, enemy_list, enemy_bullet_list, runing
    lives = 3
    score = 0
    player_pos = [WIDTH // 2, HEIGHT - MARGIN_BOTTOM - 128]
    bullet_list = []
    enemy_list = []
    enemy_bullet_list = []
    initialize_enemies()
    runing = True
    game_loop()

def main():
    """
    Función principal que inicializa las variables y comienza el bucle del juego.
    """
    reset_game()

def render():
    """
    Renderiza todos los elementos en la pantalla.
    """
    screen.fill(BLACK)
    screen.blit(player_img, player_pos)  # Renderiza la imagen del jugador con transparencia
    for enemy in enemy_list:
        screen.blit(enemy_img, enemy)  # Renderiza la imagen del enemigo con transparencia
    for bullet in bullet_list:
        pygame.draw.rect(screen, (0,255,0), pygame.Rect(bullet[0], bullet[1], 5, 10))
    for bullet in enemy_bullet_list:
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(bullet[0], bullet[1], 10, 20))  # Disparo enemigo en rojo
    font = pygame.font.Font(None, 36)
    lives_text = font.render(f'Vidas: {lives}', True, WHITE)
    score_text = font.render(f'Puntos: {score}', True, WHITE)
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (400, 10))
    pygame.display.flip()

def game_loop():
    """
    Bucle principal del juego.
    """
    clock = pygame.time.Clock()
    while runing:
        handle_events()
        move_bullets()
        move_enemy_bullets()
        move_player()
        move_enemies()
        check_collisions()
        render()
        clock.tick(60)
    print("Fin del juego.")

if __name__ == "__main__":
    main()