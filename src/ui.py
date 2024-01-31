import pygame
from datetime import datetime, timedelta


class Button:
    def __init__(self, text: str, x_pos: int, y_pos: int):
        self.image = pygame.image.load('resources/screens/components/button.png')
        self.rect = pygame.Rect(x_pos, y_pos, self.image.get_width(), self.image.get_height())
        self.font = pygame.font.Font('resources/pixel_digivolve.otf', 50)
        self.text = self.font.render(text, False, (0, 0, 0))

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

        # To get the text displayed in the centre of the box:
        # Subtract the width and height of the box and the text and divide by 2
        text_rect = self.rect.copy()
        text_rect.x += (self.rect.w - self.text.get_width()) / 2
        text_rect.y += (self.rect.h - self.text.get_height()) / 2
        screen.blit(self.text, text_rect)

    def change_text(self, text: str):
        self.text = self.font.render(text, False, (0, 0, 0))

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
        # The time check is to make sure that you can't just hold down the button
        if pygame.mouse.get_pressed()[0] and self.is_hovered and datetime.now() - self.last_pressed > timedelta(seconds=0.2):
            self.last_pressed = datetime.now()
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
    ...


class PresetDisplay(LargeContentDisplay):
    ...
