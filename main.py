import pygame
import os
import random

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Space Shooter")

# Load images
# Enemy ships
red_spaceship = pygame.image.load(os.path.join("assets", "alien_spider.png"))
crab_alien_1 = pygame.image.load(os.path.join("assets", "alien_crab_1.png"))
crab_alien_2 = pygame.image.load(os.path.join("assets", "alien_crab_2.png"))
blue_spaceship = pygame.image.load(os.path.join("assets", "alien_small.png"))
big_alien = pygame.image.load(os.path.join("assets", "alien_big.png"))
boss_alien_head = pygame.image.load(os.path.join("assets", "alien_boss_head.png"))
boss_alien_body = pygame.image.load(os.path.join("assets", "alien_boss_body.png"))
boss_alien_left = pygame.image.load(os.path.join("assets", "alien_boss_left.png"))
boss_alien_right = pygame.image.load(os.path.join("assets", "alien_boss_right.png"))

# Player ship
player_spaceship = pygame.image.load(os.path.join("assets", "ship_player_2.png"))

# Lasers
player_laser = [pygame.image.load(i) for i in
                [os.path.join("assets", "sprite_fire", f"hadouken_{i}.png") for i in range(1, 9)]]
alien_laser = [pygame.image.load(os.path.join("assets", "sprite_laser", "laser_01.png")),
               pygame.image.load(os.path.join("assets", "sprite_laser", "laser_02.png")),
               pygame.image.load(os.path.join("assets", "sprite_laser", "laser_03.png")),
               pygame.image.load(os.path.join("assets", "sprite_laser", "laser_04.png")),
               pygame.image.load(os.path.join("assets", "sprite_laser", "laser_05.png")),
               pygame.image.load(os.path.join("assets", "sprite_laser", "laser_06.png")),
               pygame.image.load(os.path.join("assets", "sprite_laser", "laser_07.png")),
               pygame.image.load(os.path.join("assets", "sprite_laser", "laser_08.png")),
               pygame.image.load(os.path.join("assets", "sprite_laser", "laser_09.png")),
               pygame.image.load(os.path.join("assets", "sprite_laser", "laser_10.png"))]

# Explosion animation sprite
explosion_sprite = [pygame.image.load(os.path.join("assets", "sprite_explosion", "explosion_01.png")),
                    pygame.image.load(os.path.join("assets", "sprite_explosion", "explosion_02.png")),
                    pygame.image.load(os.path.join("assets", "sprite_explosion", "explosion_03.png")),
                    pygame.image.load(os.path.join("assets", "sprite_explosion", "explosion_04.png")),
                    pygame.image.load(os.path.join("assets", "sprite_explosion", "explosion_05.png")),
                    pygame.image.load(os.path.join("assets", "sprite_explosion", "explosion_06.png")),
                    pygame.image.load(os.path.join("assets", "sprite_explosion", "explosion_07.png")),
                    pygame.image.load(os.path.join("assets", "sprite_explosion", "explosion_08.png")),
                    pygame.image.load(os.path.join("assets", "sprite_explosion", "explosion_09.png")),
                    pygame.image.load(os.path.join("assets", "sprite_explosion", "explosion_10.png"))]
# Healing kit
heal_sprite = [pygame.image.load(os.path.join("assets", "sprite_heal", "heal_1.png")),
               pygame.image.load(os.path.join("assets", "sprite_heal", "heal_2.png")),
               pygame.image.load(os.path.join("assets", "sprite_heal", "heal_3.png")),
               pygame.image.load(os.path.join("assets", "sprite_heal", "heal_4.png")),
               pygame.image.load(os.path.join("assets", "sprite_heal", "heal_5.png")),
               pygame.image.load(os.path.join("assets", "sprite_heal", "heal_6.png")),
               pygame.image.load(os.path.join("assets", "sprite_heal", "heal_7.png")),
               pygame.image.load(os.path.join("assets", "sprite_heal", "heal_8.png"))]

# Background & Main Menu
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-nebula.png")), (WIDTH, HEIGHT))
MM = pygame.transform.scale(pygame.image.load(os.path.join("assets", "main_menu.png")), (WIDTH, HEIGHT))
EARTH = pygame.transform.scale(pygame.image.load(os.path.join("assets", "ship_base.png")), (WIDTH, HEIGHT))

