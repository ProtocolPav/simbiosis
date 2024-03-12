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
        self.mouse_down = False

        BaseEntity.id += 1
        log(f"[ENTITY] Created Entity {type(self).__name__} with ID {self.id}")

    def get_coordinates(self) -> tuple[float, float]:
        return self.x, self.y

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.radius * 2, self.radius * 2)

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
        # elif (not 0 <= self.x + self.radius <= self.world_bottom_right[0] or
        #       not 0 <= self.x - self.radius <= self.world_bottom_right[0] or
        #       not 0 <= self.y + self.radius <= self.world_bottom_right[1] or
        #       not 0 <= self.y - self.radius <= self.world_bottom_right[1]):
        #     return False

        return False


class Creature(BaseEntity):
    def __init__(self, x_position: float, y_position: float, image: pygame.Surface, world_bottomright: tuple[int, int],
                 genes: CreatureGenes, energy: float, direction: float, food_list: list, seeing: bool,
                 memory_reaction: int, dead: bool, entity_id: int = None):
        self.id = Creature.id if entity_id is None else entity_id

        self.genes = genes
        self.energy = energy
        self.direction = direction
        self.food_list = food_list

        # Attributes used for debug
        self.reaction = None
        self.visible_entity = None
        self.check_entities = []
        self.all_check_entities = []
        self.vision_entities = []
        self.child = None

        # Memory attributes
        self.seeing = seeing
        self.memory_reaction = memory_reaction

        self.dead = dead

        super().__init__(x_position, y_position, self.genes.radius.value, image, world_bottomright)

    @classmethod
    def load(cls, x_position: float, y_position: float, image: pygame.Surface, world_bottomright: tuple[int, int],
             genes: CreatureGenes, energy: float, direction: float, seeing: bool,
             memory_reaction: int, dead: bool, entity_id: int = None):

        return cls(x_position, y_position, image, world_bottomright, genes=genes, energy=energy,
                   dead=dead, direction=direction, food_list=[], memory_reaction=memory_reaction, seeing=seeing,
                   entity_id=entity_id)

    @classmethod
    def create(cls, x_position: float, y_position: float, image: pygame.Surface, world_bottomright: tuple[int, int]):
        creature_genes = CreatureGenes.create(species=1, generation=1)
        start_energy = creature_genes.base_energy.value * 6000
        return cls(x_position, y_position, image, world_bottomright, genes=creature_genes, energy=start_energy,
                   dead=False, direction=random.randint(0, 360), food_list=[], memory_reaction=0, seeing=False)

    @classmethod
    def create_child(cls, x_position: float, y_position: float, image: pygame.Surface,
                     world_bottomright: tuple[int, int],
                     genes: CreatureGenes, energy: float):
        genes.generation.value += 1
        return cls(x_position, y_position, image, world_bottomright, genes=genes, energy=energy,
                   dead=False, direction=random.randint(0, 360), food_list=[], memory_reaction=0, seeing=False)

    def __repr__(self):
        return f"Creature(ID{self.id}, x={self.x}, y={self.y}, a={self.direction}, dead={self.dead}))"

    def direction_radians(self) -> float:
        """
        Returns the direction the creature is facing in radians
        :return:
        """
        return self.direction / (180 / math.pi)

    @staticmethod
    def map_angle(angle: float, max_range: int = 360) -> float:
        """
        Maps the angle given to fall within [0, 360]
        :param max_range:
        :param angle:
        :return:
        """
        return angle % max_range

    def move(self, deltatime: float):
        x_dist = math.cos(self.direction_radians()) * self.genes.speed.value * deltatime
        y_dist = math.sin(self.direction_radians()) * self.genes.speed.value * deltatime

        self.energy -= self.genes.movement_energy.value * math.sqrt(x_dist ** 2 + y_dist ** 2)

        self.x += x_dist
        self.y += y_dist

        if not self.within_border():
            self.direction = self.map_angle(self.direction - 90)
            self.energy -= self.genes.turning_energy.value * 1

    def collision(self, entity: BaseEntity) -> bool:
        """
        Checks if the creature is colliding with another Entity.
        :param entity:
        :return:
        """
        distance_between_points = math.sqrt((self.x - entity.x) ** 2 + (self.y - entity.y) ** 2)
        if distance_between_points <= self.radius + entity.radius:
            return True

        return False

    def vision(self, entity: BaseEntity) -> bool:
        # Because of how pygame works, angle 0 is facing to the right, and 270 is facing up
        vector = (entity.x - self.x,
                  entity.y - self.y)
        vector_distance = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
        if vector_distance < self.genes.vision_radius.value:
            self.check_entities.append(entity)

            # Map the bearing to the range [0, 360] and flip the angle
            bearing = self.map_angle(-1 * math.degrees(math.atan2(-1 * vector[1], vector[0])))

            left_boundary = self.map_angle(self.direction - self.genes.vision_angle.value // 2)
            right_boundary = self.map_angle(self.direction + self.genes.vision_angle.value // 2)

            # Checks for the minimum and maximum values, since sometimes the right boundary goes over 360 and
            # becomes a small value (e.g. 366 becomes 6 degrees)

            if left_boundary < right_boundary and left_boundary <= bearing <= right_boundary:
                return True
            elif (left_boundary > right_boundary) and (left_boundary <= bearing <= 360 or 0 <= bearing <= right_boundary):
                return True
            else:
                ...
                # Check if line segments intersect. Later...

        return False

    def react(self, entity: BaseEntity, deltatime):
        towards = 1
        away = -1

        if not self.seeing:
            offset = 0

            if isinstance(entity, Food):
                offset += self.genes.food_offset.value
            elif isinstance(entity, Creature):
                if entity.genes.species.value == self.genes.species.value:
                    offset += self.genes.known_offset.value
                else:
                    offset += self.genes.stranger_offset.value

            probability_towards = abs(self.genes.react_towards.value + offset)

            reaction = random.choices([towards, away],
                                      [probability_towards, 1 - probability_towards])[0]
            self.reaction = reaction
            self.memory_reaction = reaction
        else:
            reaction = self.memory_reaction

        vector = (entity.x - self.x,
                  entity.y - self.y)
        bearing = self.map_angle(-1 * math.degrees(math.atan2(-1 * vector[1], vector[0])))

        if bearing > self.direction:
            self.direction = self.map_angle(self.direction + self.genes.react_speed.value * reaction * deltatime)
        elif bearing < self.direction:
            self.direction = self.map_angle(self.direction - self.genes.react_speed.value * reaction * deltatime)

        self.energy -= self.genes.turning_energy.value * self.genes.react_speed.value * deltatime

        log(f"[REACTION] Creature {self.id} is reacting {'Towards' if reaction == 1 else 'Away'} {type(entity).__name__} {entity.id}")

    def birth(self, parent=None):
        if self.energy > self.genes.birth_energy.value:
            self.energy -= self.genes.birth_energy.value

            child_genes = copy.deepcopy(self.genes)
            if parent is None:
                for gene, gene_object in vars(child_genes).items():
                    gene_object.mutate()
            else:
                parent_genes = vars(parent.genes)
                for gene, gene_object in vars(child_genes).items():
                    gene_object.value = (gene_object.value + parent_genes[gene].value) // 2
                    gene_object.mutate()

            new_coords = [self.x + random.uniform(self.radius * 4, self.radius * 8) * random.choice([1, -1]),
                          self.y + random.uniform(self.radius * 4, self.radius * 8) * random.choice([1, -1])]

            self.child = Creature.create_child(new_coords[0], new_coords[1], self.image,
                                               self.world_bottom_right, child_genes, self.genes.birth_energy.value)

            if not self.child.within_border():
                self.child.dead = True

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
            self.vision_entities = []

            for entity in range_search_box:
                self.all_check_entities.append(entity)
                if self.vision(entity):
                    log(f"[VISION] Creature {self.id} is seeing {type(entity).__name__} {entity.id}")
                    self.vision_entities.append(entity)

            chosen_entity = random.choice(self.vision_entities) if len(self.vision_entities) != 0 else None
            if chosen_entity:
                self.visible_entity = chosen_entity
                self.react(chosen_entity, deltatime)
                self.seeing = True
            else:
                self.seeing = False

            self.move(deltatime)

            for entity in range_search_box:
                if self.collision(entity) and isinstance(entity, Food) and not entity.eaten:
                    log(f"[CONSUME] Creature {self.id} is eating {type(entity).__name__} {entity.id}")
                    entity.eaten = True
                    self.energy += entity.energy * self.genes.plant_energy.value
                    self.food_list.append(entity)
                    if random.randint(1, 200) == 1:
                        self.birth()

                elif self.collision(entity) and isinstance(entity, Creature):
                    log(f"[COLLIDE] Creature {self.id} is colliding with {type(entity).__name__} {entity.id}")
                    self.birth(entity)
                    angle = random.randint(90, 180)
                    self.direction += angle
                    self.energy -= self.genes.turning_energy.value * angle

        if self.energy <= 0:
            self.dead = True


class Food(BaseEntity):
    def __init__(self, x_position: float, y_position: float, image: pygame.Surface, world_bottomright: tuple[int, int],
                 energy: float, eaten: bool = False):
        super().__init__(x_position, y_position, 0.5, image, world_bottomright)

        self.energy = energy
        self.eaten = eaten

    @classmethod
    def load(cls, x_position: float, y_position: float, image: pygame.Surface, world_bottomright: tuple[int, int],
             energy: float, eaten: bool):
        return cls(x_position, y_position, image, world_bottomright, energy, eaten)

    @classmethod
    def create(cls, x_position: float, y_position: float, image: pygame.Surface, world_bottomright: tuple[int, int],
               min_energy: int, max_energy: int):
        return cls(x_position, y_position, image, world_bottomright, random.randint(min_energy, max_energy))

    def __repr__(self):
        return f"Food(ID{self.id}, x={self.x}, y={self.y}, eaten={self.eaten}))"
