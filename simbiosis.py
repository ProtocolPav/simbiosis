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

from matplotlib import pyplot, font_manager

creature_image = pygame.image.load('resources/textures/creature3.png')
food_image = pygame.image.load('resources/textures/food1.png')

pygame.display.set_caption("Simbiosis - Evolution Simulator")
pygame.display.set_icon(food_image)

clock = pygame.time.Clock()


class Simulation:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)

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
        self.quit_button = Button('quit')
        self.next_graph_button = Button('>', 100)
        self.previous_graph_button = Button('<', 100)
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
        self.world: World = World.create(size=0, start_species=0, start_creatures=0, start_food=0,
                                         food_spawn_rate=1, creature_image=self.creature_image,
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

        # Variables for graphs
        self.graph_types = [{'type': 'creature_count', 'colour': '#6495ED', 'label': 'Number of Creatures'},
                            {'type': 'food_count', 'colour': '#00A36C', 'label': 'Number of Food Pellets'},
                            {'type': 'cumulative_increase_count', 'colour': '#FFBF00', 'label': 'Cumulative Population Increase'},
                            {'type': 'increase_count', 'colour': '#F3E5AB', 'label': 'Population Increase'}]

        self.current_graph = self.graph_types[0]

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
            "data": {'creature_count': self.world.creature_count,
                     'food_count': self.world.food_count,
                     'cumulative_increase_count': self.world.cumulative_increase_count,
                     'increase_count': self.world.increase_count,
                     'death_count': self.world.cumulative_increase_count,
                     'time': self.world.time_data}
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

        self.quit_button.draw(self.screen, (self.screen.get_width() - self.quit_button.rect.w) // 2,
                              self.screen.get_height() // 2 + 245)
        if self.quit_button.check_for_press():
            self.current_menu = 'quit'

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
        titles = [TextDisplay('Choose from specially curated',
                              (217, 255, 200), 50),
                  TextDisplay('presets',
                              (217, 255, 200), 50)
                  ]

        for title in titles:
            index = titles.index(title)
            title.draw(self.screen, (self.screen.get_width() - title.rect.w) // 2,
                       30 + 10 * index + title.rect.height * index)

        self.back_button.draw(self.screen, 15, self.screen.get_height() - self.back_button.rect.h - 15)
        if self.back_button.check_for_press():
            self.current_menu = 'start'

        self.preset_1.draw(self.screen, self.screen.get_width() // 4 - self.preset_1.rect.w, 300)
        if self.preset_1.button.check_for_press():
            self.preset = 'loneisland'
            self.current_menu = 'sim_screen'

        self.preset_2.draw(self.screen, self.screen.get_width() // 4 + self.preset_2.rect.w // 4 + 25, 300)
        if self.preset_2.button.check_for_press():
            self.preset = 'redgreenblue'
            self.current_menu = 'sim_screen'

        self.preset_3.draw(self.screen, self.screen.get_width() // 2 + self.preset_3.rect.w // 4 - 25, 300)
        if self.preset_3.button.check_for_press():
            self.preset = 'evolveplus'
            self.current_menu = 'sim_screen'

        self.preset_4.draw(self.screen, self.screen.get_width() - self.screen.get_width() // 4, 300)
        if self.preset_4.button.check_for_press():
            self.preset = 'random'
            self.world: World = World.create(size=1500, start_species=10, start_creatures=100, start_food=5000,
                                             food_spawn_rate=40, creature_image=self.creature_image,
                                             food_image=self.food_image)
            self.current_menu = 'sim_screen'

        if os.path.exists(f'presets/{self.preset}.json'):
            save_dict = json.load(open(f'presets/{self.preset}.json', 'r'))
            self.world = World.load(save_dict, self.creature_image, self.food_image)
            self.current_menu = 'sim_screen'

    def graph_screen(self):
        copy_image = pygame.transform.scale(self.menu_background, self.screen.get_size())
        self.screen.blit(copy_image, (0, 0))

        # To keep each line in the title centered, I have split them up into their own texts.
        titles = [TextDisplay('View graphs about the',
                              (217, 255, 200), 50),
                  TextDisplay('current simulation',
                              (217, 255, 200), 50)
                  ]

        for title in titles:
            index = titles.index(title)
            title.draw(self.screen, (self.screen.get_width() - title.rect.w) // 2,
                       30 + 10 * index + title.rect.height * index)

        # To keep each line in the title centered, I have split them up into their own texts.
        titles = [TextDisplay('Tip: You can use the arrow keys to navigate too!',
                              (217, 255, 200), 25)
                  ]

        for title in titles:
            index = titles.index(title)
            title.draw(self.screen, (self.screen.get_width() - title.rect.w) // 2,
                       self.screen.get_height() - (60 + 10 * index + title.rect.height * index))

        self.back_button.draw(self.screen, 15, self.screen.get_height() - self.back_button.rect.h - 15)
        if self.back_button.check_for_press():
            self.current_menu = 'sim_screen'

        self.previous_graph_button.draw(self.screen, 50, (self.screen.get_height() - self.back_button.rect.h) // 2)
        if self.previous_graph_button.check_for_press():
            self.paginate_graph(-1)

        self.next_graph_button.draw(self.screen, self.screen.get_width() - self.back_button.rect.w - 50,
                                    (self.screen.get_height() - self.back_button.rect.h) // 2)
        if self.next_graph_button.check_for_press():
            self.paginate_graph(1)

        display_graph = pygame.image.load(f'resources/graphs/{self.current_graph["type"]}.png')
        position = ((self.screen.get_width() - display_graph.get_width()) // 2,
                    (self.screen.get_height() - display_graph.get_height()) // 2)
        self.screen.blit(display_graph, position)

    def draw_graph(self):
        graph_type = self.current_graph

        fig = pyplot.figure(figsize=(12, 7))
        ax: pyplot.Axes = pyplot.subplot()
        prop = font_manager.FontProperties(fname='resources/pixel_digivolve.otf')

        # Set the precision of points
        if len(self.world.time_data) > 3600*7:
            # If interval is 7 hours, one point = 15 minutes
            precision = 600
        elif len(self.world.time_data) > 3600*3:
            # If interval is 3 hours, one point = 1 minute
            precision = 60
        elif len(self.world.time_data) > 60*5:
            # If interval is 5 minutes, one point = 30 seconds
            precision = 30
        else:
            precision = 1

        # Decide on the x-axis labels in seconds, hours or minutes
        if len(self.world.time_data) > 3600:
            mapped_time_data_in_minutes = list(map(lambda x: x / 3600, self.world.time_data[0::precision]))
            mapped_data = self.world.__getattribute__(graph_type['type'])[0::precision]

            ax.set_xlabel("Time (hours)", fontproperties=prop, size=12, color='#caf7b7')
        elif len(self.world.time_data) > 60:
            mapped_time_data_in_minutes = list(map(lambda x: x / 60, self.world.time_data[0::precision]))
            mapped_data = self.world.__getattribute__(graph_type['type'])[0::precision]

            ax.set_xlabel("Time (minutes)", fontproperties=prop, size=12, color='#caf7b7')
        else:
            mapped_time_data_in_minutes = list(map(lambda x: x // 1, self.world.time_data[0::precision]))
            mapped_data = self.world.__getattribute__(graph_type['type'])[0::precision]

            ax.set_xlabel("Time (seconds)", fontproperties=prop, size=12, color='#caf7b7')

        ax.set_ylabel(graph_type['label'], fontproperties=prop, size=12, color='#caf7b7')
        ax.set_title(f'{graph_type["label"]} over Time', fontproperties=prop, size=30, color='#caf7b7')
        ax.grid(visible=True, axis='both', color='#272d35', linestyle='dashed')
        ax.grid(visible=True, axis='x', which='minor', color='#272d35', linestyle='dotted')
        ax.set_facecolor('#000712')
        ax.tick_params(axis='both', colors='#caf7b7')
        ax.margins(0.01)
        ax.plot(mapped_time_data_in_minutes, mapped_data, graph_type['colour'])

        if min(mapped_data) >= 0:
            ax.fill_between(mapped_time_data_in_minutes, mapped_data, min(mapped_data),
                            facecolor=graph_type['colour'], alpha=0.1)
        else:
            ax.fill_between(mapped_time_data_in_minutes, mapped_data, 0, facecolor='#FFBF00', alpha=0.1)
            ax.plot(mapped_time_data_in_minutes, [0 for i in mapped_data], '#D22B2B')

        fig.savefig(f'resources/graphs/{graph_type["type"]}.png', bbox_inches='tight', facecolor="#000712")

        fig.clear()

    def paginate_graph(self, direction: int):
        if direction == 1:
            default = 0
        else:
            default = -1

        index = self.graph_types.index(self.current_graph) + direction
        self.current_graph = self.graph_types[index if index < len(self.graph_types) else default]
        self.draw_graph()

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
            self.draw_graph()

    def main(self):
        while self.program_running:
            deltatime = clock.tick(120) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.program_running = False

                elif event.type == pygame.MOUSEWHEEL:
                    self.camera.zoom(event.y)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.current_menu == 'graph':
                        self.current_menu = 'sim_screen'

                    elif event.key == pygame.K_ESCAPE:
                        self.current_menu = 'start'
                        self.save_slot = 0
                        self.preset = None

                    if event.key == pygame.K_SPACE and self.current_menu == 'sim_screen':
                        self.world.paused = not self.world.paused

                    elif event.key == pygame.K_q and self.current_menu == 'sim_screen':
                        self.debug_screen = not self.debug_screen

                    elif event.key == pygame.K_g and self.current_menu == 'sim_screen':
                        self.current_menu = 'graph'
                        self.draw_graph()

                    elif event.key == pygame.K_EQUALS and self.current_menu == 'sim_screen':
                        self.world.change_tick_speed(1)

                    elif event.key == pygame.K_MINUS and self.current_menu == 'sim_screen':
                        self.world.change_tick_speed(-1)

                    elif event.key == pygame.K_0 and self.current_menu == 'sim_screen':
                        self.save_game()

                    elif event.key == pygame.K_RIGHT and self.current_menu == 'graph':
                        self.paginate_graph(1)

                    elif event.key == pygame.K_LEFT and self.current_menu == 'graph':
                        self.paginate_graph(-1)

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
                    self.graph_screen()

                case 'quit':
                    self.program_running = False

            # self.cursor_rect.topleft = pygame.mouse.get_pos()
            # self.screen.blit(self.cursor_image, self.cursor_rect)

            pygame.display.flip()


simulation = Simulation()
simulation.main()
