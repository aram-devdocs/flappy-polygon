import pygame
from game_object import GameObject

class Pipe(GameObject):
    def __init__(self, x, y, height, speed, is_top=True):
        super().__init__()
        self.image = pygame.Surface((60, height))
        self.image.fill((34, 139, 34))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.scored = False  # Flag to check if the bird has passed this pipe
        self.is_top = is_top  # Indicates whether this is the top or bottom pipe

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()