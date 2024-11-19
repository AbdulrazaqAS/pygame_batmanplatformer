import random

import pygame as pg
from os import path
import neat

from constants import *
from map import TiledMap, Camera
from sprites import Obstacle, Player, ControllablePlayer, MeleeEnemy, Knife, Batarang, Goal, HealthBar


vec = pg.math.Vector2


def collide_with_obstacles(character, hit):
	if any([isinstance(character, Knife), isinstance(character, Batarang)]):
		character.kill()
		return
	# character's bottom and obstacle top
	if abs(hit.rect.top - character.rect.bottom) < COLLISION_TOLERANCE:
		character.vel.y = 0
		character.pos.y = hit.rect.top + 3
		character.ground_count += 1

	# character's top and obstacle bottom
	if abs(hit.rect.bottom - character.rect.top) < COLLISION_TOLERANCE:
		character.vel.y = 0 
		character.pos.y = (hit.rect.bottom - 3) + (character.rect.bottom - character.rect.top)

	if character.vel.y < 0:
		if abs(hit.rect.bottom - character.rect.top) < COLLISION_TOLERANCE + 30:
			character.vel.y = 0
			character.pos.y = (hit.rect.bottom - 3) + (character.rect.bottom - character.rect.top)

	# character's left and obstacle right
	if abs(hit.rect.right - character.rect.left) < COLLISION_TOLERANCE:
		character.vel.x = 0
		character.pos.x = hit.rect.right + character.rect.width/2 + 3

	# character's right and obstacle left
	if abs(hit.rect.left - character.rect.right) < COLLISION_TOLERANCE:
		character.vel.x = 0
		character.pos.x = hit.rect.left - character.rect.width/2 - 3


def collide_with_weapon(character, weapon):
	character.health -= weapon.damage
	weapon.kill()


def collide_with_pickup(character, pickup):
	if isinstance(pickup, Goal):
		character.goal_reached = True

class Screen:
	def __init__(self, game, fps, genomes, config):
		self.game = game
		self.genomes = genomes
		self.counter = fps * 7 # 10 secs
		
		self.load()
		self.new(genomes, config)

	def load(self):
		#  prepare map
		self.map = TiledMap(path.join(self.game.map_dir, 'Base Level.tmx'))
		self.map_img, self.map.rect = self.map.make_map()

	def new(self, genomes, config):
		# sprite groups
		self.players_list = []
		self.nets = []
		self.all_sprites = pg.sprite.Group()
		self.players = pg.sprite.Group()
		self.collidables = pg.sprite.Group()
		self.attackable = pg.sprite.Group()
		self.obstacles = pg.sprite.Group()
		self.projectiles = pg.sprite.Group()
		self.pickups = pg.sprite.Group()
		self.bars = pg.sprite.Group()

		for obj in self.map.tmx_data.objects:
			obj_midbottom = vec(obj.x + obj.width/2, obj.y + obj.height)
			if obj.name == 'player':
				# For All Genomes Passed Create A New Neural Network
				for i, g in genomes:
					net = neat.nn.FeedForwardNetwork.create(g, config)
					self.nets.append(net)
					g.fitness = 0

					player_x = random.randrange(int(obj.x), int(obj.x + obj.width))
					player_y = random.randrange(int(obj.y), int(obj.y + obj.height))
					player_pos = vec(player_x, player_y)
					player = Player(self, player_pos, self.all_sprites, self.attackable, self.players, self.collidables)
					player.health_bar = HealthBar(HEALTH, 'red', 'darkred', 2, self.bars, self.all_sprites)
					self.players_list.append(player)

				player = ControllablePlayer(self, obj_midbottom, self.all_sprites, self.attackable, self.collidables)
				player.health_bar = HealthBar(HEALTH, 'green', 'darkgreen', 2, self.bars, self.all_sprites)
				self.player = player
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
			done = self.update()
			self.display()

			self.counter -= 1
			if done or self.counter <= 0:
				break


	def update_players(self):
		still_alive = 0
		for i, player in enumerate(self.players_list):
			output = self.nets[i].activate(player.get_data())
			choice = output.index(max(output))
			action = None
			if choice == 0:
				action = 'right'
			elif choice == 1:
				action = 'left'
			elif choice == 2:
				action = 'jump'
			elif choice == 3:
				action = 'shoot'
			# action = random.choice(['right', None, None, None, None, None, None])
			if not player.is_dead():
				player.act(action=action)
				still_alive += 1
				self.genomes[i][1].fitness += player.get_score()

		return still_alive

	def update(self):
		players_pos = [p.pos for p in self.players]
		done = self.update_players() == 0
		self.all_sprites.update(players_pos=players_pos)
		self.check_collisions()
		self.camera.update(self.player)

		return done

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
					if not isinstance(sprite, type(weapon.character)):
						collide_with_weapon(sprite, weapon)

		hits = pg.sprite.groupcollide(self.pickups, self.players, False, False)
		if hits:
			for pickup in hits:
				for player in hits[pickup]:
					collide_with_pickup(player, pickup)

	def create_knife(self, character, pos, direction):
		# Knife(screen, pos, damage, direction, *groups)
		Knife(self, character, pos, MELEE_ENEMY_KNIFE_DAMAGE, direction, self.projectiles, self.collidables, self.all_sprites)

	def create_batarang(self, character, pos, direction):
		# screen, character, pos, direction, *groups
		Batarang(self, character, pos, direction, self.projectiles, self.collidables, self.all_sprites)
