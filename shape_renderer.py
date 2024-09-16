import pygame
import math

class ShapeRenderer:
    @staticmethod
    def create_polygon_surface(points, color, width=0):
        # Calculate the bounding box of the polygon
        min_x = min([p[0] for p in points])
        max_x = max([p[0] for p in points])
        min_y = min([p[1] for p in points])
        max_y = max([p[1] for p in points])

        # Create a surface with the size of the bounding box
        width_surf = max_x - min_x
        height_surf = max_y - min_y
        surface = pygame.Surface((width_surf, height_surf), pygame.SRCALPHA)

        # Adjust points to the surface coordinate system
        adjusted_points = [(p[0] - min_x, p[1] - min_y) for p in points]

        # Draw the polygon
        pygame.draw.polygon(surface, color, adjusted_points, width)
        return surface

    @staticmethod
    def create_circle_surface(radius, color, width=0):
        diameter = radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (radius, radius), radius, width)
        return surface

    @staticmethod
    def create_rectangle_surface(width, height, color):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(color)
        return surface