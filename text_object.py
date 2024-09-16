import pygame

class TextObject:
    def __init__(self, text, font, x, y, color=(255, 0, 0), center=False):
        self.text = text
        self.font = font
        self.color = color
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.center = center
        if center:
            self.rect.center = (x, y)
        else:
            self.rect.topleft = (x, y)

    def update_text(self, new_text):
        self.text = new_text
        self.image = self.font.render(self.text, True, self.color)
        # Update rect size if text length changes
        old_rect = self.rect
        self.rect = self.image.get_rect()
        if self.center:
            self.rect.center = old_rect.center
        else:
            self.rect.topleft = old_rect.topleft

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def draw_center(self, surface, y_offset=0):
        # Center the text horizontally with an optional vertical offset
        rect = self.image.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + y_offset))
        surface.blit(self.image, rect)