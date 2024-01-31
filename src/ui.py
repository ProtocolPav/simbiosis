import time

import pygame
from datetime import datetime, timedelta


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

        self.last_pressed = datetime.now()

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
        # The time check is to make sure that you can't just hold down the button
        # Optional delay between a button press and action. Mainly for the menu screens
        if pygame.mouse.get_pressed()[0] and self.is_hovered and datetime.now() - self.last_pressed > timedelta(seconds=0.2):
            self.last_pressed = datetime.now()
            time.sleep(delay)
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
    def __init__(self, title_text: str, content: str):
        self.image = pygame.image.load('resources/screens/components/largecontentdisplay.png')
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
