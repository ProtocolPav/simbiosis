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

            for creature in range(start_creatures//start_species):
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
            self.spawn_food()
        if self.delta_second >= 0.2:  # BUG. This will wait until it is 0.2 and then will constnatly keep spawning until it reaches 1
            ...

        for c in self.creatures:
            c.tick(deltatime)
            if c.dead:
                self.creatures.remove(c)

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
                if not self.tree.find(temporary_coordinates):
                    spawned = True
                    self.food.append(Food(temporary_coordinates[0],
                                          temporary_coordinates[1],
                                          self.food_image,
                                          (self.size, self.size)))
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

    def draw_world(self, world: World):
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
            drawing_rect = pygame.Rect(rect_left, rect_top, creature.genes.radius.value * 2, creature.genes.radius.value * 2)
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
                # pygame.draw.rect(surface=self.screen, rect=drawing_rect, color=colour_to_draw)
                # pygame.draw.circle(surface=self.screen, center=drawing_rect.center, radius=1, color=(255, 255, 244))
                # pygame.draw.circle(surface=self.screen, center=drawing_rect.center,
                #                    radius=creature.genes.radius.value * self.zoom_level, color=(255, 255, 244), width=1)

    def debug_draw_world(self, world: World):
        pygame.draw.rect(surface=self.screen, color=[0, 10 * 0.7, 27 * 0.7], rect=world.internal_rect)

        for food_cluster in world.food_clusters:
            for food in food_cluster.food:
                pygame.draw.rect(surface=self.screen, rect=food, color=[0, 255, 0])

        for creature in world.creatures:
            pygame.draw.circle(surface=self.screen, center=creature.body.center, radius=1, color=[245, 245, 245])

            if creature.vision_rect is not None:
                pygame.draw.rect(self.screen, [255, 0, 0], creature.vision_rect)

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

            self.x_offset /= old_zoom/self.zoom_level
            self.y_offset /= old_zoom/self.zoom_level
            # After implementing the offset values, I managed to fix the zoom bug that I had since the beginning.
