# Alpha v0.4
import os

if not os.path.exists('logs/'):
    os.mkdir('logs/')
if not os.path.exists('saves/'):
    os.mkdir('saves/')

import json

import pygame
from src.world import World, Camera
from src.ui import Button, TextDisplay, LargeContentDisplay, PresetDisplay, SaveSlotDisplay

from datetime import datetime

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

        self.play_button = Button('play')
        self.load_button = Button('load')
        self.help_button = Button('help')
        self.back_button = Button('back')

        pygame.display.set_caption("Simbiosis - Evolution Simulator")

        self.clock = pygame.time.Clock()

        self.camera = Camera(self.screen)
        self.world: World = World(size=1000, start_species=1, start_creatures=1, start_food=1,
                                  creature_image=self.creature_image, food_image=self.food_image)

        # Menu Booleans
        self.program_running = True
        self.debug_screen = False

        # Variable that stores the current menu. Choose from:
        # start, help, load, select_save, select_preset, configure, sim_screen, graph
        self.current_menu = 'start'

    def save_game(self):
        save_dict = {
            "save_data": {
                "time": str(datetime.today()),
                "preset": None
            },
            "world": {
                "size": self.world.size,
                "largest_radius": self.world.largest_radius,
                "food_spawn_rate": self.world.food_spawnrate,
                "tick_speed": self.world.tick_speed,
                "seconds": self.world.seconds,
                "delta_seconds": self.world.delta_second,
                "food_seconds": self.world.food_second,
                "paused": self.world.paused
            },
            "creatures": [],
            "food": [],
            "data": {}
        }

        for creature in self.world.creatures:
            genes = creature.genes
            save_dict['creatures'].append({
                "id": creature.id,
                "energy": creature.energy,
                "direction": creature.direction,
                "dead": creature.dead,
                "seeing": creature.seeing,
                "memory_reaction": creature.memory_reaction,
                "position": [creature.x, creature.y],
                "genes": [genes.colour_red.save_gene(),
                          genes.colour_green.save_gene(),
                          genes.colour_blue.save_gene(),
                          genes.radius.save_gene(),
                          genes.speed.save_gene(),
                          genes.base_energy.save_gene(),
                          genes.movement_energy.save_gene(),
                          genes.turning_energy.save_gene(),
                          genes.birth_energy.save_gene(),
                          genes.plant_energy.save_gene(),
                          genes.vision_radius.save_gene(),
                          genes.vision_angle.save_gene(),
                          genes.react_towards.save_gene(),
                          genes.react_speed.save_gene(),
                          genes.food_offset.save_gene(),
                          genes.stranger_offset.save_gene(),
                          genes.known_offset.save_gene(),
                          genes.species.save_gene(),
                          genes.generation.save_gene()]
            })

        for food in self.world.food:
            save_dict['food'].append({
                "id": food.id,
                "eaten": food.eaten,
                "energy": food.energy,
                "position": [food.x, food.y]
            })

        files_list = os.listdir('saves/')
        save_file = open(f'saves/sim{len(files_list) + 1}.json', 'w')

        json.dump(save_dict, save_file, indent=4)
        save_file.close()

    def main(self):
        while self.program_running:
            deltatime = clock.tick(120) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.program_running = False

                elif event.type == pygame.MOUSEWHEEL:
                    self.camera.zoom(event.y)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.program_running = False

                    if event.key == pygame.K_SPACE and self.current_menu == 'sim_screen':
                        self.world.paused = not self.world.paused
                    elif event.key == pygame.K_q and self.current_menu == 'sim_screen':
                        self.debug_screen = not self.debug_screen
                    elif event.key == pygame.K_EQUALS and self.current_menu == 'sim_screen':
                        self.world.change_tick_speed(1)
                    elif event.key == pygame.K_MINUS and self.current_menu == 'sim_screen':
                        self.world.change_tick_speed(-1)
                    elif event.key == pygame.K_0 and self.current_menu == 'sim_screen':
                        self.save_game()

            match self.current_menu:
                case 'start':
                    self.start_menu()

                case 'load':
                    self.start_menu()

                case 'select_save':
                    self.choose_new_save_menu()

                case 'select_preset':
                    self.choose_preset_menu()

                case 'sim_screen':
                    self.simulation_screen(deltatime)

            # self.cursor_rect.topleft = pygame.mouse.get_pos()
            # self.screen.blit(self.cursor_image, self.cursor_rect)

            pygame.display.flip()

    def start_menu(self):
        copy_image = pygame.transform.scale(self.menu_background, self.screen.get_size())
        self.screen.blit(copy_image, (0, 0))

        copy_image = pygame.transform.scale_by(self.logo, 0.4)
        self.screen.blit(copy_image, ((self.screen.get_width() - copy_image.get_width()) // 2, 0))

        self.play_button.draw(self.screen, (self.screen.get_width() - self.play_button.rect.w) // 2,
                              self.screen.get_height() // 2 - 100)
        self.play_button.check_for_hover()
        if self.play_button.check_for_press():
            self.current_menu = 'select_save'

        self.load_button.draw(self.screen, (self.screen.get_width() - self.load_button.rect.w) // 2,
                              self.screen.get_height() // 2 + 15)
        self.load_button.check_for_hover()
        if self.load_button.check_for_press():
            self.current_menu = 'load'

        self.help_button.draw(self.screen, (self.screen.get_width() - self.help_button.rect.w) // 2,
                              self.screen.get_height() // 2 + 130)
        self.help_button.check_for_hover()
        if self.help_button.check_for_press():
            self.current_menu = 'help'

    def choose_new_save_menu(self):
        copy_image = pygame.transform.scale(self.menu_background, self.screen.get_size())
        self.screen.blit(copy_image, (0, 0))

        # To keep each line in the title centered, I have split them up into their own texts.
        titles = [TextDisplay('Select a save slot',
                              (217, 255, 200), 50),
                  TextDisplay('to save your simulation into.',
                              (217, 255, 200), 50),
                  TextDisplay('Simbiosis auto-saves every 10 minutes.',
                              (217, 255, 200), 50)
                  ]

        for title in titles:
            index = titles.index(title)
            title.draw(self.screen, (self.screen.get_width() - title.rect.w) // 2, 30 + 10 * index + title.rect.height * index)

        self.back_button.draw(self.screen, 15, self.screen.get_height() - self.back_button.rect.h - 15)
        self.back_button.check_for_hover()
        if self.back_button.check_for_press():
            self.current_menu = 'start'

        display_test = SaveSlotDisplay('Slot 1',
                                       '47 January\n \nNo preset selected')
        display_test.draw(self.screen, 500, 500)

    def choose_preset_menu(self):
        copy_image = pygame.transform.scale(self.menu_background, self.screen.get_size())
        self.screen.blit(copy_image, (0, 0))

        # To keep each line in the title centered, I have split them up into their own texts.
        titles = [TextDisplay('Choose from curated',
                              (217, 255, 200), 50),
                  TextDisplay('presets or configure',
                              (217, 255, 200), 50),
                  TextDisplay('your own simulation',
                              (217, 255, 200), 50)
                  ]

        for title in titles:
            index = titles.index(title)
            title.draw(self.screen, (self.screen.get_width() - title.rect.w) // 2, 30 + 10 * index + title.rect.height * index)

        self.back_button.draw(self.screen, 15, self.screen.get_height() - self.back_button.rect.h - 15)
        self.back_button.check_for_hover()
        if self.back_button.check_for_press():
            self.current_menu = 'start'

    def simulation_screen(self, deltatime):
        if not self.world.paused:
            self.world.tick_world(deltatime)

        self.camera.move(deltatime)
        self.camera.draw_world(self.world, self.debug_screen)
        self.camera.draw_ui(self.world)


simulation = Simulation()
simulation.main()
