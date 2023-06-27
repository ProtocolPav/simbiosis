import pygame, random

logfile = open("./log.txt", "w")

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

BORDER_SIZE = 300

PIXEL = 10
CAMERA_SPEED = 6

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.RESIZABLE)
pygame.display.set_caption("SIMbiosis")

clock = pygame.time.Clock()

def draw_background():
    pygame.draw.rect(surface=screen, color=[0,10,27], rect=[[0, 0], [screen.get_width(), screen.get_height()]])

def draw_grid():
    draw_background()
    for x in range(screen.get_width()//PIXEL):
        for y in range(screen.get_height()//PIXEL):
            rect = pygame.Rect(x*PIXEL, y*PIXEL, PIXEL, PIXEL)
            pygame.draw.rect(screen, [50,50,50], rect, 1)

class BodyPart(pygame.Rect):
    body_part_id = 0

    def __init__(self, left: float, top: float, width: float, height: float, creature_id: int):
        super().__init__(left, top, width, height)
        BodyPart.body_part_id += 1
        self.id = BodyPart.body_part_id
        self.creature_id = creature_id

        # print(f"ADDED NEW PART {self.id} FOR CREATURE {self.creature_id}")
        logfile.write(f"ADDED NEW PART {self.id} FOR CREATURE {self.creature_id}\n")

        collisions.add_body_part(self)

    def kill_bodypart(self):
        collisions.remove_body_part(self)

        # print(f"KILLED BODY {self.id} FROM CREATURE {self.creature_id}")
        logfile.write(f"KILLED BODY {self.id} FROM CREATURE {self.creature_id}\n")

    def __repr__(self):
        return f"BodyPart(ID{self.id}, Creature{self.creature_id}, {self.left}, {self.top}, {self.width}, {self.height})"


class Creature:
    creature_id = 0

    def __init__(self, x: int, y: int, length: int, r:int, g: int, b: int):
        Creature.creature_id += 1
        self.killed = False
        self.id = Creature.creature_id
        self.body: list[BodyPart] = []
        self.birth_count = 0
        self.colour = [r, g, b]
        self.speed = random.randint(1, 5)
        self.energy = random.randint(2000, 50000)
        self.vis = random.randint(1, 10)
        self.vision_rect = None
        self.seeing_something = False
        self.collided = False
        self.moving_camera = False
        self.facing = random.choice(['right', 'left', 'up', 'down'])
        random_nums = [random.random(), random.random(), 1, random.random()]
        normalization_number = 1/sum(random_nums)
        for i in random_nums:
            index = random_nums.index(i)
            random_nums[index] = i*normalization_number

        self.rtl = random_nums[0]
        self.rtr = random_nums[1]
        self.rkg = random_nums[2]
        self.rgb = random_nums[3]
        self.head_colour_multiplier = random.random()

        for i in range(length):
            x_coord = x - PIXEL*i
            y_coord = y
            bodypart = BodyPart(x_coord, y_coord, PIXEL, PIXEL, self.id)
            self.body.append(bodypart)

    def __repr__(self):
        return f"Creature ID {self.id}"

    def draw(self):
        for body_part in self.body:
            if self.body.index(body_part) == 0:
                colour_to_draw = [colour*self.head_colour_multiplier for colour in self.colour]
            else:
                colour_to_draw = self.colour
            pygame.draw.rect(surface=screen, rect=body_part, color=colour_to_draw)

    def draw_vision(self):
        pygame.draw.rect(screen, [255, 0, 0], self.vision_rect)

    def creature_camera(self, x: int = 0, y: int = 0):
        self.moving_camera = True
        for body_part in self.body:
            body_part.x += x
            body_part.y += y
        self.moving_camera = False

    def move_x(self, positive: bool):
        last_body_part = self.body.pop()

        if border.border_rect.right - PIXEL <= self.body[0].x:
            # On the rightmost border, so the creature must not face right
            self.facing = random.choice(['down', 'up', 'left'])
            last_body_part.x = self.body[0].x - PIXEL
            last_body_part.y = self.body[0].y
        elif self.body[0].x <= border.border_rect.left:
            # On the leftmost border, so creature must not face left
            self.facing = random.choice(['down', 'up', 'right'])
            last_body_part.x = self.body[0].x + PIXEL
            last_body_part.y = self.body[0].y
        else:
            last_body_part.x = (self.body[0].x + PIXEL) if positive else (self.body[0].x - PIXEL)
            last_body_part.y = self.body[0].y

        self.body.insert(0, last_body_part)

        for body in self.body:
            collisions.add_body_part(body)

    def move_y(self, positive: bool):
        last_body_part = self.body.pop()

        if border.border_rect.bottom - PIXEL <= self.body[0].y:
            # On Bottom border, so creature must not face down
            self.facing = random.choice(['up', 'right', 'left'])
            last_body_part.x = self.body[0].x
            last_body_part.y = self.body[0].y - PIXEL
        elif self.body[0].y <= border.border_rect.top:
            # On top border, so creature must not face up
            self.facing = random.choice(['down', 'right', 'left'])
            last_body_part.x = self.body[0].x
            last_body_part.y = self.body[0].y + PIXEL
        else:
            last_body_part.x = self.body[0].x
            last_body_part.y = (self.body[0].y + PIXEL) if positive else (self.body[0].y - PIXEL)

        self.body.insert(0, last_body_part)

        for body in self.body:
            collisions.add_body_part(body)

    def move(self):
        for i in range(self.speed):
            self.vision()
            self.collision()
            self.energy -= 2 * len(self.body)
            if not self.killed and not self.moving_camera:
                if self.facing == "up":
                    self.move_y(False)
                elif self.facing == "down":
                    self.move_y(True)
                elif self.facing == "right":
                    self.move_x(True)
                elif self.facing == "left":
                    self.move_x(False)

        if random.randint(1, 100) == 4:
            self.extend_creature()

        if self.energy <= 0:
            self.kill_creature()

    def vision(self):
        vision_rect = None
        choice_list = ['left', 'right', 'down', 'up']

        if not self.killed:
            if self.body[0].x == self.body[1].x:
                if self.body[1].y - self.body[0].y == PIXEL:
                    # Facing Upwards
                    vision_rect = pygame.Rect(self.body[0].x, self.body[0].y - PIXEL*self.vis, PIXEL, PIXEL*self.vis)
                    choice_list = ['right', 'left', 'up', 'down']
                elif self.body[1].y - self.body[0].y == -PIXEL:
                    # Facing Downwards
                    vision_rect = pygame.Rect(self.body[0].x, self.body[0].y + PIXEL, PIXEL, PIXEL * self.vis)
                    choice_list = ['left', 'right', 'down', 'up']
            elif self.body[0].y == self.body[1].y:
                if self.body[1].x - self.body[0].x == PIXEL:
                    # Facing Left
                    vision_rect = pygame.Rect(self.body[0].x - PIXEL*self.vis, self.body[0].y, PIXEL*self.vis, PIXEL)
                    choice_list = ['up', 'down', 'left', 'right']
                elif self.body[1].x - self.body[0].x == -PIXEL:
                    # Facing Right
                    vision_rect = pygame.Rect(self.body[0].x + PIXEL, self.body[0].y, PIXEL*self.vis, PIXEL)
                    choice_list = ['down', 'up', 'right', 'left']

            self.vision_rect = vision_rect

            collided_bodypart = vision_rect.collidedict(collisions.collisions, True)
            if collided_bodypart and not self.seeing_something:
                self.seeing_something = True
                self.facing = random.choices(choice_list,
                                             [self.rtr, self.rtl, self.rkg, self.rgb])[0]
            elif collided_bodypart is None and self.seeing_something:
                self.seeing_something = False

    def collision(self):
        if not self.killed:
            collided_part = self.body[0].collidedict(collisions.collisions, True)
            own_body_part = False
            if collided_part and not self.collided:
                for part in self.body:
                    if part.id == int(collided_part[0]):
                        own_body_part = True

                if not own_body_part:
                    self.collided = True
                    random_num = random.randint(1, 10)
                    if random_num in [1,2,3,4,5,6,7,8]:
                        self.birth()
                    if random_num in [2,4,6,8,10]:
                        self.kill_creature()

            elif collided_part is None and self.collided:
                self.collided = False

    def kill_creature(self):
        if not self.killed:
            # print(f"KILLING CREATURE{self.id}: {self.body}")
            logfile.write(f"KILLING CREATURE{self.id}: {self.body}\n")
            self.killed = True
            length = len(self.body)
            for part in range(length):
                body_part = self.body[part]
                # print(f"SENT PART{body_part.id} FOR KILLING")
                logfile.write(f"SENT PART{body_part.id} FOR KILLING\n")
                body_part.kill_bodypart()

            self.body = []

            creatures.remove(self)

    def birth(self):
        if self.birth_count < 100 and len(self.body) > 6:
            # self.birth_count += 1
            self.energy -= 1000
            body_part = self.body.pop()
            collisions.remove_body_part(body_part)
            body_part = self.body.pop()
            collisions.remove_body_part(body_part)

            new_colour = self.colour

            # if random.randint(1, 1000) == 100:
            #     mutation = (1 * random.choice([-1, 1])) * random.random()
            #     new_colour = [int(self.colour[0] + self.colour[0] * mutation),
            #                   int(self.colour[1] + self.colour[1] * mutation),
            #                   int(self.colour[2] + self.colour[2] * mutation)]

            creatures.append(Creature(self.body[0].x, self.body[0].y, 5,
                                      r=new_colour[0],
                                      g=new_colour[1],
                                      b=new_colour[2]))

    def extend_creature(self):
        if not self.killed:
            bodypart = BodyPart(self.body[-1].x+PIXEL, self.body[-1].y, PIXEL, PIXEL, self.id)
            self.body.append(bodypart)

    def adjust_for_zoom(self, scale_factor: float):
        for body_part in self.body:
            body_part.width, body_part.height = PIXEL, PIXEL

            body_part.x = round(body_part.x / scale_factor)
            body_part.y = round(body_part.y / scale_factor)


class Border:
    def __init__(self):
        self.BORDER_SIZE = BORDER_SIZE
        self.OUTLINE_SIZE = BORDER_SIZE + 1
        self.border_rect = pygame.Rect(0, 0, self.BORDER_SIZE*PIXEL, self.BORDER_SIZE*PIXEL)
        self.border_outline_rect = pygame.Rect(-5, -5, self.OUTLINE_SIZE*PIXEL, self.OUTLINE_SIZE*PIXEL)

    def draw_border(self):
        pygame.draw.rect(screen, [0, 20, 27], self.border_outline_rect, PIXEL)
        pygame.draw.rect(screen, [0,10*0.7,27*0.7], self.border_rect)

    def border_camera(self, x: int = 0, y: int = 0):
        self.border_rect.x += x
        self.border_rect.y += y

        self.border_outline_rect.x += x
        self.border_outline_rect.y += y

    def adjust_for_zoom(self, scale_factor: float):
        self.border_rect.width, self.border_outline_rect.width = self.BORDER_SIZE*PIXEL, self.OUTLINE_SIZE*PIXEL
        self.border_rect.height, self.border_outline_rect.height = self.BORDER_SIZE*PIXEL, self.OUTLINE_SIZE*PIXEL

        self.border_rect.x = round(self.border_rect.x / scale_factor)
        self.border_rect.y = round(self.border_rect.y / scale_factor)

        self.border_outline_rect.x = round(self.border_outline_rect.x / scale_factor)
        self.border_outline_rect.y = round(self.border_outline_rect.y / scale_factor)


class Collisions:
    def __init__(self):
        self.collisions = {}
        self.queue_to_add = []
        self.queue_to_remove = []
        self.dead_ids = []

    def load_body(self, body: list[BodyPart]):
        for part in body:
            self.queue_to_add.append(part)

    def add_body_part(self, bodypart: BodyPart):
        self.queue_to_add.append(bodypart)

    def remove_body_part(self, bodypart: BodyPart):
        self.queue_to_remove.append(bodypart)

    def update_dict(self):
        self.collisions = {}

        for part in self.queue_to_add:
            self.collisions[f"{part.id}"] = part

        self.queue_to_add = []

        # if len(self.queue_to_add) > 0:
        #     for bodypart in self.queue_to_add:
        #         if bodypart.id not in self.dead_ids:
        #             self.collisions[f"{bodypart.id}"] = bodypart
        #
        #             self.queue_to_add.remove(bodypart)

        # if len(self.queue_to_remove) > 0:
        #     for bodypart in self.queue_to_remove:
        #         if self.collisions.get(f"{bodypart.id}", "NOTHING FOUND") != "NOTHING FOUND":
        #             print(f"POPPING BODY{bodypart.id}")
        #             logfile.write(f"POPPING BODY{bodypart.id}\n")
        #
        #             body = self.collisions.pop(f"{bodypart.id}")
        #
        #             self.queue_to_remove.remove(body)
        #             self.dead_ids.append(bodypart.id)


run = True
collisions = Collisions()
creatures = []
for i in range(500):
    colour = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    creatures.append(Creature(PIXEL*random.randint(2, BORDER_SIZE-10),
                              PIXEL*random.randint(2, BORDER_SIZE-10),
                              random.randint(3, 16),
                              r = colour[0],
                              g = colour[1],
                              b = colour[2]
                              ))
border = Border()
ticks = 0
game_paused = False
while run:
    ticks += 1
    if not game_paused and ticks%30 == 0:
        print(len(collisions.collisions), len(creatures))
        logfile.write(f"{collisions.collisions}\n")

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_paused = not game_paused

        elif event.type == pygame.MOUSEWHEEL:
            if 2 <= PIXEL + 2*event.y <= 30:
                old_pixel_size = PIXEL
                PIXEL += 2 * event.y

                scale = old_pixel_size/PIXEL

                border.adjust_for_zoom(scale)

                for creature in creatures:
                    creature.adjust_for_zoom(scale)

    key = pygame.key.get_pressed()

    draw_background()
    # draw_grid()
    border.draw_border()


    for creature in creatures:
        if not game_paused:
            creature.move()

        creature.draw()

        if key[pygame.K_d]:
            creature.creature_camera(x=-PIXEL*CAMERA_SPEED)
        elif key[pygame.K_s]:
            creature.creature_camera(y=-PIXEL*CAMERA_SPEED)
        elif key[pygame.K_w]:
            creature.creature_camera(y=PIXEL*CAMERA_SPEED)
        elif key[pygame.K_a]:
            creature.creature_camera(x=PIXEL*CAMERA_SPEED)
        elif key[pygame.K_q]:
            creature.draw_vision()


    if key[pygame.K_d]:
        border.border_camera(x=-PIXEL*CAMERA_SPEED)
    elif key[pygame.K_s]:
        border.border_camera(y=-PIXEL*CAMERA_SPEED)
    elif key[pygame.K_w]:
        border.border_camera(y=PIXEL*CAMERA_SPEED)
    elif key[pygame.K_a]:
        border.border_camera(x=PIXEL*CAMERA_SPEED)
    elif key[pygame.K_q]:
        for rectid, rect in collisions.collisions.items():
            pygame.draw.rect(surface=screen, rect=rect, color=[255,255,255])

    collisions.update_dict()

    pygame.display.flip()
    clock.tick(25)

pygame.quit()