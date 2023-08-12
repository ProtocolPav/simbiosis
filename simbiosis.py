# Alpha v0.2
import math
import copy
import random
import yaml

from datetime import datetime

import pygame
from pygame import Rect

time_now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
logfile = open(f"./logs/log-{time_now}.txt", "w")

logfile.write(f"Start Simbiosis Simulation v0.2 Alpha\n"
              f"Start Time: {time_now}\n\n\n"
              f"Runtime Logs:\n"
              f"{'-'*60}\n")

pygame.init()

pygame.display.set_caption("SIMbiosis")

clock = pygame.time.Clock()


def log(message: str):
    print(f"[{datetime.now()}]", message)
    logfile.write(f"[{datetime.now()}] {message}\n")


class WorldQuadrant:
    def __init__(self, pos_x: int, pos_y: int, quadrant_size: int):
        self.internal_rect = pygame.Rect(pos_x, pos_y, quadrant_size, quadrant_size)

        self.collisions_dict: dict[int, CreatureBody] = {}
        self.food_collisions_dict: dict[int, Food] = {}


class World:
    def __init__(self, quadrant_size: int, quadrant_rows: int = 2, start_species: int = 4, start_creatures: int = 10,
                 start_cluster: int = 10):
        world_size = quadrant_size * quadrant_rows
        self.internal_rect = pygame.Rect(0, 0, world_size, world_size)
        self.borders = [pygame.Rect(0, -1, world_size, 1),
                        pygame.Rect(-1, 0, 1, world_size),
                        pygame.Rect(0, world_size, world_size, 1),
                        pygame.Rect(world_size, 0, 1, world_size)]
        self.creatures: list[Creature] = []
        self.food_clusters: list[FoodCluster] = []
        self.ticks = 0
        self.game_paused = False

        self.quadrants = []
        for x in range(quadrant_rows):
            for y in range(quadrant_rows):
                log(f"Appending {x * quadrant_size, y * quadrant_size, quadrant_size}")
                self.quadrants.append(WorldQuadrant(x * quadrant_size, y * quadrant_size, quadrant_size))

        for i in range(start_species):
            species_creature = Creature(random.randint(0, world_size - 1), random.randint(0, world_size - 1))
            for j in range(start_creatures):
                x = species_creature.x_pos() + random.randint(-5, 5)
                y = species_creature.y_pos() + random.randint(-5, 5)
                self.creatures.append(Creature(x, y, genes=copy.deepcopy(species_creature.genes)))

        for i in range(start_cluster):
            cluster = FoodCluster(random.randint(1, self.internal_rect.w - 1),
                                  random.randint(1, self.internal_rect.h - 1))
            self.food_clusters.append(cluster)

    def tick_game(self):
        if not self.game_paused:
            if random.choices(population=["no", "spawn cluster"], weights=[499, 1])[0] == "spawn cluster":
                self.food_clusters.append(FoodCluster(random.randint(1, self.internal_rect.w - 1),
                                                      random.randint(1, self.internal_rect.h - 1)))

            for cluster in self.food_clusters:
                if len(cluster.food) == 0:
                    self.food_clusters.remove(cluster)
                else:
                    cluster.spawn_food(self.internal_rect)
                    cluster.tick_food()

            for creature in self.creatures:
                creature.move()

            for creature in self.creatures:
                creature.collide()

    def get_creature(self, creature_id):
        for creat in self.creatures:
            if creat.id == creature_id:
                return creat


class Food(pygame.Rect):
    id = 0

    def __init__(self, pos_x: int, pos_y: int, time_to_live: int, parent_cluster):
        super().__init__(pos_x, pos_y, 1, 1)
        self.id = Food.id
        self.total_ticks = time_to_live
        self.ticks = 0
        self.cluster = parent_cluster
        self.energy = random.randint(5000, 10000)
        self.eaten = False

        Food.id += 1

    def __repr__(self):
        return f"Food({self.id}, {self.x}, {self.y})"

    def check_quadrant(self) -> WorldQuadrant:
        coordinates = (self.x, self.y)

        for quad in world.quadrants:
            y_check = quad.internal_rect.topleft[1] < coordinates[1] < quad.internal_rect.bottomright[1]
            x_check = quad.internal_rect.topleft[0] < coordinates[0] < quad.internal_rect.bottomright[0]

            if x_check and y_check:
                return quad

        return world.quadrants[0]


