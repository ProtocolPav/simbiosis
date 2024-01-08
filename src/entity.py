import math
import copy
import random

import pygame

from logs import log
from src.genes import CreatureGenes

# I decided to make a Base Entity class since both food and creatures were in the same tree, in the old implementation
# I would keep getting errors since they did not have the same methods to get the x and y coordinates


class BaseEntity:
    """
    Base Entity class to inherit from. Stores the basics such as position, rect and image
    """
    id = 1

    def __init__(self, x_position: float, y_position: float, radius: float, image: pygame.Surface,
                 world_bottomright: tuple[int, int]):
        self.id = BaseEntity.id
        self.x = x_position
        self.y = y_position
        self.radius = radius
        self.image = image
        self.world_bottom_right = world_bottomright

        BaseEntity.id += 1
        # log(f"[ENTITY] Created Entity with ID {self.id}")

    def get_coordinates(self) -> tuple[float, float]:
        return self.x, self.y

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.radius*2, self.radius*2)

    def within_border(self) -> bool:
        """
        Checks whether the centre lies within the borders.
        If it does, then it checks to see if the circle collides with the borders
        by adding and subtracting the radius to the x and y-axis
        :return:
        """
        if 0 <= self.x <= self.world_bottom_right[0] and 0 <= self.y <= self.world_bottom_right[1]:
            return True
        # This needs work and testing. Essentially this whole if statememnt is never True
        elif (not 0 <= self.x + self.radius <= self.world_bottom_right[0] or
              not 0 <= self.x - self.radius <= self.world_bottom_right[0] or
              not 0 <= self.y + self.radius <= self.world_bottom_right[1] or
              not 0 <= self.y - self.radius <= self.world_bottom_right[1]):
            return False

        return False


