import pygame as pg
from os import path

import pygame.draw

from constants import *
from base_sprite import Character, Projectile, AnimatedProjectile
from spritesheet import Spritesheet, Animation


class Player(Character):
    def __init__(self, screen, pos, *groups):
        super().__init__(pos, PLAYER_DAMAGE, groups)
        self.screen = screen
        self.pos = pos
        self.jump_release = 0
        self.crouching = False
        self.goal_reached = False

        # image
        self.load()
        self.image = self.active_anim.get_frame(0)
        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.width = self.rect.right - self.rect.left
        self.height = self.rect.top - self.rect.bottom

    def load(self):
        spritesheet = Spritesheet(path.join(self.screen.game.img_dir, 'batman_spritesheet.png'), bg=(34, 177, 76))

        # MOVEMENT ANIMATIONS
        # walking animation
        walking_frames = [[22, 346, 62, 55], [88, 348, 65, 49], [160, 345, 65, 54], [238, 344, 53, 56], \
                          [296, 338, 60, 57], [365, 342, 63, 51], [433, 343, 65, 52], [503, 343, 58, 55]]
        walking_anim = spritesheet.get_animation(walking_frames, 0.12, Animation.PlayMode.LOOP, scale=1.2)
        self.store_animation('walking', walking_anim)

        # standing animation
        standing_frames = [(28, 247, 34, 63), (73, 248, 34, 62), (115, 248, 35, 61)]
        standing_animation = spritesheet.get_animation(standing_frames, 0.20, Animation.PlayMode.LOOP, scale=1.2)
        self.store_animation('standing', standing_animation)

        # jumping animation
        jumping_frames = [(609, 343, 43, 51), (664, 337, 48, 64), (720, 338, 48, 64)]
        jumping_animation = spritesheet.get_animation(jumping_frames, 0.10, Animation.PlayMode.NORMAL, scale=1.2)
        self.store_animation('jumping', jumping_animation)

        # falling animation
        falling_frames = [(773, 344, 60, 50), (839, 323, 44, 80), (897, 326, 46, 77)]
        falling_animation = spritesheet.get_animation(falling_frames, 0.10, Animation.PlayMode.NORMAL, scale=1.2)
        self.store_animation('falling', falling_animation)

        # landing animation
        landing_frames = [(960, 336, 47, 69), (1023, 362, 47, 43), (1081, 352, 42, 52)]
        landing_animation = spritesheet.get_animation(landing_frames, 0.10, Animation.PlayMode.NORMAL, scale=1.2)
        self.store_animation('landing', landing_animation)

        # batarang throw
        batarang_throw_frames = [(20, 1004, 46, 54), (81, 997, 53, 61), (149, 1004, 82, 54), (239, 1004, 72, 54),
                                 (326, 1003, 67, 55)]
        batarang_throw_animation = spritesheet.get_animation(batarang_throw_frames, 0.10, Animation.PlayMode.NORMAL,
                                                             scale=1.2)
        self.store_animation('batarang_throw', batarang_throw_animation)

        # crouching
        crouching_frames = [(137, 450, 42, 52), (85, 460, 41, 43)]
        crouching_animation = spritesheet.get_animation(crouching_frames, 0.10, Animation.PlayMode.NORMAL,
                                                             scale=1.2)
        self.store_animation('crouching', crouching_animation)

        # win
        win_frames = [(34, 1763, 38, 65), (87, 1748, 36, 79), (129, 1737, 36, 90), (174, 1717, 36, 110), \
                      (218, 1697, 36, 130), (269, 1677, 36, 150), (314, 1657, 36, 170), (360, 1637, 36, 190), \
                      (410, 1617, 36, 210), (462, 1597, 36, 230), (509, 1541, 36, 269+18), (558, 1541, 37, 254+33)]
        win_animation = spritesheet.get_animation(win_frames, 0.10, Animation.PlayMode.NORMAL,
                                                        scale=1.2)
        self.store_animation('win', win_animation)

    def animate(self):
        if self.active_name == "walking":
            if self.vel.x == 0:
                self.set_active_animation("standing")

            if self.vel.y < 0:
                self.set_active_animation("jumping")

            if self.crouching:
                self.set_active_animation("crouching")

        if self.active_name == "standing":
            if abs(self.vel.x) > 0:
                self.set_active_animation("walking")

            if self.vel.y < 0:
                self.set_active_animation("jumping")

            if self.crouching:
                self.set_active_animation("crouching")

        if self.active_name == "jumping":
            if self.vel.y > 0:
                self.set_active_animation("falling")

        if self.active_name == "falling":
            if self.ground_count > 0:
                self.set_active_animation("landing")

        if self.active_name == "landing":
            if self.is_animation_finished():
                if abs(self.vel.x) > 0:
                    self.set_active_animation("walking")
                else:
                    self.set_active_animation("standing")
            else:
                self.vel.x = 0

        if self.active_name == "crouching":
            if not self.crouching:
                self.set_active_animation("standing")

        if self.goal_reached:
            self.set_active_animation("win")

        # if self.attack_count >= 0:
        if self.attack_count > 0:
            self.set_active_animation("batarang_throw")

        if self.goal_reached:
            self.set_active_animation("win")

        if self.active_name == 'batarang_throw':
            if self.active_anim.get_frame_index(self.elapsed_time) > 2:
                if self.shoot_count == 0:
                    if self.direction == 'R':
                        # self.screen.create_bullet(self.rect.midright, 1, PLAYER_BULLET_DAMAGE,
                        #                           self.screen.player_bullets, self.bullet_animation)
                        # self.screen.create_knife(self, self.rect.midright, 1)
                        self.screen.create_batarang(self, self.rect.midright, 1)
                    elif self.direction == 'L':
                        # self.screen.create_bullet(self.rect.midleft, -1, PLAYER_BULLET_DAMAGE,
                        #                           self.screen.player_bullets, self.bullet_animation)
                        # self.screen.create_knife(self, self.rect.midleft, -1)
                        self.screen.create_batarang(self, self.rect.midleft, -1)
                    self.shoot_count += 1

        # if self.active_name == 'batarang_throw':
        #     if self.active_anim.get_frame_index(self.elapsed_time) > 1:
        #         if self.shoot_count == 0:
        #             if self.direction == 'R':
        #                 # self.screen.create_bullet(self.rect.midright, 1, PLAYER_BULLET_DAMAGE,
        #                 #                           self.screen.player_bullets, self.bullet_animation)
        #                 self.screen.create_knife(self, self.rect.midright, 1)
        #             elif self.direction == 'L':
        #                 # self.screen.create_bullet(self.rect.midleft, -1, PLAYER_BULLET_DAMAGE,
        #                 #                           self.screen.player_bullets, self.bullet_animation)
        #                 self.screen.create_knife(self, self.rect.midleft, -1)
        #             # self.shoot_count += 1

            if self.is_animation_finished():
                self.set_active_animation("standing")
                self.shoot_count = 0
            self.attack_count = 0

        if self.active_name == "win":
            if self.health_bar.alive():
                self.health_bar.kill()
            if self.is_animation_finished():
                self.kill()

        bottom = self.rect.bottom
        self.image = self.active_anim.get_frame(self.elapsed_time)

        # flip image if necessary
        if self.direction == 'L':
            self.image = pg.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect.bottom = bottom

    def move(self):
        keys = pg.key.get_pressed()

        if keys[pg.K_DOWN]:
            self.crouching = True
        else:
            self.crouching = False

        # horizontal movement
        if keys[pg.K_LEFT] and not self.crouching:
            self.direction = 'L'
            if not self.attack_count > 0 and not self.active_name == 'batarang_throw':
                self.acc.x = -PLAYER_ACC

        elif keys[pg.K_RIGHT] and not self.crouching:
            self.direction = 'R'
            if not self.attack_count > 0 and not self.active_name == 'batarang_throw':
                self.acc.x = PLAYER_ACC

        # jumping
        if keys[pg.K_UP] and not self.crouching:
            if self.jump_release > 0:
                if self.ground_count > 0 and not self.active_name == 'falling':
                    self.vel.y = PLAYER_JUMP
                    self.ground_count = 0
                    self.jump_release = 0

        else:
            self.jump_release += 1

        if keys[pg.K_SPACE]:
            if self.attack_count == 0:
                self.attack_count += 1

    def update(self, **kwargs):
        super().update(1 / self.screen.game.fps)
        self.animate()

        # update properties
        self.width = self.rect.right - self.rect.left
        self.height = self.rect.top - self.rect.bottom

        self.rect.midbottom = self.pos


