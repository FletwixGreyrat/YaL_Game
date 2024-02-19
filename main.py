import os
import sys
import pygame
import random
import sqlite3

pygame.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

OBSTACLE_SIZE = 40

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Дино стычка")

score1 = 100000
score2 = 100000
winner = ''

in_menus = True
in_game = False
in_help = False
b_enter = False
in_win = False
level_menu = False
playlist = list()
playlist.append("music2_mastered.wav")
playlist.append("music1_mastered.wav")

pygame.mixer.music.load(playlist.pop())
pygame.mixer.music.queue(playlist.pop())
pygame.mixer.music.set_endevent(pygame.USEREVENT)
pygame.mixer.music.play(-1)


# класс препятствий
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (OBSTACLE_SIZE, OBSTACLE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))


# класс аптечки
class HealthPack(pygame.sprite.Sprite):
    def __init__(self, x, y, heal_amount):
        super().__init__()
        self.image = pygame.image.load("healme.png")
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.heal_amount = heal_amount


# базовый класс объекта
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y


# класс выстрела
class Bullet(Object):
    def __init__(self, x, y, direction):
        super().__init__(x, y)
        self.image = pygame.Surface((10, 5))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = direction

    def update(self):
        self.rect.x += bullet_speed if self.direction == "right" else -bullet_speed


# класс игрока
class Player(Object):
    def __init__(self, x, y, image, speed, direction):
        super().__init__(x, y)
        self.c_image = image
        self.image = pygame.transform.scale(image, (OBSTACLE_SIZE, OBSTACLE_SIZE))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.direction = direction
        self.hp = 100
        self.old_coor = (0, 0)

    def update(self):
        if self.direction == "left":
            self.image = pygame.transform.flip(pygame.transform.scale(self.c_image, (OBSTACLE_SIZE, OBSTACLE_SIZE)),
                                               True, False)
        else:
            self.image = pygame.transform.scale(self.c_image, (OBSTACLE_SIZE, OBSTACLE_SIZE))

    def death(self):
        for i in range(90):
            self.image = pygame.transform.rotate(self.image, 1)
            player_sprites.update()


# класс содержащий и отрисовывающий группы спрайтов
class World:
    def __init__(self):
        self.objects = []

    def add_object(self, ob):
        self.objects.append(ob)

    def get_objects(self):
        return self.objects

    def draw(self, scr):
        for i in self.objects:
            i.draw(scr)


# окно завершения игры
class Win:
    def __init__(self):
        self.option_menu = []
        self.callbacks = []
        self.tek_index = 0

    def add_option(self, option, callback):
        self.option_menu.append(option)
        self.callbacks.append(callback)

    def switch(self, direct: int):
        self.tek_index = max(0, min(self.tek_index + direct, len(self.option_menu) - 1))
        self.draw(screen)

    def select(self):
        self.callbacks[self.tek_index]()

    def draw(self, scr):
        global winner, score
        fon_img = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
        scr.blit(fon_img, (0, 0))
        font = pygame.font.Font(None, 100)
        text_coord = 200
        text = font.render(f"Очки: {score}", True, (255, 255, 255))
        text_y = 130
        screen.blit(text, (250, text_y))
        for i in range(len(self.option_menu)):
            line = self.option_menu[i]
            string_rendered = font.render(line, 1, pygame.Color('black'))
            text_coord += 10
            intro_rect = string_rendered.get_rect()
            intro_rect.top = text_coord
            intro_rect.x = 250
            text_coord += intro_rect.height

            if i == self.tek_index:
                pygame.draw.rect(scr, (255, 255, 255), intro_rect)

            scr.blit(string_rendered, intro_rect)


class LevelMenu:
    def __init__(self):
        self.option_menu = []
        self.callbacks = []
        self.tek_index = 0

    def add_option(self, option, callback):
        self.option_menu.append(option)
        self.callbacks.append(callback)

    def switch(self, direct: int):
        self.tek_index = max(0, min(self.tek_index + direct, len(self.option_menu) - 1))
        self.draw(screen)

    def select(self):
        self.callbacks[self.tek_index]()

    def draw(self, scr):
        global winner, score
        fon_img = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
        scr.blit(fon_img, (0, 0))
        font = pygame.font.Font(None, 100)
        text_coord = 200
        for i in range(len(self.option_menu)):
            line = self.option_menu[i]
            string_rendered = font.render(line, 1, pygame.Color('black'))
            text_coord += 10
            intro_rect = string_rendered.get_rect()
            intro_rect.top = text_coord
            intro_rect.x = 250
            text_coord += intro_rect.height

            if i == self.tek_index:
                pygame.draw.rect(scr, (255, 255, 255), intro_rect)

            scr.blit(string_rendered, intro_rect)


