import pygame as pg
from os import path

from constants import *
from map import TiledMap, Camera
from sprites import Obstacle, Player, MeleeEnemy, Knife, Batarang, Goal, HealthBar


vec = pg.math.Vector2


def collide_with_obstacles(character, hit):
	if any([isinstance(character, Knife), isinstance(character, Batarang)]):
		character.kill()
		return
	# character's bottom and obstacle top
	if abs(hit.rect.top - character.rect.bottom) < COLLISION_TOLERANCE:
		character.vel.y = 0
		character.pos.y = hit.rect.top + 1
		character.ground_count += 1

	# character's top and obstacle bottom
	if abs(hit.rect.bottom - character.rect.top) < COLLISION_TOLERANCE:
		character.vel.y = 0 
		character.pos.y = (hit.rect.bottom - 1) + (character.rect.bottom - character.rect.top)

	if character.vel.y < 0:
		if abs(hit.rect.bottom - character.rect.top) < COLLISION_TOLERANCE + 30:
			character.vel.y = 0
			character.pos.y = (hit.rect.bottom - 1) + (character.rect.bottom - character.rect.top)

	# character's left and obstacle right
	if abs(hit.rect.right - character.rect.left) < COLLISION_TOLERANCE:
		character.vel.x = 0
		character.pos.x = hit.rect.right + character.rect.width/2 + 1

	# character's right and obstacle left
	if abs(hit.rect.left - character.rect.right) < COLLISION_TOLERANCE:
		character.vel.x = 0
		character.pos.x = hit.rect.left - character.rect.width/2 - 1


def collide_with_weapon(character, weapon):
	character.health -= weapon.damage
	weapon.kill()


def collide_with_pickup(character, pickup):
	if isinstance(pickup, Goal):
		character.goal_reached = True

class Screen:
	def __init__(self, game):
		self.game = game
		
		self.load()
		self.new()

	def load(self):
		#  prepare map
		self.map = TiledMap(path.join(self.game.map_dir, 'Base Level.tmx'))
		self.map_img, self.map.rect = self.map.make_map()

	def new(self):
		# sprite groups
		self.all_sprites = pg.sprite.Group()
		self.collidables = pg.sprite.Group()
		self.attackable = pg.sprite.Group()
		self.obstacles = pg.sprite.Group()
		self.projectiles = pg.sprite.Group()
		self.pickups = pg.sprite.Group()
		self.bars = pg.sprite.Group()

		for obj in self.map.tmx_data.objects:
			obj_midbottom = vec(obj.x + obj.width/2, obj.y + obj.height)
			if obj.name == 'player':
				self.player = Player(self, obj_midbottom, self.all_sprites, self.attackable, self.collidables)
				self.player.health_bar = HealthBar(HEALTH, 'red', 'darkred', 2, self.bars, self.all_sprites)
			elif obj.name == 'obstacle':
				Obstacle((obj.x, obj.y), (obj.width, obj.height), self.obstacles)
			elif obj.name == 'melee_enemy':
				right_boundary_obj_id = obj.properties.get('right_boundary')
				left_boundary_obj_id = obj.properties.get('left_boundary')
				right_boundary_x = self.map.tmx_data.get_object_by_id(right_boundary_obj_id).x
				left_boundary_x = self.map.tmx_data.get_object_by_id(left_boundary_obj_id).x

				e = MeleeEnemy(self, obj_midbottom, right_boundary_x, left_boundary_x, self.all_sprites, self.attackable, self.collidables)
				e.health_bar = HealthBar(HEALTH, 'red', 'darkred', 2, self.bars, self.all_sprites)
			elif obj.name == 'goal':
				Goal(self, obj.x, obj.y, self.pickups, self.all_sprites, self.collidables)

		self.camera = Camera(self.game, self.map.width, self.map.height)

	def run(self):
		while True:
			self.game.clock.tick(self.game.fps)
			self.game.events()
			self.update()
			self.display()

	def update(self):
		self.all_sprites.update(player_pos=self.player.pos)
		self.check_collisions()
		self.camera.update(self.player)

	def display(self):
		self.game.surface.blit(self.map_img, self.camera.apply(self.map))
		self.camera.draw(self.game.surface, self.all_sprites)

		pg.display.flip()

	def check_collisions(self):
		hits = pg.sprite.groupcollide(self.collidables, self.obstacles, False, False)
		if hits:
			for sprite in hits:
				for hit in hits[sprite]:
					collide_with_obstacles(sprite, hit)

		hits = pg.sprite.groupcollide(self.attackable, self.projectiles, False, False)
		if hits:
			for sprite in hits:
				for weapon in hits[sprite]:
					if sprite != weapon.character:
						collide_with_weapon(sprite, weapon)

		hits = pg.sprite.spritecollide(self.player, self.pickups, False)
		if hits:
			for pickup in hits:
				collide_with_pickup(self.player, pickup)

	def create_knife(self, character, pos, direction):
		# Knife(screen, pos, damage, direction, *groups)
		Knife(self, character, pos, MELEE_ENEMY_KNIFE_DAMAGE, direction, self.projectiles, self.collidables, self.all_sprites)

	def create_batarang(self, character, pos, direction):
		# screen, character, pos, direction, *groups
		Batarang(self, character, pos, direction, self.projectiles, self.collidables, self.all_sprites)