class FoodCluster:
    id = 0

    def __init__(self, centre_x: int, centre_y: int):
        self.food: list[Food] = [Food(centre_x, centre_y, 500, self)]

    def spawn_food(self, world_rect: Rect):
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
                self.food.append(Food(food_rect.x, food_rect.y, random.randint(50, 500), self))

    def remove_food(self, food: Food):
        if not food.eaten:
            food.eaten = True
            self.food.remove(food)

    def tick_food(self):
        food_to_remove = []

        for food in self.food:
            food.ticks += 1

            if food.ticks >= food.total_ticks:
                food_to_remove.append(food)
            else:
                food.check_quadrant().food_collisions_dict[food.id] = food

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

    def check_quadrant(self) -> WorldQuadrant:
        coordinates = (self.x, self.y)

        for quad in world.quadrants:
            y_check = quad.internal_rect.topleft[1] < coordinates[1] < quad.internal_rect.bottomright[1]
            x_check = quad.internal_rect.topleft[0] < coordinates[0] < quad.internal_rect.bottomright[0]

            if y_check and x_check:
                return quad

        return world.quadrants[0]

    def add_to_collisions(self):
        quadrant = self.check_quadrant()

        quadrant.collisions_dict[self.id] = self

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
            if random.choices(population=["mutate", "no mutate"], weights=[299, 1])[0] == "mutate":
                self.value += random.uniform(-0.2, 0.2)

                if self.acronym in ['CLR', 'CLB', 'CLG']:
                    self.value += random.randint(2, 2)
                    if self.value < 0:
                        self.value = 10
                    elif self.value > 255:
                        self.value = 245

                if self.acronym in ['CLH', 'RTL', 'RTR', 'RTB', 'RTF', 'RBO', 'RLF', 'RRF', 'RBF', 'RFF']:
                    if self.value < 0:
                        self.value = abs(self.value)
                    elif self.value > 1:
                        self.value -= 1


class CreatureGenes:
    def __init__(self, species: int, generation: int):
        # Genes affecting Creature Appearance (Phenotype)
        self.colour_red = Gene(name="Red Colour", acronym="CLR", value=random.randint(0, 255))
        self.colour_green = Gene(name="Green Colour", acronym="CLG", value=random.randint(0, 255))
        self.colour_blue = Gene(name="Blue Colour", acronym="CLB", value=random.randint(0, 255))
        self.head = Gene(name="Head Colour Multiplier", acronym="CLH", value=random.random())
        self.maximum_length = Gene(name="Maximum Length", acronym="LMX", value=random.randint(3, 10))

        # Genes affecting Creature movement
        self.idle_speed = Gene(name="Idle Speed", acronym="SID", value=random.uniform(0, 2))
        self.maximum_speed = Gene(name="Maximum Speed", acronym="SMX", value=random.uniform(self.idle_speed.value, 10))
        self.boost_length = Gene(name="Boost Length in Ticks", acronym="BOL", value=random.uniform(0, 20))

        # Genes affecting the Creature's Energy Consumption
        self.energy_per_square = Gene(name="Energy Consumed Per Square Moved", acronym="EPS", value=random.uniform(5, 100))
        self.energy_during_boost = Gene(name="Energy Consumed During Boost", acronym="EBS",
                                        value=random.uniform(self.energy_per_square.value, 200))
        self.energy_to_birth = Gene(name="Energy Consumed To Birth", acronym="EBI", value=random.uniform(5, 100))
        self.energy_to_extend = Gene(name="Energy Consumed To Extend", acronym="EEX", value=random.uniform(5, 100))
        self.critical_hunger = Gene(name="Critical Hunger Level", acronym="HUC",
                                    value=random.uniform(self.energy_per_square.value, 200))

        # Genes affecting Creature Behaviour
        self.vision = Gene(name="Vision", acronym="VIS", value=random.uniform(1, 10))
        self.collision = Gene(name="Collision Behaviour", acronym="COL", value=random.uniform(0, 1))
        self.react_left = Gene(name="Brain Reaction Left", acronym="RTL", value=random.random())
        self.react_right = Gene(name="Brain Reaction Right", acronym="RTR", value=random.random())
        self.react_back = Gene(name="Brain Reaction Back", acronym="RTB", value=random.random())
        self.react_forward = Gene(name="Brain Reaction Forward", acronym="RTF", value=random.random())
        self.react_boost = Gene(name="Brain Reaction Boost", acronym="RBO", value=random.random())
        self.react_left_food = Gene(name="Brain Reaction Left When Seeing Food", acronym="RLF", value=random.random())
        self.react_right_food = Gene(name="Brain Reaction Right When Seeing Food", acronym="RRF", value=random.random())
        self.react_back_food = Gene(name="Brain Reaction Back When Seeing Food", acronym="RBF", value=random.random())
        self.react_forward_food = Gene(name="Brain Reaction Forward When Seeing Food", acronym="RFF", value=random.random())

        # Data Genes (No mutation, affects Data)
        self.gender = Gene(name="Gender", acronym="GND", value=random.choice([0, 1]), can_mutate=False)
        self.species = Gene(name="Species", acronym="SPE", value=species, can_mutate=False)
        self.generation = Gene(name="Generation", acronym="GEN", value=generation, can_mutate=False)


