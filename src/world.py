import math

import pygame

from src.entity import Creature, Food
from src.tree import KDTree
from logs import log

import random


class World:
    def __init__(self, size: int, creature_image: pygame.Surface, food_image: pygame.Surface,
                 start_species: int = 4, start_creatures: int = 10, start_food: int = 500):
        self.size = size

        self.creature_image = creature_image
        self.food_image = food_image

        self.creatures: list[Creature] = []
        self.food: list[Food] = []
        self.tree: KDTree = KDTree([])
        self.largest_radius = 0

        self.seconds = 0
        self.delta_second = 0
        # I decided to add a delta_second variable.
        # This counts all the deltatime until it adds up to over a second, then it restarts.

        for i in range(start_food):
            self.food.append(Food(random.randint(0, self.size - 1),
                                  random.randint(0, self.size - 1),
                                  self.food_image,
                                  (self.size, self.size)))

        for i in range(start_species):
            specimen = Creature(random.randint(0, self.size - 1),
                                random.randint(0, self.size - 1),
                                self.creature_image,
                                (self.size, self.size))

            if specimen.radius >= self.largest_radius:
                self.largest_radius = specimen.radius

            for creature in range(start_creatures // start_species):
                self.creatures.append(Creature(random.randint(0, self.size - 1),
                                               random.randint(0, self.size - 1),
                                               self.creature_image,
                                               (self.size, self.size),
                                               specimen.genes))

    def tick_world(self, deltatime: float):
        self.seconds += deltatime
        self.delta_second += deltatime

        self.tree = KDTree(self.creatures + self.food)

        if self.delta_second >= 1:
            self.delta_second = 0
        if self.delta_second >= 0.2:  # BUG. This will wait until it is 0.2 and then will constnatly keep spawning until it reaches 1
            self.spawn_food()

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
                self.creatures.remove(creature)

    def spawn_food(self):
        food = random.choice(self.food) if len(self.food) != 0 else None

        if food is None:
            self.food.append(Food(random.randint(0, self.size - 1),
                                  random.randint(0, self.size - 1),
                                  self.food_image,
                                  (self.size, self.size)))
        else:
            spawned = False
            while not spawned:
                # Does not check for if it is out of bounds yet
                temporary_coordinates = (food.x + random.randint(-5, 5), food.y + random.randint(-5, 5))

                new_food = Food(temporary_coordinates[0],
                                temporary_coordinates[1],
                                self.food_image,
                                (self.size, self.size))

                if not self.tree.find(temporary_coordinates) and new_food.within_border():
                    spawned = True
                    self.food.append(new_food)
                else:
                    food = random.choice(self.food)


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

                    pygame.draw.circle(surface=self.screen, center=drawing_rect.center, radius=1, color=(255, 255, 244))

                    pygame.draw.circle(surface=self.screen, center=drawing_rect.center,
                                       radius=creature.genes.radius.value * self.zoom_level, color=(255, 255, 244),
                                       width=1)

                    pygame.draw.circle(surface=self.screen, center=drawing_rect.center,
                                       radius=(2 * creature.genes.vision_radius.value + world.largest_radius) * self.zoom_level,
                                       color=(220, 20, 60), width=1)

                    pygame.draw.circle(surface=self.screen, center=drawing_rect.center,
                                       radius=creature.genes.vision_radius.value * self.zoom_level,
                                       color=(144, 238, 144), width=1)

                    self.font = pygame.Font('freesansbold.ttf', 2*self.zoom_level)
                    text = self.font.render(f'{creature.direction}*', color=(255, 255, 255), antialias=True)
                    text_rect = text.get_rect()
                    text_rect.center = (drawing_rect.center[0], drawing_rect.y+10*self.zoom_level)
                    self.screen.blit(text, text_rect)

                    # Calculate the end position of the first line. This is done using the direction the creature is facing.
                    # Add half of the vision radius to it, and then use the cos and sin formula to determine where it should be.
                    direction = creature.direction_radians() + math.radians(creature.genes.vision_angle.value)
                    x_dist = math.cos(direction) * creature.genes.vision_radius.value * self.zoom_level
                    y_dist = math.sin(direction) * creature.genes.vision_radius.value * self.zoom_level
                    pygame.draw.line(surface=self.screen, start_pos=drawing_rect.center,
                                     end_pos=(drawing_rect.center[0] + x_dist, drawing_rect.center[1] + y_dist),
                                     color=(144, 238, 144))

                    direction = creature.direction_radians() - math.radians(creature.genes.vision_angle.value)
                    x_dist = math.cos(direction) * creature.genes.vision_radius.value * self.zoom_level
                    y_dist = math.sin(direction) * creature.genes.vision_radius.value * self.zoom_level
                    pygame.draw.line(surface=self.screen, start_pos=drawing_rect.center,
                                     end_pos=(drawing_rect.center[0] + x_dist, drawing_rect.center[1] + y_dist),
                                     color=(144, 238, 144))

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

                    if creature.reaction is not None:
                        self.font = pygame.Font('freesansbold.ttf', 2 * self.zoom_level)
                        text = self.font.render(f'{creature.reaction[0]}', color=(255, 255, 255), antialias=True)
                        text_rect = text.get_rect()
                        text_rect.center = (drawing_rect.center[0], drawing_rect.y + 20 * self.zoom_level)
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