# окно справки
class Help:
    def __init__(self):
        self.option_menu = []

    def add_option(self, option):
        self.option_menu.append(option)

    def draw(self, scr):
        fon_img = pygame.transform.scale(load_image('Help.png'), (WIDTH, HEIGHT))
        scr.blit(fon_img, (0, 0))
        font = pygame.font.Font(None, 100)
        text_coord = 200
        for i in range(len(self.option_menu)):
            line = self.option_menu[i]
            string_rendered = font.render(line, 1, pygame.Color('black'))
            text_coord += 10
            intro_rect = string_rendered.get_rect()
            intro_rect.top = text_coord
            intro_rect.x = 100
            text_coord += intro_rect.height

            scr.blit(string_rendered, intro_rect)


# стартовое меню
class StartMenu:
    def __init__(self):
        self.option_menu = []
        self.callbacks = []
        self.tek_index = 0

    def add_option(self, option, callback):
        self.option_menu.append(option)
        self.callbacks.append(callback)

    def switch(self, direct: int):
        self.tek_index = max(0, min(self.tek_index + direct, len(self.option_menu) - 1))
        self.draw(screen)

    def select(self):
        self.callbacks[self.tek_index]()

    def draw(self, scr):
        fon_img = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
        scr.blit(fon_img, (0, 0))
        font = pygame.font.Font(None, 100)
        text_coord = 200
        for i in range(len(self.option_menu)):
            line = self.option_menu[i]
            string_rendered = font.render(line, 1, pygame.Color('black'))
            text_coord += 10
            intro_rect = string_rendered.get_rect()
            intro_rect.top = text_coord
            intro_rect.x = 250
            text_coord += intro_rect.height

            if i == self.tek_index:
                pygame.draw.rect(scr, (255, 255, 255), intro_rect)

            scr.blit(string_rendered, intro_rect)


# загрузка изображения
def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
    if colorkey == -1:
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# функция загрузки уровней
def load_level(file_path):
    ob = []
    with open(file_path, "r") as file:
        for line in file:
            ob.append(list(line.strip()))
    return ob


# запуск игры
def start_game():
    screen.fill(WHITE)
    update_pole()
    global in_menus, in_game, in_help, in_win, level_menu
    in_menus = False
    in_game = True
    in_win = False
    in_help = False
    level_menu = False


def show_help():
    screen.fill(WHITE)
    global in_menus, in_game, in_help, in_win, b_enter, level_menu
    in_menus = False
    b_enter = False
    in_game = False
    in_help = True
    in_win = False
    level_menu = False
    help_window.draw(screen)


def win_menu():
    screen.fill(WHITE)
    global in_menus, in_game, in_help, in_win, b_enter, level_menu
    in_menus = False
    in_game = False
    in_win = True
    in_help = False
    b_enter = False
    level_menu = False
    win_men.draw(screen)


def exit_game():
    global in_menus, in_game, in_help, b_enter, in_win, level_menu
    in_menus = True
    in_game = False
    b_enter = False
    in_win = False
    in_help = False
    level_menu = False
    start_menu.draw(screen)


def level_menu_start():
    screen.fill(WHITE)
    global in_menus, in_game, in_help, in_win, b_enter, level_menu
    in_menus = False
    b_enter = False
    in_game = False
    in_help = False
    in_win = False
    level_menu = True
    level_men.draw(screen)


# получение объектов из карты
def create_level(ob):
    player1_start, player2_start = None, None

    for row_index, row in enumerate(ob):
        for col_index, cell in enumerate(row):
            x, y = col_index * OBSTACLE_SIZE, row_index * OBSTACLE_SIZE
            if cell == '#':
                obstacle = Obstacle(x, y, pygame.image.load("level.jpg"))  # Замените "wall.png" на ваш файл с
                # текстурой стены
                level_group.add(obstacle)
            elif cell == '@':
                if player1_start is None:
                    player1_start = (x, y)
                else:
                    player2_start = (x, y)
            elif cell == 'H':
                health_p = HealthPack(x, y, heal_amount=20)
                health_packs_group.add(health_p)

    return player1_start, player2_start


# генерация аптечек
def generate_health_pack():
    x = random.randrange(0, WIDTH - OBSTACLE_SIZE, OBSTACLE_SIZE)
    y = random.randrange(0, HEIGHT - OBSTACLE_SIZE, OBSTACLE_SIZE)

    # Удаляем все текущие аптечки
    health_packs_group.empty()

    # Проверка, что аптечка не пересекается с препятствиями и игроками
    colliding_sprites = pygame.sprite.spritecollide(HealthPack(x, y, 0), level_group, False)
    colliding_sprites.extend(pygame.sprite.spritecollide(HealthPack(x, y, 0), player_sprites, False))

    while colliding_sprites:
        x = random.randrange(0, WIDTH - OBSTACLE_SIZE, OBSTACLE_SIZE)
        y = random.randrange(0, HEIGHT - OBSTACLE_SIZE, OBSTACLE_SIZE)
        colliding_sprites = pygame.sprite.spritecollide(HealthPack(x, y, 0), level_group, False)
        colliding_sprites.extend(pygame.sprite.spritecollide(HealthPack(x, y, 0), player_sprites, False))

    health_p = HealthPack(x, y, heal_amount=20)
    health_packs_group.add(health_p)


