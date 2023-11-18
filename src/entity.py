import math
import copy
import random

import pygame

from src.logs import log
from src.genes import CreatureGenes


class BaseEntity:
    """
    Base Entity class to inherit from. Stores the basics such as position, rect and image
    """
    def __init__(self, x_position: float, y_position: float, radius: float, image: pygame.Surface,
                 world_bottomright: tuple[int, int]):

        self.x = x_position
        self.y = y_position
        self.radius = radius
        self.image = image
        self.world_bottom_right = world_bottomright

    def get_coordinates(self) -> tuple[float, float]:
        return self.x, self.y

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.radius*2, self.radius*2)


class Creature(BaseEntity):
    id = 1

    def __init__(self, x_position: float, y_position: float, image: pygame.Surface, world_bottomright: tuple[int, int],
                 genes: CreatureGenes = None, energy: float = None):
        self.id = Creature.id

        self.genes = CreatureGenes(species=1, generation=1) if genes is None else genes
        self.energy = self.genes.base_energy.value * 6000 if energy is None else energy
        self.direction = random.randint(0, 360)

        self.dead = False

        super().__init__(x_position, y_position, self.genes.radius.value, image, world_bottomright)
        Creature.id += 1

    def __repr__(self):
        return f"Creature(ID{self.id}, x={self.x}, y={self.y}, a={self.direction}, dead={self.dead}))"

    def direction_radians(self) -> float:
        """
        Returns the direction the creature is facing in radians
        :return:
        """
        return self.direction / (180 / math.pi)

    def update_direction(self, angle: float):
        """
        Updates the direction of the creature, making sure the value falls within [0, 360]
        :param angle:
        :return:
        """
        ...

    def within_border(self) -> bool:
        """
        Checks whether the centre lies within the borders.
        If it does, then it checks to see if the circle collides with the borders
        by adding and subtracting the radius to the x and y-axis
        :return:
        """
        if 0 <= self.x <= self.world_bottom_right[0] and 0 <= self.y <= self.world_bottom_right[1]:
            return False
        elif 0 <= self.x + self.radius <= self.world_bottom_right[0] or 0 <= self.x - self.radius <= self.world_bottom_right[0]:
            return False
        elif 0 <= self.y + self.radius <= self.world_bottom_right[1] or 0 <= self.y - self.radius <= self.world_bottom_right[1]:
            return False

        return True

    def move(self, deltatime: float):
        if not self.within_border():
            # The values need tweaking as sometimes they bug out and leave the border
            self.direction += random.randint(90, 180)

        x_dist = math.cos(self.direction_radians()) * self.genes.speed.value * deltatime
        y_dist = math.sin(self.direction_radians()) * self.genes.speed.value * deltatime

        self.energy -= self.genes.movement_energy.value * math.sqrt(x_dist**2 + y_dist**2)

        self.x += x_dist
        self.y += y_dist

    def tick(self, deltatime: float) -> bool:
        """
        Runs all the processes of the creature, movement, vision, collision and returns True if the creature has died
        :param deltatime:
        :return:
        """
        if not self.dead:
            self.energy -= self.genes.base_energy.value * deltatime
            self.move(deltatime)

        if self.energy <= 0:
            self.dead = True

        return self.dead


class Food(BaseEntity):
    id = 1

    def __init__(self, x_position: float, y_position: float, image: pygame.Surface, world_bottomright: tuple[int, int]):
        # Perhaps the radius can be determined by the energy amount?
        super().__init__(x_position, y_position, 0.5, image, world_bottomright)

        self.id = Food.id
        self.energy = random.uniform(100, 1000)
        self.eaten = False

    def __repr__(self):
        return f"Food(ID{self.id}, x={self.x}, y={self.y}, eaten={self.eaten}))"
