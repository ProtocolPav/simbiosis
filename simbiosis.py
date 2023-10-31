# Alpha v0.3b
import math
import copy
import random
import yaml

from datetime import datetime

import pygame
from pygame import Rect

time_now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
logfile = open(f"./logs/log-{time_now}.txt", "w")

logfile.write(f"Start Simbiosis Simulation v0.3\n"
              f"Start Time: {time_now}\n\n\n"
              f"Runtime Logs:\n"
              f"{'-'*60}\n")

pygame.init()

creature_image = pygame.image.load('textures/creature3.png')

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
            species_creature = Creature(random.randint(60, world_size - 60), random.randint(60, world_size - 60))
            for j in range(start_creatures):
                x = species_creature.x_pos() + random.randint(-50, 50)
                y = species_creature.y_pos() + random.randint(-50, 50)
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
        self.energy = random.randint(5000, 75000)
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
        loop_length = 1 + (len(self.food) // 100)*2

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
                    new_food.check_quadrant().food_collisions_dict[new_food.id] = new_food

    def remove_food(self, food: Food):
        if not food.eaten:
            food.eaten = True
            self.food.remove(food)
            food.check_quadrant().food_collisions_dict.pop(food.id)

    def tick_food(self):
        self.food[0].check_quadrant().food_collisions_dict[self.food[0].id] = self.food[0]
        # food_to_remove = []
        #
        # for food in self.food:
        #     food.ticks += 1
        #
        #     if food.ticks >= food.total_ticks:
        #         food_to_remove.append(food)
        #
        # for food in food_to_remove:
        #     self.remove_food(food)


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
        self.head = Gene(name="Head Colour Multiplier", acronym="CLH", value=random.random())
        self.maximum_length = Gene(name="Maximum Length", acronym="LMX", value=random.randint(3, 15))

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

    def __init__(self, position_x: int, position_y: int, genes: CreatureGenes = None, start_energy: float = None):
        log(f"Created Creature with ID{Creature.id}")
        self.id = Creature.id

        self.body = CreatureBody(self.id, position_x, position_y)

        self.genes = CreatureGenes(generation=1, species=1) if genes is None else genes
        if start_energy is None:
            self.energy = self.genes.energy_per_square.value * self.genes.maximum_length.value * 5000
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

            world.creatures.append(baby)

    def __die(self):
        if not self.dead:
            log(f"[DEATH] Creature {self.id}")
            world.creatures.remove(self)
            self.dead = True

    def x_pos(self):
        return self.body.x

    def y_pos(self):
        return self.body.y

    def facing_radians(self):
        return self.facing/(180/math.pi)

    def check_collision_with_border(self, x: float, y: float) -> bool:
        # This isnt perfect as it checks just the centre point of the circle, so it produces some visual bugs
        temp_position: tuple[float, float] = (self.body.actual_x+x, self.body.actual_y+y)

        if temp_position[0] >= world.internal_rect.w - 1 or temp_position[1] >= world.internal_rect.h - 1:
            # Creature is past the border
            return True
        elif temp_position[0] <= 0 or temp_position[1] <= 0:
            # Creature is past the border in the negative directions
            return True

        return False

    def move(self):
        self.energy -= self.genes.energy_per_square.value

        if not self.dead:
            # self.__vision()

            self.energy -= self.genes.energy_per_square.value * len(self.body)

            x_dist = math.cos(self.facing_radians()) * self.genes.idle_speed.value * deltatime
            y_dist = math.sin(self.facing_radians()) * self.genes.idle_speed.value * deltatime

            if self.check_collision_with_border(x_dist, y_dist):
                self.facing += 100
                x_dist = math.cos(self.facing_radians()) * self.genes.idle_speed.value * deltatime
                y_dist = math.sin(self.facing_radians()) * self.genes.idle_speed.value * deltatime

            self.body.actual_x += x_dist
            self.body.actual_y += y_dist

            self.body.x = round(self.body.actual_x)
            self.body.y = round(self.body.actual_y)

            # self.__collide()

            self.body.add_to_collisions()

        if self.energy <= 0:
            self.__die()


class Camera:
    def __init__(self):
        self.screen = pygame.display.set_mode([1000, 700], pygame.RESIZABLE)
        self.zoom_level = 1
        self.camera_speed = 300
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
            colour_to_draw = (int(creature.genes.colour_red.value),
                              int(creature.genes.colour_green.value),
                              int(creature.genes.colour_blue.value))
            pattern = (int(255-creature.genes.colour_red.value),
                       int(255-creature.genes.colour_green.value),
                       int(255-creature.genes.colour_blue.value))
            body_part = creature.body

            # Move the Body Part Rect to the correct position
            drawing_rect = pygame.Rect(body_part.x, body_part.y, 1, 1)
            drawing_rect.x = world_rect.x + round(drawing_rect.x / scale)
            drawing_rect.y = world_rect.y + round(drawing_rect.y / scale)
            drawing_rect.width *= self.zoom_level
            drawing_rect.height *= self.zoom_level

            copy_image = creature_image.copy()
            coloured = pygame.PixelArray(copy_image)
            coloured.replace((104, 104, 104), colour_to_draw)
            coloured.replace((255,255,255), pattern)
            del coloured

            copy_image = pygame.transform.scale(copy_image, (drawing_rect.w*4, drawing_rect.h*4))
            rotated_image = pygame.transform.rotate(copy_image, -(creature.facing + 90))

            # Sets the center of the image to be aligned with the center position
            creature_rect = rotated_image.get_rect(center=drawing_rect.center)
            self.screen.blit(rotated_image, creature_rect)
            # pygame.draw.rect(surface=self.screen, rect=drawing_rect, color=colour_to_draw)
            # pygame.draw.circle(surface=self.screen, center=drawing_rect.center, radius=drawing_rect.w, color=(255, 255, 244))

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
            body_part = creature.body
            pygame.draw.circle(surface=self.screen, center=creature.body.center, radius=1, color=[245, 245, 245])

            if creature.vision_rect is not None:
                pygame.draw.rect(camera.screen, [255, 0, 0], creature.vision_rect)

    def move(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            self.centre_x += self.camera_speed * deltatime
        elif key[pygame.K_d]:
            self.centre_x -= self.camera_speed * deltatime
        elif key[pygame.K_w]:
            self.centre_y += self.camera_speed * deltatime
        elif key[pygame.K_s]:
            self.centre_y -= self.camera_speed * deltatime

    def zoom(self, change: int):
        if 1 <= self.zoom_level + 1 * change <= 10:
            self.zoom_level += 1 * change
            self.camera_speed -= 10 * change


run = True
debug = False
camera = Camera()
world = World(quadrant_size=100, quadrant_rows=8, start_species=100, start_creatures=2, start_cluster=200)

while run:
    deltatime = clock.tick(120) / 1000

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
            # quadrant.food_collisions_dict = {}

    pygame.display.flip()
