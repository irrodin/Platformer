import pygame
import random
import sys
import os

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Бесконечный платформер (исправленный)")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
PURPLE = (150, 50, 255)

# Шрифты
font_small = pygame.font.SysFont('Arial', 20)
font_large = pygame.font.SysFont('Arial', 40)

# Класс игрока
class Player:
    def __init__(self):
        self.width, self.height = 40, 60
        self.x, self.y = 100, HEIGHT - 200
        self.vel_y = 0
        self.speed = 6
        self.jump_power = -16
        self.gravity = 0.8
        self.is_jumping = False
        self.double_jump = False
        self.color = BLUE
        self.invincible = False
        self.invincible_timer = 0

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Глаза для визуализации
        eye_y = self.y + 15
        pygame.draw.circle(screen, WHITE, (self.x + 10, eye_y), 5)
        pygame.draw.circle(screen, WHITE, (self.x + 30, eye_y), 5)

    def update(self, platforms, enemies, bonuses, scroll_x):
        # Движение
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed

        # Гравитация
        self.vel_y += self.gravity
        self.y += self.vel_y

        # Проверка столкновений с платформами
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        on_ground = False
        
        for platform in platforms:
            platform_rect = platform["rect"]
            if player_rect.colliderect(platform_rect) and self.vel_y > 0:
                # Корректировка позиции игрока
                self.y = platform_rect.y - self.height
                self.vel_y = 0
                self.is_jumping = False
                self.double_jump = False
                on_ground = True
                
                # Особые платформы
                if platform["type"] == "trampoline":
                    self.vel_y = self.jump_power * 1.5
                elif platform["type"] == "breakable":
                    platforms.remove(platform)

        # Проверка столкновений с врагами
        if not self.invincible:
            for enemy in enemies[:]:
                if player_rect.colliderect(enemy["rect"]):
                    self.invincible = True
                    self.invincible_timer = 60  # 1 секунда неуязвимости
                    enemies.remove(enemy)
                    self.color = PURPLE  # Визуальный эффект
                    break

        # Проверка бонусов
        for bonus in bonuses[:]:
            if player_rect.colliderect(bonus["rect"]):
                if bonus["type"] == "jump":
                    self.double_jump = True
                elif bonus["type"] == "fly":
                    self.vel_y = self.jump_power * 0.7
                bonuses.remove(bonus)

        # Таймер неуязвимости
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.color = BLUE

        # Проверка смерти (падение или выход за экран)
        if self.y > HEIGHT or self.x < -50:
            return True
        return False

# Генерация платформ
def generate_platforms(last_x):
    platforms = []
    for _ in range(10):
        platform_type = random.choice(["normal", "moving", "breakable", "trampoline"])
        x = last_x + random.randint(100, 200)
        y = random.randint(HEIGHT - 250, HEIGHT - 50)
        width = random.randint(80, 150)
        
        if platform_type == "moving":
            color = PURPLE
            move_dir = random.choice([-1, 1])
        elif platform_type == "breakable":
            color = YELLOW
            move_dir = 0
        elif platform_type == "trampoline":
            color = (0, 200, 200)
            move_dir = 0
        else:
            color = GREEN
            move_dir = 0

        platforms.append({
            "rect": pygame.Rect(x, y, width, 20),
            "type": platform_type,
            "color": color,
            "move_dir": move_dir
        })
        last_x = x
    return platforms, last_x

# Генерация врагов
def generate_enemies(last_x):
    enemies = []
    if random.random() < 0.2:  # 20% шанс появления врага
        x = last_x + random.randint(300, 500)
        y = HEIGHT - 100 - random.randint(0, 200)
        enemies.append({
            "rect": pygame.Rect(x, y, 30, 30),
            "color": RED,
            "move_dir": random.choice([-1, 1])
        })
        last_x = x
    return enemies, last_x

# Генерация бонусов
def generate_bonuses(last_x):
    bonuses = []
    if random.random() < 0.15:  # 15% шанс бонуса
        x = last_x + random.randint(400, 600)
        y = HEIGHT - 150 - random.randint(0, 200)
        bonus_type = random.choice(["jump", "fly"])
        color = YELLOW if bonus_type == "jump" else (0, 200, 200)
        bonuses.append({
            "rect": pygame.Rect(x, y, 20, 20),
            "type": bonus_type,
            "color": color
        })
        last_x = x
    return bonuses, last_x

# Основной игровой цикл
def game_loop():
    player = Player()
    scroll_x = 0
    score = 0
    last_platform_x = 0
    last_enemy_x = 0
    last_bonus_x = 0

    platforms, last_platform_x = generate_platforms(last_platform_x)
    enemies, last_enemy_x = generate_enemies(last_enemy_x)
    bonuses, last_bonus_x = generate_bonuses(last_bonus_x)

    running = True
    while running:
        screen.fill(BLACK)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not player.is_jumping:
                        player.vel_y = player.jump_power
                        player.is_jumping = True
                    elif player.double_jump:
                        player.vel_y = player.jump_power * 0.8
                        player.double_jump = False

        # Обновление игрока
        is_dead = player.update(platforms, enemies, bonuses, scroll_x)
        if is_dead:
            return score

        # Генерация новых объектов
        if platforms[-1]["rect"].x < scroll_x + WIDTH + 200:
            new_platforms, last_platform_x = generate_platforms(last_platform_x)
            platforms.extend(new_platforms)
            
            new_enemies, last_enemy_x = generate_enemies(last_enemy_x)
            enemies.extend(new_enemies)
            
            new_bonuses, last_bonus_x = generate_bonuses(last_bonus_x)
            bonuses.extend(new_bonuses)

        # Удаление объектов за экраном
        platforms = [p for p in platforms if p["rect"].x > scroll_x - 200]
        enemies = [e for