# обновление поля
def update_pole():
    bullet_sprites.empty()

    ob = load_level(random.choice(['level.txt', 'level1.txt', 'level2.txt', 'level3.txt']))
    level_group.empty()
    health_packs_group.empty()
    player1_start, player2_start = create_level(ob)
    player1.rect.topleft = player1_start
    player1.old_coor = player1_start
    player2.rect.topleft = player2_start
    player2.old_coor = player2_start
    player1.hp = 100
    player2.hp = 100


# создание меню
start_menu = StartMenu()
start_menu.add_option("Играть", level_menu_start)
start_menu.add_option("Справка", show_help)
start_menu.draw(screen)

# окно справки
help_window = Help()

# создание меню окончания игры
win_men = Win()
win_men.add_option("Начать заново", level_menu_start)
win_men.add_option("Выход", exit_game)
bullet_speed = 10

# текстур
player1_image = pygame.image.load("dino_up.png")
player2_image = pygame.image.load("dino_up_2.png")

level_men = LevelMenu()
level_men.add_option('level.txt', start_game)
level_men.add_option('level1.txt', start_game)
level_men.add_option('level2.txt', start_game)
level_men.add_option('level3.txt', start_game)

# создание групп спрайтов
player_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()
level_group = pygame.sprite.Group()
health_packs_group = pygame.sprite.Group()