class Creature(BaseEntity):
    def __init__(self, x_position: float, y_position: float, image: pygame.Surface, world_bottomright: tuple[int, int],
                 genes: CreatureGenes = None, energy: float = None):
        self.id = Creature.id

        self.genes = CreatureGenes(species=1, generation=1) if genes is None else genes
        self.energy = self.genes.base_energy.value * 6000 if energy is None else energy
        self.direction = random.randint(0, 360)
        self.food_list = []

        # Attributes used for debug
        self.reaction = None
        self.visible_entity = None
        self.check_entities = []
        self.all_check_entities = []
        self.child = None

        # Memory attributes
        self.memory_entity = self
        self.memory_reaction = None

        self.dead = False

        super().__init__(x_position, y_position, self.genes.radius.value, image, world_bottomright)

    def __repr__(self):
        return f"Creature(ID{self.id}, x={self.x}, y={self.y}, a={self.direction}, dead={self.dead}))"

    def direction_radians(self) -> float:
        """
        Returns the direction the creature is facing in radians
        :return:
        """
        return self.direction / (180 / math.pi)

    @staticmethod
    def map_angle(angle: float) -> float:
        """
        Maps the angle given to fall within [0, 360]
        :param angle:
        :return:
        """
        return angle % 360

    def move(self, deltatime: float):
        if not self.within_border():
            # The values need tweaking as sometimes they bug out and leave the border
            angle = random.randint(90, 180)
            self.direction = self.map_angle(self.direction + angle)
            self.energy -= self.genes.turning_energy.value * angle

        x_dist = math.cos(self.direction_radians()) * self.genes.speed.value * deltatime
        y_dist = math.sin(self.direction_radians()) * self.genes.speed.value * deltatime

        self.energy -= self.genes.movement_energy.value * math.sqrt(x_dist**2 + y_dist**2)

        self.x += x_dist
        self.y += y_dist

    def collision(self, entity: BaseEntity) -> bool:
        """
        Checks if the creature is colliding with another Entity.
        :param entity:
        :return:
        """
        distance_between_points = math.sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2)
        if distance_between_points <= self.radius + entity.radius:
            return True

        return False

    def vision(self, entity: BaseEntity) -> bool:
        # Because of how pygame works, angle 0 is facing to the right, and 360 is facing up
        vector = (entity.x - self.x,
                  entity.y - self.y)
        vector_distance = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
        if vector_distance < self.genes.vision_radius.value:
            self.check_entities.append(entity)
            bearing = math.degrees(math.atan2(vector[1], vector[0]))

            angular_distance = self.map_angle(max(bearing, self.direction) - min(bearing, self.direction))
            # Sometimes the distance tends to 360 and idk why
            # I believe the issue here is with the angular distance

            # print(vector, vector_distance, bearing, angular_distance, self.genes.vision_angle.value)

            if angular_distance < self.genes.vision_angle.value:
                return True
            else:
                ...
                # Check if line segments intersect. Later...

        return False

    def react(self, entity: BaseEntity):
        towards = 1
        away = -1

        if entity.id != self.memory_entity.id:
            reaction = random.choices([towards, away],
                                      [self.genes.react_towards.value, self.genes.react_away.value])[0]
            self.reaction = reaction
            self.memory_reaction = reaction
        else:
            reaction = self.memory_reaction

        vector = (entity.x - self.x,
                  entity.y - self.y)
        bearing = math.degrees(math.atan2(vector[1], vector[0]))

        if bearing >= 0:
            self.direction = self.map_angle(self.direction + self.genes.react_speed.value*reaction)
        elif bearing < 0:
            self.direction = self.map_angle(self.direction - self.genes.react_speed.value*reaction)

        self.energy -= self.genes.turning_energy.value * self.genes.react_speed.value
        print(f"{self.id} is Reacting {'Towards' if reaction == 1 else 'Away'}")

    def birth(self):
        if self.energy > self.genes.birth_energy.value:
            self.energy -= self.genes.birth_energy.value

            self.child = Creature(self.x+self.radius*2, self.y-self.radius*2, self.image, self.world_bottom_right,
                                  copy.deepcopy(self.genes), energy=self.genes.birth_energy.value)

            for gene, gene_object in vars(self.child.genes).items():
                gene_object.mutate()

    def tick(self, deltatime: float, range_search_box: list[BaseEntity]):
        """
        Runs all the processes of the creature, movement, vision, collision
        :param range_search_box:
        :param deltatime:
        :return:
        """
        self.food_list = []

        if not self.dead:
            self.energy -= self.genes.base_energy.value * deltatime

            self.check_entities = []
            self.all_check_entities = []

            for entity in range_search_box:
                self.all_check_entities.append(entity)
                if self.vision(entity):
                    print(f"{self.id} is seeing {entity.id}")
                    self.visible_entity = entity
                    self.react(entity)

                    self.memory_entity = entity

            self.move(deltatime)

            for entity in range_search_box:
                if self.collision(entity) and isinstance(entity, Food) and not entity.eaten:
                    print(f"{self.id} is eating Food {entity.id}")
                    entity.eaten = True
                    self.energy += entity.energy
                    self.food_list.append(entity)

                elif self.collision(entity) and isinstance(entity, Creature):
                    print(f"{self.id} is colliding with Creature {entity.id}")
                    # self.birth()
                    # angle = random.randint(90, 180)
                    # self.direction += angle
                    # self.energy -= self.genes.turning_energy.value * angle

            if random.randint(1, 5) == 1:
                self.birth()

        if self.energy <= 0:
            self.dead = True


class Food(BaseEntity):
    def __init__(self, x_position: float, y_position: float, image: pygame.Surface, world_bottomright: tuple[int, int]):
        # Perhaps the radius can be determined by the energy amount?
        super().__init__(x_position, y_position, 0.5, image, world_bottomright)

        self.energy = random.uniform(100, 1000)
        self.eaten = False

    def __repr__(self):
        return f"Food(ID{self.id}, x={self.x}, y={self.y}, eaten={self.eaten}))"
