import pygame


class Button:
    def __init__(self, text: str, x_pos: int, y_pos: int):
        self.image = pygame.image.load('resources/screens/components/button.png')
        self.rect = pygame.Rect(x_pos, y_pos, self.image.get_width(), self.image.get_height())
        self.font = pygame.font.Font('resources/pixel_digivolve.otf', 50)
        self.text = self.font.render(text, False, (0, 0, 0))

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

        # To get the text displayed in the centre of the box:
        # Subtract the width and height of the box and the text and divide by 2
        text_rect = self.rect.copy()
        text_rect.x += (self.rect.w - self.text.get_width()) / 2
        text_rect.y += (self.rect.h - self.text.get_height()) / 2
        screen.blit(self.text, text_rect)

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


class SmallContentDisplay:
    def __init__(self, image: pygame.Surface, content_name: str, x_pos: int, y_pos: int):
        self.image = image
        self.rect = pygame.Rect(x_pos, y_pos, image.get_width(), image.get_height())

        # Create font object
        self.content_font = pygame.font.Font('resources/pixel_digivolve.otf', 20)
        self.value_font = pygame.font.Font('resources/pixel_digivolve.otf', 50)

        self.content_name = self.content_font.render(content_name, False, (108, 122, 103))

    def draw(self, screen: pygame.Surface, value: int, x_pos: int, y_pos: int):
        self.rect.x = x_pos
        self.rect.y = y_pos

        screen.blit(self.image, self.rect)

        # To get the text displayed in the centre of the box:
        # Subtract the width of the box and the text and divide by 2
        content_rect = self.rect.copy()
        content_rect.x += (self.rect.w - self.content_name.get_width()) // 2
        content_rect.y += 15
        screen.blit(self.content_name, content_rect)

        value_text = self.value_font.render(str(value), False, (108, 122, 103))
        value_rect = self.rect.copy()
        value_rect.x += (self.rect.w - value_text.get_width()) // 2
        value_rect.y += 30
        screen.blit(value_text, value_rect)


class LargeContentDisplay:
    ...


class PresetDisplay(LargeContentDisplay):
    ...
