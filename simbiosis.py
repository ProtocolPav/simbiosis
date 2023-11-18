# Alpha v0.4
import math
import copy
import random
import yaml

from datetime import datetime

import pygame
from pygame import Rect

time_now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
logfile = open(f"./logs/log-{time_now}.txt", "w")

logfile.write(f"Start Simbiosis Simulation v0.4\n"
              f"Start Time: {time_now}\n\n\n"
              f"Runtime Logs:\n"
              f"{'-' * 60}\n")

pygame.init()

creature_image = pygame.image.load('textures/creature3.png')
food_image = pygame.image.load('textures/food1.png')

pygame.display.set_caption("Simbiosis - Evolution Simulator")

clock = pygame.time.Clock()


def log(message: str):
    print(f"[{datetime.now()}]", message)
    logfile.write(f"[{datetime.now()}] {message}\n")


class Node:
    def __init__(self, data, left_node, right_node):
        self.data = data
        self.left_child = left_node
        self.right_child = right_node

    def __repr__(self):
        try:
            left_data = self.left_child.data
        except:
            left_data = None

        try:
            right_data = self.right_child.data
        except:
            right_data = None
        return f"Left: {left_data}\tData: {self.data}\tRight: {right_data}"


class KDTree:
    def __init__(self, points: list, depth: int = 0):
        self.nodes = []
        self.__create_tree(points, depth)
        log(f"Tree Size {len(self.nodes)}")

    def __create_tree(self, points: list, depth: int = 0):
        # Get the axis to sort the points by initially. The root note will be 0, and thus give me the x-axis (0)
        axis = depth % 2
        if len(points) != 0:
            points.sort(key=lambda x: (x.x_pos() if axis == 0 else x.y_pos()))
            middle_value = len(points) // 2
            median_point = points[middle_value]

            left = self.__create_tree(points[0:middle_value], depth + 1)
            right = self.__create_tree(points[middle_value + 1:], depth + 1)

            node = Node(median_point, left, right)
            self.nodes.insert(0, node)
            return node

    def range_search(self, point: tuple[float, float], radius: float):
        ...


class World:
    def __init__(self, size: int, start_species: int = 4, start_creatures: int = 10,
                 start_cluster: int = 10):
        world_size = size
        self.internal_rect = pygame.Rect(0, 0, world_size, world_size)
        self.borders = [pygame.Rect(0, -1, world_size, 1),
                        pygame.Rect(-1, 0, 1, world_size),
                        pygame.Rect(0, world_size, world_size, 1),
                        pygame.Rect(world_size, 0, 1, world_size)]
        self.creatures: list[Creature] = []
        self.food_clusters: list[FoodCluster] = []
        self.ticks = 0
        self.game_paused = False
        self.tree = None

        for i in range(start_species):
            species_creature = Creature(self, random.randint(60, world_size - 60), random.randint(60, world_size - 60))
            for j in range(start_creatures):
                x = species_creature.x_pos() + random.randint(-50, 50)
                y = species_creature.y_pos() + random.randint(-50, 50)
                self.creatures.append(Creature(self, x, y, genes=copy.deepcopy(species_creature.genes)))

        for i in range(start_cluster):
            cluster = FoodCluster(random.randint(1, self.internal_rect.w - 1),
                                  random.randint(1, self.internal_rect.h - 1))
            self.food_clusters.append(cluster)

    def tick_game(self, deltatime):
        if not self.game_paused:
            tree_list = []

            if random.choices(population=["no", "spawn cluster"], weights=[499, 1])[0] == "spawn cluster":
                self.food_clusters.append(FoodCluster(random.randint(1, self.internal_rect.w - 1),
                                                      random.randint(1, self.internal_rect.h - 1)))

            for cluster in self.food_clusters:
                if len(cluster.food) == 0:
                    self.food_clusters.remove(cluster)
                else:
                    cluster.spawn_food(self.internal_rect)
                    cluster.tick_food(tree_list)

            for creature in self.creatures:
                creature.move(deltatime)
                tree_list.append(creature)

            self.tree = KDTree(tree_list)

    def get_creature(self, creature_id):
        for creat in self.creatures:
            if creat.id == creature_id:
                return creat

    def spawn_food(self):
        ...