class Creature:
    id = 1

    def __init__(self, position_x: int, position_y: int, genes: CreatureGenes = None):
        log(f"Created Creature with ID{Creature.id}")
        self.id = Creature.id

        self.body: list[CreatureBody] = [CreatureBody(self.id, position_x, position_y),
                                         CreatureBody(self.id, position_x - 1, position_y)]

        self.genes = CreatureGenes(generation=1, species=1) if genes is None else genes
        self.energy = self.genes.energy_per_square.value * self.genes.maximum_length.value * 5000

        self.facing = random.choice(['right', 'left', 'up', 'down'])
        self.vision_rect = None
        self.dead = False
        self.colliding = False
        self.seeing = False

        Creature.id += 1

    def __repr__(self):
        return f"Creature(ID{self.id}, Body({self.body}))"

    def __move_x(self, direction: int):
        last_body_part = self.body.pop()

        if world.internal_rect.width - 1 <= self.body[0].x:
            # On the rightmost border, so the creature must not face right
            self.facing = random.choice(['down', 'up', 'left'])
            last_body_part.actual_x = self.body[0].actual_x - 1
            last_body_part.actual_y = self.body[0].actual_y
        elif self.body[0].x <= 0:
            # On the leftmost border, so creature must not face left
            self.facing = random.choice(['down', 'up', 'right'])
            last_body_part.actual_x = self.body[0].actual_x + 1
            last_body_part.actual_y = self.body[0].actual_y
        else:
            last_body_part.actual_x = self.body[0].actual_x - direction
            last_body_part.actual_y = self.body[0].actual_y

        last_body_part.x = round(last_body_part.actual_x)
        last_body_part.y = round(last_body_part.actual_y)

        self.body.insert(0, last_body_part)

    def __move_y(self, direction: int):
        last_body_part = self.body.pop()

        if world.internal_rect.height - 1 <= self.body[0].y:
            # On Bottom border, so creature must not face down
            self.facing = random.choice(['up', 'right', 'left'])
            last_body_part.actual_x = self.body[0].actual_x
            last_body_part.actual_y = self.body[0].actual_y - 1
        elif self.body[0].y <= 0:
            # On top border, so creature must not face up
            self.facing = random.choice(['down', 'right', 'left'])
            last_body_part.actual_x = self.body[0].actual_x
            last_body_part.actual_y = self.body[0].actual_y + 1
        else:
            last_body_part.actual_x = self.body[0].actual_x
            last_body_part.actual_y = self.body[0].actual_y - direction

        last_body_part.x = round(last_body_part.actual_x)
        last_body_part.y = round(last_body_part.actual_y)

        self.body.insert(0, last_body_part)

    def __vision(self):
        choice_list = ['left', 'right', 'down', 'up']
        vision_distance = self.genes.vision.value
        quadrant_check = self.body[0].check_quadrant()
        difference = pygame.Vector2(self.body[0].x - self.body[1].x, self.body[0].y - self.body[1].y)

        # Facing Upwards
        if difference == pygame.Vector2(0, -1):
            self.vision_rect = pygame.Rect(self.body[0].x, self.body[0].y - vision_distance, 1, 1 + vision_distance)
            choice_list = ['right', 'left', 'up', 'down']

        # Facing Downwards
        elif difference == pygame.Vector2(0, 1):
            self.vision_rect = pygame.Rect(self.body[0].x, self.body[0].y + 1, 1, vision_distance)
            choice_list = ['left', 'right', 'down', 'up']

        # Facing Left
        elif difference == pygame.Vector2(-1, 0):
            self.vision_rect = pygame.Rect(self.body[0].x - vision_distance, self.body[0].y, 1 + vision_distance, 1)
            choice_list = ['up', 'down', 'left', 'right']

        # Facing Right
        elif difference == pygame.Vector2(1, 0):
            self.vision_rect = pygame.Rect(self.body[0].x + 1, self.body[0].y, vision_distance, 1)
            choice_list = ['down', 'up', 'right', 'left']

        collision = self.vision_rect.collidedict(quadrant_check.collisions_dict, True)
        food_collision = self.vision_rect.collidedict(quadrant_check.food_collisions_dict, True)
        border_collision = self.vision_rect.collidelist(world.borders)

        if collision and not self.seeing and self.id != collision[1].creature_id:
            # log(f"Creature {self.id} is seeing something and reacting")
            self.seeing = True
            self.facing = random.choices(choice_list,
                                         [self.genes.react_right.value,
                                          self.genes.react_left.value,
                                          self.genes.react_forward.value,
                                          self.genes.react_back.value])[0]

        elif food_collision and not self.seeing:
            self.seeing = True
            self.facing = random.choices(choice_list,
                                         [self.genes.react_right_food.value,
                                          self.genes.react_left_food.value,
                                          self.genes.react_forward_food.value,
                                          self.genes.react_back_food.value])[0]

        elif border_collision != -1:
            self.facing = random.choices(choice_list,
                                         [self.genes.react_right.value,
                                          self.genes.react_left.value,
                                          self.genes.react_forward.value,
                                          self.genes.react_back.value])[0]

        elif collision is None and food_collision is None and self.seeing:
            self.seeing = False

    def __collide(self):
        choice_list = ['left', 'right', 'down', 'up']
        quadrant_check = self.body[0].check_quadrant()
        collision = self.body[0].collision_check(quadrant_check.collisions_dict)
        difference = pygame.Vector2(self.body[0].x - self.body[1].x, self.body[0].y - self.body[1].y)

        # Facing Upwards
        if difference == pygame.Vector2(0, -1):
            choice_list = ['right', 'left', 'up', 'down']

        # Facing Downwards
        elif difference == pygame.Vector2(0, 1):
            choice_list = ['left', 'right', 'down', 'up']

        # Facing Left
        elif difference == pygame.Vector2(-1, 0):
            choice_list = ['up', 'down', 'left', 'right']

        # Facing Right
        elif difference == pygame.Vector2(1, 0):
            choice_list = ['down', 'up', 'right', 'left']

        if collision and not self.colliding:
            if self.id != collision.creature_id:
                self.colliding = True

                creature = world.get_creature(collision.creature_id)

                # Get other creature and check the creature's collision value.
                # Collision affects the creature that collided with the other creature, depending on the other's genes
                if creature:
                    if 0 < creature.genes.collision.value < 1:
                        self.__birth()
                    if 0.75 < creature.genes.collision.value:
                        self.__die()

        elif not collision and self.colliding:
            self.colliding = False

        food_collision = self.body[0].collision_check(quadrant_check.food_collisions_dict)
        if food_collision:
            self.energy += food_collision.energy
            food_collision.cluster.remove_food(food_collision)
            self.__extend()
            self.facing = choice_list[0]

    def __extend(self):
        if self.energy - self.genes.energy_to_extend.value > self.genes.critical_hunger.value \
                and len(self.body) + 1 < self.genes.maximum_length.value:
            self.energy -= self.genes.energy_to_extend.value
            self.body.append(CreatureBody(self.id, self.body[-1].x, self.body[-1].y))

    def __birth(self):
        if len(self.body) >= 4:
            self.energy -= self.genes.energy_to_birth.value
            body_part = self.body.pop()
            body_part = self.body.pop()

            baby = Creature(body_part.x, body_part.y, copy.deepcopy(self.genes))

            for gene, gene_object in vars(baby.genes).items():
                gene_object.mutate()

            world.creatures.append(baby)

    def __die(self):
        if not self.dead:
            log(f"Killing Creature {self.id}")
            world.creatures.remove(self)
            self.dead = True

    def x_pos(self):
        return self.body[0].x

    def y_pos(self):
        return self.body[0].y

    def move(self):
        self.energy -= self.genes.energy_per_square.value

        for i in range(0, math.ceil(self.genes.idle_speed.value)):
            if not self.dead:
                self.__vision()

                self.energy -= self.genes.energy_per_square.value * len(self.body)

                if self.facing == "up":
                    self.__move_y(-1)
                elif self.facing == "down":
                    self.__move_y(1)
                elif self.facing == "left":
                    self.__move_x(-1)
                elif self.facing == "right":
                    self.__move_x(1)

                # self.__collide()

                for body in self.body:
                    body.add_to_collisions()

        if self.energy <= 0:
            self.__die()

    def collide(self):
        self.__collide()


