import pygame
from game_object import GameObject

class PlayerBird(GameObject):
    def __init__(self, x, y):
        super().__init__()
        self.radius = 15
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 0), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 0
        self.jump_strength = -10
        self.pipe_gap = 150

    def update(self, gravity):
        self.velocity += gravity
        self.rect.y += self.velocity

    def jump(self):
        self.velocity = self.jump_strength