class Food(pygame.Rect):
    id = 0

    def __init__(self, pos_x: int, pos_y: int, time_to_live: int, parent_cluster):
        super().__init__(pos_x, pos_y, 1, 1)
        self.id = Food.id
        self.total_ticks = time_to_live
        self.ticks = 0
        self.cluster = parent_cluster
        self.energy = random.randint(5000, 75000)
        self.eaten = False

        Food.id += 1

    def __repr__(self):
        return f"Food({self.id}, {self.x}, {self.y})"

    def x_pos(self):
        return self.x

    def y_pos(self):
        return self.y


class FoodCluster:
    id = 0

    def __init__(self, centre_x: int, centre_y: int):
        self.food: list[Food] = [Food(centre_x, centre_y, 500, self)]

    def spawn_food(self, world_rect: Rect):
        loop_length = 1 + (len(self.food) // 100) * 2

        for i in range(loop_length):
            chance_of_spawning = random.choices(population=["no spawn", "spawn"], weights=[90, 10])[0]
            if chance_of_spawning == "spawn":
                food = random.choice(self.food)
                dy = random.randint(-2, 2)
                dx = random.randint(-2, 2)

                food_rect: Rect = pygame.Rect(food.x + dx, food.y + dy, 1, 1)
                collision = food_rect.collidelist(self.food)

                # Coordinates
                world_top_left = (0, 0)
                world_bottom_right = (world_rect.w, world_rect.h)
                food_coordinate = (food.x + dx, food.y + dy)

                y_check = world_top_left[1] < food_coordinate[1] < world_bottom_right[1]
                x_check = world_top_left[0] < food_coordinate[0] < world_bottom_right[0]

                if collision == -1 and y_check and x_check:
                    new_food = Food(food_rect.x, food_rect.y, random.randint(50, 500), self)
                    self.food.append(new_food)

    def remove_food(self, food: Food):
        if not food.eaten:
            food.eaten = True
            self.food.remove(food)

    def tick_food(self, tree_list: list):
        food_to_remove = []

        for food in self.food:
            food.ticks += 1

            if food.ticks >= food.total_ticks:
                food_to_remove.append(food)
            else:
                tree_list.append(food)

        for food in food_to_remove:
            self.remove_food(food)


class CreatureBody(pygame.Rect):
    id = 1

    def __init__(self, creature_id: int, pos_x: int, pos_y: int):
        super().__init__(pos_x, pos_y, 1, 1)

        # log(f"Created Body with ID{CreatureBody.id}")
        self.id = CreatureBody.id
        self.creature_id = creature_id
        self.actual_x = self.x
        self.actual_y = self.y

        CreatureBody.id += 1

    def __repr__(self):
        return f"Body({self.id, self.x, self.y, self.width, self.height})"

    def collision_check(self, collision_dict: dict):
        collision = self.collidedict(collision_dict, True)

        if collision:
            return collision[1]
        else:
            return None


class Gene:
    def __init__(self, name: str, acronym: str, value: float, can_mutate: bool = True):
        self.name = name
        self.acronym = acronym.upper()
        self.value = value
        self.can_mutate = can_mutate

    def mutate(self):
        if self.can_mutate:
            old_value = self.value

            if random.choices(population=["mutate", "no mutate"], weights=[50, 250])[0] == "mutate":
                if self.acronym in ['CLR', 'CLB', 'CLG']:
                    self.value += random.randint(2, 2)
                    if self.value < 0:
                        self.value = 10
                    elif self.value > 255:
                        self.value = 245
                else:
                    self.value += random.uniform(-0.2, 0.2)

                if self.acronym in ['CLH', 'RTL', 'RTR', 'RTB', 'RTW', 'RAW', 'RBO', 'RTF', 'RAF', 'RLF', 'RRF', 'RBF']:
                    if self.value < 0:
                        self.value = abs(self.value)
                    elif self.value > 1:
                        self.value -= 1

            if old_value == self.value:
                log(f"[MUTATION] {self.name} No Change")
            else:
                log(f"[MUTATION] {self.name} ({old_value} -> {self.value})")


class CreatureGenes:
    def __init__(self, species: int, generation: int):
        # Genes affecting Creature Appearance (Phenotype)
        self.colour_red = Gene(name="Red Colour", acronym="CLR", value=random.randint(0, 255))
        self.colour_green = Gene(name="Green Colour", acronym="CLG", value=random.randint(0, 255))
        self.colour_blue = Gene(name="Blue Colour", acronym="CLB", value=random.randint(0, 255))
        self.radius = Gene(name="Creature Radius Size", acronym="SIZ", value=random.uniform(0.5, 7))

        # Genes affecting Creature movement
        self.idle_speed = Gene(name="Idle Speed", acronym="SID", value=random.uniform(0, 50))
        self.maximum_speed = Gene(name="Maximum Speed", acronym="SMX", value=random.uniform(self.idle_speed.value, 10))
        self.boost_length = Gene(name="Boost Length in Ticks", acronym="BOL", value=random.uniform(0, 20))

        # Genes affecting the Creature's Energy Consumption
        self.energy_per_square = Gene(name="Energy Consumed Per Square Moved", acronym="EPS", value=random.uniform(5, 100))
        self.energy_during_boost = Gene(name="Energy Consumed During Boost", acronym="EBS",
                                        value=random.uniform(self.energy_per_square.value, 200))
        self.energy_to_birth = Gene(name="Energy Consumed To Birth", acronym="EBI", value=random.uniform(100000, 1000000))
        self.energy_to_extend = Gene(name="Energy Consumed To Extend", acronym="EEX", value=random.uniform(5, 100))
        self.critical_hunger = Gene(name="Critical Hunger Level", acronym="HUC",
                                    value=random.uniform(self.energy_per_square.value, 200))

        # Genes affecting Creature Behaviour
        self.vision = Gene(name="Vision", acronym="VIS", value=random.uniform(1, 10))
        self.collision = Gene(name="Collision Behaviour", acronym="COL", value=random.uniform(0, 1))
        self.react_towards = Gene(name="Brain Reaction Towards", acronym="RTW", value=random.random())
        self.react_away = Gene(name="Brain Reaction Away", acronym="RAW", value=random.random())
        self.react_left = Gene(name="Brain Reaction Left", acronym="RTL", value=random.random())
        self.react_right = Gene(name="Brain Reaction Right", acronym="RTR", value=random.random())
        self.react_back = Gene(name="Brain Reaction Back", acronym="RTB", value=random.random())
        self.react_boost = Gene(name="Brain Reaction Boost", acronym="RBO", value=random.random())
        self.react_towards_food = Gene(name="Brain Reaction Towards When Seeing Food", acronym="RTF", value=random.random())
        self.react_away_food = Gene(name="Brain Reaction Away When Seeing Food", acronym="RAF", value=random.random())
        self.react_left_food = Gene(name="Brain Reaction Left When Seeing Food", acronym="RLF", value=random.random())
        self.react_right_food = Gene(name="Brain Reaction Right When Seeing Food", acronym="RRF", value=random.random())
        self.react_back_food = Gene(name="Brain Reaction Back When Seeing Food", acronym="RBF", value=random.random())

        # Data Genes (No mutation, affects Data)
        self.gender = Gene(name="Gender", acronym="GND", value=random.choice([0, 1]), can_mutate=False)
        self.species = Gene(name="Species", acronym="SPE", value=species, can_mutate=False)
        self.generation = Gene(name="Generation", acronym="GEN", value=generation, can_mutate=False)


class Creature:
    id = 1

    def __init__(self, world: World, position_x: int, position_y: int, genes: CreatureGenes = None, start_energy: float = None):
        log(f"Created Creature with ID{Creature.id}")
        self.id = Creature.id

        self.world = world

        self.body = CreatureBody(self.id, position_x, position_y)

        self.genes = CreatureGenes(generation=1, species=1) if genes is None else genes
        if start_energy is None:
            self.energy = self.genes.energy_per_square.value * 5000 * self.genes.radius.value
        else:
            self.energy = start_energy

        self.facing = random.randint(0, 360)
        self.vision_rect = None
        self.dead = False
        self.colliding = False
        self.seeing = False

        Creature.id += 1

    def __repr__(self):
        return f"Creature(ID{self.id}, Body({self.body}))"

    def __vision(self):
        choice_list = ['forward', ['to the right', 'to the left', 'backwards']]
        vision_distance = self.genes.vision.value
        quadrant_check = self.body[0].check_quadrant()
        difference = pygame.Vector2(self.body[0].x - self.body[1].x, self.body[0].y - self.body[1].y)

        # Facing Upwards
        if difference == pygame.Vector2(0, -1):
            self.vision_rect = pygame.Rect(self.body[0].x, self.body[0].y - vision_distance, 1, 1 + vision_distance)
            choice_list = ['up', ['right', 'left', 'down']]

        # Facing Downwards
        elif difference == pygame.Vector2(0, 1):
            self.vision_rect = pygame.Rect(self.body[0].x, self.body[0].y + 1, 1, vision_distance)
            choice_list = ['down', ['left', 'right', 'up']]

        # Facing Left
        elif difference == pygame.Vector2(-1, 0):
            self.vision_rect = pygame.Rect(self.body[0].x - vision_distance, self.body[0].y, 1 + vision_distance, 1)
            choice_list = ['left', ['up', 'down', 'right']]

        # Facing Right
        elif difference == pygame.Vector2(1, 0):
            self.vision_rect = pygame.Rect(self.body[0].x + 1, self.body[0].y, vision_distance, 1)
            choice_list = ['right', ['down', 'up', 'left']]

        collision = self.vision_rect.collidedict(quadrant_check.collisions_dict, True)
        food_collision = self.vision_rect.collidedict(quadrant_check.food_collisions_dict, True)
        border_collision = self.vision_rect.collidelist(world.borders)

        if collision and not self.seeing and self.id != collision[1].creature_id:
            log(f"[VISION] Creature {self.id} is seeing something and reacting")
            self.seeing = True
            new_facing = random.choices(choice_list, [self.genes.react_towards.value, self.genes.react_away.value])[0]
            if type(new_facing) == list:
                self.facing = random.choices(new_facing,
                                             [self.genes.react_right.value,
                                              self.genes.react_left.value,
                                              self.genes.react_back.value])[0]
            else:
                self.facing = new_facing

        elif food_collision and not self.seeing:
            log(f"[VISION] Creature {self.id} is seeing food and reacting. {food_collision}")
            self.seeing = True
            new_facing = random.choices(choice_list, [self.genes.react_towards_food.value, self.genes.react_away_food.value])[0]
            if type(new_facing) == list:
                self.facing = random.choices(new_facing,
                                             [self.genes.react_right_food.value,
                                              self.genes.react_left_food.value,
                                              self.genes.react_back_food.value])[0]
            else:
                self.facing = new_facing

        elif border_collision != -1:
            log(f"[VISION] Creature {self.id} is seeing the border and reacting")
            new_facing = random.choices(choice_list, [self.genes.react_towards.value, self.genes.react_away.value])[0]
            if type(new_facing) == list:
                self.facing = random.choices(new_facing,
                                             [self.genes.react_right.value,
                                              self.genes.react_left.value,
                                              self.genes.react_back.value])[0]
            else:
                self.facing = new_facing

        elif collision is None and food_collision is None and self.seeing:
            self.seeing = False

    def __collide(self):
        quadrant_check = self.body[0].check_quadrant()
        collision = self.body[0].collision_check(quadrant_check.collisions_dict)

        if collision and not self.colliding:
            if self.id != collision.creature_id:
                self.colliding = True

                creature = world.get_creature(collision.creature_id)

                # Get other creature and check the creature's collision value.
                # Collision affects the creature that collided with the other creature, depending on the other's genes
                if creature:
                    log(f"[COLLISION] Creature {self.id} is colliding with another creature")
                    if 0 < creature.genes.collision.value < 1:
                        self.__birth()
                    if 0.75 < creature.genes.collision.value:
                        self.__die()

        elif not collision and self.colliding:
            self.colliding = False

        food_collision = self.body[0].collision_check(quadrant_check.food_collisions_dict)
        food_collision = self.body[0].collidedict(quadrant_check.food_collisions_dict, True)
        if food_collision:
            log(f"[COLLISION] Creature {self.id} is colliding with food {food_collision}")
            self.energy += food_collision[1].energy
            food_collision[1].cluster.remove_food(food_collision[1])
            self.__extend()
            # Make the creature not see anything, so that it can check for more food
            self.seeing = False

    def __extend(self):
        if self.energy - self.genes.energy_to_extend.value > self.genes.critical_hunger.value \
                and len(self.body) + 1 < self.genes.maximum_length.value:
            self.energy -= self.genes.energy_to_extend.value
            self.body.append(CreatureBody(self.id, self.body[-1].x, self.body[-1].y))

    def __birth(self):
        if len(self.body) >= 4 and self.energy - self.genes.energy_to_birth.value > 0:
            log(f"[BIRTH] Creature {self.id} is birthing")
            self.energy -= self.genes.energy_to_birth.value
            body_part = self.body.pop()
            body_part = self.body.pop()

            baby = Creature(body_part.x, body_part.y, copy.deepcopy(self.genes), self.genes.energy_to_birth.value)

            for gene, gene_object in vars(baby.genes).items():
                gene_object.mutate()

            self.world.creatures.append(baby)

    def __die(self):
        if not self.dead:
            log(f"[DEATH] Creature {self.id}")
            self.world.creatures.remove(self)
            self.dead = True

    def x_pos(self):
        return self.body.actual_x

    def y_pos(self):
        return self.body.actual_y

    def facing_radians(self):
        return self.facing / (180 / math.pi)

    def check_collision_with_border(self, x: float, y: float) -> bool:
        # This isnt perfect as it checks just the centre point of the circle, so it produces some visual bugs
        temp_position: tuple[float, float] = (self.body.actual_x + x, self.body.actual_y + y)

        if temp_position[0] >= self.world.internal_rect.w - 2 or temp_position[1] >= self.world.internal_rect.h - 2:
            # Creature is past the border
            return True
        elif temp_position[0] <= 0 or temp_position[1] <= 0:
            # Creature is past the border in the negative directions
            return True

        return False

    def move(self, deltatime):
        self.energy -= self.genes.energy_per_square.value

        if not self.dead:
            # self.__vision()

            self.energy -= self.genes.energy_per_square.value

            x_dist = math.cos(self.facing_radians()) * self.genes.idle_speed.value * deltatime
            y_dist = math.sin(self.facing_radians()) * self.genes.idle_speed.value * deltatime

            if self.check_collision_with_border(x_dist, y_dist):
                self.facing += random.randint(90, 270)
                x_dist = math.cos(self.facing_radians()) * self.genes.idle_speed.value * deltatime
                y_dist = math.sin(self.facing_radians()) * self.genes.idle_speed.value * deltatime

            self.body.actual_x += x_dist
            self.body.actual_y += y_dist

            self.body.x = round(self.body.actual_x)
            self.body.y = round(self.body.actual_y)

            # self.__collide()

        if self.energy <= 0:
            self.__die()


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
        world_rect = pygame.Rect(0, 0, world.internal_rect.width, world.internal_rect.height)
        world_rect.height *= self.zoom_level
        world_rect.width *= self.zoom_level
        world_rect.centerx = self.centre_x + self.x_offset
        world_rect.centery = self.centre_y + self.y_offset

        pygame.draw.rect(surface=self.screen, color=[0, 10 * 0.7, 27 * 0.7], rect=world_rect)

        scale = 1 / self.zoom_level

        # Draw Food
        for food_cluster in world.food_clusters:
            for food in food_cluster.food:
                # Move the Body Part Rect to the correct position
                drawing_rect = pygame.Rect(food.x, food.y, 1, 1)
                drawing_rect.x = world_rect.x + round(drawing_rect.x / scale)
                drawing_rect.y = world_rect.y + round(drawing_rect.y / scale)
                drawing_rect.width *= self.zoom_level
                drawing_rect.height *= self.zoom_level

                if -2 < drawing_rect.x < self.screen.get_width() and -2 < drawing_rect.y < self.screen.get_height():
                    copy_image = food_image.copy()
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
            body_part = creature.body

            # Move the Body Part Rect to the correct position
            # This is important as the position values I give is the top left point of the rectangle,
            # but the point that is stored is the centre point, so I must adjust for that
            rect_left = body_part.x - creature.genes.radius.value
            rect_top = body_part.y - creature.genes.radius.value
            drawing_rect = pygame.Rect(rect_left, rect_top, creature.genes.radius.value * 2, creature.genes.radius.value * 2)
            drawing_rect.x = world_rect.x + round(drawing_rect.x / scale)
            drawing_rect.y = world_rect.y + round(drawing_rect.y / scale)
            drawing_rect.width *= self.zoom_level
            drawing_rect.height *= self.zoom_level

            bound = -(creature.genes.radius.value / scale * 2)

            # Don't draw if the creature is off the screen. Saves program from processing useless things
            if bound < drawing_rect.x < self.screen.get_width() and bound < drawing_rect.y < self.screen.get_height():
                copy_image = creature_image.copy()
                coloured = pygame.PixelArray(copy_image)
                coloured.replace((104, 104, 104), colour_to_draw)
                coloured.replace((255, 255, 255), pattern)
                del coloured

                copy_image = pygame.transform.scale(copy_image, (drawing_rect.w, drawing_rect.h))
                rotated_image = pygame.transform.rotate(copy_image, -(creature.facing + 90))

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


class Button:
    def __init__(self, image: pygame.Surface, x_pos: int, y_pos: int):
        self.rect = pygame.Rect(x_pos, y_pos, image.get_width(), image.get_height())
        self.image = image

        # Create the image of the button when it is hovered/pressed
        self.pressed = self.image.copy()
        pygame.PixelArray(self.pressed).replace((0, 0, 0), (46, 139, 87))

        self.is_hovered = False

    def draw(self, screen: pygame.Surface, x_pos: int, y_pos: int):
        self.rect.x = x_pos
        self.rect.y = y_pos

        if not self.is_hovered:
            screen.blit(self.image, self.rect)
        else:
            screen.blit(self.pressed, self.rect)

    def check_for_hover(self):
        mos_x, mos_y = pygame.mouse.get_pos()
        x_inside = False
        y_inside = False

        if mos_x > self.rect.x and (mos_x < self.rect.x + self.rect.w):
            x_inside = True
        if mos_y > self.rect.y and (mos_y < self.rect.y + self.rect.h):
            y_inside = True
        if x_inside and y_inside:
            self.is_hovered = True
        else:
            self.is_hovered = False

    def check_for_press(self):
        if pygame.mouse.get_pressed()[0] and self.is_hovered:
            return True


class Simulation:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1800, 950), pygame.RESIZABLE)

        pygame.mouse.set_visible(False)
        self.cursor_image = pygame.image.load('textures/cursor.png')
        self.cursor_rect = self.cursor_image.get_rect()

        self.creature_image = pygame.image.load('textures/creature3.png')
        self.food_image = pygame.image.load('textures/food1.png')
        self.menu_background = pygame.image.load('screens/menu_background.png')
        self.logo = pygame.image.load('screens/logo.png')
        self.buttons = {'play': Button(pygame.image.load('screens/buttons/play.png'),
                                       (self.screen.get_width() - 64) // 2,
                                       self.screen.get_height() // 2 - 100)}

        pygame.display.set_caption("Simbiosis - Evolution Simulator")

        self.clock = pygame.time.Clock()

        self.camera = Camera(self.screen)
        self.world = None

        # Menu Booleans
        self.program_running = True
        self.start_menu_screen = True
        self.help_menu = False
        self.load_menu = False
        self.game_being_played = False
        self.world_paused = False
        self.debug_screen = False

    def main(self):
        while self.program_running:
            deltatime = clock.tick(120) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.program_running = False
                elif event.type == pygame.MOUSEWHEEL:
                    self.camera.zoom(event.y)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.world.game_paused = not self.world.game_paused
                    elif event.key == pygame.K_q:
                        self.debug_screen = not self.debug_screen
                    elif event.key == pygame.K_ESCAPE:
                        self.program_running = False

            if self.start_menu_screen:
                self.start_menu()
            elif self.game_being_played:
                if not self.world_paused:
                    self.world.tick_game(deltatime)

                self.camera.move(deltatime)
                self.camera.draw_world(self.world)

            self.cursor_rect.topleft = pygame.mouse.get_pos()
            self.screen.blit(self.cursor_image, self.cursor_rect)

            pygame.display.flip()

    def start_menu(self):
        copy_image = pygame.transform.scale(self.menu_background, self.screen.get_size())
        self.screen.blit(copy_image, (0, 0))

        copy_image = pygame.transform.scale_by(self.logo, 0.4)
        self.screen.blit(copy_image, ((self.screen.get_width() - copy_image.get_width()) // 2, 0))

        play_button = self.buttons['play']
        play_button.draw(self.screen, (self.screen.get_width() - play_button.rect.w) // 2,
                         self.screen.get_height() // 2 - 100)
        play_button.check_for_hover()
        if play_button.check_for_press():
            self.world = World(size=1000, start_species=10, start_creatures=10, start_cluster=200)
            self.game_being_played = True
            self.start_menu_screen = False


simulation = Simulation()
simulation.main()
