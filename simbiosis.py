# Alpha v0.4
import pygame
from src.world import World, Camera


pygame.init()

creature_image = pygame.image.load('textures/creature3.png')
food_image = pygame.image.load('textures/food1.png')

pygame.display.set_caption("Simbiosis - Evolution Simulator")

clock = pygame.time.Clock()


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
        self.world: World = World(size=1000, start_species=10, start_creatures=100, start_food=100,
                                  creature_image=self.creature_image, food_image=self.food_image)

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
                        self.world_paused = not self.world_paused
                    elif event.key == pygame.K_q:
                        self.debug_screen = not self.debug_screen
                    elif event.key == pygame.K_ESCAPE:
                        self.program_running = False

            if self.start_menu_screen:
                self.start_menu()
            elif self.game_being_played:
                if not self.world_paused:
                    self.world.tick_world(deltatime)

                self.camera.move(deltatime)
                self.camera.draw_world(self.world, self.debug_screen)

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
            self.game_being_played = True
            self.start_menu_screen = False


simulation = Simulation()
simulation.main()