class Camera:
    def __init__(self):
        self.screen = pygame.display.set_mode([1000, 700], pygame.RESIZABLE)
        self.zoom_level = 2
        self.camera_speed = 40
        self.centre_x = self.screen.get_width() // 2
        self.centre_y = self.screen.get_height() // 2

    def draw(self, world: World):
        # Draw Background Colour
        pygame.draw.rect(surface=self.screen,
                         color=[0, 10, 27],
                         rect=[[0, 0], [self.screen.get_width(), self.screen.get_height()]])

        # Draw Border
        world_rect = pygame.Rect(0, 0, world.internal_rect.width, world.internal_rect.height)
        world_rect.height *= self.zoom_level
        world_rect.width *= self.zoom_level
        world_rect.centerx = self.centre_x
        world_rect.centery = self.centre_y

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

                pygame.draw.rect(surface=self.screen, rect=drawing_rect, color=[170, 255, 170])

        # Draw Creatures
        for creature in world.creatures:
            for body_part in creature.body:
                colour_to_draw = [int(creature.genes.colour_red.value),
                                  int(creature.genes.colour_green.value),
                                  int(creature.genes.colour_blue.value)]

                if creature.body.index(body_part) == 0:
                    colour_to_draw = [int(colour * creature.genes.head.value) for colour in colour_to_draw]

                # Move the Body Part Rect to the correct position
                drawing_rect = pygame.Rect(body_part.x, body_part.y, 1, 1)
                drawing_rect.x = world_rect.x + round(drawing_rect.x / scale)
                drawing_rect.y = world_rect.y + round(drawing_rect.y / scale)
                drawing_rect.width *= self.zoom_level
                drawing_rect.height *= self.zoom_level

                pygame.draw.rect(surface=self.screen, rect=drawing_rect, color=colour_to_draw)

    def debug_draw(self, world: World):
        pygame.draw.rect(surface=self.screen, color=[0, 10 * 0.7, 27 * 0.7], rect=world.internal_rect)
        colour_change = 210 / len(world.quadrants)
        colour = 30
        for world_quadrant in world.quadrants:
            pygame.draw.rect(surface=self.screen, color=[0, colour, colour], rect=world_quadrant.internal_rect)
            colour += colour_change

        for food_cluster in world.food_clusters:
            for food in food_cluster.food:
                pygame.draw.rect(surface=self.screen, rect=food, color=[0, 255, 0])

        for creature in world.creatures:
            for body_part in creature.body:
                pygame.draw.rect(surface=self.screen, rect=body_part, color=[245, 245, 245])

            if creature.vision_rect is not None:
                pygame.draw.rect(camera.screen, [255, 0, 0], creature.vision_rect)

    def move(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            self.centre_x += self.camera_speed
        elif key[pygame.K_d]:
            self.centre_x -= self.camera_speed
        elif key[pygame.K_w]:
            self.centre_y += self.camera_speed
        elif key[pygame.K_s]:
            self.centre_y -= self.camera_speed

    def zoom(self, change: int):
        if 2 <= self.zoom_level + 2 * change <= 20:
            self.zoom_level += 2 * change
            self.camera_speed -= 2 * change


run = True
debug = False
camera = Camera()
world = World(quadrant_size=100, quadrant_rows=4, start_species=5, start_creatures=10, start_cluster=100)

while run:
    deltatime = clock.tick(25)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEWHEEL:
            camera.zoom(event.y)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                world.game_paused = not world.game_paused
            elif event.key == pygame.K_q:
                debug = not debug

    world.tick_game()

    camera.move()
    camera.draw(world)
    camera.debug_draw(world) if debug else ...

    if not world.game_paused:
        for quadrant in world.quadrants:
            index = world.quadrants.index(quadrant)
            quadrant.collisions_dict = {}
            quadrant.food_collisions_dict = {}

    pygame.display.flip()