class Obstacle(pg.sprite.Sprite):
    def __init__(self, pos, size, *groups):
        super().__init__(groups)

        # rect
        self.rect = pg.Rect(pos, size)

        # position
        self.x = pos[0]
        self.y = pos[1]
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class MeleeEnemy(Character):
    def __init__(self, screen, pos, right_boundary_x, left_boundary_x, *groups):
        super().__init__(pos, MELEE_ENEMY_DAMAGE, groups)
        self.screen = screen
        self.range = KNIFE_RANGE
        self.pos = pos
        self.right_boundary_x = right_boundary_x
        self.left_boundary_x = left_boundary_x

        # image
        self.load()
        self.image = self.active_anim.get_frame(0)
        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.width = self.rect.right - self.rect.left
        self.height = self.rect.top - self.rect.bottom

    def load(self):
        spritesheet = Spritesheet(path.join(self.screen.game.img_dir, 'melee_enemy_spritesheet.png'), bg=(0, 64, 128))

        # MOVEMENT ANIMATIONS
        # walking animation
        walking_frames = [(8, 94, 46, 74), (65, 94, 50, 74), (127, 93, 37, 75), (172, 93, 39, 75), \
                          (218, 94, 43, 74), (272, 93, 43, 75), (320, 93, 49, 75)]
        walking_anim = spritesheet.get_animation(walking_frames, 0.12, Animation.PlayMode.LOOP, scale=0.9)
        self.store_animation('walking', walking_anim)

        # knife_attack animation
        knife_attack_frames = [(6, 176, 46, 80), (56, 172, 52, 84), (113, 181, 53, 75), (171, 183, 39, 73), \
                               (220, 180, 30, 76), (259, 180, 31, 76)]
        knife_attack_animation = spritesheet.get_animation(knife_attack_frames, 0.12, Animation.PlayMode.NORMAL, scale=0.9)
        self.store_animation('knife_attack', knife_attack_animation)

        # Backward fall animation
        backward_fall_frames = [(10, 326, 31, 67), (51, 316, 26, 77), (85, 331, 58, 53), (153, 354, 72, 32), \
                                (234, 367, 74, 26), (313, 374, 80, 20), (399, 372, 80, 22), (484, 350, 55, 43)]
        backward_fall_animation = spritesheet.get_animation(backward_fall_frames, 0.10, Animation.PlayMode.NORMAL, scale=0.9)
        self.store_animation('backward_fall', backward_fall_animation)

        # Death animation
        death_frames = [(10, 326, 31, 67), (51, 316, 26, 77), (85, 331, 58, 53), (153, 354, 72, 32), \
                                (234, 367, 74, 26), (313, 374, 80, 20)]
        death_animation = spritesheet.get_animation(death_frames, 0.10, Animation.PlayMode.NORMAL,
                                                            scale=0.9)
        self.store_animation('death', death_animation)

        # Forward fall animation
        forward_fall_frames = [(85, 378, 31, 75), (149, 407, 64, 40), (223, 420, 70, 27), (297, 432, 79, 16), \
                               (381, 428, 80, 20), (471, 415, 69, 32)]
        forward_fall_animation = spritesheet.get_animation(forward_fall_frames, 0.10, Animation.PlayMode.NORMAL,
                                                            scale=0.9)
        self.store_animation('forward_fall', forward_fall_animation)

        # Getting up animation
        getting_up_frames = [(558, 375, 47, 40), (623, 347, 32, 66), (677, 346, 32, 68)]
        getting_up_animation = spritesheet.get_animation(getting_up_frames, 0.10, Animation.PlayMode.NORMAL, scale=0.9)
        self.store_animation('getting_up', getting_up_animation)

        # Crouching animation
        crouching_frames = [(5, 9, 35, 76), (49, 41, 30, 44), (84, 39, 30, 46)]
        crouching_animation = spritesheet.get_animation(crouching_frames, 0.10, Animation.PlayMode.NORMAL, scale=0.9)
        self.store_animation('crouching', crouching_animation)

    def animate(self):
        if self.active_name == "walking":
            pass
            # if self.vel.x == 0:
            #     self.set_active_animation("standing")

            # if self.vel.y < 0:
            #     self.set_active_animation("jumping")

        if self.active_name == "standing":
            pass

        if self.attack_count > 0 and not self.is_dead():
            self.set_active_animation("knife_attack")

        if self.is_dead():
            self.set_active_animation("death")

        if self.active_name == 'knife_attack':
            if self.active_anim.get_frame_index(self.elapsed_time) > 2:
                if self.shoot_count == 0:
                    if self.direction == 'R':
                        self.screen.create_knife(self, self.rect.midright, 1)
                    elif self.direction == 'L':
                        self.screen.create_knife(self, self.rect.midleft, -1)
                    self.shoot_count += 1

            if self.is_animation_finished():
                self.set_active_animation("walking")
                self.shoot_count = 0
            self.attack_count = 0

        if self.active_name == 'death':
            if self.is_animation_finished():
                self.health_bar.kill()
                self.kill()

        bottom = self.rect.bottom
        self.image = self.active_anim.get_frame(self.elapsed_time)

        # flip image if necessary
        if self.direction == 'L':
            self.image = pg.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect.bottom = bottom

    def move(self):
        # horizontal movement
        if self.pos.x >= self.right_boundary_x or self.pos.x <= self.left_boundary_x:
            self.direction = 'L' if self.direction == 'R' else 'R'

        if self.direction == 'L':
            if not self.attack_count > 0 and not self.active_name == 'knife_attack':
                self.acc.x = -MELEE_ENEMY_ACC
        elif self.direction == 'R':
            if not self.attack_count > 0 and not self.active_name == 'knife_attack':
                self.acc.x = MELEE_ENEMY_ACC


    def saw_player(self, player_pos):
        player_x, player_y = player_pos.x, player_pos.y

        distance_to_player = abs(player_x - self.pos.x)
        player_in_range = distance_to_player <= self.range and abs(player_y-self.pos.y) <= self.image.get_rect().height / 1.5
        #print(f'{player_y} - {self.pos.y} <= {self.height}, {abs(player_y-self.pos.y)} <= {self.height}')
        is_facing_player = any([self.direction == 'L' and player_x <= self.pos.x,
                                self.direction == 'R' and player_x >= self.pos.x])
        if player_in_range and is_facing_player:
            return True

        return False

    def update(self, player_pos):
        super().update(1 / self.screen.game.fps)
        self.animate()

        if self.saw_player(player_pos):
            self.attack_count = 1

        # update properties
        self.width = self.rect.right - self.rect.left
        self.height = self.rect.top - self.rect.bottom

        self.rect.midbottom = self.pos


