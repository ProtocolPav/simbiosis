import math

import pygame

from src.entity import Creature, Food
from src.genes import CreatureGenes
from src.tree import KDTree
from src.characteristics import generate_characteristics

from datetime import timedelta

import random


class World:
    def __init__(self, creature_image: pygame.Surface, food_image: pygame.Surface, world_size: int,
                 creatures: list[Creature], foods: list[Food], largest_radius: float, tick_speed: int,
                 food_spawn_rate: int, seconds: float, delta_seconds: float, food_seconds: float, paused: bool,
                 creature_count: list, food_count: list, birth_count: list, time_data: list):
        self.creature_image = creature_image
        self.food_image = food_image

        self.size = world_size

        self.creatures = creatures
        self.food = foods
        self.tree: KDTree = KDTree([])
        self.largest_radius = largest_radius

        self.food_spawnrate = food_spawn_rate
        self.food_second_split = 1 / food_spawn_rate
        self.tick_speed = tick_speed

        self.min_food_energy = 1000
        self.max_food_energy = 100000
        self.mutation_chance = 0.2
        self.mutation_factor = 2

        self.seconds = seconds
        self.delta_second = delta_seconds
        self.food_second = food_seconds

        self.time_data: list[float] = time_data
        self.creature_count = creature_count
        self.food_count = food_count
        self.birth_count = birth_count

        self.births = 0

        self.paused = paused

    @classmethod
    def load(cls, save_dict: dict, creature_image: pygame.Surface, food_image: pygame.Surface):
        """
        This method is used when loading from a save file. It takes all the data from the file
        and pushes it to __init__
        :return:
        """
        creatures_list = []
        for creature in save_dict['creatures']:
            genes = CreatureGenes.load(creature['genes'])
            creatures_list.append(Creature.load(creature['position'][0], creature['position'][1], creature_image,
                                                (save_dict['world']['size'], save_dict['world']['size']),
                                                genes, creature['energy'], creature['direction'], creature['seeing'],
                                                creature['memory_reaction'], creature['dead'], creature['id']))

        food_list = []
        for food in save_dict['food']:
            food_list.append(Food.load(food['position'][0], food['position'][1], food_image,
                                       (save_dict['world']['size'], save_dict['world']['size']),
                                       food['energy'], food['eaten']))

        world_data = save_dict['world']
        graph_data: dict = save_dict['data']
        graph_data['creature_count'] = graph_data.get('creature_count', [len(creatures_list)])
        graph_data['food_count'] = graph_data.get('food_count', [len(food_list)])
        graph_data['birth_count'] = graph_data.get('birth_count', [0])
        graph_data['time_data'] = graph_data.get('time', [world_data['seconds']])

        return cls(creature_image, food_image, world_data['size'], creatures_list, food_list,
                   world_data['largest_radius'], world_data['tick_speed'], world_data['food_spawn_rate'],
                   world_data['seconds'], world_data['delta_seconds'], world_data['food_seconds'],
                   world_data['paused'], graph_data['creature_count'], graph_data['food_count'],
                   graph_data['birth_count'], graph_data['time_data'])

    @classmethod
    def create(cls, size: int, creature_image: pygame.Surface, food_image: pygame.Surface,
               food_spawn_rate: int,
               start_species: int = 4, start_creatures: int = 10, start_food: int = 500):
        """
        This method is used when creating a new world, normally when starting a new simulation.
        :return:
        """

        creatures_list: list[Creature] = []
        food_list: list[Food] = []
        largest_radius = 0

        for i in range(start_food):
            food_list.append(Food.create(random.randint(0, size - 1),
                                         random.randint(0, size - 1),
                                         food_image,
                                         (size, size),
                                         min_energy=5000,
                                         max_energy=50000))

        for i in range(start_species):
            specimen = Creature.create(random.randint(0, size - 1),
                                       random.randint(0, size - 1),
                                       creature_image,
                                       (size, size))

            if specimen.radius >= largest_radius:
                largest_radius = specimen.radius

            for creature in range(start_creatures // start_species):
                creatures_list.append(Creature.create_child(random.randint(0, size - 1),
                                                            random.randint(0, size - 1),
                                                            creature_image,
                                                            (size, size),
                                                            specimen.genes, specimen.energy))

        return cls(creature_image, food_image, world_size=size, creatures=creatures_list, foods=food_list,
                   largest_radius=largest_radius, tick_speed=1, food_spawn_rate=food_spawn_rate, delta_seconds=0,
                   seconds=0, food_seconds=0, paused=False, creature_count=[len(creatures_list)], food_count=[len(food_list)],
                   birth_count=[0], time_data=[0])

    def tick_world(self, deltatime: float):
        for i in range(self.tick_speed):
            self.seconds += deltatime
            self.delta_second += deltatime
            self.food_second += deltatime

            self.tree = KDTree(self.creatures + self.food)

            for creature in self.creatures:
                coordinates = creature.get_coordinates()
                boxsize = 2 * creature.genes.vision_radius.value + self.largest_radius
                creature_check = self.tree.range_search(coordinates,
                                                        (coordinates[0] - boxsize, coordinates[1] + boxsize),
                                                        (coordinates[0] + boxsize, coordinates[1] - boxsize))
                creature.tick(deltatime, creature_check)

                for food in creature.food_list:
                    self.food.remove(food)

                if creature.dead:
                    self.births -= 1
                    self.creatures.remove(creature)

                if self.delta_second >= 1:
                    creature.visible_entity = None

                if creature.child is not None:
                    self.births += 1
                    self.creatures.append(creature.child)
                    creature.child = None

            if self.delta_second >= 1:
                self.delta_second = 0

                self.time_data.append(self.seconds)
                self.creature_count.append(len(self.creatures))
                self.food_count.append(len(self.food))
                self.birth_count.append(self.births)

                self.births = 0

            if self.food_second >= self.food_second_split:
                self.spawn_food()
                self.food_second -= self.food_second_split

    def spawn_food(self):
        food = random.choice(self.food) if len(self.food) != 0 else None

        if food is None:
            self.food.append(Food.create(random.randint(0, self.size - 1),
                                         random.randint(0, self.size - 1),
                                         self.food_image,
                                         (self.size, self.size),
                                         self.min_food_energy, self.max_food_energy))
        else:
            spawned = False
            while not spawned:
                temporary_coordinates = (food.x + random.randint(-20, 20), food.y + random.randint(-20, 20))

                new_food = Food.create(temporary_coordinates[0],
                                       temporary_coordinates[1],
                                       self.food_image,
                                       (self.size, self.size),
                                       self.min_food_energy, self.max_food_energy)

                if not self.tree.find(temporary_coordinates) and new_food.within_border():
                    spawned = True
                    self.food.append(new_food)
                else:
                    food = random.choice(self.food)

    def change_tick_speed(self, direction: int):
        if 0 < self.tick_speed + direction <= 10:
            self.tick_speed += direction


class Camera:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.zoom_level = 1
        self.camera_speed = 1500
        self.centre_x = self.screen.get_width() // 2
        self.centre_y = self.screen.get_height() // 2
        self.x_offset = 0
        self.y_offset = 0
        self.font = pygame.Font('freesansbold.ttf', 25)

    def draw_world(self, world: World, debug: bool = False):
        # Draw Background Colour
        pygame.draw.rect(surface=self.screen,
                         color=[0, 10, 27],
                         rect=[[0, 0], [self.screen.get_width(), self.screen.get_height()]])

        # Draw Border
        world_rect = pygame.Rect(0, 0, world.size, world.size)
        world_rect.height *= self.zoom_level
        world_rect.width *= self.zoom_level
        world_rect.centerx = self.centre_x + self.x_offset
        world_rect.centery = self.centre_y + self.y_offset

        pygame.draw.rect(surface=self.screen, color=[0, 10 * 0.7, 27 * 0.7], rect=world_rect)

        scale = 1 / self.zoom_level

        # Draw Food
        for food in world.food:
            # Move the Body Part Rect to the correct position
            drawing_rect = pygame.Rect(food.x, food.y, 1, 1)
            drawing_rect.x = world_rect.x + round(drawing_rect.x / scale)
            drawing_rect.y = world_rect.y + round(drawing_rect.y / scale)
            drawing_rect.width *= self.zoom_level
            drawing_rect.height *= self.zoom_level

            if -2 < drawing_rect.x < self.screen.get_width() and -2 < drawing_rect.y < self.screen.get_height():
                copy_image = food.image.copy()
                copy_image = pygame.transform.scale(copy_image, (drawing_rect.w, drawing_rect.h))
                rotated_image = pygame.transform.rotate(copy_image, random.randint(0, 360))
                food_rect = rotated_image.get_rect(center=drawing_rect.center)
                self.screen.blit(rotated_image, food_rect)

                # pygame.draw.rect(surface=self.screen, rect=drawing_rect, color=[170, 255, 170])

        # Draw Creatures
        for creature in world.creatures:
            colour_to_draw = (int(creature.genes.colour_red.value),
                              int(creature.genes.colour_green.value),
                              int(creature.genes.colour_blue.value))
            pattern = (int(255 - creature.genes.colour_red.value),
                       int(255 - creature.genes.colour_green.value),
                       int(255 - creature.genes.colour_blue.value))

            # Move the Body Part Rect to the correct position
            # This is important as the position values I give is the top left point of the rectangle,
            # but the point that is stored is the centre point, so I must adjust for that
            rect_left = creature.x - creature.genes.radius.value
            rect_top = creature.y - creature.genes.radius.value
            drawing_rect = pygame.Rect(rect_left, rect_top, creature.genes.radius.value * 2,
                                       creature.genes.radius.value * 2)
            drawing_rect.x = world_rect.x + round(drawing_rect.x / scale)
            drawing_rect.y = world_rect.y + round(drawing_rect.y / scale)
            drawing_rect.width *= self.zoom_level
            drawing_rect.height *= self.zoom_level

            bound = -(creature.genes.radius.value / scale * 2)

            # Don't draw if the creature is off the screen. Saves program from processing useless things
            if bound < drawing_rect.x < self.screen.get_width() and bound < drawing_rect.y < self.screen.get_height():
                copy_image = creature.image.copy()
                coloured = pygame.PixelArray(copy_image)
                coloured.replace((104, 104, 104), colour_to_draw)
                coloured.replace((255, 255, 255), pattern)
                del coloured

                copy_image = pygame.transform.scale(copy_image, (drawing_rect.w, drawing_rect.h))
                rotated_image = pygame.transform.rotate(copy_image, -(creature.direction + 90))

                # Sets the center of the image to be aligned with the center position
                creature_rect = rotated_image.get_rect(center=drawing_rect.center)
                self.screen.blit(rotated_image, creature_rect)

                # Display creature Characteristics if the user is hovering over the creature
                if self.check_for_mouse_hover(creature_rect):
                    generate_characteristics(creature, world.creatures)
                    self.screen.blit(copy_image, creature_rect)

                if debug:
                    # Draw all the vision lines to see what entities the creature is checking against
                    for entity in creature.all_check_entities:
                        rect_left = entity.x - entity.radius
                        rect_top = entity.y - entity.radius
                        drawing_rect2 = pygame.Rect(rect_left, rect_top, entity.radius * 2,
                                                    entity.radius * 2)
                        drawing_rect2.x = world_rect.x + round(drawing_rect2.x / scale)
                        drawing_rect2.y = world_rect.y + round(drawing_rect2.y / scale)
                        drawing_rect2.width *= self.zoom_level
                        drawing_rect2.height *= self.zoom_level

                        pygame.draw.rect(surface=self.screen, rect=drawing_rect2, color=[23, 5, 60])
                        pygame.draw.line(surface=self.screen, color=[23, 5, 60],
                                         start_pos=drawing_rect.center, end_pos=drawing_rect2.center)

                    for entity in creature.check_entities:
                        rect_left = entity.x - entity.radius
                        rect_top = entity.y - entity.radius
                        drawing_rect2 = pygame.Rect(rect_left, rect_top, entity.radius * 2,
                                                    entity.radius * 2)
                        drawing_rect2.x = world_rect.x + round(drawing_rect2.x / scale)
                        drawing_rect2.y = world_rect.y + round(drawing_rect2.y / scale)
                        drawing_rect2.width *= self.zoom_level
                        drawing_rect2.height *= self.zoom_level

                        pygame.draw.rect(surface=self.screen, rect=drawing_rect2, color=[120, 55, 170])
                        pygame.draw.line(surface=self.screen, color=[120, 55, 170],
                                         start_pos=drawing_rect.center, end_pos=drawing_rect2.center)

                    for entity in creature.vision_entities:
                        rect_left = entity.x - entity.radius
                        rect_top = entity.y - entity.radius
                        drawing_rect2 = pygame.Rect(rect_left, rect_top, entity.radius * 2,
                                                    entity.radius * 2)
                        drawing_rect2.x = world_rect.x + round(drawing_rect2.x / scale)
                        drawing_rect2.y = world_rect.y + round(drawing_rect2.y / scale)
                        drawing_rect2.width *= self.zoom_level
                        drawing_rect2.height *= self.zoom_level

                        pygame.draw.rect(surface=self.screen, rect=drawing_rect2, color=[255, 0, 0])
                        pygame.draw.line(surface=self.screen, color=[255, 0, 0],
                                         start_pos=drawing_rect.center, end_pos=drawing_rect2.center)

                    # Display the centre position of the creature
                    pygame.draw.circle(surface=self.screen, center=drawing_rect.center, radius=1, color=(255, 255, 244))

                    # Display the radius of the creature
                    pygame.draw.circle(surface=self.screen, center=drawing_rect.center,
                                       radius=creature.genes.radius.value * self.zoom_level, color=(255, 255, 244),
                                       width=1)

                    # Display the Range Search area for the creature's vision and collision detection
                    pygame.draw.circle(surface=self.screen, center=drawing_rect.center,
                                       radius=(
                                                      2 * creature.genes.vision_radius.value + world.largest_radius) * self.zoom_level,
                                       color=(220, 20, 60), width=1)

                    # Display the creature's vision radius
                    pygame.draw.circle(surface=self.screen, center=drawing_rect.center,
                                       radius=creature.genes.vision_radius.value * self.zoom_level,
                                       color=(144, 238, 144), width=1)

                    # Display the vision angle of the creature
                    # Calculate the end position of the first line. This is done using the direction the creature is facing.
                    # Add half of the vision radius to it, and then use the cos and sin formula to determine where it should be.
                    direction = creature.direction_radians() + math.radians(creature.genes.vision_angle.value / 2)
                    x_dist = math.cos(direction) * creature.genes.vision_radius.value * self.zoom_level
                    y_dist = math.sin(direction) * creature.genes.vision_radius.value * self.zoom_level
                    pygame.draw.line(surface=self.screen, start_pos=drawing_rect.center,
                                     end_pos=(drawing_rect.center[0] + x_dist, drawing_rect.center[1] + y_dist),
                                     color=(144, 238, 144))

                    direction = creature.direction_radians() - math.radians(creature.genes.vision_angle.value / 2)
                    x_dist = math.cos(direction) * creature.genes.vision_radius.value * self.zoom_level
                    y_dist = math.sin(direction) * creature.genes.vision_radius.value * self.zoom_level
                    pygame.draw.line(surface=self.screen, start_pos=drawing_rect.center,
                                     end_pos=(drawing_rect.center[0] + x_dist, drawing_rect.center[1] + y_dist),
                                     color=(144, 238, 144))

                    # Display the entity that the creature is "seeing"
                    if creature.visible_entity:
                        rect_left = creature.visible_entity.x - creature.visible_entity.radius
                        rect_top = creature.visible_entity.y - creature.visible_entity.radius
                        drawing_rect2 = pygame.Rect(rect_left, rect_top, creature.visible_entity.radius * 2,
                                                    creature.visible_entity.radius * 2)
                        drawing_rect2.x = world_rect.x + round(drawing_rect2.x / scale)
                        drawing_rect2.y = world_rect.y + round(drawing_rect2.y / scale)
                        drawing_rect2.width *= self.zoom_level
                        drawing_rect2.height *= self.zoom_level

                        pygame.draw.rect(surface=self.screen, rect=drawing_rect2, color=[255, 255, 255])
                        pygame.draw.line(surface=self.screen, color=[255, 255, 255],
                                         start_pos=drawing_rect.center, end_pos=drawing_rect2.center)

                    # Display the direction the creature is facing towards
                    self.font = pygame.Font('freesansbold.ttf', 2 * self.zoom_level)
                    text = self.font.render(f'{creature.direction}*', color=(255, 255, 255), antialias=True)
                    text_rect = text.get_rect()
                    text_rect.center = (drawing_rect.center[0], drawing_rect.y + 10 * self.zoom_level)
                    self.screen.blit(text, text_rect)

                    # Display the previous reaction of the creature towards an entity
                    if creature.reaction is not None:
                        self.font = pygame.Font('freesansbold.ttf', 2 * self.zoom_level)
                        text = self.font.render(f'{creature.reaction}', color=(255, 255, 255), antialias=True)
                        text_rect = text.get_rect()
                        text_rect.center = (drawing_rect.center[0], drawing_rect.y + 12 * self.zoom_level)
                        self.screen.blit(text, text_rect)

                    # Display the Energy of the creature
                    self.font = pygame.Font('freesansbold.ttf', 2 * self.zoom_level)
                    text = self.font.render(f'{round(creature.energy)}E', color=(255, 255, 255), antialias=True)
                    text_rect = text.get_rect()
                    text_rect.center = (drawing_rect.center[0], drawing_rect.y + 14 * self.zoom_level)
                    self.screen.blit(text, text_rect)

    def move(self, deltatime):
        self.centre_x = self.screen.get_width() // 2
        self.centre_y = self.screen.get_height() // 2
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            self.x_offset += self.camera_speed * deltatime
        elif key[pygame.K_d]:
            self.x_offset -= self.camera_speed * deltatime
        elif key[pygame.K_w]:
            self.y_offset += self.camera_speed * deltatime
        elif key[pygame.K_s]:
            self.y_offset -= self.camera_speed * deltatime

    def zoom(self, change: int):
        if 1 <= self.zoom_level + 2 * change <= 200:
            old_zoom = self.zoom_level
            self.zoom_level += 2 * change
            self.camera_speed += 10 * change

            self.x_offset /= old_zoom / self.zoom_level
            self.y_offset /= old_zoom / self.zoom_level
            # After implementing the offset values, I managed to fix the zoom bug that I had since the beginning.

    @staticmethod
    def check_for_mouse_hover(rect: pygame.Rect):
        mos_x, mos_y = pygame.mouse.get_pos()
        x_inside = False
        y_inside = False

        if mos_x > rect.x and (mos_x < rect.x + rect.w):
            x_inside = True
        if mos_y > rect.y and (mos_y < rect.y + rect.h):
            y_inside = True
        if x_inside and y_inside:
            return True
        return False
