# Alpha v0.4
import pygame
from src.world import World, Camera
from src.ui import Button


pygame.init()

creature_image = pygame.image.load('resources/textures/creature3.png')
food_image = pygame.image.load('resources/textures/food1.png')

pygame.display.set_caption("Simbiosis - Evolution Simulator")
pygame.display.set_icon(food_image)

clock = pygame.time.Clock()


class Simulation:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1800, 950), pygame.RESIZABLE)

        # pygame.mouse.set_visible(False)
        # self.cursor_image = pygame.image.load('resources/textures/cursor.png')
        # self.cursor_rect = self.cursor_image.get_rect()

        self.creature_image = pygame.image.load('resources/textures/creature3.png')
        self.food_image = pygame.image.load('resources/textures/food1.png')
        self.menu_background = pygame.image.load('resources/screens/menu_background.png')
        self.logo = pygame.image.load('resources/screens/logo.png')
        self.buttons = {'play': Button('play',
                                       (self.screen.get_width() - 64) // 2,
                                       self.screen.get_height() // 2 - 100),
                        'load': Button('load',
                                       (self.screen.get_width() - 64) // 2,
                                       self.screen.get_height() // 2 - 200),
                        'help': Button('help',
                                       (self.screen.get_width() - 64) // 2,
                                       self.screen.get_height() // 2 - 300)
                        }

        pygame.display.set_caption("Simbiosis - Evolution Simulator")

        self.clock = pygame.time.Clock()

        self.camera = Camera(self.screen)
        self.world: World = World(size=1000, start_species=10, start_creatures=100, start_food=10,
                                  creature_image=self.creature_image, food_image=self.food_image)

        # Menu Booleans
        self.program_running = True
        self.start_menu_screen = True
        self.help_menu = False
        self.load_menu = False
        self.game_being_played = False
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
                        self.world.paused = not self.world.paused
                    elif event.key == pygame.K_q:
                        self.debug_screen = not self.debug_screen
                    elif event.key == pygame.K_ESCAPE:
                        self.program_running = False
                    elif event.key == pygame.K_EQUALS:
                        self.world.change_tick_speed(1)
                    elif event.key == pygame.K_MINUS:
                        self.world.change_tick_speed(-1)

            if self.start_menu_screen:
                self.start_menu()
            elif self.game_being_played:
                if not self.world.paused:
                    self.world.tick_world(deltatime)

                self.camera.move(deltatime)
                self.camera.draw_world(self.world, self.debug_screen)
                self.camera.draw_ui(self.world)

            # self.cursor_rect.topleft = pygame.mouse.get_pos()
            # self.screen.blit(self.cursor_image, self.cursor_rect)

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

        load_button = self.buttons['load']
        load_button.draw(self.screen, (self.screen.get_width() - load_button.rect.w) // 2,
                         self.screen.get_height() // 2 + 15)
        load_button.check_for_hover()
        if load_button.check_for_press():
            ...

        help_button = self.buttons['help']
        help_button.draw(self.screen, (self.screen.get_width() - help_button.rect.w) // 2,
                         self.screen.get_height() // 2 + 130)
        help_button.check_for_hover()
        if help_button.check_for_press():
            ...


simulation = Simulation()
simulation.main()