class Knife(Projectile):
    def __init__(self, screen, character, pos, damage, direction, *groups):
        super().__init__(pos, MELEE_ENEMY_KNIFE_SPEED, damage, KNIFE_RANGE, groups)
        self.character = character
        self.screen = screen

        # image
        self.image = pg.image.load(path.join(self.screen.game.img_dir, 'knife.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.center = pos

        # flip image if necessary
        if direction == -1:
            self.direction = 'L'
            self.image = pg.transform.flip(self.image, True, False)

        self.width = self.rect.right - self.rect.left
        self.height = self.rect.top - self.rect.bottom

    def move(self):
        # horizontal movement
        if self.direction == 'L':
            self.pos.x -= MELEE_ENEMY_KNIFE_SPEED
        elif self.direction == 'R':
            self.pos.x += MELEE_ENEMY_KNIFE_SPEED

    def update(self, **kwargs):
        super().update(1 / self.screen.game.fps)
        self.move()
        self.rect.center = self.pos.x, self.pos.y


class Batarang(AnimatedProjectile):
    def __init__(self, screen, character, pos, direction, *groups):
        super().__init__(pos, BATARANG_SPEED, BATARANG_DAMAGE, BATARANG_RANGE, groups)
        self.character = character
        self.screen = screen

        # image
        self.load()
        self.image = self.active_anim.get_frame(0)
        self.rect = self.image.get_rect()
        self.rect.center = pos

        if direction == -1:
            self.direction = 'L'
            # self.image = pg.transform.flip(self.image, True, False)

        self.width = self.rect.right - self.rect.left
        self.height = self.rect.top - self.rect.bottom

    def load(self):
        spritesheet = Spritesheet(path.join(self.screen.game.img_dir, 'batman_spritesheet.png'), bg=(34, 177, 76))

        # MOVEMENT ANIMATIONS
        # moving animation
        moving_frames = [(401, 1025, 15, 18), (423, 1028, 36, 10), (466, 1025, 16, 18), (491, 1031, 36, 10)]
        moving_anim = spritesheet.get_animation(moving_frames, 0.09, Animation.PlayMode.LOOP, scale=0.8)
        self.store_animation('moving', moving_anim)

    def animate(self):
        # bottom = self.rect.bottom
        self.image = self.active_anim.get_frame(self.elapsed_time)

        # flip image if necessary
        if self.direction == 'L':
            self.image = pg.transform.flip(self.image, True, False)

        # self.rect = self.image.get_rect()
        # self.rect.bottom = bottom

    def move(self):
        # horizontal movement
        if self.direction == 'L':
            self.pos.x -= MELEE_ENEMY_KNIFE_SPEED
        elif self.direction == 'R':
            self.pos.x += MELEE_ENEMY_KNIFE_SPEED

    def update(self, **kwargs):
        super().update(1 / self.screen.game.fps)
        self.move()
        self.animate()
        self.rect.center = self.pos.x, self.pos.y


class Goal(pg.sprite.Sprite):
    def __init__(self, screen, x, y, *groups):
        super().__init__(groups)
        self.x = x
        self.y = y
        self.screen = screen

        self.image = pg.image.load(path.join(self.screen.game.img_dir, 'goal.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.center = x, y


class HealthBar(pg.sprite.Sprite):
    def __init__(self, max_health, color, border_color, border_thickness=2, *groups):
        super().__init__(groups)
        self.max_health = max_health
        self.health = max_health
        self.width = HEALTH_BAR_WIDTH
        self.height = HEALTH_BAR_HEIGHT

        self.color = color
        self.border_color = border_color
        self.border_thickness = border_thickness

        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()

    def update_(self, health, position):
        self.image.fill((0, 0, 0, 0))  # Clear image: fill with transparent
        rect = (0, 0, self.width, self.height)
        pg.draw.rect(self.image, self.border_color, rect, self.border_thickness)

        health_width = int(health / self.max_health * (self.width - self.border_thickness * 2))
        inner_rect = (self.border_thickness, self.border_thickness, health_width, self.height - (self.border_thickness * 2))
        pg.draw.rect(self.image, self.color, inner_rect)

        self.rect.midbottom = position
