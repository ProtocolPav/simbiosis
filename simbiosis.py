# Alpha v0.4
import os
import random
import time

if not os.path.exists('logs/'):
    os.mkdir('logs/')
if not os.path.exists('saves/'):
    os.mkdir('saves/')

import json

import pygame
from src.world import World, Camera
from src.ui import Button, TextDisplay, SmallContentDisplay, PresetDisplay, SaveSlotDisplay

from datetime import datetime, timedelta

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
        self.no_save_slot_button = Button('Play without\n     saving', 23)

        self.save_display_1 = SaveSlotDisplay('Slot 1',
                                              'Empty')
        self.save_display_2 = SaveSlotDisplay('Slot 2',
                                              'Empty')
        self.save_display_3 = SaveSlotDisplay('Slot 3',
                                              'Empty')
        self.save_display_4 = SaveSlotDisplay('Slot 4',
                                              'Empty')

        self.generate_save_slot_displays()

        self.preset_1 = PresetDisplay('Lone Island',
                                      'two species compete\nfor one island of food\nlocated in the centre.\n'
                                      'they are complete\nopposites.\nwho will win?')
        self.preset_2 = PresetDisplay('RedGreenBlue',
                                      'the reds, the greens\nand the blues exist in\n'
                                      'one world. their\ncolour defines the\nspecies. how many new\ncolours will be made?')
        self.preset_3 = PresetDisplay('Evolve+',
                                      'an environment\ndesigned to foster\nevolution. everything\n'
                                      'is precisely adjusted.\nwatch as the species\ngrow and change.')
        self.preset_4 = PresetDisplay('Random',
                                      'A completely random\nset of species.\nWill you get\nlucky?')

        self.sim_screen_pause_button = Button('Pause')
        self.sim_screen_tickspeed_button = Button('x1')
        self.sim_screen_graph_button = Button('Graphs', 45)

        self.sim_screen_time_display = SmallContentDisplay('time', 5, 5)
        self.sim_screen_creature_display = SmallContentDisplay('creatures', 5, 5)
        self.sim_screen_species_display = SmallContentDisplay('species', 5, 5)
        self.sim_screen_food_display = SmallContentDisplay('food', 5, 5)

        pygame.display.set_caption("Simbiosis - Evolution Simulator")

        self.clock = pygame.time.Clock()

        self.camera = Camera(self.screen)
        self.world: World = World.create(size=1500, start_species=10, start_creatures=100, start_food=5000,
                                         food_spawn_rate=40, creature_image=self.creature_image,
                                         food_image=self.food_image)

        # Menu Booleans
        self.program_running = True
        self.debug_screen = False

        # Variable that stores the current menu. Choose from:
        # start, help, load, select_save, select_preset, configure, sim_screen, graph
        self.current_menu = 'start'

        # Variable that holds the save slot
        self.save_slot = 0
        self.preset = None

    def generate_save_slot_displays(self):
        attributes = ['save_display_1', 'save_display_2', 'save_display_3', 'save_display_4']

        for attr in attributes:
            slot_num = attr[-1]
            if os.path.exists(f'saves/sim{slot_num}.json'):
                save_dict = json.load(open(f'saves/sim{slot_num}.json', 'r'))

                date = datetime.strptime(save_dict['save_data']['time'], "%Y-%m-%d %H:%M:%S.%f")
                formatted_date = date.strftime('%B %d %Y\n%I:%M%p')

                preset = f"Preset: {save_dict['save_data']['preset']}" if save_dict['save_data']['preset'] else "No Preset"
                self.__setattr__(attr, SaveSlotDisplay(f'Slot {slot_num}',
                                                       f'{formatted_date}\n\n{preset}'))

    def save_game(self):
        save_dict = {
            "save_data": {
                "time": str(datetime.today()),
                "preset": self.preset
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
            save_genes = []

            for gene_name, value in genes.__dict__.items():
                save_genes.append(value.save_gene(gene_name))

            save_dict['creatures'].append({
                "id": creature.id,
                "energy": creature.energy,
                "direction": creature.direction,
                "dead": creature.dead,
                "seeing": creature.seeing,
                "memory_reaction": creature.memory_reaction,
                "position": [creature.x, creature.y],
                "genes": save_genes
            })

        for food in self.world.food:
            save_dict['food'].append({
                "id": food.id,
                "eaten": food.eaten,
                "energy": food.energy,
                "position": [food.x, food.y]
            })

        save_file = open(f'saves/sim{self.save_slot}.json', 'w')

        json.dump(save_dict, save_file, indent=4)
        save_file.close()

    def start_menu(self):
        copy_image = pygame.transform.scale(self.menu_background, self.screen.get_size())
        self.screen.blit(copy_image, (0, 0))

        copy_image = pygame.transform.scale_by(self.logo, 0.4)
        self.screen.blit(copy_image, ((self.screen.get_width() - copy_image.get_width()) // 2, 0))

        self.play_button.draw(self.screen, (self.screen.get_width() - self.play_button.rect.w) // 2,
                              self.screen.get_height() // 2 - 100)
        if self.play_button.check_for_press():
            self.current_menu = 'select_save'

        self.load_button.draw(self.screen, (self.screen.get_width() - self.load_button.rect.w) // 2,
                              self.screen.get_height() // 2 + 15)
        if self.load_button.check_for_press():
            self.current_menu = 'load'

        self.help_button.draw(self.screen, (self.screen.get_width() - self.help_button.rect.w) // 2,
                              self.screen.get_height() // 2 + 130)
        if self.help_button.check_for_press():
            self.current_menu = 'help'

    def load_save_menu(self):
        copy_image = pygame.transform.scale(self.menu_background, self.screen.get_size())
        self.screen.blit(copy_image, (0, 0))

        # To keep each line in the title centered, I have split them up into their own texts.
        titles = [TextDisplay('Select a save slot',
                              (217, 255, 200), 50),
                  TextDisplay('to load from.',
                              (217, 255, 200), 50),
                  TextDisplay('Simbiosis auto-saves every 10 minutes.',
                              (217, 255, 200), 50)
                  ]

        for title in titles:
            index = titles.index(title)
            title.draw(self.screen, (self.screen.get_width() - title.rect.w) // 2,
                       30 + 10 * index + title.rect.height * index)

        self.back_button.draw(self.screen, 15, self.screen.get_height() - self.back_button.rect.h - 15)
        if self.back_button.check_for_press():
            self.current_menu = 'start'

        self.save_display_1.draw(self.screen, self.screen.get_width() // 4 - self.save_display_1.rect.w, 300)
        if self.save_display_1.button.check_for_press():
            self.save_slot = 1

        self.save_display_2.draw(self.screen, self.screen.get_width() // 4 + self.save_display_2.rect.w // 4 + 25, 300)
        if self.save_display_2.button.check_for_press():
            self.save_slot = 2

        self.save_display_3.draw(self.screen, self.screen.get_width() // 2 + self.save_display_3.rect.w // 4 - 25, 300)
        if self.save_display_3.button.check_for_press():
            self.save_slot = 3

        self.save_display_4.draw(self.screen, self.screen.get_width() - self.screen.get_width() // 4, 300)
        if self.save_display_4.button.check_for_press():
            self.save_slot = 4

        if os.path.exists(f'saves/sim{self.save_slot}.json'):
            save_dict = json.load(open(f'saves/sim{self.save_slot}.json', 'r'))
            self.world = World.load(save_dict, self.creature_image, self.food_image)
            self.preset = save_dict['save_data']['preset']
            self.current_menu = 'sim_screen'

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
            title.draw(self.screen, (self.screen.get_width() - title.rect.w) // 2,
                       30 + 10 * index + title.rect.height * index)

        self.back_button.draw(self.screen, 15, self.screen.get_height() - self.back_button.rect.h - 15)
        if self.back_button.check_for_press():
            self.current_menu = 'start'

        self.save_display_1.draw(self.screen, self.screen.get_width() // 4 - self.save_display_1.rect.w, 300)
        if self.save_display_1.button.check_for_press(0.1):
            self.save_slot = 1
            self.current_menu = 'select_preset'

        self.save_display_2.draw(self.screen, self.screen.get_width() // 4 + self.save_display_2.rect.w // 4 + 25, 300)
        if self.save_display_2.button.check_for_press(0.1):
            self.save_slot = 2
            self.current_menu = 'select_preset'

        self.save_display_3.draw(self.screen, self.screen.get_width() // 2 + self.save_display_3.rect.w // 4 - 25, 300)
        if self.save_display_3.button.check_for_press(0.1):
            self.save_slot = 3
            self.current_menu = 'select_preset'

        self.save_display_4.draw(self.screen, self.screen.get_width() - self.screen.get_width() // 4, 300)
        if self.save_display_4.button.check_for_press(0.1):
            self.save_slot = 4
            self.current_menu = 'select_preset'

        self.no_save_slot_button.draw(self.screen, (self.screen.get_width() - self.no_save_slot_button.rect.w) // 2,
                                      self.screen.get_height() - 200)
        if self.no_save_slot_button.check_for_press(0.1):
            self.save_slot = 5
            self.current_menu = 'select_preset'

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
            title.draw(self.screen, (self.screen.get_width() - title.rect.w) // 2,
                       30 + 10 * index + title.rect.height * index)

        self.back_button.draw(self.screen, 15, self.screen.get_height() - self.back_button.rect.h - 15)
        if self.back_button.check_for_press():
            self.current_menu = 'start'

        self.preset_1.draw(self.screen, self.screen.get_width() // 4 - self.preset_1.rect.w, 400)
        if self.preset_1.button.check_for_press():
            self.preset = 'loneisland'
            self.current_menu = 'sim_screen'

        self.preset_2.draw(self.screen, self.screen.get_width() // 4 + self.preset_2.rect.w // 4 + 25, 400)
        if self.preset_2.button.check_for_press():
            self.preset = 'redgreenblue'
            self.current_menu = 'sim_screen'

        self.preset_3.draw(self.screen, self.screen.get_width() // 2 + self.preset_3.rect.w // 4 - 25, 400)
        if self.preset_3.button.check_for_press():
            self.preset = 'evolveplus'
            self.current_menu = 'sim_screen'

        self.preset_4.draw(self.screen, self.screen.get_width() - self.screen.get_width() // 4, 400)
        if self.preset_4.button.check_for_press():
            self.preset = 'random'
            self.current_menu = 'sim_screen'

        if os.path.exists(f'presets/{self.preset}.json'):
            save_dict = json.load(open(f'presets/{self.preset}.json', 'r'))
            self.world = World.load(save_dict, self.creature_image, self.food_image)
            self.current_menu = 'sim_screen'

    def simulation_screen(self, deltatime):
        if not self.world.paused:
            self.world.tick_world(deltatime)

        self.camera.move(deltatime)
        self.camera.draw_world(self.world, self.debug_screen)

        BUTTON_SIZE = 100

        world_time = timedelta(seconds=round(self.world.seconds))
        self.sim_screen_time_display.draw(self.screen, world_time, 10, 15)
        self.sim_screen_creature_display.draw(self.screen, len(self.world.creatures), 10, BUTTON_SIZE + 30)
        self.sim_screen_species_display.draw(self.screen, 1, 10, BUTTON_SIZE * 2 + 45)
        self.sim_screen_food_display.draw(self.screen, len(self.world.food), 10, BUTTON_SIZE * 3 + 60)

        self.sim_screen_pause_button.draw(self.screen, 10, self.screen.get_height() - BUTTON_SIZE - 15)
        if self.sim_screen_pause_button.check_for_press():
            self.world.paused = not self.world.paused

        if self.world.paused:
            self.sim_screen_pause_button.change_text('play')
        else:
            self.sim_screen_pause_button.change_text('pause')

        self.sim_screen_tickspeed_button.draw(self.screen, 10, self.screen.get_height() - BUTTON_SIZE * 2 - 30)
        if self.sim_screen_tickspeed_button.check_for_press():
            if self.world.tick_speed < 10:
                self.world.change_tick_speed(1)
            else:
                self.world.tick_speed = 1
        self.sim_screen_tickspeed_button.change_text(f'x{self.world.tick_speed}')

        self.sim_screen_graph_button.draw(self.screen, self.screen.get_width() - BUTTON_SIZE * 2 - 20,
                                          self.screen.get_height() - BUTTON_SIZE - 15)
        if self.sim_screen_graph_button.check_for_press():
            self.current_menu = 'graph'

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
                        self.current_menu = 'start'

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
                    self.load_save_menu()

                case 'select_save':
                    self.choose_new_save_menu()

                case 'select_preset':
                    self.choose_preset_menu()

                case 'help':
                    ...

                case 'sim_screen':
                    self.simulation_screen(deltatime)

                case 'graph':
                    self.simulation_screen(deltatime)

            # self.cursor_rect.topleft = pygame.mouse.get_pos()
            # self.screen.blit(self.cursor_image, self.cursor_rect)

            pygame.display.flip()


simulation = Simulation()
simulation.main()
