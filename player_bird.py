import pygame
from game_object import GameObject
from shape_renderer import ShapeRenderer
import math

class PlayerBird(GameObject):
    def __init__(self, x, y, jump_strength):
        super().__init__()
        self.velocity = 0
        self.jump_strength = jump_strength
        self.angle = 0  # For rotation effect
        self.jump_cooldown = 280
        self.last_jump_time = 0

        # Define the polygon points for the bird (triangle)
        size = 20
        self.points = [
            (0, -size // 2),
            (size // 2, size // 2),
            (-size // 2, size // 2)
        ]

        # Create the polygon surface
        self.image_original = ShapeRenderer.create_polygon_surface(self.points, (255, 255, 0))
        self.image = self.image_original
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, gravity):
        self.velocity += gravity
        self.rect.y += self.velocity

        # Optional: Rotate the bird based on velocity
        self.angle = -self.velocity * 3  # Adjust multiplier for effect
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def jump(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_jump_time >= self.jump_cooldown:
            self.velocity = self.jump_strength
            self.last_jump_time = current_time

    def no_jump(self):
        pass