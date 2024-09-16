import pygame

class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = None  # Will be set in subclasses
        self.rect = None   # Will be set in subclasses

    def update(self):
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)