# Sounds
fanfare_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "NFF-bravo.wav"))
explode_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "NFF-explode.wav"))
collide_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "NFF-dry-punch.wav"))
laser_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "NFF-laser.wav"))
hit_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "NFF-laser-collide.wav"))
alien_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "NFF-alien-hit.wav"))
destroy_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "NFF-dirt-hit.wav"))
heal_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "NFF-bubbling.wav"))
victory_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "chipquest.wav"))


# Objects
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.images = img  # list of images
        self.index = 0
        self.mask = pygame.mask.from_surface(self.images[self.index])

    def draw(self, window):
        window.blit(self.images[self.index // 4], (self.x, self.y))
        self.index += 1
        if self.index >= len(self.images) * 4:
            self.index = 0

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0  # cool-down for shooting

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):  # checks if lasers shot by enemies hit the player
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                pygame.mixer.Sound.play(hit_sound)
                obj.health -= 5
                obj.damage = True
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            pygame.mixer.Sound.play(laser_sound)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def double_shoot(self):
        if self.cool_down_counter == 0:
            pygame.mixer.Sound.play(laser_sound)
            laser1 = Laser(self.x + 20, self.y, self.laser_img)
            laser2 = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser1)
            self.lasers.append(laser2)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = player_spaceship
        self.laser_img = player_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.kills = []
        self.damage = False
        self.damage_count = 0

    # control lasers shot by player and hitting an enemy
    def move_lasers(self, vel, objects):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objects:
                    if laser.collision(obj):
                        obj.health -= 10
                        pygame.mixer.Sound.play(alien_sound)
                        if obj.health > 0 and obj.ship_img == crab_alien_1:
                            obj.ship_img = crab_alien_2
                        if obj.health <= 0:
                            pygame.mixer.Sound.play(destroy_sound)
                            self.kills.append(DeadEnemy(obj.x, obj.y, obj.health))
                            objects.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        # Damage animation collide with enemies
        if self.damage:
            self.ship_img = change_color(self.ship_img, (255, 0, 0))
            self.damage_count += 1
        if self.damage_count > 20:
            self.ship_img = player_spaceship
            self.damage = False
            self.damage_count = 0
        # Draw health bar
        self.healthbar(window)
        # Draw enemies exploding
        for dead_enemy in self.kills:
            window.blit(dead_enemy.explosion_img[dead_enemy.index // 4], (dead_enemy.x - 50, dead_enemy.y - 50))
            dead_enemy.index += 1
            if dead_enemy.index >= len(dead_enemy.explosion_img) * 4:
                dead_enemy.index = 0
                self.kills.remove(dead_enemy)

    def healthbar(self, window):
        pygame.draw.rect(
            window, (255, 255, 255), (self.x, self.y + self.ship_img.get_height() - 10,
                                      self.ship_img.get_width(), 12))
        pygame.draw.rect(
            window, (255, 0, 0), (self.x + 2, self.y + self.ship_img.get_height() - 8,
                                  self.ship_img.get_width() - 4, 8))
        pygame.draw.rect(
            window, (0, 255, 0), (self.x + 2, self.y + self.ship_img.get_height() - 8,
                                  (self.ship_img.get_width() - 4) * (self.health / self.max_health), 8))


class Enemy(Ship):
    COLOR_MAP = {
        "spider": (red_spaceship, alien_laser, 10),
        "crab": (crab_alien_1, alien_laser, 20),
        "small": (blue_spaceship, alien_laser, 10),
        "big": (big_alien, alien_laser, 50),
        "boss_head": (boss_alien_head, alien_laser, 200),
        "boss_body": (boss_alien_body, alien_laser, 240),
        "boss_left": (boss_alien_left, alien_laser, 160),
        "boss_right": (boss_alien_right, alien_laser, 160)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img, self.health = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def double_shoot(self):
        if self.cool_down_counter == 0:
            laser1 = Laser(self.x + 50, self.y, self.laser_img)
            laser2 = Laser(self.x - 25, self.y, self.laser_img)
            self.lasers.append(laser1)
            self.lasers.append(laser2)
            self.cool_down_counter = 1

    def draw(self, window):
        super().draw(window)


class DeadEnemy:
    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.health = health
        self.explosion = False
        self.explosion_img = explosion_sprite
        self.index = 0

    def draw(self, window):
        if self.explosion:
            window.blit(self.explosion_img[self.index // 4], (self.x - 50, self.y - 50))
            self.index += 1
            if self.index >= len(self.explosion_img) * 4:
                self.index = 0

    def explode(self):
        if self.health <= 0:
            self.explosion = True


class Medkit:
    def __init__(self, x, y, heal):
        self.x = x
        self.y = y
        self.heal = heal
        self.images = heal_sprite
        self.index = 0
        self.mask = pygame.mask.from_surface(self.images[self.index])

    def move(self, vel):
        self.y += vel

    def draw(self, window):
        window.blit(self.images[self.index // 4], (self.x, self.y))
        self.index += 1
        if self.index >= len(self.images) * 4:
            self.index = 0


# Collide: Function to determine overlapping of lasers with objects
def collide(obj1, obj2):
    offset_x = int(obj2.x - obj1.x)
    offset_y = int(obj2.y - obj1.y)
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


# Function to change color
def change_color(image, color):
    colouredImage = pygame.Surface(image.get_size())
    colouredImage.fill(color)

    finalImage = image.copy()
    finalImage.blit(colouredImage, (0, 0), special_flags=pygame.BLEND_MULT)
    return finalImage


# Button maker function
def button(msg, x, y, width, height, icolor, acolor, action=None):
    small_font = pygame.font.Font(os.path.join("assets", "slkscr.ttf"), 20)
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(WIN, acolor, (x, y, width, height))
        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(WIN, icolor, (x, y, width, height))
    button_label = small_font.render(msg, True, (0, 0, 0))
    text_center = (x + width / 2 - button_label.get_width() / 2, y + height / 2 - button_label.get_height() / 2)
    WIN.blit(button_label, text_center)


# Main menu
def main_menu():
    pygame.mixer.music.load(os.path.join("assets", "sounds", "a_bit_of_hope.mp3"))
    pygame.mixer.music.play(-1)
    pygame.mouse.set_visible(True)
    run = True
    while run:
        WIN.blit(MM, (0, 0))
        button("Start", WIDTH / 2 - 50, 500, 100, 50, (255, 255, 255), (0, 255, 0), main)
        button("Quit", WIDTH / 2 - 50, 580, 100, 50, (255, 255, 255), (0, 255, 0), quitgame)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    pygame.quit()


# Quit Game
def quitgame():
    pygame.quit()
    quit()


# Pause Game
pause = False


def paused():
    global pause
    pause = True
    pygame.mouse.set_visible(True)
    pygame.mixer.music.pause()
    large_font = pygame.font.Font(os.path.join("assets", "slkscr.ttf"), 40)
    pause_label = large_font.render("Game Paused...", True, (255, 255, 255))
    WIN.blit(pause_label, (WIDTH / 2 - pause_label.get_width() / 2, 300))
    while pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        button("Continue", WIDTH / 2 - 60, 400, 120, 50, (255, 255, 255), (0, 255, 0), unpause)
        button("Quit", WIDTH / 2 - 60, 500, 120, 50, (255, 255, 255), (0, 255, 0), quitgame)
        pygame.display.update()


# Unpause Game
def unpause():
    global pause
    pygame.mixer.music.unpause()
    pygame.mouse.set_visible(False)
    pause = False


# Main Loop
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    # Fonts
    main_font = pygame.font.Font(os.path.join("assets", "slkscr.ttf"), 25)
    lost_font = pygame.font.Font(os.path.join("assets", "slkscr.ttf"), 40)
    # Background initial positions
    BGY1 = 0
    BGY2 = -BG.get_height()
    # Enemies to store where enemies are
    enemies = []
    boss_parts = []
    wave_length = 5
    enemy_vel = 1
    # define velocities
    player_vel = 7
    player_laser_vel = 10
    laser_vel = 7
    # Player starting position
    player = Player(WIDTH / 2 - 50, HEIGHT - 150)
    # Make list of med kits
    med_kits = []
    # Sound
    pygame.mixer.music.load(os.path.join("assets", "sounds", "retro_funk_short.ogg"))
    pygame.mixer.music.play(-1)
    # Clock
    clock = pygame.time.Clock()
    # Lost variables
    lost = False
    lost_count = 0
    # Level display
    time_to_blit = False
    blit_time = 0
    # Hide the mouse cursor
    pygame.mouse.set_visible(False)
    # Final Battle
    final_battle = False

    def redraw_window():  # can only be called inside of main function
        # Background
        WIN.blit(BG, (0, BGY1))
        WIN.blit(BG, (0, BGY2))
        WIN.blit(EARTH, (0, HEIGHT - EARTH.get_height()))

        # Draw enemies
        for enemy in enemies:
            enemy.draw(WIN)
        for part in boss_parts:
            part.draw(WIN)

        # Draw player
        player.draw(WIN)

        # Draw Med kits
        for med_kit in med_kits:
            med_kit.draw(WIN)

        # Draw text
        lives_label = main_font.render(f"Lives: {lives}", True, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", True, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # Display Level Title
        if time_to_blit:
            level_label = lost_font.render(f"Level: {level}", True, (255, 255, 255))
            pygame.draw.rect(WIN, (0, 0, 0), (0, 300, WIDTH, 100 + level_label.get_height()))
            WIN.blit(level_label, (WIDTH / 2 - level_label.get_width() / 2, 350))
            if level == 4:
                bonus_label = main_font.render("+ Double-shoot!", True, (255, 255, 255))
                WIN.blit(bonus_label, (WIDTH / 2 - bonus_label.get_width() / 2, 390))
            if level == 8:
                bonus_label = main_font.render("Final battle!", True, (255, 255, 255))
                WIN.blit(bonus_label, (WIDTH / 2 - bonus_label.get_width() / 2, 390))

        # Draw Game Over
        if lost:
            lost_label = lost_font.render("Game Over", True, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))
            pygame.mouse.set_visible(True)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        # Losing
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS * 5:
                run = False
                pygame.mixer.music.load(os.path.join("assets", "sounds", "a_bit_of_hope.mp3"))
                pygame.mixer.music.play(-1)
            else:
                continue

        # Move Background
        BGY1 += 2.5
        BGY2 += 2.5
        if BGY1 > BG.get_height():
            BGY1 = -BG.get_height()
        if BGY2 > BG.get_height():
            BGY2 = -BG.get_height()

        # Making a new level
        if len(enemies) == 0 and level < 8:
            level += 1
            # Call display level title
            time_to_blit = True

            # Sound of finishing level
            pygame.mixer.music.stop()
            pygame.mixer.Sound.play(fanfare_sound)
            pygame.mixer.music.play(-1)

            # Create new wave of enemies
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["spider", "crab", "small"]))
                enemies.append(enemy)
            if level >= 3:
                for i in range(level - 2):
                    big = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), "big")
                    enemies.append(big)

            # Create Med kit if player is hurt
            if player.health <= player.max_health / 2:
                med_kit = Medkit(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), 30)
                med_kits.append(med_kit)

        if len(enemies) == 0 and len(boss_parts) == 0 and level == 8 and not final_battle:
            pygame.mixer.music.load(os.path.join("assets", "sounds", "old_video_game.mp3"))
            pygame.mixer.music.play(-1)
            boss_left = Enemy(WIDTH / 2 - 86 - 130, -200, "boss_left")
            boss_right = Enemy(WIDTH / 2 - 86 + 130, -200, "boss_right")
            boss_body = Enemy(WIDTH / 2 - 86, -200, "boss_body")
            boss_head = Enemy(WIDTH / 2 - 86, -200 + 47, "boss_head")
            boss_parts.append(boss_left)
            boss_parts.append(boss_right)
            boss_parts.append(boss_body)
            boss_parts.append(boss_head)
            final_battle = True

        # Winning
        if len(boss_parts) == 0 and final_battle:
            pygame.mixer.Sound.play(hit_sound)
            run = False
            victory_menu()

        # Display level Title
        if time_to_blit:
            blit_time += 1
        if blit_time >= 80:
            time_to_blit = False
            blit_time = 0

        # Quit game when press the X
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # Track keys pressed
        keys = pygame.key.get_pressed()  # get dict of all keys pressed
        # WASD keys movement
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_width() + 10 < HEIGHT:  # down
            player.y += player_vel
        # Shooting
        if level < 4:
            if keys[pygame.K_SPACE]:  # shoot
                player.shoot()
        else:
            if keys[pygame.K_SPACE]:  # double shoot
                player.double_shoot()
        # Arrow keys movement
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_width() + 10 < HEIGHT:  # down
            player.y += player_vel
        # Pause
        if keys[pygame.K_p]:  # pause
            paused()

        # Control Enemies
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            # Enemy Shooting
            if enemy.ship_img == big_alien and random.randrange(0, 3 * 60) == 1:
                enemy.double_shoot()
            elif enemy.ship_img == boss_alien_body and random.randrange(0, 3 * 60) == 1:
                enemy.double_shoot()
            elif enemy.ship_img == boss_alien_head and random.randrange(0, 3 * 60) == 1:
                enemy.double_shoot()
            elif random.randrange(0, 3 * 60) == 1:
                enemy.shoot()

            # Collisions with enemies
            if collide(enemy, player):
                player.health -= 20
                pygame.mixer.Sound.play(collide_sound)
                player.kills.append(DeadEnemy(enemy.x, enemy.y, enemy.health))
                enemies.remove(enemy)
                player.damage = True

            # Remove off screen enemies
            elif enemy.y + enemy.get_height() > HEIGHT:
                pygame.mixer.Sound.play(explode_sound)
                lives -= 1
                player.kills.append(DeadEnemy(enemy.x, enemy.y, enemy.health))
                enemies.remove(enemy)

        # Control Enemy Boss
        for part in boss_parts[:]:
            if part.y <= 57 and part.ship_img == boss_alien_head:
                part.move(enemy_vel)
            elif part.y <= 10:
                part.move(enemy_vel)

            # Move lasers
            part.move_lasers(laser_vel, player)

            # Enemy Boss Shooting
            if random.randrange(0, 3 * 60) == 1:
                part.double_shoot()
            elif random.randrange(0, 3 * 60) == 1:
                part.shoot()

            # Collisions with Enemy Boss parts
            if collide(part, player):
                player.health -= 20
                part.health -= 20
                pygame.mixer.Sound.play(collide_sound)
                player.damage = True

        # Control Med kit
        for med_kit in med_kits:
            med_kit.move(enemy_vel)

            # Player getting Med kit
            if collide(med_kit, player):
                if player.health + med_kit.heal > player.max_health:
                    player.health = player.max_health
                else:
                    player.health += med_kit.heal
                pygame.mixer.Sound.play(heal_sound)
                med_kits.remove(med_kit)

        # Player lasers
        if not final_battle:
            player.move_lasers(-player_laser_vel, enemies)
        else:
            player.move_lasers(-player_laser_vel, boss_parts)


# Victory screen
def victory_menu():
    clock = pygame.time.Clock()
    counter = 0
    run = True
    pygame.mouse.set_visible(True)
    start_count = True
    pygame.mixer.Sound.play(victory_sound)
    pygame.mixer.music.load(os.path.join("assets", "sounds", "land_of_8_bits.mp3"))
    victory_font = pygame.font.Font(os.path.join("assets", "slkscr.ttf"), 40)
    victory_font_small = pygame.font.Font(os.path.join("assets", "slkscr.ttf"), 30)
    victory_label_1 = victory_font.render("Victory!", True, (255, 255, 255))
    victory_label_2 = victory_font_small.render("You defeated the alien forces", True, (255, 255, 255))
    WIN.blit(victory_label_1, (WIDTH / 2 - victory_label_1.get_width() / 2, 280))
    WIN.blit(victory_label_2, (WIDTH / 2 - victory_label_2.get_width() / 2, 320))
    while start_count:
        clock.tick(60)
        counter += 1
        if counter >= 80:
            pygame.mixer.music.play(-1)
            start_count = False
            counter = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        button("Play again", WIDTH / 2 - 100, 400, 200, 50, (255, 255, 255), (0, 255, 0), main)
        button("Quit", WIDTH / 2 - 100, 500, 200, 50, (255, 255, 255), (0, 255, 0), quitgame)
        pygame.display.update()


main_menu()