# создание игроков
player1 = Player(50, HEIGHT // 2 - OBSTACLE_SIZE // 2, player1_image, 2, "right")
player2 = Player(WIDTH - 100, HEIGHT // 2 - OBSTACLE_SIZE // 2, player2_image, 2, "left")
player_sprites.add(player1, player2)

# создание и заполнение класса World, содержащего и отрисовывающего группы спрайтов
world = World()
world.add_object(player_sprites)
world.add_object(bullet_sprites)
world.add_object(level_group)
world.add_object(health_packs_group)

# настройки здоровья
health_bar_width = 50
health_bar_height = 5
health_bar_offset = 20

# Интервал появления аптечек
HEALTH_PACK_INTERVAL_MIN = 30000  # 30 секунд
HEALTH_PACK_INTERVAL_MAX = 45000  # 45 секунд
next_health_pack_time = pygame.time.get_ticks() + random.randint(HEALTH_PACK_INTERVAL_MIN, HEALTH_PACK_INTERVAL_MAX)
# игровой цикл
while True:
    # проверка условий
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if len(playlist) > 1:
                pygame.mixer.music.queue(playlist.pop())
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # выбор компонента в меню
        if in_menus and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                start_menu.switch(1)
            elif event.key == pygame.K_UP:
                start_menu.switch(-1)
            elif event.key == pygame.K_RETURN:
                start_menu.select()

        # выбор компонента в меню окончания игры
        if in_win and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                win_men.switch(1)
            elif event.key == pygame.K_UP:
                win_men.switch(-1)
            elif event.key == pygame.K_RETURN and not b_enter:
                win_men.select()

        if level_menu and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                level_men.switch(1)
            elif event.key == pygame.K_UP:
                level_men.switch(-1)
            elif event.key == pygame.K_RETURN and not b_enter:
                level_men.select()

        # переход в главное меню при нажатии ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            exit_game()
        # фиксит баг с выстрелом
        if event.type == pygame.KEYUP and event.key == pygame.K_RETURN and in_game:
            b_enter = True

        # создание выстрелов
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and in_game:
                bullet = Bullet(
                    player1.rect.x + player1.rect.width if player1.direction == "right" else player1.rect.x - 10,
                    player1.rect.y + player1.rect.height // 2 - 2, player1.direction)
                bullet_sprites.add(bullet)
                pygame.mixer.Sound('выстрел.wav').play()

            if event.key == pygame.K_RETURN and b_enter:
                bullet = Bullet(
                    player2.rect.x + player2.rect.width if player2.direction == "right" else player2.rect.x - 10,
                    player2.rect.y + player2.rect.height // 2 - 2, player2.direction)
                bullet_sprites.add(bullet)
                pygame.mixer.Sound('выстрел.wav').play()

    if in_game:
        # движение персонажей
        keys = pygame.key.get_pressed()
        if not pygame.sprite.spritecollide(player1, level_group, False):
            player1.old_coor = player1.rect.topleft
            if keys[pygame.K_w] and player1.rect.top > 0:
                player1.rect.y -= player1.speed
            if keys[pygame.K_s] and player1.rect.bottom < HEIGHT:
                player1.rect.y += player1.speed
            if keys[pygame.K_a] and player1.rect.left > 0:
                player1.rect.x -= player1.speed
                player1.direction = "left"
            if keys[pygame.K_d] and player1.rect.right < WIDTH:
                player1.rect.x += player1.speed
                player1.direction = "right"
        else:
            player1.rect.topleft = player1.old_coor
        if not pygame.sprite.spritecollide(player2, level_group, False):
            player2.old_coor = player2.rect.topleft
            if keys[pygame.K_UP] and player2.rect.top > 0:
                player2.rect.y -= player2.speed
            if keys[pygame.K_DOWN] and player2.rect.bottom < HEIGHT:
                player2.rect.y += player2.speed
            if keys[pygame.K_LEFT] and player2.rect.left > 0:
                player2.rect.x -= player2.speed
                player2.direction = "left"
            if keys[pygame.K_RIGHT] and player2.rect.right < WIDTH:
                player2.rect.x += player2.speed
                player2.direction = "right"
        else:
            player2.rect.topleft = player2.old_coor

        # Обновление позиций и состояний всех спрайтов
        player_sprites.update()
        bullet_sprites.update()
        level_group.update()
        health_packs_group.update()

        # удаление пуль при контакте со стенами
        bullet_hits_level = pygame.sprite.groupcollide(bullet_sprites, level_group, True, False)
        for bullet, level in bullet_hits_level.items():
            pygame.mixer.Sound('bullethit.mp3').play()
            bullet.kill()  # Удаляем пулю

        # проверка столкновений с пулями
        bullet_hits_player1 = pygame.sprite.spritecollide(player1, bullet_sprites, True)
        bullet_hits_player2 = pygame.sprite.spritecollide(player2, bullet_sprites, True)
        if bullet_hits_player1:
            player1.hp -= 10
            pygame.mixer.Sound('bullethitflesh.mp3').play()
            if player1.hp <= 0:
                player1.death()
                score = score2
                pygame.mixer.Sound('death.mp3').play()
                winner = 'Второй'
                in_game = False
                con = sqlite3.connect('scores.sqlite')
                cur = con.cursor()
                cur.execute(f"""INSERT INTO scores(winner, score) VALUES('{winner}', {score})""").fetchall()
                con.commit()
                player1.death()
                winner = ''
        if bullet_hits_player2:
            player2.hp -= 10
            pygame.mixer.Sound('bullethitflesh.mp3').play()
            if player2.hp <= 0:
                player1.death()
                score = score1
                pygame.mixer.Sound('death.mp3').play()
                winner = 'Первый'
                in_game = False
                con = sqlite3.connect('scores.sqlite')
                cur = con.cursor()
                cur.execute(f"""INSERT INTO scores(winner, score) VALUES('{winner}', {score})""").fetchall()
                con.commit()
                player2.death()
                winner = ''

        # Проверка на столкновение с аптечкой
        health_pack_hits_player1 = pygame.sprite.spritecollide(player1, health_packs_group, True)
        health_pack_hits_player2 = pygame.sprite.spritecollide(player2, health_packs_group, True)

        for health_pack_hits_player in [health_pack_hits_player1, health_pack_hits_player2]:
            for health_pack in health_pack_hits_player:
                # Восстановление здоровья и удаление аптечки
                if health_pack_hits_player is health_pack_hits_player1:
                    player1.hp = min(100, player1.hp + health_pack.heal_amount)
                    score1 += 1000
                elif health_pack_hits_player is health_pack_hits_player2:
                    player2.hp = min(100, player2.hp + health_pack.heal_amount)
                    score2 += 1000

        # Генерация аптечек
        current_time = pygame.time.get_ticks()
        if current_time >= next_health_pack_time:
            generate_health_pack()
            next_health_pack_time = current_time + random.randint(HEALTH_PACK_INTERVAL_MIN, HEALTH_PACK_INTERVAL_MAX)

        # Отрисовка фона и всех спрайтов
        screen.fill(WHITE)
        world.draw(screen)

        for player, player_health in [(player1, player1.hp), (player2, player2.hp)]:
            pygame.draw.rect(screen, GREEN,
                             (player.rect.x, player.rect.y - health_bar_offset, player_health / 100 * player.rect.width,
                              health_bar_height))

    if not in_game and not in_menus and not in_help and not level_menu:
        win_menu()

    pygame.display.flip()
    pygame.time.Clock().tick(60)

    score1 -= 10
    score2 -= 10