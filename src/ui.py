import time

import pygame
from src.entity import Creature


class TextDisplay:
    def __init__(self, text: str, colour: tuple[int, int, int], size: int):
        self.font = pygame.font.Font('resources/pixel_digivolve.otf', size)
        self.text = self.font.render(text, False, colour)
        self.rect = pygame.Rect(0, 0, self.text.get_width(), self.text.get_height())

    def draw(self, screen: pygame.Surface, x_pos: int, y_pos: int):
        self.rect.x = x_pos
        self.rect.y = y_pos

        screen.blit(self.text, self.rect)


class Button:
    def __init__(self, text: str, textsize: int = 50):
        self.image = pygame.image.load('resources/screens/components/button.png')
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.text = TextDisplay(text, (0, 0, 0), textsize)

        # Create the image of the button when it is hovered/pressed
        self.pressed = self.image.copy()
        pygame.PixelArray(self.pressed).replace((0, 0, 0), (46, 139, 87))

        self.mouse_down = False

        self.is_hovered = False

    def draw(self, screen: pygame.Surface, x_pos: int, y_pos: int):
        self.rect.x = x_pos
        self.rect.y = y_pos

        if not self.is_hovered:
            screen.blit(self.image, self.rect)
        else:
            screen.blit(self.pressed, self.rect)

        self.text.draw(screen, x_pos + (self.rect.w - self.text.rect.w) // 2, y_pos + (self.rect.h - self.text.rect.h) // 2)

    def change_text(self, text: str, textsize: int = 50):
        self.text = TextDisplay(text, (0, 0, 0), textsize)

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

    def check_for_press(self, delay: float = 0):
        self.check_for_hover()
        if pygame.mouse.get_pressed()[0] and self.is_hovered:
            self.mouse_down = True
        elif not pygame.mouse.get_pressed()[0] and self.mouse_down:
            self.mouse_down = False
            return True


class SmallContentDisplay:
    def __init__(self, content_name: str, x_pos: int, y_pos: int):
        self.image = pygame.image.load('resources/screens/components/contentdisplay.png')
        self.rect = pygame.Rect(x_pos, y_pos, self.image.get_width(), self.image.get_height())

        # Create font object
        self.content_font = pygame.font.Font('resources/pixel_digivolve.otf', 20)
        self.value_font = pygame.font.Font('resources/pixel_digivolve.otf', 40)

        self.content_name = self.content_font.render(content_name, False, (108, 122, 103))

    def draw(self, screen: pygame.Surface, value, x_pos: int, y_pos: int):
        self.rect.x = x_pos
        self.rect.y = y_pos

        screen.blit(self.image, self.rect)

        # To get the text displayed in the centre of the box:
        # Subtract the width of the box and the text and divide by 2
        content_rect = self.rect.copy()
        content_rect.x += (self.rect.w - self.content_name.get_width()) // 2
        content_rect.y += 15
        screen.blit(self.content_name, content_rect)

        if type(value) is int and value >= 1000:
            value = f'{round(value / 1000, 1)}k'
        value_text = self.value_font.render(str(value), False, (108, 122, 103))
        value_rect = self.rect.copy()
        value_rect.x += (self.rect.w - value_text.get_width()) // 2
        value_rect.y += 35
        screen.blit(value_text, value_rect)


class LargeContentDisplay:
    def __init__(self, title_text: str, content: str, long: bool = False):
        if long:
            image = 'longcontentdisplay2'
        else:
            image = 'largecontentdisplay'

        self.image = pygame.image.load(f'resources/screens/components/{image}.png')
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())

        self.title = TextDisplay(title_text, (73, 82, 69), 35)
        self.content = [TextDisplay(line, (102, 122, 103), 20) for line in content.split('\n')]

    def draw(self, screen: pygame.Surface, x_pos: int, y_pos: int):
        self.rect.x = x_pos
        self.rect.y = y_pos

        screen.blit(self.image, self.rect)

        self.title.draw(screen, x_pos + (self.rect.w - self.title.rect.w) // 2, y_pos + 10)

        for line in self.content:
            index = self.content.index(line)
            line.draw(screen, x_pos + (self.rect.w - line.rect.w) // 2, y_pos + 20 + self.title.rect.h + 20*index)


class PresetDisplay(LargeContentDisplay):
    def __init__(self, title_text: str, content: str):
        super().__init__(title_text, content)

        self.button = Button('select', 45)

    def draw(self, screen: pygame.Surface, x_pos: int, y_pos: int):
        super().draw(screen, x_pos, y_pos)
        self.button.draw(screen, x_pos + (self.rect.w - self.button.rect.w) // 2, y_pos + self.rect.h - self.button.rect.h - 15)


class SaveSlotDisplay(LargeContentDisplay):
    def __init__(self, title_text: str, content: str):
        super().__init__(title_text, content)

        self.button: Button = Button('select', 45)

    def draw(self, screen: pygame.Surface, x_pos: int, y_pos: int):
        super().draw(screen, x_pos, y_pos)
        self.button.draw(screen, x_pos + (self.rect.w - self.button.rect.w) // 2, y_pos + self.rect.h - self.button.rect.h - 15)


class CreatureCharacteristicsDisplay(LargeContentDisplay):
    def __init__(self, creature: Creature):
        display_content = (f"ID: {creature.id}\n"
                           f"Species ID: {creature.genes.species.value}\n"
                           f"Generation: {creature.genes.generation.value}\n"
                           f"Energy: {round(creature.energy)} e\n"
                           f"Position: [{round(creature.get_coordinates()[0])}, {round(creature.get_coordinates()[1])}]\n\n"
                           f"---------- GENES ---------\n"
                           f"Colour: [{creature.genes.colour_red.value}, {creature.genes.colour_green.value}, "
                           f"{creature.genes.colour_blue.value}]\n"
                           f"Size: {creature.genes.radius.get_value()*2} px\n"
                           f"Speed: {creature.genes.speed.get_value()} px/s\n"
                           f"Vision Radius: {creature.genes.vision_radius.get_value()} px\n"
                           f"Vision Angle: {creature.genes.vision_angle.get_value()} °\n"
                           f"Reaction Speed: {creature.genes.react_speed.get_value()} °/s\n\n\n"
                           f"--- ENERGY CONSUMPTION ---\n"
                           f"Base: {creature.genes.base_energy.get_value()} e/s\n"
                           f"Movement: {creature.genes.movement_energy.get_value()} e/px\n"
                           f"Turning: {creature.genes.turning_energy.get_value()} e/°\n"
                           f"Birthing: {round(creature.genes.birth_energy.value)} e\n"
                           f"Food: {creature.genes.plant_energy.get_value()*100}% of Plant food\n\n\n"
                           f"-- REACTION PROBABILITIES --\n"
                           f"Towards Something: {creature.genes.react_towards.get_value()}\n"
                           f"Towards Food: {creature.genes.react_towards.get_value() + creature.genes.food_offset.get_value()}\n"
                           f"Towards Stranger: {creature.genes.react_towards.get_value() + creature.genes.stranger_offset.get_value()}\n"
                           f"Towards Same Species: {creature.genes.react_towards.get_value() + creature.genes.known_offset.get_value()}")

        super().__init__("Creature Stats", display_content, long=True)
