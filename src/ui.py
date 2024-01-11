import pygame


class Button:
    def __init__(self, image: pygame.Surface, x_pos: int, y_pos: int):
        self.image = image
        self.rect = pygame.Rect(x_pos, y_pos, image.get_width(), image.get_height())

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


class SmallContentDisplay:
    ...


class LargeContentDisplay:
    ...


class PresetDisplay(LargeContentDisplay):
    ...
