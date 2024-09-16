import pygame
from game_object import GameObject
from shape_renderer import ShapeRenderer

class Pipe(GameObject):
    def __init__(self, x, y, width, height, speed, is_top=True):
        super().__init__()
        self.speed = speed
        self.scored = False  # Flag to check if the bird has passed this pipe
        self.is_top = is_top  # Indicates whether this is the top or bottom pipe

        # Create the rectangle surface for the pipe
        self.image = ShapeRenderer.create_rectangle_surface(width, height, (34, 139, 34))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()